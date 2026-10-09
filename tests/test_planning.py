import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from pipeline_tools.planning import (
    append_progress,
    archive_task_sheet,
    finalize_evidence,
    planning_preflight,
    validate_project_facts,
    validate_requirement_facts,
    validate_task_plan,
    sync_goal_document,
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
    def _generation_fixture(self, tasks):
        project = {
            'schema': 1, 'sources': [{'id': 'source', 'path': 'implement-plan.md'}],
            'resources': [{'id': 'resource', 'path': 'src/app.py'}, {'id': 'resource-tests', 'path': 'tests/test_planning.py'}],
            'operations': [{'id': 'op', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2, 'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
            'chain': chain(),
        }
        requirements = {
            'schema': 1, 'sources': [{'id': 'source', 'path': 'implement-plan.md'}],
            'requirements': [{'id': 'r1', 'source_refs': ['source']}],
            'operations': project['operations'], 'acceptance_tests': project['acceptance_tests'],
        }
        plan = {
            'schema': 1, 'non_goals': ['本任务不扩展范围'],
            'requirements': ['r1'], 'resources': ['src/app.py', 'tests/test_planning.py'],
            'operations': project['operations'], 'acceptance_tests': project['acceptance_tests'],
            'tasks': tasks,
        }
        return project, requirements, plan

    def _feature_task(self):
        return {
            'id': 'feature-task', 'type': 'vertical-feature', 'requirements': ['r1'],
            'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['op'],
            'chain': chain(), 'depends_on': [],
        }

    def _generation_repo(self, root):
        (root / 'implement-plan.md').write_text('current target', encoding='utf-8')
        (root / 'src').mkdir(exist_ok=True)
        (root / 'src' / 'app.py').write_text('app', encoding='utf-8')
        subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=root, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
        subprocess.run(['git', 'add', '.'], cwd=root, check=True)
        subprocess.run(['git', 'commit', '-qm', 'base'], cwd=root, check=True)

    def _scene_repo(self, root):
        """A committed Git repository with `/ .worktrees/` ignored."""
        subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=root, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
        (root / '.gitignore').write_text('/.worktrees/\n', encoding='utf-8')
        subprocess.run(['git', 'add', '.gitignore'], cwd=root, check=True)
        subprocess.run(['git', 'commit', '-qm', 'base'], cwd=root, check=True)

    def _commit_all(self, root, message):
        subprocess.run(['git', 'add', '-A'], cwd=root, check=True)
        subprocess.run(['git', 'commit', '-qm', message], cwd=root, check=True)

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
            plan = {"schema": 1, "non_goals": ["本任务不扩展范围"], "requirements": ["req"], "resources": ["resource", "tests/test_planning.py"], "operations": project["operations"], "acceptance_tests": project["acceptance_tests"], "tasks": [{"id": "current-task", "type": "prerequisite", "requirements": ["req"], "resources": ["resource", "tests/test_planning.py"], "operations": ["op"], "depends_on": [], "non_user_completion_reason": "enabling groundwork; no user-facing outcome"}]}
            (root / "implement-plan.md").write_text("current target", encoding="utf-8")
            (root / "src").mkdir(); (root / "src" / "app.py").write_text("app", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True); subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True); subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True); subprocess.run(["git", "add", "."], cwd=root, check=True); subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            historical = root / "docs" / "tasks" / "historical-task.md"; historical.parent.mkdir(parents=True); historical.write_text("historical artifact", encoding="utf-8")
            result = generate_task_sheets(root, "current-run", project, requirements, plan)
            self.assertEqual(result["status"], "pass", result)
            self.assertEqual(result["task_ids"], ["current-task"])
            self.assertTrue((root / "docs" / "tasks" / "current-task.md").is_file())
            self.assertEqual(historical.read_text(encoding="utf-8"), "historical artifact")

    def test_goal_document_resolution_precedence_and_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'goal.md').write_text('legacy goal', encoding='utf-8')
            (root / 'implement-plan.md').write_text('older plan', encoding='utf-8')
            path, message = sync_goal_document(root)
            self.assertEqual(path, root / 'docs' / 'goal.md')
            self.assertIn('goal.md', message)
            self.assertIn('legacy goal', path.read_text(encoding='utf-8'))
            self.assertNotIn('older plan', path.read_text(encoding='utf-8'))

            path.write_text('canonical', encoding='utf-8')
            (root / 'goal.md').write_text('changed legacy', encoding='utf-8')
            resolved, message = sync_goal_document(root)
            self.assertIsNone(message)
            self.assertEqual(resolved.read_text(encoding='utf-8'), 'canonical')

    def test_goal_document_falls_back_to_implement_plan(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'implement-plan.md').write_text('older plan', encoding='utf-8')
            path, message = sync_goal_document(root)
            self.assertIn('implement-plan.md', message)
            self.assertIn('older plan', path.read_text(encoding='utf-8'))

    def test_planning_preflight(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / '.git').mkdir()
            self.assertEqual(planning_preflight(root)['status'], 'blocked')
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            result = planning_preflight(root)
            self.assertEqual(result['status'], 'blocked')
            self.assertIn('requirements_sha256', result)

    def test_planning_preflight_dry_run_does_not_migrate_legacy_layout(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / '.workflow').mkdir()
            (root / 'implement-plan.md').write_text('real requirements', encoding='utf-8')
            result = planning_preflight(root, apply=False)
            self.assertEqual(result['status'], 'blocked')
            self.assertTrue((root / '.workflow').is_dir())
            self.assertTrue(any('explicit apply' in error for error in result['errors']))

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

    def test_planning_preflight_clears_stale_failure_record_on_success(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
            (root / 'goal.md').write_text('real requirements', encoding='utf-8')
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'base'], cwd=root, check=True)
            from pipeline_tools.layout import recovery_index_path, temporary_root
            recorded = recovery_index_path(root)
            blocked = planning_preflight(root, expected_requirements_sha256='0' * 64, apply=True)
            self.assertEqual(blocked['status'], 'blocked')
            self.assertTrue(recorded.is_file())
            self.assertFalse((root / '.pipeline' / 'planning').exists())
            self.assertIn('temporary://', recorded.read_text(encoding='utf-8'))
            self.assertTrue(any(path.name.endswith('-preflight.json') for path in temporary_root(root).iterdir()))
            result = planning_preflight(root, apply=True)
            self.assertEqual(result['status'], 'pass', result)
            self.assertFalse((root / '.pipeline' / 'planning').exists())

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
            first = planning_preflight(root, apply=True)
            self.assertEqual(first['status'], 'pass')
            (root / 'implement-plan.md').write_text('changed requirements', encoding='utf-8')
            drift = planning_preflight(root, expected_requirements_sha256=first['requirements_sha256'], expected_branch='wrong', apply=True)
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
                'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
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
                       'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
                       'chain': chain(), 'depends_on': []}],
        }
        errors = validate_task_plan(plan)
        self.assertTrue(any('top-level' in error and 'acceptance' in error for error in errors))

    def test_task_plan_requires_complete_top_level_acceptance_records(self):
        base = {
            'schema': 1, 'non_goals': ['本任务不扩展范围'], 'requirements': ['r1'], 'resources': ['src/app.py', 'tests/test_planning.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                  'test_ref': 'tests/test_planning.py',
                                  'command_ref': 'python -m unittest'}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
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
            'resources': ['src/app.py', 'tests/test_planning.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{
                'id': 'acceptance-test-1', 'evidence_level': 2,
                'test_ref': 'tests/test_planning.py: test_task_plan_validation',
                'command_ref': 'python -m unittest tests.test_planning -v',
            }],
            'tasks': [{
                'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
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
            lock = directory / '.lifecycle.lock'
            self.assertTrue(lock.exists())
            lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
            self.assertEqual(finalize_evidence(directory, 'demo', True)['status'], 'finalized')
            self.assertTrue(lock.exists())
            self.assertEqual((lock.stat().st_dev, lock.stat().st_ino), lock_identity)
            (directory / 'final-check.md').write_text('tampered', encoding='utf-8')
            stale = finalize_evidence(directory, 'demo', True)
            self.assertEqual(stale['status'], 'blocked')
            self.assertTrue(any('hash mismatch' in item for item in stale['missing']))

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
                '.lifecycle.lock', 'executor-report.md', 'executor-result.json', 'final-check.md',
                'final-result.json', 'finalization.json', 'review-report.md',
                'reviewer-result.json',
            ]))
            lock = directory / '.lifecycle.lock'
            lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
            self.assertEqual(finalize_evidence(directory, 'demo', True)['status'], 'finalized')
            self.assertEqual((lock.stat().st_dev, lock.stat().st_ino), lock_identity)

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
            result = planning_preflight(root, apply=True)
            self.assertEqual(result['status'], 'pass')
            self.assertEqual(result['task_scenes'], {'sheets_without_worktree': [], 'worktrees_without_sheet': [], 'uncommitted_sheets': [], 'leftover_evidence': []})
            self.assertNotIn('reconcile existing task scenes before planning', result['next_actions'])

    def test_task_plan_rejects_evidence_level_below_risk_floor(self):
        def plan_with(risk, project_type, level):
            chain_value = chain()
            return {
                'schema': 1, 'risk': risk, 'project_type': project_type,
                'non_goals': ['本任务不扩展范围'],
                'requirements': ['r1'], 'resources': ['src/app.py', 'tests/test_planning.py'],
                'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
                'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': level,
                                      'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
                'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                           'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
                           'chain': chain_value, 'depends_on': []}],
            }

        below = validate_task_plan(plan_with('high', 'web', 1))
        self.assertTrue(any('below the required floor' in error for error in below), below)
        conforming = validate_task_plan(plan_with('high', 'web', 3))
        self.assertEqual(conforming, [])

    def test_task_plan_requires_explicit_non_goals(self):
        base = {
            'schema': 1, 'non_goals': ['本任务不扩展范围'],
            'requirements': ['r1'], 'resources': ['src/app.py', 'tests/test_planning.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                  'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
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
                'requirements': ['r1'], 'resources': ['src/app.py', 'tests/test_planning.py'],
                'operations': [operation],
                'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                      'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
                'tasks': [{'id': 't1', 'type': 'prerequisite', 'requirements': ['r1'],
                           'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
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
                'resources': ['src/app.py', 'src/db.py', 'tests/test_planning.py'],
                'operations': [operation],
                'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                      'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
                'tasks': [{'id': 't1', 'type': 'prerequisite', 'requirements': ['r1'],
                           'resources': ['src/app.py', 'src/db.py', 'tests/test_planning.py'], 'operations': ['create'],
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
            'requirements': ['r1'], 'resources': ['src/app.py', 'tests/test_planning.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                  'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
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
            self.assertTrue(any("goal.md hash changed" in error for error in result["errors"]), result["errors"])

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
            result = planning_preflight(root, apply=True)
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

    def test_task_plan_rejects_acceptance_test_ref_outside_task_resources(self):
        plan = {
            'schema': 1, 'non_goals': ['本任务不扩展范围'],
            'requirements': ['r1'], 'resources': ['tests/test_planning.py'],
            'operations': [{'id': 'create', 'resources': ['tests/test_planning.py'],
                            'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                  'test_ref': 'tests/test_evidence.py: EvidenceTests.test_all_reports_require_machine_evidence',
                                  'command_ref': 'python -m unittest'}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['tests/test_planning.py'], 'operations': ['create'],
                       'chain': chain(), 'depends_on': []}],
        }
        errors = validate_task_plan(plan)
        self.assertTrue(any('outside' in error for error in errors), errors)

    def test_task_plan_accepts_acceptance_test_ref_inside_task_resources(self):
        plan = {
            'schema': 1, 'non_goals': ['本任务不扩展范围'],
            'requirements': ['r1'], 'resources': ['src/app.py', 'tests/test_planning.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'],
                            'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                  'test_ref': 'tests/test_planning.py: PlanningTests.test_task_plan_validation',
                                  'command_ref': 'python -m unittest'}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
                       'chain': chain(), 'depends_on': []}],
        }
        self.assertEqual(validate_task_plan(plan), [])

    def test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned(self):
        plan = {
            'schema': 1, 'non_goals': ['本任务不扩展范围'],
            'requirements': ['r1'], 'resources': ['tests/test_evidence.py'],
            'operations': [{'id': 'create', 'resources': ['tests/test_evidence.py'],
                            'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2,
                                  'test_ref': 'tests/test_acceptance_id_and_template_compliance.py: '
                                              'AcceptanceIdAndTemplateComplianceTests.test_template_and_evidence_example_use_complete_format',
                                  'command_ref': 'python -m unittest'}],
            'tasks': [{'id': 't1', 'type': 'vertical-feature', 'requirements': ['r1'],
                       'resources': ['tests/test_evidence.py'], 'operations': ['create'],
                       'chain': chain(), 'depends_on': []}],
        }
        errors = validate_task_plan(plan)
        self.assertTrue(any('outside' in error for error in errors), errors)

    def test_new_task_plan_rejects_the_derived_type(self):
        from pipeline_tools.planning import generate_task_sheets
        feature = self._feature_task()
        _project, _requirements, plan = self._generation_fixture([feature])
        self.assertEqual(validate_task_plan(plan), [])

        declared = dict(plan)
        declared['tasks'] = [dict(
            feature, type='derived', parent_task_id='parent-task',
            derived_from={'task_id': 'parent-task', 'commit': 'a' * 40, 'branch': 'parent-branch', 'parent_task_type': 'repair'},
        )]
        errors = validate_task_plan(declared)
        self.assertTrue(errors, errors)
        self.assertTrue(any('derived' in error for error in errors), errors)

        # The type alone is enough to fail closed with a readable reason.
        bare = dict(plan)
        bare['tasks'] = [dict(feature, type='derived')]
        bare_errors = validate_task_plan(bare)
        self.assertTrue(bare_errors, bare_errors)
        self.assertTrue(any('derived' in error for error in bare_errors), bare_errors)

        derived_form = dict(plan)
        derived_form['tasks'] = [dict(feature, parent_task_id='parent-task')]
        errors = validate_task_plan(derived_form)
        self.assertTrue(any('derived' in error for error in errors), errors)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project, requirements, derived_plan = self._generation_fixture([
                dict(feature, type='derived', parent_task_id='parent-task'),
            ])
            self._generation_repo(root)
            result = generate_task_sheets(root, 'derived-run', project, requirements, derived_plan)
            self.assertEqual(result['status'], 'blocked', result)
            self.assertFalse((root / 'docs' / 'tasks').exists())

    def test_generated_sheets_never_declare_derived(self):
        from pipeline_tools.contract import validate_task
        from pipeline_tools.planning import generate_task_sheets
        tasks = [
            self._feature_task(),
            {
                'id': 'repair-task', 'type': 'repair', 'requirements': ['r1'],
                'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['op'],
                'chain': chain(), 'depends_on': ['feature-task'],
            },
            {
                'id': 'prereq-task', 'type': 'prerequisite', 'requirements': ['r1'],
                'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['op'],
                'depends_on': ['repair-task'],
                'non_user_completion_reason': 'enabling groundwork; no user-facing outcome',
            },
        ]
        project, requirements, plan = self._generation_fixture(tasks)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._generation_repo(root)
            result = generate_task_sheets(root, 'three-type-run', project, requirements, plan)
            self.assertEqual(result['status'], 'pass', result)
            self.assertEqual(result['task_ids'], ['feature-task', 'repair-task', 'prereq-task'])
            for task_id in result['task_ids']:
                sheet = root / 'docs' / 'tasks' / f'{task_id}.md'
                self.assertEqual(validate_task(sheet), [])
                contract = json.loads(
                    sheet.read_text(encoding='utf-8').split('```pipeline-contract\n', 1)[1].split('\n```', 1)[0]
                )
                self.assertIn(contract['task_type'], {'vertical-feature', 'prerequisite', 'repair'})
                self.assertNotEqual(contract['task_type'], 'derived')
                self.assertNotIn('derived_from', contract)

    # --- Finalization accepts the report schema the templates produce --------

    def _finalization_contract(self):
        return {
            'schema': 2, 'task_id': 'demo', 'task_type': 'repair',
            'implement_plan': {'path': 'implement-plan.md'},
            'allowed_paths': ['pipeline_tools/**', 'tests/**', 'docs/tasks/**'],
            'forbidden_paths': ['implement-plan.md', 'IDEA.md', '.pipeline/**'],
            'operations': [{'id': 'finalize', 'kind': 'repair', 'scope': 'evidence',
                            'acceptance_tests': ['acceptance-test-demo']}],
            'chain': {name: ['pipeline_tools/core.py'] for name in (
                'entry', 'interaction', 'application', 'domain', 'persistence', 'readback', 'recovery')},
            'dependencies': [], 'required_evidence_levels': [3],
            'acceptance_tests': [{
                'id': 'acceptance-test-demo', 'evidence_level': 3,
                'test_ref': 'tests/test_planning.py',
                'command_ref': 'python -m pytest -q tests/test_planning.py',
            }],
        }

    # Prose that follows a report's machine block and carries further fenced blocks.
    TRAILING_FENCED_PROSE = (
        '\n## Observations\n\n'
        'The task branch reused the existing reader rather than adding a second one.\n\n'
        '```text\nfirst trailing block\n```\n\n'
        'A second illustration of the same rule:\n\n'
        '```python\nprint("hello")\n```\n\n'
        '```json\n{"note": "a third trailing block"}\n```\n'
    )

    def _write_schema_two_evidence(self, directory, *, branch, worktree, head, revision=1,
                                   main_cwd=None, task_id='demo', trailing_prose=False):
        """Write the six finalization inputs in the schema 2 shape the templates emit."""
        directory.mkdir(parents=True, exist_ok=True)
        for name, role in (('executor-report.md', 'executor'), ('review-report.md', 'reviewer'),
                           ('final-check.md', 'main-final')):
            body = '```pipeline-evidence\n' + json.dumps({
                'schema': 2, 'task_id': task_id, 'worktree': worktree, 'branch': branch,
                'head': head, 'sheet_revision': revision, 'observed_at_commit': head,
                'generated_at': '2026-01-01T00:00:00+00:00',
                'role': role, 'round': 1, 'status': 'PASS',
                'commands': [{
                    'command': 'python -m pytest -q tests/test_planning.py', 'exit_code': 0,
                    'cwd': main_cwd if name == 'final-check.md' else worktree,
                    'evidence_ref': name,
                }],
                'assertions': ['the observed result matches the contract'],
                'evidence_refs': [name], 'unverified': [],
            }) + '\n```\n'
            if trailing_prose:
                body += self.TRAILING_FENCED_PROSE
            (directory / name).write_text(body, encoding='utf-8')
        for name, role in (('executor-result.json', 'executor'), ('reviewer-result.json', 'reviewer'),
                           ('final-result.json', 'main-final')):
            value = {
                'schema': 1, 'task_id': task_id, 'role': role, 'status': 'pass', 'exit_code': 0,
                'acceptance': [{'id': 'acceptance-test-demo', 'status': 'pass', 'exit_code': 0,
                                'evidence_refs': ['executor-report.md']}],
                'unverified': [],
            }
            if name == 'final-result.json':
                value['decision'] = 'READY_FOR_EVIDENCE_FINALIZATION'
            (directory / name).write_text(json.dumps(value), encoding='utf-8')

    def _rewrite_schema_two_report(self, directory, name, **fields):
        path = directory / name
        lines = path.read_text(encoding='utf-8').splitlines()
        value = json.loads(lines[1])
        for key, item in fields.items():
            if item is None:
                value.pop(key, None)
            else:
                value[key] = item
        path.write_text('```pipeline-evidence\n' + json.dumps(value) + '\n```\n', encoding='utf-8')

    def test_finalization_accepts_schema_two_reports(self):
        import sys
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()

            def git(*args, cwd=root, check=True):
                return subprocess.run(['git', '-C', str(cwd), *args], check=check, capture_output=True, text=True)

            git('init', '-q', '-b', 'main')
            git('config', 'user.email', 'test@example.invalid')
            git('config', 'user.name', 'Test')
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_text('stable\n', encoding='utf-8')
            (root / '.gitignore').write_text('/.worktrees/\n', encoding='utf-8')
            sheet = root / 'docs' / 'tasks' / 'demo.md'
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                '<!-- Task ID: demo -->\n```pipeline-contract\n'
                + json.dumps(self._finalization_contract()) + '\n```\n', encoding='utf-8')
            git('add', '.')
            git('commit', '-qm', 'baseline')
            baseline = git('rev-parse', 'HEAD').stdout.strip()
            worktree = root / '.worktrees' / 'demo'
            git('worktree', 'add', '-b', 'demo-task', str(worktree), baseline)
            # The task branch writes the stage reports under its own identity: the
            # recorded branch and worktree are the task branch and task worktree.
            self._write_schema_two_evidence(
                worktree / '.pipeline' / 'demo',
                branch='demo-task', worktree=str(worktree), head=baseline, main_cwd=str(root),
            )
            git('add', '.pipeline', cwd=worktree)
            git('commit', '-qm', 'task stage reports', cwd=worktree)
            (worktree / 'src' / 'app.py').write_text('task change\n', encoding='utf-8')
            git('add', 'src/app.py', cwd=worktree)
            git('commit', '-qm', 'task product change', cwd=worktree)
            git('merge', '--no-ff', '-m', 'merge demo-task', 'demo-task')
            merged = git('rev-parse', 'HEAD').stdout.strip()
            self.assertNotEqual(baseline, merged)
            evidence = root / '.pipeline' / 'demo'
            self.assertTrue((evidence / 'executor-report.md').is_file())
            recorded = json.loads((evidence / 'executor-report.md').read_text(
                encoding='utf-8').split('```pipeline-evidence\n')[1].split('\n```')[0])
            self.assertEqual('demo-task', recorded['branch'])
            self.assertEqual(str(worktree), recorded['worktree'])

            env = {**os.environ, 'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '1',
                   'PYTHONPATH': str(Path(__file__).resolve().parent.parent)}
            finalize = subprocess.run(
                [sys.executable, '-m', 'pipeline_tools', 'planning', 'evidence-finalize', str(evidence),
                 '--task-id', 'demo', '--success'],
                cwd=root, env=env, capture_output=True, text=True, timeout=120)
            self.assertEqual(finalize.returncode, 0, finalize.stdout + finalize.stderr)
            self.assertEqual(json.loads(finalize.stdout)['status'], 'finalized')
            self.assertTrue((evidence / 'finalization.json').is_file())
            verify = subprocess.run(
                [sys.executable, '-m', 'pipeline_tools', 'evidence', 'verify', str(evidence),
                 '--task-id', 'demo', '--phase', 'finalized'],
                cwd=root, env=env, capture_output=True, text=True, timeout=120)
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_finalization_still_rejects_incomplete_reports(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d) / '.pipeline' / 'demo'
            self._write_schema_two_evidence(
                directory, branch='demo-task', worktree='worktree', head='a' * 40)
            self.assertEqual(finalize_evidence(directory, 'demo', True)['status'], 'finalized')

        cases = (
            ('executor-report.md', 'missing-field', {'assertions': None}),
            ('review-report.md', 'role-mismatch', {'role': 'executor'}),
            ('executor-report.md', 'task-mismatch', {'task_id': 'other-task'}),
        )
        observed = []
        for name, label, fields in cases:
            with tempfile.TemporaryDirectory() as d:
                directory = Path(d) / '.pipeline' / 'demo'
                self._write_schema_two_evidence(
                    directory, branch='demo-task', worktree='worktree', head='a' * 40)
                self._rewrite_schema_two_report(directory, name, **fields)
                result = finalize_evidence(directory, 'demo', True)
                self.assertEqual(result['status'], 'blocked', (label, result))
                self.assertIn(f'invalid {name}', result['missing'], label)
                self.assertFalse((directory / 'finalization.json').exists(), label)
                observed.append(label)
        self.assertEqual(sorted(observed), ['missing-field', 'role-mismatch', 'task-mismatch'])

    # --- The machine block ends at the first fence after its opening ---------

    def _fence_line_numbers(self, path):
        lines = path.read_text(encoding='utf-8').splitlines()
        starts = [i for i, line in enumerate(lines) if line.strip() == '```pipeline-evidence']
        self.assertEqual(len(starts), 1, path)
        closes = [i for i in range(starts[0] + 1, len(lines)) if lines[i].strip() == '```']
        return starts, closes

    def test_evidence_block_reader_accepts_fences_after_the_machine_block(self):
        reports = ('executor-report.md', 'review-report.md', 'final-check.md')
        with tempfile.TemporaryDirectory() as d:
            root, evidence, _baseline, _merged = self._merged_finalization_repo(
                d, trailing_prose=True)
            before = {name: (evidence / name).read_bytes() for name in reports}
            for name in reports:
                _starts, closes = self._fence_line_numbers(evidence / name)
                # The report carries the machine block plus further fenced blocks.
                self.assertGreaterEqual(len(closes), 2, name)
            gate = self._run_cli(root, 'gate', 'post-merge', str(evidence),
                                 '--task-id', 'demo', '--branch', 'main')
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
            finalize = self._run_cli(root, 'planning', 'evidence-finalize', str(evidence),
                                     '--task-id', 'demo', '--success')
            self.assertEqual(finalize.returncode, 0, finalize.stdout + finalize.stderr)
            self.assertEqual(json.loads(finalize.stdout)['status'], 'finalized')
            self.assertTrue((evidence / 'finalization.json').is_file())
            for name in reports:
                self.assertEqual(before[name], (evidence / name).read_bytes(), name)

    def test_evidence_block_reader_still_rejects_malformed_blocks(self):
        from pipeline_tools.planning import _read_evidence_block

        value = {
            'schema': 2, 'task_id': 'demo', 'worktree': 'worktree', 'branch': 'demo-task',
            'head': 'a' * 40, 'sheet_revision': 1, 'observed_at_commit': 'a' * 40,
            'generated_at': '2026-01-01T00:00:00+00:00', 'role': 'executor', 'round': 1,
            'status': 'PASS',
            'commands': [{'command': 'python -m pytest -q', 'exit_code': 0,
                          'cwd': 'worktree', 'evidence_ref': 'executor-report.md'}],
            'assertions': ['the observed result matches the contract'],
            'evidence_refs': ['executor-report.md'], 'unverified': [],
        }
        body = json.dumps(value)
        cases = {
            'missing-opening-fence': body + '\n',
            'duplicate-opening-fence': (
                '```pipeline-evidence\n' + body + '\n```\n'
                '```pipeline-evidence\n' + body + '\n```\n'
            ),
            'missing-closing-fence': '```pipeline-evidence\n' + body + '\n',
            'invalid-json': '```pipeline-evidence\n{"schema": 2, "task_id":\n```\n',
        }
        observed = []
        for label, text in cases.items():
            with tempfile.TemporaryDirectory() as d:
                directory = Path(d) / '.pipeline' / 'demo'
                self._write_schema_two_evidence(
                    directory, branch='demo-task', worktree='worktree', head='a' * 40)
                (directory / 'executor-report.md').write_text(text, encoding='utf-8')
                self.assertIsNone(_read_evidence_block(directory / 'executor-report.md'), label)
                result = finalize_evidence(directory, 'demo', True)
                self.assertEqual(result['status'], 'blocked', (label, result))
                self.assertIn('invalid executor-report.md', result['missing'], label)
                self.assertFalse((directory / 'finalization.json').exists(), label)
                observed.append(label)
        self.assertEqual(sorted(observed), [
            'duplicate-opening-fence', 'invalid-json',
            'missing-closing-fence', 'missing-opening-fence',
        ])

    def test_finalization_and_gate_readers_agree_on_the_same_report(self):
        from pipeline_tools.core import _read_machine_evidence
        from pipeline_tools.planning import _read_evidence_block

        reports = ('executor-report.md', 'review-report.md', 'final-check.md')
        with tempfile.TemporaryDirectory() as d:
            root, evidence, _baseline, _merged = self._merged_finalization_repo(
                d, trailing_prose=True)
            for name in reports:
                path = evidence / name
                gate_value, gate_errors = _read_machine_evidence(path)
                self.assertEqual(gate_errors, [], name)
                self.assertIsNotNone(gate_value, name)
                self.assertEqual(gate_value, _read_evidence_block(path), name)
            gate = self._run_cli(root, 'gate', 'post-merge', str(evidence),
                                 '--task-id', 'demo', '--branch', 'main')
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
            finalize = self._run_cli(root, 'planning', 'evidence-finalize', str(evidence),
                                     '--task-id', 'demo', '--success')
            self.assertEqual(finalize.returncode, 0, finalize.stdout + finalize.stderr)
            payload = json.loads(finalize.stdout)
            self.assertNotIn('invalid executor-report.md', payload.get('missing', []))
            self.assertNotIn('invalid review-report.md', payload.get('missing', []))
            self.assertEqual(payload['status'], 'finalized')

    # --- The finalization marker head across its own evidence commit ---------

    def _run_cli(self, root, *args, timeout=120):
        import sys
        env = {**os.environ, 'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '1',
               'PYTHONPATH': str(Path(__file__).resolve().parent.parent)}
        return subprocess.run([sys.executable, '-m', 'pipeline_tools', *args],
                              cwd=root, env=env, capture_output=True, text=True, timeout=timeout)

    def _merged_finalization_repo(self, root, trailing_prose=False):
        """Main repo plus the merged task branch that wrote the schema-2 evidence."""
        root = Path(root).resolve()

        def git(*args, cwd=root, check=True):
            return subprocess.run(['git', '-C', str(cwd), *args], check=check, capture_output=True, text=True)

        git('init', '-q', '-b', 'main')
        git('config', 'user.email', 'test@example.invalid')
        git('config', 'user.name', 'Test')
        (root / 'src').mkdir()
        (root / 'src' / 'app.py').write_text('stable\n', encoding='utf-8')
        (root / '.gitignore').write_text('/.worktrees/\n', encoding='utf-8')
        sheet = root / 'docs' / 'tasks' / 'demo.md'
        sheet.parent.mkdir(parents=True)
        sheet.write_text(
            '<!-- Task ID: demo -->\n```pipeline-contract\n'
            + json.dumps(self._finalization_contract()) + '\n```\n', encoding='utf-8')
        git('add', '.')
        git('commit', '-qm', 'baseline')
        baseline = git('rev-parse', 'HEAD').stdout.strip()
        worktree = root / '.worktrees' / 'demo'
        git('worktree', 'add', '-b', 'demo-task', str(worktree), baseline)
        self._write_schema_two_evidence(
            worktree / '.pipeline' / 'demo',
            branch='demo-task', worktree=str(worktree), head=baseline, main_cwd=str(root),
            trailing_prose=trailing_prose,
        )
        git('add', '.pipeline', cwd=worktree)
        git('commit', '-qm', 'task stage reports', cwd=worktree)
        (worktree / 'src' / 'app.py').write_text('task change\n', encoding='utf-8')
        git('add', 'src/app.py', cwd=worktree)
        git('commit', '-qm', 'task product change', cwd=worktree)
        git('merge', '--no-ff', '-m', 'merge demo-task', 'demo-task')
        return root, root / '.pipeline' / 'demo', baseline, git('rev-parse', 'HEAD').stdout.strip()

    def _unmerged_finalization_repo(self, root):
        """Single-branch repo whose evidence directory is finalized in place."""
        root = Path(root).resolve()

        def git(*args, check=True):
            return subprocess.run(['git', '-C', str(root), *args], check=check, capture_output=True, text=True)

        git('init', '-q', '-b', 'main')
        git('config', 'user.email', 'test@example.invalid')
        git('config', 'user.name', 'Test')
        (root / 'src').mkdir()
        (root / 'src' / 'app.py').write_text('stable\n', encoding='utf-8')
        git('add', '.')
        git('commit', '-qm', 'baseline')
        evidence = root / '.pipeline' / 'demo'
        self._write_schema_two_evidence(
            evidence, branch='main', worktree=str(root),
            head=git('rev-parse', 'HEAD').stdout.strip())
        return root, evidence, git

    def test_finalization_marker_head_survives_evidence_only_commits(self):
        from pipeline_tools.core import verify_finalization_snapshot
        with tempfile.TemporaryDirectory() as d:
            root, evidence, _baseline, merged = self._merged_finalization_repo(d)
            gate = self._run_cli(root, 'gate', 'post-merge', str(evidence),
                                 '--task-id', 'demo', '--branch', 'main')
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
            finalize = self._run_cli(root, 'planning', 'evidence-finalize', str(evidence),
                                     '--task-id', 'demo', '--success')
            self.assertEqual(finalize.returncode, 0, finalize.stdout + finalize.stderr)
            self.assertEqual(json.loads(finalize.stdout)['status'], 'finalized')
            marker_path = evidence / 'finalization.json'
            self.assertTrue(marker_path.is_file())
            marker = json.loads(marker_path.read_text(encoding='utf-8'))
            self.assertEqual(merged, marker['identity']['head'])
            # Publishing the marker is itself a commit, so it moves HEAD past the
            # head the marker recorded.
            subprocess.run(['git', '-C', str(root), 'add', '.pipeline/demo/finalization.json'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'finalization marker'], check=True)
            published = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                       check=True, capture_output=True, text=True).stdout.strip()
            self.assertNotEqual(merged, published)
            moved = subprocess.run(['git', '-C', str(root), 'diff', '--name-only', merged, 'HEAD'],
                                   check=True, capture_output=True, text=True).stdout.split()
            self.assertEqual(['.pipeline/demo/finalization.json'], moved)
            self.assertEqual([], verify_finalization_snapshot(evidence, marker))
            verify = self._run_cli(root, 'evidence', 'verify', str(evidence),
                                   '--task-id', 'demo', '--phase', 'finalized')
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
            again = self._run_cli(root, 'planning', 'evidence-finalize', str(evidence),
                                  '--task-id', 'demo', '--success')
            self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
            self.assertEqual(json.loads(again.stdout)['status'], 'finalized')

    def test_finalization_marker_head_is_still_stale_after_product_commits(self):
        from pipeline_tools.core import verify_finalization_snapshot
        with tempfile.TemporaryDirectory() as d:
            root, evidence, git = self._unmerged_finalization_repo(d)
            self.assertEqual(finalize_evidence(evidence, 'demo', True)['status'], 'finalized')
            marker = json.loads((evidence / 'finalization.json').read_text(encoding='utf-8'))
            # Publishing the marker (task evidence only) keeps it valid...
            git('add', '.pipeline/demo/finalization.json')
            git('commit', '-qm', 'finalization marker')
            self.assertEqual([], verify_finalization_snapshot(evidence, marker))
            # ...but a product-path commit after the marker head still fails.
            (root / 'src' / 'app.py').write_text('product change\n', encoding='utf-8')
            git('add', 'src/app.py')
            git('commit', '-qm', 'product change')
            self.assertIn('finalization head is stale', verify_finalization_snapshot(evidence, marker))
            # A recorded head that is not an ancestor of HEAD stays fail-closed.
            marker['identity']['head'] = '1' * 40
            self.assertEqual(['finalization head is stale'], verify_finalization_snapshot(evidence, marker))

    def test_finalization_marker_snapshot_mismatch_is_still_rejected(self):
        from pipeline_tools.core import verify_finalization_snapshot
        with tempfile.TemporaryDirectory() as d:
            root, evidence, git = self._unmerged_finalization_repo(d)
            self.assertEqual(finalize_evidence(evidence, 'demo', True)['status'], 'finalized')
            marker = json.loads((evidence / 'finalization.json').read_text(encoding='utf-8'))
            git('add', '.pipeline/demo/finalization.json')
            git('commit', '-qm', 'finalization marker')
            # The evidence-only advance is tolerated, so the only verdict left is
            # the retention snapshot.
            (evidence / 'final-check.md').write_text('tampered\n', encoding='utf-8')
            self.assertEqual(
                ['finalization retained evidence hash mismatch'],
                verify_finalization_snapshot(evidence, marker),
            )
            blocked = finalize_evidence(evidence, 'demo', True)
            self.assertEqual(blocked['status'], 'blocked')
            self.assertIn('finalization retained evidence hash mismatch', blocked['missing'])

    # --- Local state files survive finalization pruning ----------------------

    def _revision_chain_evidence_dir(self, evidence):
        """Give the merged task a revision-2 chain the reports were produced for."""
        digest = 'b' * 64
        (evidence / 'amendments.json').write_text(json.dumps({
            'schema': 1, 'task_id': 'demo',
            'revisions': [{
                'revision': 2, 'at': '2026-01-01T00:00:00+00:00', 'by': 'main',
                'requested_by': 'main', 'reason': 'tighten one acceptance assertion',
                'previous_sheet_sha256': 'a' * 64, 'sheet_sha256': digest,
                'changes': {},
            }],
        }), encoding='utf-8')
        (evidence / 'goal.json').write_text(json.dumps({
            'schema': 1, 'task_id': 'demo', 'task_sheet_sha256': digest,
        }), encoding='utf-8')
        for name in ('executor-report.md', 'review-report.md', 'final-check.md'):
            self._rewrite_schema_two_report(evidence, name, sheet_revision=2)
        return digest

    def test_finalization_keeps_local_state_files(self):
        from pipeline_tools.core import (
            RETAINED_EVIDENCE_NAMES,
            _recorded_task_sheet_sha256,
            task_sheet_revision,
        )
        with tempfile.TemporaryDirectory() as d:
            root, evidence, _baseline, _merged = self._merged_finalization_repo(d)
            digest = self._revision_chain_evidence_dir(evidence)
            goal_before = (evidence / 'goal.json').read_bytes()
            (evidence / 'raw-process.log').write_text('scratch\n', encoding='utf-8')
            gate = self._run_cli(root, 'gate', 'post-merge', str(evidence),
                                 '--task-id', 'demo', '--branch', 'main')
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
            finalize = self._run_cli(root, 'planning', 'evidence-finalize', str(evidence),
                                     '--task-id', 'demo', '--success')
            self.assertEqual(finalize.returncode, 0, finalize.stdout + finalize.stderr)
            self.assertEqual(json.loads(finalize.stdout)['status'], 'finalized')
            # The freeze record and the revision chain survive pruning...
            self.assertTrue((evidence / 'goal.json').is_file())
            self.assertTrue((evidence / 'amendments.json').is_file())
            # ...unchanged, so the facts the tool reads back are still the ones the
            # reports were produced against.
            self.assertEqual(goal_before, (evidence / 'goal.json').read_bytes())
            self.assertEqual(2, task_sheet_revision(root, 'demo')[0])
            self.assertEqual(digest, _recorded_task_sheet_sha256(root, 'demo'))
            # The retained evidence set is untouched...
            for name in RETAINED_EVIDENCE_NAMES:
                self.assertTrue((evidence / name).is_file(), name)
            # ...while an unrelated process artifact is still pruned.
            self.assertFalse((evidence / 'raw-process.log').exists())
            spared = set(RETAINED_EVIDENCE_NAMES) | {'goal.json', 'amendments.json'}
            leftovers = sorted(
                path.name for path in evidence.iterdir()
                if path.name not in spared and path.name != '.lifecycle.lock'
            )
            self.assertEqual([], leftovers)

    def test_finalized_verification_survives_another_tasks_evidence_commit(self):
        from pipeline_tools.core import verify_finalization_snapshot
        with tempfile.TemporaryDirectory() as d:
            root, evidence, _baseline, merged = self._merged_finalization_repo(d)
            gate = self._run_cli(root, 'gate', 'post-merge', str(evidence),
                                 '--task-id', 'demo', '--branch', 'main')
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
            finalize = self._run_cli(root, 'planning', 'evidence-finalize', str(evidence),
                                     '--task-id', 'demo', '--success')
            self.assertEqual(finalize.returncode, 0, finalize.stdout + finalize.stderr)
            self.assertEqual(json.loads(finalize.stdout)['status'], 'finalized')
            marker_path = evidence / 'finalization.json'
            subprocess.run(['git', '-C', str(root), 'add', '.pipeline/demo/finalization.json'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'finalization marker'], check=True)
            marker_bytes = marker_path.read_bytes()
            # Another task publishes its own evidence: a .pipeline path, not a
            # product change, so it must not invalidate this closed task.
            other = root / '.pipeline' / 'other-task'
            other.mkdir(parents=True)
            (other / 'executor-report.md').write_text('other task evidence\n', encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', '.pipeline/other-task'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'other task evidence'], check=True)
            moved = subprocess.run(
                ['git', '-C', str(root), 'diff', '--name-only', merged, 'HEAD'],
                check=True, capture_output=True, text=True,
            ).stdout.split()
            self.assertIn('.pipeline/other-task/executor-report.md', moved)
            self.assertNotIn('src/app.py', moved)
            # The verdict survives without deleting the marker or rewriting its identity.
            self.assertTrue(marker_path.is_file())
            self.assertEqual(marker_bytes, marker_path.read_bytes())
            marker = json.loads(marker_bytes)
            self.assertEqual(merged, marker['identity']['head'])
            self.assertEqual([], verify_finalization_snapshot(evidence, marker))
            verify = self._run_cli(root, 'evidence', 'verify', str(evidence),
                                   '--task-id', 'demo', '--phase', 'finalized')
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    # --- Task sheet archival ------------------------------------------------

    def test_sheet_resolver_finds_all_three_locations(self):
        """The resolver locates all three sheet homes and never guesses.

        A sheet's state is encoded by its location: `docs/tasks/` for in-flight
        work, the task's evidence directory for a terminal task, and the flat
        archive for a terminal task without an evidence directory.  Ambiguity and
        absence are errors, so a caller cannot silently pick a candidate.
        """
        from pipeline_tools.core import task_sheet_resolution

        task_id = 'sheet-task'
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            active = root / 'docs' / 'tasks' / f'{task_id}.md'
            evidence_sheet = root / '.pipeline' / task_id / f'{task_id}.md'
            archived = root / '.pipeline' / 'archive' / f'{task_id}.md'
            active.parent.mkdir(parents=True)
            active.write_text('# active sheet\n', encoding='utf-8')

            resolved, errors = task_sheet_resolution(root, task_id)
            self.assertEqual([], errors)
            self.assertEqual(active, resolved)

            active.unlink()
            evidence_sheet.parent.mkdir(parents=True)
            evidence_sheet.write_text('# terminal sheet\n', encoding='utf-8')
            resolved, errors = task_sheet_resolution(root, task_id)
            self.assertEqual([], errors)
            self.assertEqual(evidence_sheet, resolved)

            evidence_sheet.unlink()
            archived.parent.mkdir(parents=True)
            archived.write_text('# archived sheet\n', encoding='utf-8')
            resolved, errors = task_sheet_resolution(root, task_id)
            self.assertEqual([], errors)
            self.assertEqual(archived, resolved)

            # The same id in two places is ambiguous, not a preference.
            active.write_text('# active sheet\n', encoding='utf-8')
            resolved, errors = task_sheet_resolution(root, task_id)
            self.assertIsNone(resolved)
            self.assertEqual(1, len(errors), errors)
            self.assertIn('multiple locations', errors[0])

            # No location at all is a missing contract.
            active.unlink()
            archived.unlink()
            resolved, errors = task_sheet_resolution(root, task_id)
            self.assertIsNone(resolved)
            self.assertEqual(['task sheet not found for sheet-task'], errors)

    def test_worklist_checks_ignore_terminal_sheets(self):
        """The worklist reads only active sheets for "sheet without worktree".

        A terminal sheet — one living in its evidence directory or in the flat
        archive — is closed work, not an interrupted in-flight task, so it must
        not raise the warning.  A sheet still in `docs/tasks/` without a worktree
        must keep raising it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._scene_repo(root)
            (root / '.pipeline' / 'closed-task').mkdir(parents=True)
            (root / '.pipeline' / 'closed-task' / 'closed-task.md').write_text(
                '# closed\n', encoding='utf-8')
            (root / '.pipeline' / 'archive').mkdir(parents=True)
            (root / '.pipeline' / 'archive' / 'archived-task.md').write_text(
                '# archived\n', encoding='utf-8')
            (root / 'docs' / 'tasks').mkdir(parents=True)
            (root / 'docs' / 'tasks' / 'pending-task.md').write_text(
                '# pending\n', encoding='utf-8')
            self._commit_all(root, 'task sheets in three states')

            result = planning_preflight(root)
            scenes = result['task_scenes']
            self.assertEqual(['pending-task'], scenes['sheets_without_worktree'])
            self.assertNotIn('closed-task', scenes['sheets_without_worktree'])
            self.assertNotIn('archived-task', scenes['sheets_without_worktree'])
            self.assertEqual(
                [], [item for item in scenes['leftover_evidence']
                    if item in {'closed-task', 'archived-task', 'archive'}])
            warned = ' '.join(result['warnings'])
            self.assertIn('pending-task', warned)
            for task_id in ('closed-task', 'archived-task'):
                self.assertNotIn(task_id, warned)

    def test_archive_directory_is_not_treated_as_task_evidence(self):
        """`.pipeline/archive` is a sheet quarantine, not a task evidence dir.

        The evidence scan excludes it alongside the `planning` and `metrics`
        bookkeeping directories, so it never appears as a task named `archive`
        and never produces leftover-evidence noise.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._scene_repo(root)
            (root / '.pipeline' / 'archive').mkdir(parents=True)
            (root / '.pipeline' / 'archive' / 'closed-task.md').write_text(
                '# closed\n', encoding='utf-8')
            (root / '.pipeline' / 'archive' / 'notes.md').write_text(
                '# notes, not evidence\n', encoding='utf-8')
            self._commit_all(root, 'archive a terminal sheet')

            result = planning_preflight(root)
            scenes = result['task_scenes']
            for key, values in scenes.items():
                self.assertNotIn('archive', values, key)
            self.assertEqual([], scenes['leftover_evidence'])
            reported = ' '.join(result['warnings'] + result['errors'])
            self.assertNotIn('archive', reported)

    def test_archived_sheet_still_answers_worktree_without_sheet(self):
        """A terminal sheet still satisfies "no worktree without a sheet".

        The invariant is about a task worktree existing without its committed
        sheet; a sheet that was archived after the work was delivered still
        answers it, so the scene is not reported as a violation.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._scene_repo(root)
            (root / '.pipeline' / 'archive').mkdir(parents=True)
            (root / '.pipeline' / 'archive' / 'closed-task.md').write_text(
                '# closed\n', encoding='utf-8')
            self._commit_all(root, 'archive a terminal sheet')
            (root / '.worktrees' / 'closed-task').mkdir(parents=True)

            result = planning_preflight(root)
            self.assertEqual([], result['task_scenes']['worktrees_without_sheet'])
            self.assertNotIn(
                'task worktree has no committed task sheet: closed-task',
                result['errors'],
            )

    def _archival_scene(self, root, *, with_worktree):
        """A merged task with complete evidence and an optional live worktree."""
        self._scene_repo(root)
        sheet = root / 'docs' / 'tasks' / 'demo.md'
        sheet.parent.mkdir(parents=True)
        sheet.write_text(
            '<!-- Task ID: demo -->\n```pipeline-contract\n'
            + json.dumps(self._finalization_contract()) + '\n```\n', encoding='utf-8')
        self._write_valid_finalization_fixture(root / '.pipeline' / 'demo')
        self._commit_all(root, 'frozen sheet and stage evidence')
        if with_worktree:
            subprocess.run(
                ['git', 'worktree', 'add', '-b', 'demo-task', '.worktrees/demo', 'HEAD'],
                cwd=root, check=True, capture_output=True)
        return root, root / '.pipeline' / 'demo', sheet

    def test_finalization_moves_the_sheet_and_refuses_while_the_worktree_lives(self):
        """Finalization archives the sheet, and a live worktree blocks the move.

        With the worktree deleted the closed task's sheet moves from
        `docs/tasks/` to its evidence directory and stays tracked by Git.  While
        `.worktrees/<task-id>` still exists the delivery is unfinished, so the
        step is blocked and moves nothing.
        """
        # (a) the worktree still lives: blocked, no file moved.
        with tempfile.TemporaryDirectory() as d:
            root, evidence, sheet = self._archival_scene(Path(d), with_worktree=True)
            self.assertEqual(finalize_evidence(evidence, 'demo', True)['status'], 'finalized')
            blocked = archive_task_sheet(root, 'demo')
            self.assertEqual('blocked', blocked['status'], blocked)
            self.assertIn('.worktrees/demo', ' '.join(blocked['errors']))
            self.assertTrue(sheet.is_file())
            self.assertFalse((evidence / 'demo.md').exists())

        # (b) the worktree is gone: the sheet moves and stays tracked.
        with tempfile.TemporaryDirectory() as d:
            root, evidence, sheet = self._archival_scene(Path(d), with_worktree=False)
            self.assertEqual(finalize_evidence(evidence, 'demo', True)['status'], 'finalized')
            moved = archive_task_sheet(root, 'demo')
            self.assertEqual('archived', moved['status'], moved)
            self.assertEqual('docs/tasks/demo.md', moved['from'])
            self.assertEqual('.pipeline/demo/demo.md', moved['to'])
            self.assertTrue(moved['tracked'])
            self.assertFalse(sheet.exists())
            self.assertTrue((evidence / 'demo.md').is_file())
            self.assertEqual(
                0,
                subprocess.run(
                    ['git', 'ls-files', '--error-unmatch', '.pipeline/demo/demo.md'],
                    cwd=root, capture_output=True).returncode,
            )
            # The moved sheet is still resolvable, now from its terminal home.
            from pipeline_tools.core import task_sheet_resolution
            resolved, errors = task_sheet_resolution(root, 'demo')
            self.assertEqual([], errors)
            self.assertEqual(evidence / 'demo.md', resolved)
            # Repeating the step is an idempotent no-op.
            again = archive_task_sheet(root, 'demo')
            self.assertEqual('archived', again['status'], again)
            self.assertTrue((evidence / 'demo.md').is_file())
            self.assertFalse(sheet.exists())

    def test_migrated_sheets_keep_their_bytes_and_are_tracked(self):
        """The migration moves terminal sheets without touching a byte.

        A terminal sheet with an evidence directory lands in
        ``.pipeline/<task-id>/<task-id>.md``; one without lands in
        ``.pipeline/archive/<task-id>.md``.  In both cases the bytes are
        identical to the frozen sheet and Git still tracks it, so no freeze
        hash or retained snapshot can move.
        """
        import hashlib

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._scene_repo(root)
            task_ids = ('closed-with-evidence', 'closed-archived', 'another-closed')
            (root / 'docs' / 'tasks').mkdir(parents=True)
            for task_id in task_ids:
                (root / 'docs' / 'tasks' / f'{task_id}.md').write_text(
                    f'<!-- Task ID: {task_id} -->\n', encoding='utf-8')
            for task_id in ('closed-with-evidence', 'another-closed'):
                (root / '.pipeline' / task_id).mkdir(parents=True)
            self._commit_all(root, 'frozen task sheets')

            before = {
                task_id: hashlib.sha256(
                    (root / 'docs' / 'tasks' / f'{task_id}.md').read_bytes()
                ).hexdigest()
                for task_id in task_ids
            }
            for task_id in task_ids:
                moved = archive_task_sheet(root, task_id)
                self.assertEqual('archived', moved['status'], moved)
                self.assertTrue(moved['tracked'], moved)

            for task_id in task_ids:
                if task_id == 'closed-archived':
                    target = root / '.pipeline' / 'archive' / f'{task_id}.md'
                else:
                    target = root / '.pipeline' / task_id / f'{task_id}.md'
                self.assertTrue(target.is_file(), target)
                self.assertFalse((root / 'docs' / 'tasks' / f'{task_id}.md').exists(), task_id)
                self.assertEqual(
                    before[task_id],
                    hashlib.sha256(target.read_bytes()).hexdigest(),
                    task_id,
                )
                self.assertEqual(
                    0,
                    subprocess.run(
                        ['git', 'ls-files', '--error-unmatch', target.relative_to(root).as_posix()],
                        cwd=root, capture_output=True).returncode,
                    task_id,
                )

    def test_migration_leaves_no_active_sheet_without_a_worktree(self):
        """A migrated terminal sheet leaves the in-flight worklist.

        Once the sheet of a closed task lives in its evidence directory or in the
        archive it is no longer in-flight work, so the scene check must not count
        it as a sheet without a worktree.  A terminal sheet left behind in
        ``docs/tasks/`` would still be counted, so the fixture names any
        straggler rather than asserting a clean repository.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._scene_repo(root)
            (root / 'docs' / 'tasks').mkdir(parents=True)
            (root / 'docs' / 'tasks' / 'pending-task.md').write_text(
                '<!-- Task ID: pending-task -->\n', encoding='utf-8')
            for task_id in ('closed-a', 'closed-b'):
                (root / '.pipeline' / task_id).mkdir(parents=True)
                (root / '.pipeline' / task_id / f'{task_id}.md').write_text(
                    f'# {task_id}\n', encoding='utf-8')
            (root / '.pipeline' / 'archive').mkdir(parents=True)
            (root / '.pipeline' / 'archive' / 'closed-c.md').write_text(
                '# closed-c\n', encoding='utf-8')
            self._commit_all(root, 'migrated terminal sheets')

            scenes = planning_preflight(root)['task_scenes']
            self.assertEqual(['pending-task'], scenes['sheets_without_worktree'], scenes)
            self.assertEqual(
                [],
                [task_id for task_id in scenes['sheets_without_worktree']
                 if task_id in {'closed-a', 'closed-b', 'closed-c'}],
                scenes,
            )
            # The archive is not a task evidence directory and a moved sheet
            # answers the directory, so nothing is left over.
            self.assertEqual([], scenes['leftover_evidence'], scenes)

    def test_orphan_evidence_directory_is_no_longer_leftover(self):
        """An evidence directory with no sheet is leftover until a note names it.

        Adding a sheet named after the directory (``.pipeline/<id>/<id>.md``)
        makes the directory resolvable by filename and removes it from the
        leftover set, without changing anything the resolver already holds.
        """
        from pipeline_tools.core import task_sheet_resolution

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._scene_repo(root)
            task_id = 'orphan-continuation'
            evidence = root / '.pipeline' / task_id
            evidence.mkdir(parents=True)
            (evidence / 'executor-report.md').write_text('report\n', encoding='utf-8')
            self._commit_all(root, 'orphan evidence directory')

            before = planning_preflight(root)['task_scenes']
            self.assertIn(task_id, before['leftover_evidence'], before)
            resolved, errors = task_sheet_resolution(root, task_id)
            self.assertIsNone(resolved, errors)

            (evidence / f'{task_id}.md').write_text(
                f'<!-- Task ID: {task_id} -->\n', encoding='utf-8')
            self._commit_all(root, 'historical note names the directory')

            after = planning_preflight(root)['task_scenes']
            self.assertNotIn(task_id, after['leftover_evidence'], after)
            resolved, errors = task_sheet_resolution(root, task_id)
            self.assertEqual([], errors, errors)
            self.assertEqual(evidence / f'{task_id}.md', resolved)


if __name__ == '__main__': unittest.main()
