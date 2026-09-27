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

    def test_current_implement_plan_target_isolated_from_historical_task_inputs(self):
        from pipeline_tools.planning import generate_task_sheets
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project = {"schema": 1, "sources": [{"id": "source", "path": "implement-plan.md"}], "resources": [{"id": "resource", "path": "src/app.py"}], "operations": [{"id": "op", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_planning.py", "command_ref": "python -m unittest"}], "chain": chain()}
            requirements = {"schema": 1, "sources": [{"id": "source", "path": "implement-plan.md"}], "requirements": [{"id": "req", "source_refs": ["source"]}], "operations": project["operations"], "acceptance_tests": project["acceptance_tests"]}
            plan = {"schema": 1, "non_goals": ["本任务不扩展范围"], "requirements": ["req"], "resources": ["resource"], "operations": project["operations"], "acceptance_tests": project["acceptance_tests"], "tasks": [{"id": "current-task", "type": "prerequisite", "requirements": ["req"], "resources": ["resource"], "operations": ["op"], "depends_on": [], "non_user_completion_reason": "enabling groundwork; no user-facing outcome"}]}
            (root / "implement-plan.md").write_text("current target", encoding="utf-8")
            (root / "src").mkdir(); (root / "src" / "app.py").write_text("app", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True); subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True); subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True); subprocess.run(["git", "add", "."], cwd=root, check=True); subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            historical = root / "docs" / "tasks" / "historical-task.md"; historical.parent.mkdir(parents=True); historical.write_text("historical artifact", encoding="utf-8")
            result = generate_task_sheets(root, "current-run", project, requirements, plan)
            self.assertEqual(result["status"], "pass", result)
            self.assertEqual(result["task_ids"], ["current-task"])
            self.assertTrue((root / "docs" / "tasks" / "current-task.md").is_file())
            self.assertEqual(historical.read_text(encoding="utf-8"), "historical artifact")

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
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
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
                {'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']},
                {'id': 'read', 'resources': ['src/db.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-2']},
            ],
            'acceptance_tests': [
                {'id': 'acceptance-test-1', 'evidence_level': 2, 'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'},
                {'id': 'acceptance-test-2', 'evidence_level': 2, 'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'},
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
        derived['operations'] = [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}]
        derived['tasks'] = [dict(plan['tasks'][0], type='derived', parent_task_id='missing')]
        self.assertTrue(any('derived' in error or 'parent' in error for error in validate_task_plan(derived)))

    def test_task_plan_rejects_missing_top_level_acceptance_records(self):
        plan = {
            'schema': 1, 'requirements': ['r1'], 'resources': ['src/app.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['src/app.py'], 'operations': ['create'],
                       'chain': chain(), 'depends_on': []}],
        }
        errors = validate_task_plan(plan)
        self.assertTrue(any('top-level' in error and 'acceptance' in error for error in errors))

    def test_task_plan_requires_complete_top_level_acceptance_records(self):
        base = {
            'schema': 1, 'non_goals': ['本任务不扩展范围'], 'requirements': ['r1'], 'resources': ['src/app.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
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
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
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
            'non_goals': ['本任务不扩展范围'],
            'requirements': ['r1'],
            'resources': ['src/app.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{
                'id': 'acceptance-test-1', 'evidence_level': 2,
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

    def test_planning_preflight_reports_pre_existing_task_scenes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            (root / 'docs' / 'tasks').mkdir(parents=True)
            (root / 'docs' / 'tasks' / 'stale-sheet.md').write_text('# stale', encoding='utf-8')
            (root / '.worktrees' / 'orphan-worktree').mkdir(parents=True)
            (root / '.pipeline' / 'leftover-task').mkdir(parents=True)
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'base'], cwd=root, check=True)
            result = planning_preflight(root)
            self.assertIn('task_scenes', result)
            self.assertEqual(result['task_scenes']['sheets_without_worktree'], ['stale-sheet'])
            self.assertEqual(result['task_scenes']['worktrees_without_sheet'], ['orphan-worktree'])
            self.assertEqual(result['task_scenes']['leftover_evidence'], ['leftover-task'])
            self.assertTrue(any('worktree' in error for error in result['errors']))
            self.assertIn('reconcile existing task scenes before planning', result['next_actions'])

    def test_planning_preflight_clean_repository_reports_no_task_scenes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'base'], cwd=root, check=True)
            result = planning_preflight(root)
            self.assertEqual(result['status'], 'pass')
            self.assertEqual(result['task_scenes'], {'sheets_without_worktree': [], 'worktrees_without_sheet': [], 'uncommitted_sheets': [], 'leftover_evidence': []})
            self.assertNotIn('reconcile existing task scenes before planning', result['next_actions'])

    def test_task_plan_rejects_evidence_level_below_risk_floor(self):
        def plan_with(risk, project_type, level):
            chain_value = chain()
            return {
                'schema': 1, 'risk': risk, 'project_type': project_type,
                'non_goals': ['本任务不扩展范围'],
                'requirements': ['r1'], 'resources': ['src/app.py'],
                'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
                'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': level,
                                      'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
                'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                           'resources': ['src/app.py'], 'operations': ['create'],
                           'chain': chain_value, 'depends_on': []}],
            }

        below = validate_task_plan(plan_with('high', 'web', 1))
        self.assertTrue(any('below the required floor' in error for error in below), below)
        conforming = validate_task_plan(plan_with('high', 'web', 3))
        self.assertEqual(conforming, [])

    def test_task_plan_requires_explicit_non_goals(self):
        base = {
            'schema': 1, 'non_goals': ['本任务不扩展范围'],
            'requirements': ['r1'], 'resources': ['src/app.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                  'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['src/app.py'], 'operations': ['create'],
                       'chain': chain(), 'depends_on': []}],
        }
        self.assertEqual(validate_task_plan(base), [])
        missing = {key: value for key, value in base.items() if key != 'non_goals'}
        self.assertTrue(any('non_goals' in error for error in validate_task_plan(missing)))
        self.assertTrue(any('non_goals' in error for error in validate_task_plan(dict(base, non_goals=[]))))
        self.assertTrue(any('non_goals' in error for error in validate_task_plan(dict(base, non_goals=['   ']))))

    def test_task_plan_validates_resource_semantics_without_a_kind_literal(self):
        def plan_with(operation):
            return {
                'schema': 1, 'non_goals': ['本任务不扩展范围'],
                'requirements': ['r1'], 'resources': ['src/app.py'],
                'operations': [operation],
                'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                      'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
                'tasks': [{'id': 't1', 'type': 'prerequisite', 'requirements': ['r1'],
                           'resources': ['src/app.py'], 'operations': ['create'],
                           'depends_on': []}],
            }

        empty = plan_with({'id': 'create', 'acceptance_tests': ['acceptance-test-1'], 'resources': []})
        self.assertTrue(any('resources' in error for error in validate_task_plan(empty)))
        unknown = plan_with({'id': 'create', 'acceptance_tests': ['acceptance-test-1'], 'resources': ['missing-resource']})
        self.assertTrue(any('unknown id' in error for error in validate_task_plan(unknown)))
        single = plan_with({'id': 'create', 'acceptance_tests': ['acceptance-test-1'], 'resource_mode': 'single', 'resources': ['src/app.py']})
        self.assertEqual(validate_task_plan(single), [])

    def test_task_plan_requires_explicit_resource_mode_regardless_of_kind(self):
        def plan_with(operation):
            return {
                'schema': 1, 'non_goals': ['本任务不扩展范围'],
                'requirements': ['r1'],
                'resources': ['src/app.py', 'src/db.py'],
                'operations': [operation],
                'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                      'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
                'tasks': [{'id': 't1', 'type': 'prerequisite', 'requirements': ['r1'],
                           'resources': ['src/app.py', 'src/db.py'], 'operations': ['create'],
                           'depends_on': []}],
            }

        implicit = plan_with({'id': 'create', 'kind': 'execute',
                              'acceptance_tests': ['acceptance-test-1'],
                              'resources': ['src/app.py', 'src/db.py']})
        implicit_errors = validate_task_plan(implicit)
        self.assertTrue(any('resource_mode' in error for error in implicit_errors), implicit_errors)

        batch = plan_with({'id': 'create', 'kind': 'execute', 'resource_mode': 'batch',
                           'acceptance_tests': ['acceptance-test-1'],
                           'resources': ['src/app.py', 'src/db.py']})
        self.assertEqual(validate_task_plan(batch), [])

        mismatched = plan_with({'id': 'create', 'kind': 'execute', 'resource_mode': 'batch',
                                'acceptance_tests': ['acceptance-test-1'],
                                'resources': ['src/app.py']})
        mismatched_errors = validate_task_plan(mismatched)
        self.assertTrue(any('resource_mode' in error for error in mismatched_errors), mismatched_errors)

    def test_task_plan_rejects_invalid_risk_and_project_type(self):
        base = {
            'schema': 1, 'non_goals': ['本任务不扩展范围'],
            'requirements': ['r1'], 'resources': ['src/app.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                  'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['src/app.py'], 'operations': ['create'],
                       'chain': chain(), 'depends_on': []}],
        }
        self.assertEqual(validate_task_plan(base), [])
        bad_risk = dict(base, risk='banana')
        self.assertTrue(any('risk' in error for error in validate_task_plan(bad_risk)))
        bad_type = dict(base, project_type='banana')
        self.assertTrue(any('project_type' in error for error in validate_task_plan(bad_type)))
        high_unproven = dict(base, risk='high')
        self.assertTrue(any('below the required floor' in error for error in validate_task_plan(high_unproven)))


    def test_planning_preflight_blocks_on_expected_requirements_hash_drift(self):
        from pipeline_tools.planning import planning_preflight
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "implement-plan.md").write_text("frozen requirements\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            result = planning_preflight(root, expected_requirements_sha256="0" * 64)
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("implement-plan.md hash changed" in error for error in result["errors"]), result["errors"])

    def test_planning_preflight_blocks_on_uncommitted_task_sheet(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "implement-plan.md").write_text("real requirements", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            (root / "docs" / "tasks").mkdir(parents=True)
            (root / "docs" / "tasks" / "t9.md").write_text("sheet", encoding="utf-8")
            subprocess.run(["git", "worktree", "add", "-b", "t9-branch", ".worktrees/t9", "HEAD"], cwd=root, check=True)
            result = planning_preflight(root)
            self.assertEqual(result["status"], "blocked", result)
            self.assertIn("t9", result["task_scenes"]["uncommitted_sheets"])
            self.assertTrue(any("task sheet" in error for error in result["errors"]), result["errors"])

    def test_planning_preflight_migrates_lone_legacy_workflow(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "implement-plan.md").write_text("real requirements", encoding="utf-8")
            (root / ".workflow" / "task-a").mkdir(parents=True)
            (root / ".workflow" / "task-a" / "note.txt").write_text("legacy", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            result = planning_preflight(root)
            self.assertEqual(result["status"], "pass", result)
            self.assertFalse((root / ".workflow").exists())
            self.assertTrue((root / ".pipeline" / "task-a" / "note.txt").is_file())

    def test_planning_preflight_does_not_misreport_project_named_worktrees(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / ".worktrees" / "not-an-orphan"
            root.mkdir(parents=True)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "implement-plan.md").write_text("real requirements", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            result = planning_preflight(root)
            self.assertNotIn("isolated worktree is orphaned", result["errors"], result)


if __name__ == '__main__': unittest.main()
