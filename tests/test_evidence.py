import json
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.core import evidence_freshness, evidence_verify, gate_check


def report(role, task_id='demo', branch='feature/demo', status='PASS'):
    evidence = {
        'schema': 1,
        'task_id': task_id,
        'worktree': '.worktrees/demo',
        'branch': branch,
        'role': role,
        'round': 1,
        'status': status,
        'commands': [
            {
                'command': 'python -m unittest',
                'exit_code': 0,
                'evidence_ref': '.pipeline/demo/test.log',
            }
        ],
        'assertions': ['the observed result matches the contract'],
        'evidence_refs': ['.pipeline/demo/test.log'],
        'unverified': [],
    }
    return '```pipeline-evidence\n' + json.dumps(evidence) + '\n```\n'


class EvidenceTests(unittest.TestCase):
    def _make_git_repo(self, root):
        import subprocess

        def run(*args):
            return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True)

        run('init', '-q')
        run('config', 'user.email', 'test@example.invalid')
        run('config', 'user.name', 'Test')
        (root / 'src').mkdir()
        (root / 'src' / 'app.py').write_text('stable\n', encoding='utf-8')
        run('add', '.')
        run('commit', '-qm', 'product baseline')
        return run('rev-parse', 'HEAD').stdout.strip()

    def _write_result(self, root, directory, product_head):
        result = {
            'schema': 1,
            'task_id': 'demo',
            'role': 'executor',
            'status': 'pass',
            'identity': {'product_head': product_head},
            'acceptance': [{'id': 'acceptance-test-1', 'evidence_refs': ['.pipeline/demo/test.log']}],
            'unverified': [],
        }
        path = directory / 'executor-result.json'
        path.write_text(json.dumps(result), encoding='utf-8')
        return path

    def test_freshness_allows_only_task_evidence_commit_after_product_head(self):
        import subprocess

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            product_head = self._make_git_repo(root)
            directory = root / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            (directory / 'test.log').write_text('evidence\n', encoding='utf-8')
            # Freshness must be able to read a frozen contract, otherwise the
            # missing requirements source is a blocker rather than a pass.
            self._task_with_plan_hash(root)
            result_path = self._write_result(root, directory, product_head)
            subprocess.run(['git', '-C', str(root), 'add', '.pipeline'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'evidence'], check=True)
            value = evidence_freshness(root, directory, result_path)
            self.assertEqual(value['status'], 'pass', value)
            self.assertEqual(value['unverified'], [])
            self.assertTrue(any(item.get('fact') == 'evidence_only' and item.get('value') for item in value['observed']))

    def test_freshness_blocks_product_drift_from_product_head(self):
        import subprocess

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            product_head = self._make_git_repo(root)
            directory = root / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            (directory / 'test.log').write_text('evidence\n', encoding='utf-8')
            result_path = self._write_result(root, directory, product_head)
            (root / 'src' / 'app.py').write_text('changed\n', encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', 'src/app.py', '.pipeline'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'product drift'], check=True)
            value = evidence_freshness(root, directory, result_path)
            self.assertEqual(value['status'], 'blocked')
            self.assertIn('product/test HEAD drifted', value['errors'])

    def test_freshness_without_product_head_keeps_strict_legacy_check(self):
        import subprocess

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            product_head = self._make_git_repo(root)
            directory = root / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            (directory / 'test.log').write_text('evidence\n', encoding='utf-8')
            result_path = self._write_result(root, directory, product_head)
            result = json.loads(result_path.read_text(encoding='utf-8'))
            result['identity'] = {'head': product_head}
            result_path.write_text(json.dumps(result), encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', '.pipeline'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'evidence'], check=True)
            value = evidence_freshness(root, directory, result_path)
            self.assertEqual(value['status'], 'blocked')
            self.assertIn('result HEAD is stale', value['errors'])

    def _make_evidence_dir(self, root, statuses=None):
        directory = root / '.pipeline' / 'demo'
        directory.mkdir(parents=True)
        artifact = directory / 'test.log'
        artifact.write_text('observed test output', encoding='utf-8')
        statuses = statuses or {}
        for name, role in {
            'executor-report.md': 'executor',
            'review-report.md': 'reviewer',
            'final-check.md': 'main-final',
        }.items():
            status = statuses.get(role, 'PASS')
            (directory / name).write_text(report(role, status=status), encoding='utf-8')
        return directory

    def test_all_reports_require_machine_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            self.assertEqual(evidence_verify(directory, 'demo', 'feature/demo'), [])

    def test_task_relative_evidence_references_resolve_from_canonical_task_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            for name in ('executor-report.md', 'review-report.md', 'final-check.md'):
                report_path = directory / name
                report_path.write_text(
                    report_path.read_text(encoding='utf-8').replace('.pipeline/demo/test.log', 'test.log'),
                    encoding='utf-8',
                )
            self.assertEqual(evidence_verify(directory, 'demo', 'feature/demo'), [])

    def test_nonpassing_report_is_structurally_valid_but_gate_rejects_it(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root, {'reviewer': 'BLOCKED'})
            self.assertEqual(evidence_verify(directory, 'demo', 'feature/demo'), [])
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertTrue(any('review-report.md' in error for error in errors))

    def test_missing_evidence_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = root / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            for name, role in {
                'executor-report.md': 'executor',
                'review-report.md': 'reviewer',
                'final-check.md': 'main-final',
            }.items():
                (directory / name).write_text(report(role), encoding='utf-8')
            errors = evidence_verify(directory, 'demo', 'feature/demo')
            self.assertTrue(any('evidence_ref' in error for error in errors))

    def test_absolute_evidence_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            absolute = str(root / '.pipeline' / 'demo' / 'test.log').replace('\\', '/')
            for name, role in {
                'executor-report.md': 'executor',
                'review-report.md': 'reviewer',
                'final-check.md': 'main-final',
            }.items():
                text = report(role).replace('.pipeline/demo/test.log', absolute)
                (directory / name).write_text(text, encoding='utf-8')
            errors = evidence_verify(directory, 'demo', 'feature/demo')
            self.assertTrue(any('relative' in error for error in errors))

    def test_passing_report_with_nonzero_command_is_rejected_by_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            text = report('executor').replace('"exit_code": 0', '"exit_code": 7')
            (directory / 'executor-report.md').write_text(text, encoding='utf-8')
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertTrue(errors)
            self.assertTrue(any('non-zero' in error for error in errors))

    def test_missing_report_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(evidence_verify(Path(d) / 'demo', 'demo'))

    def test_identity_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'demo'
            p.mkdir()
            for name, role in (
                ('executor-report.md', 'executor'),
                ('review-report.md', 'reviewer'),
                ('final-check.md', 'main-final'),
            ):
                (p / name).write_text(report(role, task_id='other'), encoding='utf-8')
            self.assertTrue(evidence_verify(p, 'demo', 'feature/demo'))

    def test_prose_markers_without_machine_block_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'demo'
            p.mkdir()
            text = 'task-id demo worktree x branch feature/demo round 1 command c exit code 0 assertion a evidence e'
            for name in ('executor-report.md', 'review-report.md', 'final-check.md'):
                (p / name).write_text(text, encoding='utf-8')
            errors = evidence_verify(p, 'demo', 'feature/demo')
            self.assertTrue(any('pipeline-evidence' in error for error in errors))

    def test_gate_requires_pass_statuses(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'demo'
            p.mkdir()
            (p / 'executor-report.md').write_text(report('executor'), encoding='utf-8')
            (p / 'review-report.md').write_text(report('reviewer', status='BLOCKED'), encoding='utf-8')
            (p / 'final-check.md').write_text(report('main-final', status='READY-TO-MERGE'), encoding='utf-8')
            errors = gate_check(p, 'demo', 'feature/demo', 'pre-merge')
            self.assertTrue(any('review-report.md' in error for error in errors))

    def _task_with_plan_hash(self, root, task_id='demo'):
        import hashlib

        root = Path(root)
        plan = root / 'implement-plan.md'
        plan.write_text('frozen plan\n', encoding='utf-8')
        digest = hashlib.sha256(plan.read_bytes()).hexdigest()
        directory = root / '.pipeline' / task_id
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'implement-plan.json').write_text(
            json.dumps({'schema': 1, 'task_id': task_id, 'sha256': digest}), encoding='utf-8',
        )
        contract = {
            'schema': 1, 'task_id': task_id,
            'allowed_paths': ['src/**'], 'forbidden_paths': [],
            'acceptance_tests': [{
                'id': 'AT1', 'evidence_level': 1,
                'test_ref': 'tests/test_evidence.py', 'command_ref': 'python -m unittest',
            }],
        }
        sheet = root / 'docs' / 'tasks' / f'{task_id}.md'
        sheet.parent.mkdir(parents=True)
        sheet.write_text(
            f'<!-- Task ID: {task_id} -->\n```pipeline-contract\n' + json.dumps(contract) + '\n```\n',
            encoding='utf-8',
        )
        return plan

    def test_gate_pre_merge_blocks_implement_plan_drift_after_dispatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            plan = self._task_with_plan_hash(root)
            plan.write_text('mutated plan\n', encoding='utf-8')
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertTrue(any('drift' in error for error in errors), errors)

    def test_schema2_task_with_recorded_hash_detects_drift(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            plan = self._task_with_plan_hash(root)
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertEqual([error for error in errors if 'implement-plan' in error], [])
            plan.write_text('mutated plan\n', encoding='utf-8')
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertTrue(any('drift' in error for error in errors), errors)


    def _task_without_recorded_hash(self, root, task_id='demo'):
        root = Path(root)
        (root / 'implement-plan.md').write_text('frozen plan\n', encoding='utf-8')
        contract = {
            'schema': 2, 'task_id': task_id, 'task_type': 'repair',
            'implement_plan': {'path': 'implement-plan.md'},
            'allowed_paths': ['src/**'], 'forbidden_paths': [],
            'operations': [{
                'id': 'op', 'kind': 'validate', 'scope': 'task',
                'acceptance_tests': ['acceptance-test-1'],
            }],
            'chain': {
                name: ['src/app.py']
                for name in ('entry', 'interaction', 'application', 'domain',
                             'persistence', 'readback', 'recovery')
            },
            'dependencies': [],
            'acceptance_tests': [{
                'id': 'acceptance-test-1', 'evidence_level': 2,
                'test_ref': 'tests/test_evidence.py', 'command_ref': 'python -m unittest',
            }],
            'required_evidence_levels': [2],
        }
        sheet = root / 'docs' / 'tasks' / f'{task_id}.md'
        sheet.parent.mkdir(parents=True, exist_ok=True)
        sheet.write_text(
            f'<!-- Task ID: {task_id} -->\n```pipeline-contract\n' + json.dumps(contract) + '\n```\n',
            encoding='utf-8',
        )

    def test_schema2_task_without_recorded_hash_passes_gate_and_reports_unverified(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            self._task_without_recorded_hash(root)
            self.assertFalse((root / '.pipeline' / 'demo' / 'implement-plan.json').exists())
            unverified = []
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge', unverified=unverified)
            self.assertEqual([error for error in errors if 'implement-plan' in error], [], errors)
            self.assertTrue(any('unrecorded' in item for item in unverified), unverified)

    def test_freshness_contract_missing_is_a_blocker_never_a_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            result_path = directory / 'executor-result.json'
            result_path.write_text(json.dumps({
                'schema': 1, 'task_id': 'demo', 'role': 'executor', 'status': 'pass',
                'identity': {}, 'acceptance': [], 'unverified': [],
            }), encoding='utf-8')
            self.assertFalse((root / 'docs' / 'tasks' / 'demo.md').exists())
            value = evidence_freshness(root, directory, result_path)
            self.assertEqual(value['status'], 'blocked')
            self.assertTrue(value['unverified'], value)
            self.assertTrue(any('contract' in error for error in value['errors']), value)

    def test_gate_and_freshness_agree_on_missing_contract(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            result_path = directory / 'executor-result.json'
            result_path.write_text(json.dumps({
                'schema': 1, 'task_id': 'demo', 'role': 'executor', 'status': 'pass',
                'identity': {}, 'acceptance': [], 'unverified': [],
            }), encoding='utf-8')
            gate_unverified = []
            gate_errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge', unverified=gate_unverified)
            freshness = evidence_freshness(root, directory, result_path)
            self.assertTrue(any('contract' in error for error in gate_errors), gate_errors)
            self.assertEqual(freshness['status'], 'blocked')
            self.assertTrue(any('contract' in error for error in freshness['errors']), freshness)
            self.assertTrue(freshness['unverified'])

    def test_gate_unverified_is_empty_when_recorded_hash_matches(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            self._task_with_plan_hash(root)
            unverified = []
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge', unverified=unverified)
            self.assertEqual([error for error in errors if 'implement-plan' in error], [], errors)
            self.assertEqual(unverified, [])

    def test_evidence_block_parses_when_body_contains_other_code_fences(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'demo'
            p.mkdir()
            for name, role in (
                ('executor-report.md', 'executor'),
                ('review-report.md', 'reviewer'),
                ('final-check.md', 'main-final'),
            ):
                text = report(role) + '\n## body\n\n```python\nprint(1)\n```\n'
                (p / name).write_text(text, encoding='utf-8')
            errors = evidence_verify(p, 'demo', 'feature/demo')
            self.assertFalse(any('closed' in error for error in errors), errors)

    def test_evidence_block_without_closing_fence_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'demo'
            p.mkdir()
            for name, role in (
                ('executor-report.md', 'executor'),
                ('review-report.md', 'reviewer'),
                ('final-check.md', 'main-final'),
            ):
                block = report(role)
                (p / name).write_text(block[: block.rindex('```')], encoding='utf-8')
            errors = evidence_verify(p, 'demo', 'feature/demo')
            self.assertTrue(any('not closed' in error for error in errors), errors)

    def test_declared_expected_exit_code_allows_nonzero_result(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            text = report('reviewer').replace(
                '"exit_code": 0', '"exit_code": 4, "expected_exit_code": 4'
            )
            (directory / 'review-report.md').write_text(text, encoding='utf-8')
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertFalse(any('exit_code' in error for error in errors), errors)

    def test_undeclared_nonzero_exit_code_is_still_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            text = report('reviewer').replace('"exit_code": 0', '"exit_code": 4')
            (directory / 'review-report.md').write_text(text, encoding='utf-8')
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertIn('review-report.md contains a non-zero command exit_code', errors)

    def test_expected_exit_code_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            text = report('reviewer').replace(
                '"exit_code": 0', '"exit_code": 4, "expected_exit_code": 3'
            )
            (directory / 'review-report.md').write_text(text, encoding='utf-8')
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertTrue(any('expected_exit_code' in error for error in errors), errors)

    def test_non_integer_expected_exit_code_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            text = report('reviewer').replace(
                '"exit_code": 0', '"exit_code": 0, "expected_exit_code": "zero"'
            )
            (directory / 'review-report.md').write_text(text, encoding='utf-8')
            errors = evidence_verify(directory, 'demo', 'feature/demo')
            self.assertTrue(any('expected_exit_code' in error for error in errors), errors)

    def test_gate_rejects_boolean_expected_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            text = report('reviewer').replace(
                '"exit_code": 0', '"exit_code": 1, "expected_exit_code": true'
            )
            (directory / 'review-report.md').write_text(text, encoding='utf-8')
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertTrue(any('expected_exit_code' in error for error in errors), errors)


class MachineResultGateTests(unittest.TestCase):
    def test_pre_merge_requires_all_three_machine_results(self):
        from pipeline_tools.core import _machine_result_errors

        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            errors = _machine_result_errors(directory, 'pre-merge')
            self.assertIn('missing executor-result.json', errors)
            self.assertIn('missing reviewer-result.json', errors)
            self.assertIn('missing final-result.json', errors)

    def test_unreadable_machine_result_is_rejected(self):
        from pipeline_tools.core import _machine_result_errors

        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            for name in ('executor-result.json', 'reviewer-result.json', 'final-result.json'):
                (directory / name).write_text('{}', encoding='utf-8')
            (directory / 'reviewer-result.json').write_text('not json', encoding='utf-8')
            errors = _machine_result_errors(directory, 'pre-merge')
            self.assertIn('reviewer-result.json is not a readable JSON object', errors)

    def test_valid_machine_results_are_accepted(self):
        from pipeline_tools.core import _machine_result_errors

        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            for name in ('executor-result.json', 'reviewer-result.json', 'final-result.json'):
                (directory / name).write_text('{}', encoding='utf-8')
            self.assertEqual(_machine_result_errors(directory, 'pre-merge'), [])


if __name__ == '__main__':
    unittest.main()

