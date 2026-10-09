import json
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.core import (
    evidence_freshness,
    evidence_revision_status,
    evidence_verify,
    gate_check,
    verify_structured_result,
)


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
    def _canonical_evidence_dir(self, root, task_id='demo'):
        directory = Path(root) / '.pipeline' / task_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

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

    def test_schema2_report_identity_must_match_current_git_identity(self):
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            head = self._make_git_repo(root)
            directory = root / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            (directory / 'test.log').write_text('evidence\n', encoding='utf-8')
            for role, name in (('executor', 'executor-report.md'), ('reviewer', 'review-report.md'), ('main-final', 'final-check.md')):
                value = json.loads(report(role).split('\n')[1])
                value.update({'schema': 2, 'head': '0' * 40, 'generated_at': '2026-01-01T00:00:00+00:00', 'worktree': str(root / 'wrong')})
                (directory / name).write_text('```pipeline-evidence\n' + json.dumps(value) + '\n```\n', encoding='utf-8')
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertTrue(any('current Git identity' in error for error in errors), errors)
            self.assertNotEqual(head, '0' * 40)

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
            self.assertTrue(evidence_verify(self._canonical_evidence_dir(d), 'demo'))

    def test_identity_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._canonical_evidence_dir(d)
            for name, role in (
                ('executor-report.md', 'executor'),
                ('review-report.md', 'reviewer'),
                ('final-check.md', 'main-final'),
            ):
                (p / name).write_text(report(role, task_id='other'), encoding='utf-8')
            self.assertTrue(evidence_verify(p, 'demo', 'feature/demo'))

    def test_prose_markers_without_machine_block_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._canonical_evidence_dir(d)
            text = 'task-id demo worktree x branch feature/demo round 1 command c exit code 0 assertion a evidence e'
            for name in ('executor-report.md', 'review-report.md', 'final-check.md'):
                (p / name).write_text(text, encoding='utf-8')
            errors = evidence_verify(p, 'demo', 'feature/demo')
            self.assertTrue(any('pipeline-evidence' in error for error in errors))

    def test_gate_requires_pass_statuses(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._canonical_evidence_dir(d)
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
            p = self._canonical_evidence_dir(d)
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
            p = self._canonical_evidence_dir(d)
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

    def _commit_freshness_fixture(self, root, directory, product_head, refs):
        import subprocess

        result = {
            'schema': 1,
            'task_id': 'demo',
            'role': 'executor',
            'status': 'pass',
            'identity': {'product_head': product_head},
            'acceptance': [{'id': 'acceptance-test-1', 'evidence_refs': refs}],
            'unverified': [],
        }
        result_path = directory / 'executor-result.json'
        result_path.write_text(json.dumps(result), encoding='utf-8')
        subprocess.run(['git', '-C', str(root), 'add', '.pipeline'], check=True)
        subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'evidence'], check=True)
        return result_path

    def test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            product_head = self._make_git_repo(root)
            directory = root / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            (directory / 'test.log').write_text('evidence\n', encoding='utf-8')
            self._task_with_plan_hash(root)
            result_path = self._commit_freshness_fixture(root, directory, product_head, ['test.log'])
            value = evidence_freshness(root, directory, result_path)
            self.assertNotIn('evidence artifact missing', value['errors'], value)
            self.assertEqual(value['status'], 'pass', value)

    def test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            product_head = self._make_git_repo(root)
            directory = root / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            (directory / 'test.log').write_text('evidence\n', encoding='utf-8')
            self._task_with_plan_hash(root)
            absolute = str(directory / 'test.log').replace('\\', '/')
            result_path = self._commit_freshness_fixture(
                root, directory, product_head, [absolute, '../outside.log']
            )
            value = evidence_freshness(root, directory, result_path)
            self.assertIn('evidence artifact missing', value['errors'], value)
            self.assertEqual(value['status'], 'blocked', value)

    def test_freshness_allows_metrics_only_commit_after_product_head(self):
        import subprocess

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            product_head = self._make_git_repo(root)
            directory = root / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            (directory / 'test.log').write_text('evidence\n', encoding='utf-8')
            self._task_with_plan_hash(root)
            result_path = self._commit_freshness_fixture(root, directory, product_head, ['test.log'])
            metrics = root / '.pipeline' / 'metrics'
            metrics.mkdir(parents=True, exist_ok=True)
            (metrics / 'event-1.json').write_text('{"schema": 1}\n', encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', '.pipeline/metrics'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'metrics'], check=True)
            value = evidence_freshness(root, directory, result_path)
            self.assertNotIn('product/test HEAD drifted', value['errors'], value)
            self.assertTrue(
                any(item.get('fact') == 'evidence_only' and item.get('value') for item in value['observed']),
                value,
            )

    def test_references_execution_and_review_documents_freshness_resolution_basis(self):
        root = Path(__file__).parents[1]
        acceptance = (root / 'references' / 'acceptance-evidence.md').read_text(encoding='utf-8')
        execution = (root / 'references' / 'execution-and-review.md').read_text(encoding='utf-8')
        for text in (acceptance, execution):
            self.assertIn('acceptance[].evidence_refs', text)
            self.assertIn('证据目录', text)
            self.assertIn('.pipeline/metrics/', text)
        self.assertIn('evidence_only', acceptance)
        self.assertIn('evidence_only', execution)

    def test_gate_rejects_acceptance_test_ref_method_absent_from_named_file(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._make_evidence_dir(root)
            (root / 'tests').mkdir()
            (root / 'tests' / 'test_present.py').write_text(
                'class PresentTests(unittest.TestCase):\n'
                '    def test_present(self):\n'
                '        pass\n',
                encoding='utf-8',
            )
            contract = {
                'schema': 2, 'task_id': 'demo', 'task_type': 'repair',
                'implement_plan': {'path': 'implement-plan.md'},
                'allowed_paths': ['tests/test_present.py'], 'forbidden_paths': [],
                'operations': [{'id': 'op', 'kind': 'validate', 'scope': 'task',
                                'acceptance_tests': ['acceptance-test-1']}],
                'chain': {name: ['src/app.py'] for name in (
                    'entry', 'interaction', 'application', 'domain',
                    'persistence', 'readback', 'recovery')},
                'dependencies': [],
                'acceptance_tests': [{
                    'id': 'acceptance-test-1', 'evidence_level': 2,
                    'test_ref': 'tests/test_present.py: PresentTests.test_absent',
                    'command_ref': 'python -m unittest',
                }],
                'required_evidence_levels': [2],
            }
            sheet = root / 'docs' / 'tasks' / 'demo.md'
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                '<!-- Task ID: demo -->\n```pipeline-contract\n'
                + json.dumps(contract) + '\n```\n',
                encoding='utf-8',
            )
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertTrue(
                any('acceptance-test-1' in error and 'absent' in error for error in errors),
                errors,
            )

            contract['acceptance_tests'][0]['test_ref'] = (
                'tests/test_present.py: PresentTests.test_present'
            )
            sheet.write_text(
                '<!-- Task ID: demo -->\n```pipeline-contract\n'
                + json.dumps(contract) + '\n```\n',
                encoding='utf-8',
            )
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertFalse(
                any('test_ref' in error and 'absent' in error for error in errors),
                errors,
            )


    def _status_report_directory(self, root, statuses):
        directory = root / '.pipeline' / 'demo'
        directory.mkdir(parents=True)
        (directory / 'test.log').write_text('observed test output', encoding='utf-8')
        roles = {
            'executor-report.md': 'executor',
            'review-report.md': 'reviewer',
            'final-check.md': 'main-final',
        }
        for name, role in roles.items():
            (directory / name).write_text(report(role, status=statuses[role]), encoding='utf-8')
        return directory

    def _result(self, directory, status, acceptance_status):
        value = {
            'schema': 1,
            'task_id': 'demo',
            'role': 'executor',
            'status': status,
            'acceptance': [
                {
                    'id': 'acceptance-test-1',
                    'status': acceptance_status,
                    'exit_code': 0,
                    'evidence_refs': ['test.log'],
                }
            ],
            'unverified': [],
        }
        path = directory / 'executor-result.json'
        path.write_text(json.dumps(value), encoding='utf-8')
        return path

    def test_gate_accepts_normalized_report_statuses(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._status_report_directory(root, {
                'executor': 'pass',
                'reviewer': 'ready-to-merge',
                'main-final': 'Pass',
            })
            self.assertEqual(evidence_verify(directory, 'demo', 'feature/demo'), [])
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertFalse(any('status is invalid' in error for error in errors), errors)
            self.assertFalse(any('not mergeable' in error for error in errors), errors)

    def test_schema_two_report_requires_head_and_generated_at(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._status_report_directory(root, {'executor': 'PASS', 'reviewer': 'PASS', 'main-final': 'PASS'})
            path = directory / 'executor-report.md'
            value, _ = __import__('pipeline_tools.core', fromlist=['_read_machine_evidence'])._read_machine_evidence(path)
            value['schema'] = 2
            value.pop('head', None)
            value.pop('generated_at', None)
            path.write_text('```pipeline-evidence\n' + json.dumps(value) + '\n```\n', encoding='utf-8')
            errors = evidence_verify(directory, 'demo', 'feature/demo')
            self.assertTrue(any('head must be' in error for error in errors))
            self.assertTrue(any('generated_at must be' in error for error in errors))

    def test_result_verify_accepts_normalized_result_statuses(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            (directory / 'test.log').write_text('observed test output', encoding='utf-8')
            path = self._result(directory, 'PASS', 'Pass')
            self.assertEqual(verify_structured_result(path, 'demo', 'executor'), [])

    def test_result_verify_accepts_legacy_pass_with_conditions(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            (directory / 'test.log').write_text('observed test output', encoding='utf-8')
            path = self._result(directory, 'pass_with_conditions', 'pass_with_conditions')
            self.assertEqual(verify_structured_result(path, 'demo', 'executor'), [])

    def test_gate_accepts_legacy_pass_with_conditions_in_report(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._status_report_directory(root, {
                'executor': 'PASS_WITH_CONDITIONS',
                'reviewer': 'PASS_WITH_CONDITIONS',
                'main-final': 'PASS_WITH_CONDITIONS',
            })
            self.assertEqual(evidence_verify(directory, 'demo', 'feature/demo'), [])
            errors = gate_check(directory, 'demo', 'feature/demo', 'pre-merge')
            self.assertFalse(any('not mergeable' in error for error in errors), errors)

    def test_unknown_report_status_stays_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = self._status_report_directory(root, {
                'executor': 'PASS',
                'reviewer': 'NOT_A_STATUS',
                'main-final': 'PASS',
            })
            errors = evidence_verify(directory, 'demo', 'feature/demo')
            self.assertTrue(any('review-report.md status is invalid' in error for error in errors), errors)

    def test_unknown_result_status_stays_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            (directory / 'test.log').write_text('observed test output', encoding='utf-8')
            path = self._result(directory, 'NOT_A_STATUS', 'pass')
            errors = verify_structured_result(path, 'demo', 'executor')
            self.assertIn('invalid status', errors)

    def test_result_acceptance_requires_identity_exit_code_and_existing_refs(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            path = directory / 'result.json'
            value = self._result(directory, 'pass', 'pass')
            data = json.loads(value.read_text(encoding='utf-8'))
            data['acceptance'][0].update({'id': '', 'exit_code': True, 'evidence_refs': ['../escape']})
            value.write_text(json.dumps(data), encoding='utf-8')
            errors = verify_structured_result(value, 'demo', 'executor', directory)
            self.assertTrue(any('id must be a non-empty string' in error for error in errors))
            self.assertTrue(any('exit_code must be an integer' in error for error in errors))
            self.assertTrue(any('evidence_ref is missing' in error for error in errors))

    def test_result_acceptance_rejects_empty_evidence_refs(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            path = self._result(directory, 'pass', 'pass')
            data = json.loads(path.read_text(encoding='utf-8'))
            data['acceptance'][0]['evidence_refs'] = []
            path.write_text(json.dumps(data), encoding='utf-8')
            errors = verify_structured_result(path, 'demo', 'executor', directory)
            self.assertTrue(any('evidence_refs must be a non-empty array' in error for error in errors))


    # --- Phase-aware evidence identity ---------------------------------------

    REPORT_FILES = ('executor-report.md', 'review-report.md', 'final-check.md')

    def _git(self, cwd, *args, check=True):
        import subprocess

        return subprocess.run(
            ['git', '-C', str(cwd), *args], check=check, capture_output=True, text=True,
        )

    def _task_contract_sheet(self, root, task_id='demo'):
        contract = {
            'schema': 1,
            'task_id': task_id,
            'allowed_paths': ['src/**', '.pipeline/**'],
            'forbidden_paths': [],
            'acceptance_tests': [{
                'id': 'acceptance-test-1',
                'evidence_level': 3,
                'test_ref': 'tests/test_evidence.py',
                'command_ref': 'python -m pytest -q tests/test_evidence.py',
            }],
        }
        sheet = root / 'docs' / 'tasks' / f'{task_id}.md'
        sheet.parent.mkdir(parents=True, exist_ok=True)
        sheet.write_text(
            f'<!-- Task ID: {task_id} -->\n```pipeline-contract\n' + json.dumps(contract) + '\n```\n',
            encoding='utf-8',
        )
        return sheet

    def _write_identity_reports(self, directory, worktree, branch, head, main_cwd, *, revision=1):
        """Write the three schema-2 stage reports under one recorded identity."""
        directory.mkdir(parents=True, exist_ok=True)
        for name, role in (
            ('executor-report.md', 'executor'),
            ('review-report.md', 'reviewer'),
            ('final-check.md', 'main-final'),
        ):
            value = {
                'schema': 2,
                'task_id': 'demo',
                'worktree': str(worktree),
                'branch': branch,
                'role': role,
                'round': 1,
                'status': 'PASS',
                'head': head,
                'sheet_revision': revision,
                'observed_at_commit': head,
                'generated_at': '2026-01-01T00:00:00+00:00',
                'commands': [{
                    'command': 'python -m pytest -q tests/test_evidence.py',
                    'exit_code': 0,
                    'cwd': str(main_cwd) if name == 'final-check.md' else str(worktree),
                    'evidence_ref': 'test.log',
                }],
                'assertions': ['the recorded identity is judged by the phase criteria'],
                'evidence_refs': ['test.log'],
                'unverified': [],
            }
            (directory / name).write_text(
                '```pipeline-evidence\n' + json.dumps(value) + '\n```\n', encoding='utf-8'
            )

    def _set_final_check_cwd(self, directory, cwd):
        path = directory / 'final-check.md'
        value = self._report_value(path)
        value['commands'][0]['cwd'] = str(cwd)
        path.write_text(
            '```pipeline-evidence\n' + json.dumps(value) + '\n```\n', encoding='utf-8'
        )

    def _report_value(self, path):
        from pipeline_tools.core import _read_machine_evidence

        value, errors = _read_machine_evidence(Path(path))
        self.assertEqual(errors, [], path)
        return value

    def _rewrite_report_identity(self, directory, **fields):
        for name in self.REPORT_FILES:
            path = directory / name
            value = self._report_value(path)
            value.update(fields)
            path.write_text(
                '```pipeline-evidence\n' + json.dumps(value) + '\n```\n', encoding='utf-8'
            )

    def _report_bytes(self, directory):
        return {name: (directory / name).read_bytes() for name in self.REPORT_FILES}

    def _task_branch_repo(self, root, task_id='demo', branch='demo-task'):
        """Main repo plus the canonical task worktree that wrote the reports.

        The three reports are committed on ``branch`` only, followed by a product
        change, so merging the branch into the main branch moves the current head
        past every commit the reports recorded and introduces product paths.
        """
        (root / 'src').mkdir(parents=True)
        (root / 'src' / 'app.py').write_text('stable\n', encoding='utf-8')
        (root / '.gitignore').write_text('/.worktrees/\n', encoding='utf-8')
        self._task_contract_sheet(root, task_id)
        directory = root / '.pipeline' / task_id
        directory.mkdir(parents=True)
        (directory / 'test.log').write_text('observed test output\n', encoding='utf-8')
        for name, role in (('executor-result.json', 'executor'), ('reviewer-result.json', 'reviewer')):
            (directory / name).write_text(json.dumps({
                'schema': 1, 'task_id': task_id, 'role': role, 'status': 'pass',
                'acceptance': [], 'unverified': [],
            }), encoding='utf-8')
        (directory / 'final-result.json').write_text(json.dumps({
            'schema': 1, 'task_id': task_id, 'role': 'final', 'status': 'pass', 'exit_code': 0,
            'acceptance': [{
                'id': 'acceptance-test-1', 'status': 'pass', 'exit_code': 0,
                'evidence_refs': ['test.log'],
            }],
            'unverified': [],
        }), encoding='utf-8')
        self._git(root, 'init', '-q', '-b', 'main')
        self._git(root, 'config', 'user.email', 'test@example.invalid')
        self._git(root, 'config', 'user.name', 'Test')
        self._git(root, 'add', '.')
        self._git(root, 'commit', '-qm', 'product baseline')
        reported_head = self._git(root, 'rev-parse', 'HEAD').stdout.strip()
        self._git(root, 'worktree', 'add', '-b', branch, f'.worktrees/{task_id}', reported_head)
        worktree = (root / '.worktrees' / task_id).resolve()
        self._write_identity_reports(
            worktree / '.pipeline' / task_id, worktree, branch, reported_head, root.resolve()
        )
        self._git(worktree, 'add', '.pipeline')
        self._git(worktree, 'commit', '-qm', 'task stage reports')
        (worktree / 'src' / 'app.py').write_text('task product change\n', encoding='utf-8')
        self._git(worktree, 'add', 'src/app.py')
        self._git(worktree, 'commit', '-qm', 'task product change')
        return directory, worktree, reported_head

    def test_post_merge_identity_uses_task_id_and_revision_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory, worktree, reported_head = self._task_branch_repo(root)
            self._git(root, 'merge', '--no-ff', '-m', 'merge demo-task', 'demo-task')
            current = self._git(root, 'branch', '--show-current').stdout.strip()
            self.assertEqual('main', current)
            recorded = self._report_value(directory / 'executor-report.md')
            # Every commit reference the reports recorded now disagrees with the
            # current checkout, and the merge introduced a product-path change, so
            # no commit-relative criterion could hold.
            self.assertEqual('demo-task', recorded['branch'])
            self.assertEqual(str(worktree), recorded['worktree'])
            self.assertEqual(reported_head, recorded['head'])
            self.assertEqual(reported_head, recorded['observed_at_commit'])
            self.assertEqual(1, recorded['sheet_revision'])
            self.assertNotEqual(recorded['branch'], current)
            self.assertIn(
                'src/app.py',
                self._git(root, 'diff', '--name-only', reported_head, 'HEAD').stdout.split(),
            )
            # The commit binding the active phase applies still rejects them.
            self.assertTrue(evidence_verify(directory, 'demo', 'main'))
            self.assertEqual([], evidence_verify(directory, 'demo', 'main', phase='finalized'))
            before = self._report_bytes(directory)
            errors = gate_check(directory, 'demo', 'main', 'post-merge')
            self.assertEqual(errors, [])
            for name, content in before.items():
                self.assertEqual((directory / name).read_bytes(), content, name)

    def test_post_merge_rejects_revision_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory, _worktree, _head = self._task_branch_repo(root)
            self._git(root, 'merge', '--no-ff', '-m', 'merge demo-task', 'demo-task')
            self._rewrite_report_identity(directory, sheet_revision=2)
            before = self._report_bytes(directory)
            errors = evidence_verify(directory, 'demo', 'main', phase='finalized')
            for name in self.REPORT_FILES:
                self.assertIn(
                    f'{name} was produced against task sheet revision 2 but the current revision is 1',
                    errors,
                )
            self.assertTrue(errors)
            self.assertTrue(gate_check(directory, 'demo', 'main', 'post-merge'))
            for name, content in before.items():
                self.assertEqual((directory / name).read_bytes(), content, name)
            # A report that declares no usable revision cannot be identified either.
            self._rewrite_report_identity(directory, sheet_revision=None)
            errors = evidence_verify(directory, 'demo', 'main', phase='finalized')
            for name in self.REPORT_FILES:
                self.assertIn(f'{name} sheet_revision must be a positive integer', errors)
            self.assertTrue(gate_check(directory, 'demo', 'main', 'post-merge'))

    def test_post_merge_rejects_task_id_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory, _worktree, _head = self._task_branch_repo(root)
            self._git(root, 'merge', '--no-ff', '-m', 'merge demo-task', 'demo-task')
            # (a) a report that names another task.
            self._rewrite_report_identity(directory, task_id='other-task')
            errors = evidence_verify(directory, 'demo', 'main', phase='finalized')
            for name in self.REPORT_FILES:
                self.assertIn(f'{name} task identity mismatch', errors)
            self.assertTrue(gate_check(directory, 'demo', 'main', 'post-merge'))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # (b) the evidence directory itself must name the verified task, even
            # when every report inside it agrees on another task id.
            directory, _worktree, _head = self._task_branch_repo(root)
            self._git(root, 'merge', '--no-ff', '-m', 'merge demo-task', 'demo-task')
            self._rewrite_report_identity(directory, task_id='other-task')
            errors = evidence_verify(directory, 'other-task', 'main', phase='finalized')
            self.assertEqual(['evidence directory does not match the verified task id'], errors)

    def test_post_merge_requires_main_worktree_reverification(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory, worktree, _head = self._task_branch_repo(root)
            self._git(root, 'merge', '--no-ff', '-m', 'merge demo-task', 'demo-task')
            self._set_final_check_cwd(directory, worktree)
            # Identity is accepted, so the verdict can only come from the
            # re-verification requirement itself.
            self.assertEqual([], evidence_verify(directory, 'demo', 'main', phase='finalized'))
            errors = gate_check(directory, 'demo', 'main', 'post-merge')
            self.assertIn('post-merge re-verification in the main worktree is missing', errors)
            self.assertTrue(errors)
            self._set_final_check_cwd(directory, root)
            self.assertEqual([], gate_check(directory, 'demo', 'main', 'post-merge'))

    def test_pre_merge_commit_identity_is_not_weakened(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory, worktree, reported_head = self._task_branch_repo(root)
            # The task branch is not merged, and the judged directory holds the same
            # reports: task branch, canonical task worktree, implementation commit.
            self._write_identity_reports(directory, worktree, 'demo-task', reported_head, root.resolve())
            self.assertNotEqual(
                0, self._git(root, 'merge-base', '--is-ancestor', 'demo-task', 'HEAD', check=False).returncode
            )
            head_errors = [f'{name} head does not match current Git identity' for name in self.REPORT_FILES]
            branch_errors = [f'{name} branch does not match current Git identity' for name in self.REPORT_FILES]
            worktree_errors = [f'{name} worktree does not match current Git identity' for name in self.REPORT_FILES]
            mismatch_errors = [f'{name} branch mismatch' for name in self.REPORT_FILES]

            # (a) unmerged branch plus its own worktree: the recorded head is still
            # the current head, so exactly the branch/worktree criteria fail.
            errors = evidence_verify(directory, 'demo', 'main')
            self.assertEqual(sorted(branch_errors + worktree_errors + mismatch_errors), sorted(errors))

            # (b) a head that is not an ancestor of HEAD keeps the strict rule.
            self._rewrite_report_identity(directory, head='1' * 40)
            errors = evidence_verify(directory, 'demo', 'main')
            self.assertEqual(
                sorted(head_errors + branch_errors + worktree_errors + mismatch_errors), sorted(errors)
            )

            # (c) a worktree outside the canonical task worktree keeps it too.
            self._rewrite_report_identity(directory, worktree=str(root / 'old-worktree'))
            errors = evidence_verify(directory, 'demo', 'main')
            self.assertEqual(
                sorted(head_errors + branch_errors + worktree_errors + mismatch_errors), sorted(errors)
            )

            # The pre-merge gate consumes the same verdicts.
            gate_errors = gate_check(directory, 'demo', 'main', 'pre-merge')
            for error in dict.fromkeys(head_errors + branch_errors + worktree_errors + mismatch_errors):
                self.assertIn(error, gate_errors)

            # The post-merge phase deliberately drops that binding: identity there is
            # the task id plus the task sheet revision.
            self.assertEqual([], evidence_verify(directory, 'demo', 'main', phase='finalized'))

    def test_cli_evidence_verify_forwards_the_phase(self):
        import os
        import subprocess
        import sys

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory, _worktree, reported_head = self._task_branch_repo(root)
            self._git(root, 'merge', '--no-ff', '-m', 'merge demo-task', 'demo-task')
            self.assertIn(
                'src/app.py',
                self._git(root, 'diff', '--name-only', reported_head, 'HEAD').stdout.split(),
            )
            repo = Path(__file__).resolve().parent.parent
            env = {**os.environ, 'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '1', 'PYTHONPATH': str(repo)}
            command = [sys.executable, '-m', 'pipeline_tools', 'evidence', 'verify', str(directory),
                       '--task-id', 'demo', '--branch', 'main', '--phase']
            active = subprocess.run([*command, 'active'], cwd=root, env=env, capture_output=True, text=True, timeout=60)
            finalized = subprocess.run([*command, 'finalized'], cwd=root, env=env, capture_output=True, text=True, timeout=60)
            # The same evidence, the two phases: only the active one applies the
            # commit binding; the finalized one keeps the marker check.
            self.assertIn('head does not match current Git identity', active.stdout + active.stderr)
            self.assertIn('worktree does not match current Git identity', active.stdout + active.stderr)
            self.assertEqual('FAIL: finalization.json is missing', finalized.stdout.strip())
            self.assertEqual('', finalized.stderr.strip())

    def test_legacy_evidence_gains_no_new_finalized_errors(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._make_git_repo(root)
            self._task_contract_sheet(root)
            directory = self._canonical_evidence_dir(root)
            (directory / 'test.log').write_text('observed test output\n', encoding='utf-8')

            def write_historical(**fields):
                for name, role in (
                    ('executor-report.md', 'executor'),
                    ('review-report.md', 'reviewer'),
                    ('final-check.md', 'main-final'),
                ):
                    value = {
                        'schema': 2, 'task_id': 'demo', 'worktree': str(root), 'branch': 'main',
                        'head': 'a' * 40, 'generated_at': '2026-01-01T00:00:00+00:00',
                        'role': role, 'round': 1, 'status': 'PASS',
                        'commands': [{'command': 'python -m pytest -q tests/test_evidence.py',
                                      'exit_code': 0, 'evidence_ref': 'test.log'}],
                        'assertions': ['the observed result matches the contract'],
                        'evidence_refs': ['test.log'], 'unverified': [],
                    }
                    value.update(fields)
                    (directory / name).write_text(
                        '```pipeline-evidence\n' + json.dumps(value) + '\n```\n', encoding='utf-8')

            # Historical shape: neither the revision nor the observation commit is
            # recorded, so the finalized criteria do not apply and nothing is added.
            write_historical()
            self.assertEqual([], evidence_verify(directory, 'demo', 'main', phase='finalized'))
            status = evidence_revision_status(
                root, 'demo', {},
                {name: self._report_value(directory / name) for name in self.REPORT_FILES},
            )
            self.assertEqual([], status['errors'])
            for name in self.REPORT_FILES:
                self.assertTrue(
                    any(f'{name} does not record the task sheet revision' in item
                        for item in status['unverified']),
                    (name, status['unverified']),
                )

            # Evidence that does carry the fields is still judged by them.
            write_historical(sheet_revision=2)
            errors = evidence_verify(directory, 'demo', 'main', phase='finalized')
            for name in self.REPORT_FILES:
                self.assertIn(
                    f'{name} was produced against task sheet revision 2 but the current revision is 1', errors)

            write_historical(sheet_revision=1, observed_at_commit='')
            errors = evidence_verify(directory, 'demo', 'main', phase='finalized')
            for name in self.REPORT_FILES:
                self.assertIn(f'{name} observed_at_commit must be a non-empty string', errors)

            # A declared-but-unusable revision stays an error rather than a silent pass.
            write_historical(sheet_revision=None)
            errors = evidence_verify(directory, 'demo', 'main', phase='finalized')
            for name in self.REPORT_FILES:
                self.assertIn(f'{name} sheet_revision must be a positive integer', errors)

    # --- A closed task still fails after product-path commits ----------------

    def test_finalized_verification_still_fails_after_product_commits(self):
        from pipeline_tools.core import verify_finalization_snapshot
        from pipeline_tools.planning import finalize_evidence

        def closed_repo(root):
            """Merge the task, finalize its evidence and publish the marker."""
            directory, _worktree, _head = self._task_branch_repo(root)
            self._git(root, 'merge', '--no-ff', '-m', 'merge demo-task', 'demo-task')
            # Point every reference at a retained name so finalization's dangling
            # reference check has nothing to object to, then approve the finalize.
            for name in self.REPORT_FILES:
                path = directory / name
                path.write_text(
                    path.read_text(encoding='utf-8').replace('test.log', 'executor-report.md'),
                    encoding='utf-8',
                )
            final = directory / 'final-result.json'
            value = json.loads(
                final.read_text(encoding='utf-8').replace('test.log', 'executor-report.md')
            )
            value['decision'] = 'READY_FOR_EVIDENCE_FINALIZATION'
            final.write_text(json.dumps(value), encoding='utf-8')
            result = finalize_evidence(directory, 'demo', True, require_canonical=True)
            self.assertEqual('finalized', result['status'], result)
            self._git(root, 'add', '.pipeline/demo/finalization.json')
            self._git(root, 'commit', '-qm', 'finalization marker')
            published = self._git(root, 'rev-parse', 'HEAD').stdout.strip()
            marker = json.loads((directory / 'finalization.json').read_text(encoding='utf-8'))
            self.assertEqual([], verify_finalization_snapshot(directory, marker))
            return directory, marker, published

        # (a) a product-only commit after the recorded head still invalidates it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory, marker, _published = closed_repo(root)
            (root / 'src' / 'app.py').write_text('later product change\n', encoding='utf-8')
            self._git(root, 'add', 'src/app.py')
            self._git(root, 'commit', '-qm', 'later product change')
            self.assertIn('finalization head is stale', verify_finalization_snapshot(directory, marker))

        # (b) a mixed commit that touches an evidence path and a product path must
        # stay fail-closed: the range is not evidence-only.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory, marker, published = closed_repo(root)
            (directory / 'scratch.md').write_text('scratch\n', encoding='utf-8')
            (root / 'src' / 'app.py').write_text('mixed change\n', encoding='utf-8')
            self._git(root, 'add', '.pipeline/demo/scratch.md', 'src/app.py')
            self._git(root, 'commit', '-qm', 'mixed evidence and product')
            moved = self._git(root, 'diff', '--name-only', published, 'HEAD').stdout.split()
            self.assertEqual(sorted(['.pipeline/demo/scratch.md', 'src/app.py']), sorted(moved))
            self.assertIn('finalization head is stale', verify_finalization_snapshot(directory, marker))

    # --- Retention rule: a task's own sheet, and the archive quarantine ------

    def test_task_sheet_and_archive_are_exempt_from_the_retained_name_rule(self):
        """A task's own sheet is retained; the archive subtree is exempt.

        The forward baseline gate judges additions and deletions against the
        retained set.  A task's sheet belongs beside its evidence
        (``.pipeline/<task-id>/<task-id>.md``) so publishing it is not drift, and
        the flat ``.pipeline/archive/`` quarantine is not an evidence directory at
        all.  The other direction stays fail-closed: a *different* non-retained
        file in the same evidence directory is still a violation.
        """
        from pipeline_tools.core import commit_history_check, is_retained_evidence_path

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            evidence_root = self._make_git_repo(root)
            evidence = root / '.pipeline' / 'demo'
            evidence.mkdir(parents=True)
            (evidence / 'demo.md').write_text('own task sheet\n', encoding='utf-8')
            archive = root / '.pipeline' / 'archive'
            archive.mkdir(parents=True)
            (archive / 'closed-task.md').write_text('archived sheet\n', encoding='utf-8')
            self._git(root, 'add', '.pipeline')
            self._git(root, 'commit', '-qm', 'own sheet and archived sheet')

            self.assertTrue(is_retained_evidence_path('.pipeline/demo/demo.md'))
            self.assertFalse(is_retained_evidence_path('.pipeline/demo/notes.md'))
            self.assertEqual([], commit_history_check(root, '.pipeline/demo', since=evidence_root))

            # The reverse direction: another non-retained file in the same task
            # evidence directory is still drift.
            (evidence / 'notes.md').write_text('scratch\n', encoding='utf-8')
            self._git(root, 'add', '.pipeline/demo/notes.md')
            self._git(root, 'commit', '-qm', 'stray evidence file')
            violations = commit_history_check(root, '.pipeline/demo', since=evidence_root)
            self.assertEqual(len(violations), 1, violations)
            self.assertIn('notes.md', violations[0])

    def test_pipeline_evidence_bytes_survive_a_checkout(self):
        """``.pipeline/** -text`` keeps evidence bytes byte-identical on checkout.

        Evidence must survive a checkout unchanged: the attribute makes a
        checked-out report or machine result the same byte sequence that was
        committed.  Declaring it must also not rewrite an already committed byte,
        which is proved by comparing that blob's hash before and after the
        attribute is added.  Ordinary text is the control: the repository-wide
        `* text=auto eol=lf` rule still normalizes it, so the evidence path is
        demonstrably the thing the new attribute protects.
        """
        import subprocess

        payload = b'first line\r\nsecond line\r\n'
        # The rule under test is the one this repository declares: the test reads
        # the deliverable instead of restating it, so removing the attribute from
        # `.gitattributes` fails here too.
        declared = (Path(__file__).resolve().parents[1] / '.gitattributes').read_text(encoding='utf-8')
        self.assertIn('.pipeline/** -text', declared)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'origin'
            root.mkdir()
            self._git(root, 'init', '-q', '-b', 'main')
            self._git(root, 'config', 'user.email', 'test@example.invalid')
            self._git(root, 'config', 'user.name', 'Test')
            self._git(root, 'config', 'core.autocrlf', 'false')
            # The pre-attribute repository: only the repository-wide text rule.
            (root / '.gitattributes').write_text('* text=auto eol=lf\n', encoding='utf-8')
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_bytes(payload)
            evidence = root / '.pipeline' / 'demo' / 'final-check.md'
            evidence.parent.mkdir(parents=True)
            evidence.write_bytes(payload)
            self._git(root, 'add', '.')
            self._git(root, 'commit', '-qm', 'evidence committed before the attribute')
            before = self._git(root, 'rev-parse', 'HEAD:.pipeline/demo/final-check.md').stdout.strip()

            (root / '.gitattributes').write_text(declared, encoding='utf-8')
            self._git(root, 'add', '.gitattributes')
            self._git(root, 'commit', '-qm', 'declare evidence non-text')
            after = self._git(root, 'rev-parse', 'HEAD:.pipeline/demo/final-check.md').stdout.strip()
            # Adding the attribute rewrote no already committed byte.
            self.assertEqual(before, after)

            # New evidence is now committed byte for byte, while ordinary text
            # under the same repository-wide rule is still normalized.
            fresh = root / '.pipeline' / 'demo' / 'review-report.md'
            fresh.write_bytes(payload)
            (root / 'src' / 'control.txt').write_bytes(payload)
            self._git(root, 'add', '.')
            self._git(root, 'commit', '-qm', 'evidence committed after the attribute')

            def blob(path):
                return subprocess.run(
                    ['git', '-C', str(root), 'cat-file', 'blob', f'HEAD:{path}'],
                    check=True, capture_output=True,
                ).stdout

            self.assertEqual(payload, blob(fresh.relative_to(root).as_posix()))
            self.assertNotEqual(payload, blob('src/control.txt'))

            clone = Path(d) / 'clone'
            subprocess.run(
                ['git', 'clone', '-q', str(root), str(clone)],
                check=True, capture_output=True, text=True,
            )
            self.assertEqual(payload, (clone / '.pipeline' / 'demo' / 'review-report.md').read_bytes())

    def test_closed_task_markers_still_verify_after_the_migration(self):
        """Moving a closed sheet into its evidence directory keeps the marker valid.

        A finalization marker snapshots the retained evidence vocabulary, not the
        task sheet, so migrating the sheet with ``git mv`` must not produce a
        ``finalization retained evidence hash mismatch``.  A stale head is the
        only drift a later commit may introduce, and it is recorded rather than
        fatal.
        """
        from pipeline_tools.core import (
            git_identity,
            retained_evidence_snapshot,
            verify_finalization_snapshot,
        )

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._make_git_repo(root)
            task_ids = ('closed-1', 'closed-2', 'closed-3')
            (root / 'docs' / 'tasks').mkdir(parents=True)
            directories = {}
            for task_id in task_ids:
                (root / 'docs' / 'tasks' / f'{task_id}.md').write_text(
                    f'<!-- Task ID: {task_id} -->\n', encoding='utf-8')
                directory = root / '.pipeline' / task_id
                directory.mkdir(parents=True)
                for name in ('executor-report.md', 'review-report.md', 'final-check.md'):
                    (directory / name).write_text('report\n', encoding='utf-8')
                for name in ('executor-result.json', 'reviewer-result.json', 'final-result.json'):
                    (directory / name).write_text('{}\n', encoding='utf-8')
                directories[task_id] = directory
            self._git(root, 'add', '.')
            self._git(root, 'commit', '-qm', 'closed tasks frozen')
            identity = git_identity(root)
            for task_id, directory in directories.items():
                (directory / 'finalization.json').write_text(json.dumps({
                    'schema': 1, 'task_id': task_id,
                    'retained_sha256': retained_evidence_snapshot(directory),
                    'identity': identity,
                }), encoding='utf-8')
            self._git(root, 'add', '.pipeline')
            self._git(root, 'commit', '-qm', 'finalization markers')

            for task_id in task_ids:
                self._git(root, 'mv', f'docs/tasks/{task_id}.md',
                          f'.pipeline/{task_id}/{task_id}.md')
            self._git(root, 'commit', '-qm', 'migrate closed task sheets')

            self.assertEqual(3, len(directories))
            for task_id, directory in directories.items():
                marker = json.loads((directory / 'finalization.json').read_text(encoding='utf-8'))
                errors = verify_finalization_snapshot(directory, marker, root)
                self.assertNotIn(
                    'finalization retained evidence hash mismatch', errors, (task_id, errors))
                self.assertTrue((directory / f'{task_id}.md').is_file(), task_id)


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

