import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from pipeline_tools.planning import (
    append_progress,
    finalize_evidence,
    planning_preflight,
    validate_project_facts,
    validate_requirement_facts,
    validate_task_plan,
)


def chain():
    return {
        'entry': ['cli.py'],
        'interaction': ['cli.py'],
        'application': ['app.py'],
        'domain': ['domain.py'],
        'persistence': ['db.py'],
        'readback': ['app.py'],
        'recovery': ['app.py'],
    }


class PlanningTests(unittest.TestCase):
    def _write_valid_finalization_fixture(self, directory):
        directory.mkdir(parents=True)
        for name, role in (
            ('executor-report.md', 'executor'),
            ('review-report.md', 'reviewer'),
            ('final-check.md', 'main-final'),
        ):
            (directory / name).write_text(
                '```pipeline-evidence\n' + json.dumps({
                    'schema': 1, 'task_id': 'demo', 'worktree': 'worktree',
                    'branch': 'branch', 'role': role, 'round': 1, 'status': 'PASS',
                    'commands': [{'command': 'python -m unittest', 'exit_code': 0, 'evidence_ref': name}],
                    'assertions': ['verified'], 'evidence_refs': [name], 'unverified': [],
                }) + '\n```\n', encoding='utf-8'
            )
        for name, role in (('executor-result.json', 'executor'), ('reviewer-result.json', 'reviewer')):
            (directory / name).write_text(json.dumps({
                'schema': 1, 'task_id': 'demo', 'role': role, 'status': 'pass',
                'acceptance': [{'id': 'acceptance-test-1', 'status': 'pass', 'exit_code': 0, 'evidence_refs': [name]}],
                'unverified': [],
            }), encoding='utf-8')
        (directory / 'final-result.json').write_text(json.dumps({
            'schema': 1, 'task_id': 'demo', 'role': 'main-final', 'status': 'pass',
            'decision': 'READY_FOR_EVIDENCE_FINALIZATION',
            'acceptance': [{'id': 'acceptance-test-1', 'status': 'pass', 'exit_code': 0, 'evidence_refs': ['final-check.md']}],
            'unverified': [],
        }), encoding='utf-8')

    def test_planning_preflight(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / '.git').mkdir()
            self.assertEqual(planning_preflight(root)['status'], 'blocked')
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            result = planning_preflight(root)
            self.assertEqual(result['status'], 'blocked')
            self.assertIn('requirements_sha256', result)

    def test_planning_preflight_accepts_non_repository_target_when_tool_checkout_is_valid(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            result = planning_preflight(root)
            self.assertTrue(any('Git' in error or 'worktree' in error for error in result['errors']))
            self.assertNotIn('pipeline tool command failed', result['errors'])

    def test_planning_preflight_rejects_tool_command_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            result = planning_preflight(root, tool_available=False)
            self.assertIn('pipeline tool unavailable', result['errors'])
            self.assertEqual(result['status'], 'blocked')

    def test_planning_preflight_records_failure_without_overwriting_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / '.git').mkdir()
            (root / '.workflow').mkdir()
            (root / '.pipeline').mkdir()
            (root / '.pipeline' / 'sentinel').write_text('keep', encoding='utf-8')
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            result = planning_preflight(root)
            self.assertEqual(result['status'], 'blocked')
            self.assertFalse((root / '.pipeline' / 'planning').exists())
            self.assertEqual((root / '.pipeline' / 'sentinel').read_text(encoding='utf-8'), 'keep')

    def test_planning_preflight_rejects_unstable_plan_placeholder(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / '.git').mkdir()
            (root / 'implement-plan.md').write_text('TODO: fill this in', encoding='utf-8')
            result = planning_preflight(root)
            self.assertEqual(result['status'], 'blocked')
            self.assertIsNone(result['requirements_sha256'])

    def test_planning_preflight_detects_hash_and_worktree_drift(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'base'], cwd=root, check=True)
            first = planning_preflight(root)
            self.assertEqual(first['status'], 'pass')
            (root / 'implement-plan.md').write_text('changed requirements', encoding='utf-8')
            drift = planning_preflight(root, expected_requirements_sha256=first['requirements_sha256'], expected_branch='wrong')
            self.assertEqual(drift['status'], 'blocked')
            self.assertTrue(any('hash' in error or 'branch' in error for error in drift['errors']))

    def test_planning_preflight_rejects_workflow_pipeline_conflict_without_migration(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / '.git').mkdir()
            (root / '.workflow').mkdir()
            (root / '.pipeline').mkdir()
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            result = planning_preflight(root)
            self.assertEqual(result['status'], 'blocked')
            self.assertTrue(any('workflow' in error and 'pipeline' in error for error in result['errors']))

    def test_requirement_facts_validation_requires_sources_and_complete_tests(self):
        valid = {
            'schema': 1,
            'sources': [{'id': 'plan', 'path': 'implement-plan.md'}],
            'requirements': [{'id': 'r1', 'source_refs': ['plan']}],
            'operations': [{'id': 'create', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{
                'id': 'acceptance-test-1',
                'evidence_level': 1,
                'test_ref': 'tests/test_planning.py: test_requirement_facts_validation_requires_sources_and_complete_tests',
                'command_ref': 'python -m unittest tests.test_planning -v',
            }],
        }
        self.assertEqual(validate_requirement_facts(valid), [])
        self.assertTrue(validate_requirement_facts(dict(valid, sources=[])))
        self.assertTrue(validate_requirement_facts({**valid, 'operations': [{'id': 'create'}]}))

    def test_task_plan_rejects_missing_coverage_and_invalid_derived_parent(self):
        plan = {
            'schema': 1,
            'requirements': ['r1', 'r2'],
            'resources': ['src/app.py', 'src/db.py'],
            'operations': [
                {'id': 'create', 'acceptance_tests': ['acceptance-test-1']},
                {'id': 'read', 'acceptance_tests': ['acceptance-test-2']},
            ],
            'acceptance_tests': [
                {'id': 'acceptance-test-1', 'evidence_level': 1, 'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'},
                {'id': 'acceptance-test-2', 'evidence_level': 1, 'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'},
            ],
            'tasks': [{
                'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                'resources': ['src/app.py'], 'operations': ['create'],
                'chain': chain(), 'depends_on': [],
            }],
        }
        errors = validate_task_plan(plan)
        self.assertTrue(any('coverage' in error or 'uncovered' in error for error in errors))
        derived = dict(plan)
        derived['requirements'] = ['r1']
        derived['resources'] = ['src/app.py']
        derived['operations'] = [{'id': 'create', 'acceptance_tests': ['acceptance-test-1']}]
        derived['tasks'] = [dict(plan['tasks'][0], type='derived', parent_task_id='missing')]
        self.assertTrue(any('derived' in error or 'parent' in error for error in validate_task_plan(derived)))

    def test_task_plan_rejects_missing_top_level_acceptance_records(self):
        plan = {
            'schema': 1, 'requirements': ['r1'], 'resources': ['src/app.py'],
            'operations': [{'id': 'create', 'acceptance_tests': ['acceptance-test-1']}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['src/app.py'], 'operations': ['create'],
                       'chain': chain(), 'depends_on': []}],
        }
        errors = validate_task_plan(plan)
        self.assertTrue(any('top-level' in error and 'acceptance' in error for error in errors))

    def test_task_plan_requires_complete_top_level_acceptance_records(self):
        base = {
            'schema': 1, 'requirements': ['r1'], 'resources': ['src/app.py'],
            'operations': [{'id': 'create', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 1,
                                  'test_ref': 'tests/test_planning.py',
                                  'command_ref': 'python -m unittest'}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['src/app.py'], 'operations': ['create'],
                       'chain': chain(), 'depends_on': []}],
        }
        for bad in (
            dict(base, acceptance_tests=[]),
            dict(base, acceptance_tests=[{'id': 'acceptance-test-1'}]),
            dict(base, acceptance_tests=[base['acceptance_tests'][0], dict(base['acceptance_tests'][0])]),
            dict(base, acceptance_tests=[dict(base['acceptance_tests'][0], id='acceptance-test-2')]),
        ):
            self.assertTrue(validate_task_plan(bad), bad)
        self.assertEqual(validate_task_plan(base), [])

    def test_project_facts_validation(self):
        valid = {
            'schema': 1,
            'sources': [{'id': 'app', 'path': 'src/app.py'}],
            'resources': [{'id': 'app', 'path': 'src/app.py'}],
            'operations': [{'id': 'create', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{
                'id': 'acceptance-test-1', 'evidence_level': 1,
                'test_ref': 'tests/test_planning.py: test_project_facts_validation',
                'command_ref': 'python -m unittest tests.test_planning -v',
            }],
            'chain': chain(),
        }
        self.assertEqual(validate_project_facts(valid), [])
        bad = dict(valid, sources=[])
        self.assertTrue(validate_project_facts(bad))
        bad_path = dict(valid, resources=[{'id': 'escape', 'path': '../outside.py'}])
        self.assertTrue(validate_project_facts(bad_path, Path.cwd()))

    def test_project_facts_rejects_operation_without_acceptance_binding(self):
        valid = {
            'schema': 1,
            'sources': [{'id': 'app', 'path': 'src/app.py'}],
            'resources': [{'id': 'app', 'path': 'src/app.py'}],
            'operations': [{'id': 'create'}],
            'chain': chain(),
        }
        errors = validate_project_facts(valid)
        self.assertTrue(any('acceptance' in error for error in errors))

    def test_project_facts_rejects_empty_chain_without_not_applicable_reason(self):
        valid = {
            'schema': 1,
            'sources': [{'id': 'app', 'path': 'src/app.py'}],
            'resources': [{'id': 'app', 'path': 'src/app.py'}],
            'operations': ['create'],
            'chain': {**chain(), 'persistence': []},
        }
        errors = validate_project_facts(valid)
        self.assertTrue(any('persistence' in error for error in errors))
        valid['chain']['persistence'] = {'not_applicable': True, 'reason': 'no persistence in this project'}
        self.assertEqual(validate_project_facts(valid), [])

    def test_task_plan_validation(self):
        plan = {
            'schema': 1,
            'requirements': ['r1'],
            'resources': ['src/app.py'],
            'operations': [{'id': 'create', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{
                'id': 'acceptance-test-1', 'evidence_level': 1,
                'test_ref': 'tests/test_planning.py: test_task_plan_validation',
                'command_ref': 'python -m unittest tests.test_planning -v',
            }],
            'tasks': [{
                'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                'resources': ['src/app.py'], 'operations': ['create'],
                'chain': chain(), 'depends_on': [],
            }],
        }
        self.assertEqual(validate_task_plan(plan), [])
        self.assertTrue(validate_task_plan(dict(plan, tasks=[dict(plan['tasks'][0], depends_on=['t1'])])))

    def test_progress_is_role_scoped_and_append_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            first = append_progress(root, 'demo', 'executor', {'event': 'started'})
            append_progress(root, 'demo', 'executor', {'event': 'finished'})
            self.assertEqual(first.name, 'executor-progress.jsonl')
            self.assertEqual(len(first.read_text(encoding='utf-8').splitlines()), 2)
            with self.assertRaises(ValueError):
                append_progress(root, '../escape', 'executor', {'event': 'bad'})
            with self.assertRaises(ValueError):
                append_progress(root, 'demo', 'executor', {'token': '= secret'})
            with self.assertRaises(ValueError):
                append_progress(root, 'demo', 'executor', {'task_id': 'other'})
            (root / '.pipeline' / 'linked').symlink_to(root.parent, target_is_directory=True)
            with self.assertRaises(ValueError):
                append_progress(root, 'linked', 'executor', {'event': 'escape'})

    def test_progress_rejects_sensitive_nested_values_and_keeps_task_sheet_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sheet = root / 'docs' / 'tasks' / 'demo.md'
            sheet.parent.mkdir(parents=True)
            sheet.write_text('frozen', encoding='utf-8')
            with self.assertRaises(ValueError):
                append_progress(root, 'demo', 'reviewer', {'details': {'authorization': 'Bearer abcdef123'}})
            append_progress(root, 'demo', 'main', {'event': 'checked'})
            self.assertEqual(sheet.read_text(encoding='utf-8'), 'frozen')

    def test_finalization_requires_main_approval_and_keeps_raw_on_failure(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d) / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            for name in ('executor-report.md', 'executor-result.json', 'review-report.md', 'reviewer-result.json', 'final-check.md', 'final-result.json'):
                (directory / name).write_text('{}', encoding='utf-8')
            (directory / 'raw.log').write_text('raw', encoding='utf-8')
            blocked = finalize_evidence(directory, 'demo', True)
            self.assertEqual(blocked['status'], 'blocked')
            self.assertTrue((directory / 'raw.log').exists())
            (directory / 'final-result.json').write_text(json.dumps({'status': 'PASS', 'decision': 'READY_FOR_EVIDENCE_FINALIZATION'}), encoding='utf-8')
            result = finalize_evidence(directory, 'demo', True)
            self.assertEqual(result['status'], 'blocked')
            self.assertTrue((directory / 'raw.log').exists())
            self.assertFalse((directory / 'finalization.json').exists())

            for name in ('executor-report.md', 'review-report.md', 'final-check.md'):
                (directory / name).write_text(
                    '```pipeline-evidence\n' + json.dumps({
                        'schema': 1, 'task_id': 'demo', 'worktree': 'worktree',
                        'branch': 'branch', 'role': 'executor' if name.startswith('executor') else 'reviewer' if name.startswith('review') else 'main-final',
                        'round': 1, 'status': 'PASS',
                        'commands': [{'command': 'python -m unittest', 'exit_code': 0, 'evidence_ref': 'executor-report.md'}],
                        'assertions': ['verified'], 'evidence_refs': ['executor-report.md'], 'unverified': [],
                    }) + '\n```\n', encoding='utf-8'
                )
            for name, role in (('executor-result.json', 'executor'), ('reviewer-result.json', 'reviewer')):
                (directory / name).write_text(json.dumps({
                    'schema': 1, 'task_id': 'demo', 'role': role, 'status': 'pass',
                    'acceptance': [{'id': 'acceptance-test-1', 'status': 'pass', 'exit_code': 0, 'evidence_refs': ['executor-report.md']}],
                    'unverified': [],
                }), encoding='utf-8')
            (directory / 'final-result.json').write_text(json.dumps({
                'schema': 1, 'task_id': 'demo', 'role': 'main-final', 'status': 'pass',
                'decision': 'READY_FOR_EVIDENCE_FINALIZATION',
                'acceptance': [{'id': 'acceptance-test-1', 'status': 'pass', 'exit_code': 0, 'evidence_refs': ['final-check.md']}],
                'unverified': [],
            }), encoding='utf-8')
            result = finalize_evidence(directory, 'demo', True)
            self.assertEqual(result['status'], 'finalized')
            self.assertFalse((directory / 'raw.log').exists())
            self.assertTrue((directory / 'finalization.json').exists())
            self.assertEqual(finalize_evidence(directory, 'demo', True)['status'], 'finalized')

    def test_finalization_cleanup_failure_leaves_no_marker(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d) / '.pipeline' / 'demo'
            self._write_valid_finalization_fixture(directory)
            (directory / 'raw.log').write_text('raw', encoding='utf-8')
            original_replace = os.replace

            def fail_cleanup(source, target):
                if Path(source).name == 'raw.log':
                    raise OSError('injected cleanup failure')
                return original_replace(source, target)

            with mock.patch('pipeline_tools.planning.os.replace', fail_cleanup):
                result = finalize_evidence(directory, 'demo', True)
            self.assertEqual(result['status'], 'blocked')
            self.assertIsNone(result['finalization'])
            self.assertFalse((directory / 'finalization.json').exists())

    def test_finalization_cleanup_failure_mid_delete_preserves_all_raw_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d) / '.pipeline' / 'demo'
            self._write_valid_finalization_fixture(directory)
            raw_files = {'raw-first.log': b'first raw', 'raw-second.log': b'second raw'}
            for name, content in raw_files.items():
                (directory / name).write_bytes(content)
            original_unlink = Path.unlink
            calls = {'count': 0}

            def fail_second_delete(path, *args, **kwargs):
                if path.parent.name == '.finalization-staging':
                    calls['count'] += 1
                    if calls['count'] == 2:
                        raise OSError('injected second delete failure')
                return original_unlink(path, *args, **kwargs)

            with mock.patch.object(Path, 'unlink', fail_second_delete):
                result = finalize_evidence(directory, 'demo', True)
            self.assertEqual(result['status'], 'blocked')
            self.assertFalse((directory / 'finalization.json').exists())
            for name, content in raw_files.items():
                self.assertEqual((directory / name).read_bytes(), content)

    def test_finalization_cleanup_failure_preserves_raw_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d) / '.pipeline' / 'demo'
            self._write_valid_finalization_fixture(directory)
            raw = directory / 'raw.log'
            raw.write_bytes(b'raw bytes')
            original_replace = os.replace

            def fail_cleanup(source, target):
                if Path(source).name == 'raw.log':
                    raise OSError('injected cleanup failure')
                return original_replace(source, target)

            with mock.patch('pipeline_tools.planning.os.replace', fail_cleanup):
                finalize_evidence(directory, 'demo', True)
            self.assertEqual(raw.read_bytes(), b'raw bytes')
            self.assertFalse((directory / 'finalization.json').exists())

    def test_finalization_cleanup_failure_retry_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d) / '.pipeline' / 'demo'
            self._write_valid_finalization_fixture(directory)
            raw = directory / 'raw.log'
            raw.write_text('raw', encoding='utf-8')
            original_replace = os.replace

            def fail_cleanup(source, target):
                if Path(source).name == 'raw.log':
                    raise OSError('injected cleanup failure')
                return original_replace(source, target)

            with mock.patch('pipeline_tools.planning.os.replace', fail_cleanup):
                first = finalize_evidence(directory, 'demo', True)
                second = finalize_evidence(directory, 'demo', True)
            self.assertEqual(first['status'], 'blocked')
            self.assertEqual(second['status'], 'blocked')
            self.assertTrue(raw.exists())
            self.assertFalse((directory / 'finalization.json').exists())
            recovered = finalize_evidence(directory, 'demo', True)
            self.assertEqual(recovered['status'], 'finalized')
            snapshot = sorted(path.relative_to(directory).as_posix() for path in directory.rglob('*'))
            self.assertEqual(snapshot, sorted([
                'executor-report.md', 'executor-result.json', 'final-check.md',
                'final-result.json', 'finalization.json', 'review-report.md',
                'reviewer-result.json',
            ]))
            self.assertEqual(finalize_evidence(directory, 'demo', True)['status'], 'finalized')

    def test_finalization_preserves_referenced_raw_evidence_on_reference_gap(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d) / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            report = {
                'schema': 1, 'task_id': 'demo', 'role': 'executor', 'status': 'PASS',
                'evidence_refs': ['raw.log'],
            }
            (directory / 'executor-report.md').write_text('```pipeline-evidence\n' + json.dumps(report) + '\n```\n', encoding='utf-8')
            for name in ('review-report.md', 'final-check.md'):
                (directory / name).write_text('```pipeline-evidence\n' + json.dumps({'task_id': 'demo', 'role': 'reviewer' if 'review' in name else 'main-final', 'status': 'PASS'}) + '\n```\n', encoding='utf-8')
            for name, role in (('executor-result.json', 'executor'), ('reviewer-result.json', 'reviewer')):
                (directory / name).write_text(json.dumps({'task_id': 'demo', 'role': role, 'status': 'PASS'}), encoding='utf-8')
            (directory / 'final-result.json').write_text(json.dumps({'task_id': 'demo', 'role': 'main-final', 'status': 'PASS', 'decision': 'READY_FOR_EVIDENCE_FINALIZATION'}), encoding='utf-8')
            (directory / 'raw.log').write_text('raw', encoding='utf-8')
            result = finalize_evidence(directory, 'demo', True)
            self.assertEqual(result['status'], 'blocked')
            self.assertTrue((directory / 'raw.log').exists())
            self.assertFalse((directory / 'finalization.json').exists())

if __name__ == '__main__': unittest.main()
