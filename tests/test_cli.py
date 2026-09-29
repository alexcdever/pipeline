import atexit
import contextlib
import hashlib
import io
import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

from pipeline_tools.__main__ import main

from pipeline_tools.layout import metrics_dirs

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

_ISOLATED_METRICS_ROOT: Path | None = None


def auto_metrics_requested(env):
    """Whether an environment mapping leaves automatic metrics collection on."""
    value = env.get('PIPELINE_TOOLS_DISABLE_AUTO_METRICS', '')
    return value.strip().lower() not in {'1', 'true', 'yes', 'on'}


def isolated_metrics_root():
    """A throwaway non-repository cwd for runs that enable automatic metrics.

    Automatic collection resolves its project root from the invocation cwd. The
    suite must never point that at this checkout, or the repository
    ``.pipeline/metrics/`` directory gains an event on every run, tracked or not.
    """
    global _ISOLATED_METRICS_ROOT
    if _ISOLATED_METRICS_ROOT is None or not _ISOLATED_METRICS_ROOT.is_dir():
        _ISOLATED_METRICS_ROOT = Path(tempfile.mkdtemp(prefix='pipeline-metrics-isolation-'))
        atexit.register(shutil.rmtree, _ISOLATED_METRICS_ROOT, ignore_errors=True)
    return _ISOLATED_METRICS_ROOT


def metrics_snapshot(directory):
    """Name -> content hash for the JSON events in a metrics directory."""
    directory = Path(directory)
    if not directory.is_dir():
        return {}
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in directory.glob('*.json')}


def run_cli(args, cwd=None, env=None):
    e = dict(os.environ)
    # These tests cover the legacy command surface. Automatic collection has
    # explicit tests and is disabled here to avoid mutating this checkout.
    e.setdefault('PIPELINE_TOOLS_DISABLE_AUTO_METRICS', '1')
    # The CLI must import from this checkout even when an isolated cwd is used.
    e['PYTHONPATH'] = str(ROOT) if not e.get('PYTHONPATH') else str(ROOT) + os.pathsep + e['PYTHONPATH']
    if env: e.update(env)
    if cwd is None:
        # A run that genuinely enables automatic metrics must not resolve its
        # project root to this repository, even when the caller relies on the
        # default cwd.
        cwd = isolated_metrics_root() if auto_metrics_requested(e) else ROOT
    return subprocess.run([PY, '-m', 'pipeline_tools', *args], capture_output=True, text=True, cwd=str(cwd), env=e, timeout=60)

def make_repo(tmp):
    """Temporary git repo with one commit; returns (path, head_sha)."""
    p = Path(tmp)
    def g(*args):
        r = subprocess.run(['git', '-C', str(p), *args], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return r.stdout
    subprocess.run(['git', 'init', '-q'], cwd=p, capture_output=True)
    g('config', 'user.email', 'test@example.invalid')
    g('config', 'user.name', 'Test')
    (p / 'ok.txt').write_text('x', encoding='utf-8')
    g('add', '.'); g('commit', '-q', '-m', 'base')
    return p, g('rev-parse', 'HEAD').strip()


class CLITests(unittest.TestCase):
    def _write_machine_report(self, directory, role, task_id='demo', branch='feature/demo'):
        value = {
            'schema': 1, 'task_id': task_id, 'worktree': str(directory), 'branch': branch,
            'role': role, 'round': 1, 'status': 'PASS',
            'commands': [{'command': 'python -m unittest', 'exit_code': 0, 'evidence_ref': 'test.log'}],
            'assertions': ['machine assertion'], 'evidence_refs': ['test.log'], 'unverified': [],
        }
        name = {'executor': 'executor-report.md', 'reviewer': 'review-report.md', 'main-final': 'final-check.md'}[role]
        (directory / name).write_text('```pipeline-evidence\n' + json.dumps(value) + '\n```\n', encoding='utf-8')

    def test_evidence_finalize_current_command_preserves_raw_on_block_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); evidence = root / '.pipeline' / 'demo'; evidence.mkdir(parents=True)
            raw = evidence / 'raw.log'; raw.write_text('raw', encoding='utf-8')
            blocked = run_cli(['planning', 'evidence-finalize', str(evidence), '--task-id', 'demo', '--success'])
            self.assertEqual(blocked.returncode, 3, (blocked.stdout, blocked.stderr))
            self.assertTrue(raw.is_file()); self.assertFalse((evidence / 'finalization.json').exists())
            (evidence / 'finalization.json').write_text(json.dumps({'schema': 1, 'task_id': 'demo', 'status': 'finalized'}), encoding='utf-8')
            repeat = run_cli(['planning', 'evidence-finalize', str(evidence), '--task-id', 'demo', '--success'])
            self.assertEqual(repeat.returncode, 0, (repeat.stdout, repeat.stderr))
            self.assertEqual(json.loads(repeat.stdout)['status'], 'finalized')

    def test_evidence_verify_current_command_reports_machine_identity_and_finalization_state(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); evidence = root / '.pipeline' / 'demo'; evidence.mkdir(parents=True)
            (evidence / 'test.log').write_text('ok', encoding='utf-8')
            for role in ('executor', 'reviewer', 'main-final'):
                self._write_machine_report(evidence, role)
            (evidence / 'finalization.json').write_text(json.dumps({'schema': 1, 'task_id': 'demo', 'status': 'finalized'}), encoding='utf-8')
            verified = run_cli(['evidence', 'verify', str(evidence), '--task-id', 'demo', '--branch', 'feature/demo', '--phase', 'finalized'])
            self.assertEqual(verified.returncode, 0, (verified.stdout, verified.stderr))

    def test_result_verify_cli_accepts_final_role(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / 'final-result.json'
            path.write_text(json.dumps({
                'schema': 1,
                'task_id': 'demo',
                'role': 'main-final',
                'status': 'pass',
                'acceptance': [{'id': 'acceptance-test-1', 'status': 'pass', 'exit_code': 0, 'evidence_refs': ['test.log']}],
                'unverified': [],
            }), encoding='utf-8')
            verified = run_cli(['result', 'verify', str(path), '--task-id', 'demo', '--role', 'final'])
            self.assertEqual(verified.returncode, 0, (verified.stdout, verified.stderr))

    def test_result_verify_cli_accepts_reviewer_role(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / 'reviewer-result.json'
            path.write_text(json.dumps({
                'schema': 1,
                'task_id': 'demo',
                'role': 'reviewer',
                'status': 'pass_with_conditions',
                'acceptance': [{'id': 'acceptance-test-1', 'status': 'pass', 'exit_code': 0, 'evidence_refs': ['test.log']}],
                'unverified': [],
            }), encoding='utf-8')
            verified = run_cli(['result', 'verify', str(path), '--task-id', 'demo', '--role', 'reviewer'])
            self.assertEqual(verified.returncode, 0, (verified.stdout, verified.stderr))

    def test_help(self):
        p = run_cli(['--help'])
        self.assertEqual(p.returncode, 0)
        for word in ('task', 'scope', 'command', 'evidence', 'gate', 'metrics', 'lifecycle', 'planning'):
            self.assertIn(word, p.stdout)

    def test_planning_cli_commands_return_meaningful_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            valid = root / 'facts.json'
            valid.write_text(json.dumps({
                'schema': 1,
                'sources': [{'id': 'source', 'path': 'implement-plan.md'}],
                'resources': [{'id': 'resource', 'path': 'src/app.py'}],
                'operations': [{'id': 'op', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
                'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 1, 'test_ref': 'tests/test_x.py', 'command_ref': 'python -m unittest'}],
                'chain': {'entry': ['cli.py'], 'interaction': ['cli.py'], 'application': ['app.py'], 'domain': ['domain.py'], 'persistence': ['db.py'], 'readback': ['app.py'], 'recovery': ['app.py']},
            }), encoding='utf-8')
            p = run_cli(['planning', 'facts-validate', str(valid), '--root', str(root)])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            self.assertEqual(json.loads(p.stdout)['status'], 'pass')
            p = run_cli(['planning', 'facts-validate', str(root / 'missing.json'), '--root', str(root)])
            self.assertEqual(p.returncode, 2, (p.stdout, p.stderr))
            p = run_cli(['planning', 'progress-append', str(root), '--task-id', 'demo', '--role', 'bad', '{}'])
            self.assertEqual(p.returncode, 2, (p.stdout, p.stderr))
            p = run_cli(['planning', 'preflight', str(root)])
            self.assertEqual(p.returncode, 3, (p.stdout, p.stderr))

    def test_planning_generate_task_sheets_cli_lifecycle(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
            (root / 'implement-plan.md').write_text('stable implement plan\n', encoding='utf-8')
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_text('app\n', encoding='utf-8')
            chain = {name: ['src/app.py'] for name in ('entry', 'interaction', 'application', 'domain', 'persistence', 'readback', 'recovery')}
            acceptance = [{'id': 'acceptance-test-1', 'evidence_level': 2, 'test_ref': 'tests/test_cli.py: test_planning_generate_task_sheets_cli_lifecycle', 'command_ref': 'python -m unittest tests.test_cli -v'}]
            project = {'schema': 1, 'sources': [{'id': 'source', 'path': 'implement-plan.md'}], 'resources': [{'id': 'resource', 'path': 'src/app.py'}, {'id': 'test-resource', 'path': 'tests/test_cli.py'}], 'operations': [{'id': 'operate', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}], 'acceptance_tests': acceptance, 'chain': chain}
            requirements = {'schema': 1, 'sources': [{'id': 'source', 'path': 'implement-plan.md'}], 'requirements': [{'id': 'requirement', 'source_refs': ['source']}], 'operations': [{'id': 'operate', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}], 'acceptance_tests': acceptance}
            plan = {'schema': 1, 'non_goals': ['本任务不扩展用户可见范围'], 'requirements': ['requirement'], 'resources': ['resource', 'test-resource'], 'operations': [{'id': 'operate', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}], 'acceptance_tests': acceptance, 'tasks': [{'id': 'cli-task', 'type': 'prerequisite', 'requirements': ['requirement'], 'resources': ['resource', 'test-resource'], 'operations': ['operate'], 'depends_on': [], 'non_user_completion_reason': 'produces the enabling artifact consumed by later user-facing work'}]}
            paths = []
            for name, value in [('project.json', project), ('requirements.json', requirements), ('plan.json', plan)]:
                path = root / name
                path.write_text(json.dumps(value), encoding='utf-8')
                paths.append(path)
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'base'], cwd=root, check=True)
            command = ['planning', 'generate-task-sheets', str(root), '--run-id', 'cli-run', '--project-facts', str(paths[0]), '--requirement-facts', str(paths[1]), '--task-plan', str(paths[2])]
            success = run_cli(command)
            self.assertEqual(success.returncode, 0, (success.stdout, success.stderr))
            value = json.loads(success.stdout)
            self.assertEqual(value['status'], 'pass')
            self.assertEqual(value['task_id'], None)
            self.assertEqual(value['run_id'], 'cli-run')
            self.assertTrue((root / 'docs' / 'tasks' / 'cli-task.md').is_file())
            repeat = run_cli(command)
            self.assertEqual(repeat.returncode, 3, (repeat.stdout, repeat.stderr))
            repeated = json.loads(repeat.stdout)
            self.assertEqual(repeated['status'], 'blocked')
            self.assertTrue(any('already exists' in error for error in repeated['errors']))
            (root / 'requirements.json').write_text(json.dumps({**requirements, 'sources': []}), encoding='utf-8')
            failed = run_cli(command[:-1] + [str(root / 'requirements.json')])
            self.assertEqual(failed.returncode, 3, (failed.stdout, failed.stderr))
            failure = json.loads(failed.stdout)
            self.assertEqual(failure['status'], 'blocked')
            self.assertFalse((root / '.pipeline' / 'planning').exists())

    def test_planning_cli_task_plan_validate_accepts_root_and_rejects_bad_plan(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan = root / 'plan.json'
            plan.write_text(json.dumps({'schema': 1, 'requirements': [], 'resources': [], 'operations': [], 'tasks': []}), encoding='utf-8')
            p = run_cli(['planning', 'task-plan-validate', str(plan), '--root', str(root)])
            self.assertEqual(p.returncode, 2, (p.stdout, p.stderr))
            self.assertEqual(json.loads(p.stdout)['status'], 'fail')

    def _write_derived_parent_sheet(self, root):
        sheet = root / 'docs' / 'tasks' / 'parent-run.md'
        sheet.parent.mkdir(parents=True, exist_ok=True)
        contract = {
            'schema': 4, 'task_id': 'parent-run', 'task_type': 'prerequisite',
            'goal': {'path': 'goal.md', 'sha256': '0' * 64, 'planning_run_id': 'parent-run'},
            'risk': 'medium', 'project_type': 'service',
            'non_goals': ['parent sheet fixture'],
            'allowed_paths': ['src/app.py'], 'forbidden_paths': ['goal.md'],
            'requirements': ['r1'], 'resources': ['src/app.py'],
            'operations': [{'id': 'create', 'kind': 'execute', 'scope': 'task', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'chain': {name: {'not_applicable': True, 'reason': 'fixture'} for name in ('entry', 'interaction', 'application', 'domain', 'persistence', 'readback', 'recovery')},
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2, 'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
            'dependencies': [], 'required_evidence_levels': [2],
            'non_user_completion_reason': 'parent fixture groundwork',
        }
        sheet.write_text(
            '# parent-run\n\n<!-- Task ID: parent-run -->\n\n```pipeline-contract\n'
            + json.dumps(contract, indent=2) + '\n```\n',
            encoding='utf-8',
        )
        return sheet

    def _derived_plan_for_cli(self):
        return {
            'schema': 1, 'non_goals': ['本任务不扩展范围'],
            'requirements': ['r1'],
            'resources': ['src/app.py', 'tests/test_planning.py'],
            'operations': [{'id': 'create', 'resources': ['src/app.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}],
            'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2, 'test_ref': 'tests/test_planning.py', 'command_ref': 'python -m unittest'}],
            'tasks': [{
                'id': 'derived-task', 'type': 'derived', 'requirements': ['r1'],
                'resources': ['src/app.py', 'tests/test_planning.py'], 'operations': ['create'],
                'depends_on': [], 'parent_task_id': 'parent-run',
                'derived_from': {'task_id': 'parent-run', 'commit': 'a' * 40, 'branch': 'parent-branch'},
            }],
        }

    def test_task_plan_validate_cli_forwards_root_for_derived_parent(self):
        from pipeline_tools.planning import validate_task_plan

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_text('app\n', encoding='utf-8')
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'base'], cwd=root, check=True)
            self._write_derived_parent_sheet(root)
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'parent sheet'], cwd=root, check=True)

            plan = self._derived_plan_for_cli()
            plan_path = root / 'plan.json'
            plan_path.write_text(json.dumps(plan), encoding='utf-8')

            # The cross-run parent lives at HEAD, so the Python API accepts the plan
            # only when it is handed the root that proves the parent exists.
            self.assertEqual(validate_task_plan(plan, root=root), [])

            with_root = run_cli(['planning', 'task-plan-validate', str(plan_path), '--root', str(root)])
            self.assertEqual(with_root.returncode, 0, (with_root.stdout, with_root.stderr))
            self.assertEqual(json.loads(with_root.stdout), {'status': 'pass', 'errors': []})

            # Without --root the CLI cannot prove the cross-run parent and fails
            # closed, matching the Python API called without a root.
            without_root = run_cli(['planning', 'task-plan-validate', str(plan_path)])
            self.assertEqual(without_root.returncode, 2, (without_root.stdout, without_root.stderr))
            self.assertEqual(json.loads(without_root.stdout)['status'], 'fail')
            self.assertTrue(any('parent-run' in error for error in json.loads(without_root.stdout)['errors']))


    def test_json_output_has_common_envelope_and_can_be_saved(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / 'result.json'
            p = run_cli(['--format', 'json', '--output', str(output), 'task', 'validate', str(ROOT / 'docs' / 'tasks' / 'pipeline-tools-v1.md')])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            value = json.loads(p.stdout)
            self.assertEqual(value['schema'], 1)
            self.assertEqual(value['status'], 'pass')
            self.assertEqual(json.loads(output.read_text(encoding='utf-8')), value)

    def test_command_run_with_dashdash_separator(self):
        # README documents: command run --cwd . --log L --timeout 30 -- python -c "print('hi')"
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / 'ok.log'
            p = run_cli(['command', 'run', '--cwd', str(ROOT), '--log', str(log), '--timeout', '30',
                         '--', PY, '-c', "print('hi')"])
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn('hi', log.read_text(encoding='utf-8'))
            self.assertIn('"exit_code": 0', p.stdout.replace("'", '"'))

    def test_command_run_nonzero_exit_is_fail_1(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / 'fail.log'
            p = run_cli(['command', 'run', '--cwd', str(ROOT), '--log', str(log), '--timeout', '30',
                         '--', PY, '-c', 'raise SystemExit(7)'])
            self.assertEqual(p.returncode, 1, (p.stdout, p.stderr))
            self.assertIn('"exit_code": 7', p.stdout.replace("'", '"'))

    def test_command_run_missing_executable_is_config_2(self):
        with tempfile.TemporaryDirectory() as d:
            p = run_cli(['command', 'run', '--cwd', str(ROOT), '--log', str(Path(d) / 'x.log'),
                         '--timeout', '5', '--', 'definitely-not-a-real-exe-xyz', 'arg'])
            self.assertEqual(p.returncode, 2, (p.stdout, p.stderr))
            self.assertNotIn('Traceback', p.stderr)

    def test_command_run_default_timeout_is_180_seconds(self):
        from pipeline_tools.__main__ import _build_parser
        args = _build_parser().parse_args(["command", "run", "--cwd", ".", "--log", "x.log", "--", PY, "-c", "print('ok')"])
        self.assertEqual(args.timeout, 180)

    def test_command_run_timeout_is_3_with_timed_out_flag(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / 'slow.log'
            p = run_cli(['command', 'run', '--cwd', str(ROOT), '--log', str(log), '--timeout', '1',
                         '--', PY, '-c', 'import time; time.sleep(5)'])
            self.assertEqual(p.returncode, 3, (p.stdout, p.stderr))
            self.assertIn('"timed_out": true', p.stdout.replace("'", '"'))

    def test_command_run_empty_command_is_config_2(self):
        with tempfile.TemporaryDirectory() as d:
            p = run_cli(['command', 'run', '--cwd', str(ROOT), '--log', str(Path(d) / 'x.log'),
                         '--timeout', '5', '--'])
            self.assertEqual(p.returncode, 2, (p.stdout, p.stderr))

    def test_gate_cli_surfaces_unverified_on_text_and_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            directory = root / '.pipeline' / 'demo'
            directory.mkdir(parents=True)
            (directory / 'test.log').write_text('observed', encoding='utf-8')
            for role in ('executor', 'reviewer', 'main-final'):
                self._write_machine_report(directory, role)
            for name, role in (
                ('executor-result.json', 'executor'),
                ('reviewer-result.json', 'reviewer'),
                ('final-result.json', 'main-final'),
            ):
                (directory / name).write_text(json.dumps({
                    'schema': 1, 'task_id': 'demo', 'role': role, 'status': 'pass',
                    'acceptance': [{
                        'id': 'acceptance-test-1', 'status': 'pass', 'exit_code': 0,
                        'evidence_refs': ['.pipeline/demo/test.log'],
                    }],
                    'unverified': [],
                }), encoding='utf-8')
            (root / 'docs' / 'tasks').mkdir(parents=True)
            (root / 'implement-plan.md').write_text('plan\n', encoding='utf-8')
            contract = {
                'schema': 2, 'task_id': 'demo', 'task_type': 'repair',
                'implement_plan': {'path': 'implement-plan.md'},
                'allowed_paths': ['src/**'], 'forbidden_paths': [],
                'operations': [{'id': 'op', 'kind': 'validate', 'scope': 'task', 'acceptance_tests': ['acceptance-test-1']}],
                'chain': {name: ['src/app.py'] for name in ('entry', 'interaction', 'application', 'domain', 'persistence', 'readback', 'recovery')},
                'dependencies': [],
                'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2, 'test_ref': 'tests/test_cli.py', 'command_ref': 'python -m unittest'}],
                'required_evidence_levels': [2],
            }
            (root / 'docs' / 'tasks' / 'demo.md').write_text(
                '<!-- Task ID: demo -->\n```pipeline-contract\n' + json.dumps(contract) + '\n```\n',
                encoding='utf-8',
            )
            text = run_cli(['gate', 'pre-merge', str(directory), '--task-id', 'demo', '--branch', 'feature/demo'])
            self.assertEqual(text.returncode, 0, (text.stdout, text.stderr))
            self.assertIn('UNVERIFIED', text.stdout)
            self.assertIn('unrecorded', text.stdout)
            value = run_cli(['--format', 'json', 'gate', 'pre-merge', str(directory), '--task-id', 'demo', '--branch', 'feature/demo'])
            self.assertEqual(value.returncode, 0, (value.stdout, value.stderr))
            payload = json.loads(value.stdout)
            self.assertEqual(payload['status'], 'pass')
            self.assertTrue(any('unrecorded' in item for item in payload['unverified']), payload)

    def test_worktree_dispatch_cli_lifecycle_and_blocked_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root, head = make_repo(d)
            sheet = root / 'docs' / 'tasks' / 'dispatch.md'
            sheet.parent.mkdir(parents=True)
            sheet.write_text('''# dispatch\n<!-- Task ID: dispatch-task -->\n```pipeline-contract\n{"schema":2,"task_id":"dispatch-task","task_type":"prerequisite","implement_plan":{"path":"implement-plan.md"},"allowed_paths":["src/**"],"forbidden_paths":[],"operations":[{"id":"create","kind":"create","scope":"worktree","acceptance_tests":["acceptance-test-1"]}],"chain":{"entry":["cli.py"],"interaction":["cli.py"],"application":["app.py"],"domain":["domain.py"],"persistence":[".worktrees/<task-id>/"],"readback":["cli.py"],"recovery":["app.py"]},"dependencies":[],"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":3,"test_ref":"tests/test_cli.py","command_ref":"python -m unittest"}],"required_evidence_levels":[3]}\n```\n''', encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'freeze'], check=True)
            head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
            command = ['--format', 'json', 'dispatch', 'worktree-create', str(root), str(sheet), '--task-id', 'dispatch-task', '--branch', 'dispatch-branch', '--baseline', head]
            created = run_cli(command)
            self.assertEqual(created.returncode, 0, (created.stdout, created.stderr))
            value = json.loads(created.stdout)
            self.assertEqual(value['status'], 'pass')
            self.assertEqual(value['identity']['branch'], 'dispatch-branch')
            self.assertEqual(value['identity']['head'], head)
            readback = run_cli(command)
            self.assertEqual(readback.returncode, 3, (readback.stdout, readback.stderr))
            blocked = json.loads(readback.stdout)
            self.assertEqual(blocked['status'], 'blocked')
            self.assertTrue(blocked['blockers'])

    def test_task_preflight_and_freeze_check_subcommands(self):
        # SKILL.md stable interface: `pipeline-tools task preflight` / `task freeze-check`
        with tempfile.TemporaryDirectory() as d:
            repo, head = make_repo(d)
            for name in ('preflight', 'freeze-check'):
                p = run_cli(['task', name, str(repo), '--contract', head])
                self.assertEqual(p.returncode, 0, (name, p.stdout, p.stderr))
            # non-ancestor contract commit -> exit 4
            p = run_cli(['task', 'freeze-check', str(repo), '--contract', 'deadbeef'])
            self.assertEqual(p.returncode, 4, (p.stdout, p.stderr))

    def test_scope_check_multiple_allowed_flags(self):
        with tempfile.TemporaryDirectory() as d:
            repo, _ = make_repo(d)
            (repo / 'src').mkdir()
            (repo / 'src' / 'a.py').write_text('x', encoding='utf-8')
            (repo / 'docs').mkdir()
            (repo / 'docs' / 'b.md').write_text('x', encoding='utf-8')
            p = run_cli(['scope', 'check', str(repo), '--allowed', 'src/**', '--allowed', 'docs/**'])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))

    def test_scope_history_cli_since_passes_baseline_and_reports_drift(self):
        with tempfile.TemporaryDirectory() as d:
            repo, _ = make_repo(d)
            evidence = repo / '.pipeline' / 'demo'
            evidence.mkdir(parents=True)
            (evidence / 'historical-raw.log').write_text('raw', encoding='utf-8')
            subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(repo), 'commit', '-qm', 'historical evidence'],
                           check=True, capture_output=True)
            baseline = subprocess.check_output(
                ['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True
            ).strip()

            without_since = run_cli(['scope', 'history', str(repo), '--evidence-root', '.pipeline/demo'])
            self.assertEqual(without_since.returncode, 4, (without_since.stdout, without_since.stderr))

            bounded = run_cli([
                '--format', 'json', 'scope', 'history', str(repo),
                '--evidence-root', '.pipeline/demo', '--since', baseline,
            ])
            self.assertEqual(bounded.returncode, 0, (bounded.stdout, bounded.stderr))
            envelope = json.loads(bounded.stdout)
            self.assertEqual(envelope['command'], 'scope.history')
            self.assertEqual(envelope['status'], 'pass')

            (evidence / 'fresh-raw.log').write_text('raw', encoding='utf-8')
            subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(repo), 'commit', '-qm', 'fresh evidence'],
                           check=True, capture_output=True)
            drifted = run_cli([
                '--format', 'json', 'scope', 'history', str(repo),
                '--evidence-root', '.pipeline/demo', '--since', baseline,
            ])
            self.assertEqual(drifted.returncode, 4, (drifted.stdout, drifted.stderr))
            drift = json.loads(drifted.stdout)
            self.assertEqual(drift['status'], 'drift')
            self.assertTrue(any('fresh-raw.log' in error for error in drift['errors']), drift)
            self.assertFalse(any('historical-raw.log' in error for error in drift['errors']), drift)

    def test_metrics_roundtrip_and_purge(self):
        with tempfile.TemporaryDirectory() as d:
            root, _head = make_repo(d)
            p = run_cli(['metrics', 'record', str(root), 'test', '--confidence', 'observed',
                         '--task-id', 'demo', '--result', 'pass'])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            p = run_cli(['metrics', 'report', str(root)])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            self.assertIn('"core_events": 1', p.stdout.replace("'", '"'))
            p = run_cli(['metrics', 'purge', str(root)])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            self.assertEqual(list(metrics_dirs(root)[-1].glob('*.json')), [])

    def test_cli_automatically_migrates_legacy_workflow_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            legacy = root / '.workflow' / 'metrics'
            legacy.mkdir(parents=True)
            (legacy / 'old.json').write_text('{"schema": 1, "confidence": "observed", "event": "old", "result": "pass"}', encoding='utf-8')
            p = run_cli(['metrics', 'aggregate', str(root)])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            self.assertFalse((root / '.workflow').exists())
            self.assertTrue((root / '.pipeline' / 'metrics' / 'old.json').exists())

    def test_workflow_command_automatically_records_tracked_metric(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            task = root / 'task.md'
            task.write_text('''# Demo\n<!-- Task ID: demo -->\n```pipeline-contract\n{"schema":1,"task_id":"demo","allowed_paths":["src/**"],"forbidden_paths":[],"acceptance_tests":[{"id":"AT1","evidence_level":1,"test_ref":"tests/x.py","command_ref":"python -m unittest"}]}\n```\n''', encoding='utf-8')
            p = run_cli(['task', 'validate', str(task)], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            files = list(metrics_dirs(root)[-1].glob('*.json'))
            self.assertEqual(len(files), 1)
            value = json.loads(files[0].read_text(encoding='utf-8'))
            self.assertEqual(value['event'], 'task_validate')
            self.assertEqual(value['confidence'], 'observed')
            self.assertEqual(value['task_id'], 'demo')
            self.assertEqual(value['result'], 'pass')
            self.assertEqual(value['source'], 'pipeline_tools')
            self.assertEqual(value['evidence_ref'], 'task.md')
            self.assertIsInstance(value['duration_s'], float)
            # Tracking is the project developer's choice: this test must not
            # forbid the repository's own policy in either direction.
            ignored = subprocess.run(['git', '-C', str(ROOT), 'check-ignore', '--no-index', '.pipeline/metrics/event.json'], capture_output=True, text=True, timeout=60)
            self.assertIn(ignored.returncode, (0, 1), (ignored.stdout, ignored.stderr))

    def test_automatic_timeout_records_feedback_event(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root / 'timeout.log'
            p = run_cli(['command', 'run', '--cwd', str(root), '--log', str(log), '--timeout', '1', '--task-id', 'demo', '--', PY, '-c', 'import time; time.sleep(5)'], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 3, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            self.assertEqual({value['event'] for value in values}, {'command_run', 'timeout'})
            command = next(value for value in values if value['event'] == 'command_run')
            self.assertTrue(command['timed_out'])
            self.assertEqual(command['result'], 'blocked')
            timeout = next(value for value in values if value['event'] == 'timeout')
            self.assertEqual(timeout['result'], 'blocked')
            self.assertEqual(timeout['task_id'], 'demo')

    def test_automatic_command_uses_task_id_from_workflow_log_path(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root / '.pipeline' / 'demo' / 'test.log'
            p = run_cli(['command', 'run', '--cwd', str(root), '--log', str(log), '--timeout', '5', '--', PY, '-c', 'print("ok")'], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            self.assertEqual(len(values), 1)
            self.assertEqual(values[0]['task_id'], 'demo')
            self.assertEqual(values[0]['evidence_ref'], '.pipeline/demo/test.log')

    def test_automatic_retry_preserves_attempt_and_reason_for_first_retry(self):
        self.test_automatic_retry_records_first_retry_attempt()

    def test_automatic_retry_records_first_retry_attempt(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = run_cli(['command', 'run', '--cwd', str(root), '--log', 'retry.log', '--timeout', '5', '--attempt', '1', '--', PY, '-c', 'print("ok")'], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            self.assertEqual({value['event'] for value in values}, {'command_run', 'retry'})
            retry = next(value for value in values if value['event'] == 'retry')
            self.assertEqual(retry['attempt'], 1)
            self.assertEqual(retry['reason'], 'attempt_1')

    def test_malformed_non_metrics_command_records_a_failure_metric(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = run_cli(['command', 'run', '--cwd', str(root)], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 2, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            self.assertEqual(len(values), 1)
            self.assertEqual(values[0]['event'], 'command_run')
            self.assertEqual(values[0]['result'], 'fail')

    def test_top_level_parse_error_records_a_failure_metric(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = run_cli(['not-a-command'], cwd=root, env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0', 'PYTHONPATH': str(ROOT)})
            self.assertEqual(p.returncode, 2, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            self.assertEqual(len(values), 1)
            self.assertEqual(values[0]['event'], 'cli_parse_error')

    def test_unknown_top_level_and_help_invocations_record_automatic_metrics(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for argv, expected in ((['not-a-command'], 'cli_parse_error'), (['task', 'validate', '--help'], 'cli_help')):
                p = run_cli(argv, cwd=root, env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0', 'PYTHONPATH': str(ROOT)})
                self.assertIn(p.returncode, (0, 2))
                values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
                self.assertEqual(values[-1]['event'], expected)

    def test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stderr = io.StringIO()
            argv = ['command', 'run', '--cwd', str(root), '--log', 'test.log', '--', PY, '-c', 'import sys; sys.exit(1)']
            # Collection must actually be enabled for this fail-soft scenario; the
            # ambient test environment disables it to avoid mutating this checkout.
            with mock.patch.dict(os.environ, {'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'}), \
                    mock.patch('pipeline_tools.__main__.metric_event', side_effect=OSError('read-only')), \
                    contextlib.redirect_stderr(stderr):
                result = main(argv)
            self.assertEqual(result, 1)
            self.assertIn('automatic_metrics_not_collected', stderr.getvalue())

    def test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code(self):
        isolated = isolated_metrics_root()
        repo_metrics = ROOT / '.pipeline' / 'metrics'
        before = metrics_snapshot(repo_metrics)
        log = isolated / 'pipeline-wrapper-test.log'
        command = [PY, '-m', 'pipeline_tools', 'command', 'run', '--cwd', str(isolated),
                   '--log', str(log), '--timeout', '30', '--', PY, '-c', 'raise SystemExit(7)']
        for enabled in ('0', '1'):
            with self.subTest(automatic_metrics=enabled):
                env = dict(os.environ, PIPELINE_TOOLS_DISABLE_AUTO_METRICS=enabled,
                           PYTHONPATH=str(ROOT))
                completed = subprocess.run(command, capture_output=True, text=True, env=env, timeout=60)
                self.assertEqual(completed.returncode, 1, (enabled, completed.stdout, completed.stderr))
                self.assertIn('"exit_code": 7', completed.stdout.replace("'", '"'))
        # Isolation must not weaken the wrapper: the outer command's real exit
        # code still propagates, and the enabled run wrote only under the
        # throwaway root.
        self.assertEqual(metrics_snapshot(repo_metrics), before)
        self.assertTrue(metrics_snapshot(isolated / '.pipeline' / 'metrics'))

    def test_repository_metrics_are_ignored_and_untracked(self):
        gitignore = (ROOT / '.gitignore').read_text(encoding='utf-8')
        self.assertIn('.pipeline/metrics/', gitignore)
        ignored = subprocess.run(['git', '-C', str(ROOT), 'check-ignore', '.pipeline/metrics/event.json'], capture_output=True, text=True, timeout=60)
        self.assertEqual(ignored.returncode, 0, (ignored.stdout, ignored.stderr))
        tracked = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '.pipeline/metrics/'], capture_output=True, text=True, timeout=60)
        self.assertEqual(tracked.returncode, 0, (tracked.stdout, tracked.stderr))
        self.assertEqual(tracked.stdout.strip(), '', tracked.stdout)

    def test_cli_suite_does_not_write_repository_metrics(self):
        repo_metrics = ROOT / '.pipeline' / 'metrics'
        before = metrics_snapshot(repo_metrics)
        # A real automatic-metrics run: a malformed top-level invocation still
        # records a cli_parse_error event, so collection genuinely happens.
        completed = run_cli(['not-a-command'],
                            env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
        self.assertEqual(completed.returncode, 2, (completed.stdout, completed.stderr))
        self.assertEqual(metrics_snapshot(repo_metrics), before)

    def test_cli_suite_leaves_tracked_metrics_unchanged(self):
        repo_metrics = ROOT / '.pipeline' / 'metrics'
        before = metrics_snapshot(repo_metrics)
        isolated = isolated_metrics_root()
        log = isolated / 'suite-guard.log'
        command = [PY, '-m', 'pipeline_tools', 'command', 'run', '--cwd', str(isolated),
                   '--log', str(log), '--timeout', '30', '--', PY, '-c', 'print("ok")']
        for enabled in ('0', '1'):
            with self.subTest(automatic_metrics=enabled):
                env = dict(os.environ, PIPELINE_TOOLS_DISABLE_AUTO_METRICS=enabled,
                           PYTHONPATH=str(ROOT))
                completed = subprocess.run(command, capture_output=True, text=True, env=env, timeout=60)
                self.assertEqual(completed.returncode, 0, (enabled, completed.stdout, completed.stderr))
                self.assertEqual(metrics_snapshot(repo_metrics), before, enabled)

    def test_auto_metrics_enabled_run_keeps_metrics_out_of_repository(self):
        repo_metrics = ROOT / '.pipeline' / 'metrics'
        before = metrics_snapshot(repo_metrics)
        isolated = isolated_metrics_root()
        isolated_metrics = isolated / '.pipeline' / 'metrics'
        isolated_before = metrics_snapshot(isolated_metrics)
        # No explicit cwd: an enabled automatic-metrics run resolves its
        # project root from the harness default and must stay out of the
        # repository. A malformed top-level invocation still records a
        # cli_parse_error event, so this genuinely exercises collection.
        completed = run_cli(['not-a-command'],
                            env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
        self.assertEqual(completed.returncode, 2, (completed.stdout, completed.stderr))
        self.assertEqual(metrics_snapshot(repo_metrics), before)
        after = metrics_snapshot(isolated_metrics)
        self.assertEqual(len(after), len(isolated_before) + 1)
        self.assertTrue(set(after) - set(isolated_before))

    def test_planning_cli_rejects_historical_task_as_current_target(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "implement-plan.md").write_text("current", encoding="utf-8")
            historical = root / "docs" / "tasks" / "historical.md"; historical.parent.mkdir(parents=True); historical.write_text("historical", encoding="utf-8")
            completed = run_cli(["planning", "task-plan-validate", str(historical), "--root", str(root)])
            self.assertNotEqual(completed.returncode, 0)
            self.assertNotIn("dispatch-ready", completed.stdout + completed.stderr)

    def test_planning_to_dispatch_cli_blocks_when_facts_envelope_has_conflicts(self):
        with tempfile.TemporaryDirectory() as d:
            root, head = make_repo(d)
            (root / 'implement-plan.md').write_text('stable planning requirements\n', encoding='utf-8')
            chain_value = {name: ['ok.txt'] for name in ('entry', 'interaction', 'application', 'domain', 'persistence', 'readback', 'recovery')}
            acceptance = [{'id': 'acceptance-test-1', 'evidence_level': 1, 'test_ref': 'tests/test_cli.py', 'command_ref': 'python -m unittest'}]
            project = {'schema': 1, 'sources': [{'id': 'source', 'path': 'implement-plan.md'}], 'resources': [{'id': 'resource', 'path': 'ok.txt'}], 'operations': [{'id': 'op', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}], 'acceptance_tests': acceptance, 'chain': chain_value, 'facts': [], 'assumptions': [], 'unknowns': [], 'conflicts': [{'id': 'blocking', 'status': 'blocking'}], 'non_goals': ['本项目没有用户可见扩展'], 'decision_blockers': []}
            requirements = {'schema': 1, 'sources': [{'id': 'source', 'path': 'implement-plan.md'}], 'requirements': [{'id': 'requirement', 'source_refs': ['source']}], 'operations': [{'id': 'op', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}], 'acceptance_tests': acceptance}
            plan = {'schema': 1, 'non_goals': ['本项目没有用户可见扩展'], 'requirements': ['requirement'], 'resources': ['resource'], 'operations': [{'id': 'op', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}], 'acceptance_tests': acceptance, 'tasks': [{'id': 'cli-dispatch-task', 'type': 'prerequisite', 'requirements': ['requirement'], 'resources': ['resource'], 'operations': ['op'], 'depends_on': []}]}
            paths = []
            for name, value in (('project.json', project), ('requirements.json', requirements), ('plan.json', plan)):
                path = root / name; path.write_text(json.dumps(value), encoding='utf-8'); paths.append(path)
            command = ['--format', 'json', 'planning', 'to-dispatch', str(root), '--run-id', 'cli-envelope-run', '--project-facts', str(paths[0]), '--requirement-facts', str(paths[1]), '--task-plan', str(paths[2]), '--task-id', 'cli-dispatch-task', '--baseline', head]
            completed = subprocess.run([PY, '-m', 'pipeline_tools', *command], cwd=str(root), capture_output=True, text=True,
                                       env=dict(os.environ, PIPELINE_TOOLS_DISABLE_AUTO_METRICS='1', PYTHONPATH=str(ROOT)), timeout=60)
            self.assertNotEqual(completed.returncode, 0, (completed.stdout, completed.stderr))
            value = json.loads(completed.stdout)
            self.assertEqual(value['status'], 'blocked')
            self.assertEqual(value['stages'][-1]['name'], 'facts-gate')
            self.assertFalse((root / '.worktrees' / 'cli-dispatch-task').exists())

    def test_subcommand_help_records_a_help_metric(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = run_cli(['task', 'validate', '--help'], cwd=root, env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0', 'PYTHONPATH': str(ROOT)})
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            self.assertEqual(len(values), 1)
            self.assertEqual(values[0]['event'], 'cli_help')

    def test_automatic_metrics_redact_sensitive_path_components(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root / '.pipeline' / 'demo' / 'secret' / 'test.log'
            p = run_cli(['command', 'run', '--cwd', str(root), '--log', str(log), '--timeout', '5', '--task-id', 'demo', '--', PY, '-c', 'print("ok")'], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            self.assertEqual(len(values), 1)
            self.assertIsNone(values[0]['evidence_ref'])
            self.assertNotIn('secret', values[0]['task_id'].lower())

    def test_automatic_runtime_and_lifecycle_events_keep_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            workflow = root / '.pipeline' / 'demo'
            p = run_cli(['runtime', 'handshake', str(root), str(workflow), '--role', 'reviewer', '--node', '0.0.0'], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 3, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            handshake = next(value for value in values if value['event'] == 'runtime_handshake')
            self.assertEqual(handshake['task_id'], 'demo')
            self.assertEqual(handshake['evidence_ref'], '.pipeline/demo/capability-handshake.json')
            p = run_cli(['lifecycle', 'status', str(root), '--task-id', 'demo', '--evidence', str(workflow)], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            lifecycle = next(value for value in values if value['event'] == 'lifecycle_status')
            self.assertEqual(lifecycle['task_id'], 'demo')
            self.assertEqual(lifecycle['evidence_ref'], '.pipeline/demo')

    def test_metrics_commands_do_not_recursively_record_stage_metrics(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = run_cli(['metrics', 'record', str(root), 'manual', '--confidence', 'observed', '--task-id', 'demo'], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            p = run_cli(['metrics', 'report', str(root)], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            self.assertEqual(len(values), 1)
            self.assertEqual(values[0]['event'], 'manual')

    def test_metrics_report_filters_by_task_and_terminal(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for event, result, task, terminal in (
                ('evidence_verify', 'blocked', 'task-a', False),
                ('gate_pre_merge', 'pass', 'task-a', True),
                ('task_validate', 'pass', 'task-b', True),
            ):
                args = ['metrics', 'record', str(root), event, '--confidence', 'observed', '--task-id', task, '--result', result]
                if terminal:
                    args.extend(['--terminal'])
                p = run_cli(args)
                self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            p = run_cli(['metrics', 'report', str(root), '--task-id', 'task-a', '--terminal-only'])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            value = json.loads(p.stdout)
            self.assertEqual(value['events'], 1)
            self.assertEqual(value['terminal_gate_pass_count'], 1)

    def test_evidence_readiness_reports_missing_final_check_without_gate_claim(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            evidence = root / '.pipeline' / 'demo'
            evidence.mkdir(parents=True)
            p = run_cli(['--format', 'json', 'evidence', 'readiness', str(evidence), '--task-id', 'demo'])
            self.assertEqual(p.returncode, 3, (p.stdout, p.stderr))
            value = json.loads(p.stdout)
            self.assertEqual(value['status'], 'not_ready')
            self.assertIn('final-check.md', value['missing'])

    def test_evidence_readiness_records_not_ready_feedback(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            evidence = root / '.pipeline' / 'demo'
            evidence.mkdir(parents=True)
            p = run_cli(
                ['--format', 'json', 'evidence', 'readiness', str(evidence), '--task-id', 'demo'],
                env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'},
            )
            self.assertEqual(p.returncode, 3, (p.stdout, p.stderr))
            values = [json.loads(path.read_text(encoding='utf-8')) for path in metrics_dirs(root)[-1].glob('*.json')]
            self.assertEqual({value['event'] for value in values}, {'evidence_readiness', 'evidence_not_ready'})
            derived = next(value for value in values if value['event'] == 'evidence_not_ready')
            self.assertEqual(derived['confidence'], 'derived')
            self.assertEqual(derived['blocker_class'], 'evidence')

    def test_automatic_events_carry_task_and_evidence_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root, _head = make_repo(d)
            task = root / 'task.md'
            task.write_text('''# Demo\n<!-- Task ID: demo -->\n```pipeline-contract\n{"schema":1,"task_id":"demo","allowed_paths":["src/**"],"forbidden_paths":[],"acceptance_tests":[{"id":"AT1","evidence_level":1,"test_ref":"tests/x.py","command_ref":"python -m unittest"}]}\n```\n''', encoding='utf-8')
            p = run_cli(['task', 'validate', str(task)], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            value = json.loads(next(metrics_dirs(root)[-1].glob('*.json')).read_text(encoding='utf-8'))
            self.assertEqual(value['task_id'], 'demo')
            self.assertEqual(value['evidence_root'], None)
            self.assertFalse(value['terminal'])
            self.assertTrue(value['run_id'].startswith('demo-'))
            self.assertEqual(value['phase'], 'contract')
            self.assertIsNotNone(value['head'])
            self.assertIsNotNone(value['branch'])

    def test_runtime_preflight_and_role_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            p = run_cli(['runtime', 'preflight', str(root), '--node', '0.0.0'])
            self.assertEqual(p.returncode, 3, (p.stdout, p.stderr))
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_text('x', encoding='utf-8')
            p = run_cli(['runtime', 'role-scope', str(root), '--role', 'main-agent', '--product-pattern', 'src/**'])
            self.assertEqual(p.returncode, 4, (p.stdout, p.stderr))
            p = run_cli(['runtime', 'role-scope', str(root), '--role', 'main-agent', '--product-pattern', 'src/**', '--authorized'])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))

    def test_runtime_preflight_uses_windows_pnpm_command_name(self):
        import platform

        if platform.system() != 'Windows':
            self.skipTest('Windows command resolution only')
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            fake_bin = Path(d) / 'bin'
            fake_bin.mkdir()
            (fake_bin / 'pnpm.cmd').write_text('@echo 10.27.0\n', encoding='utf-8')
            env = {
                'PATH': str(fake_bin) + ';' + os.environ.get('PATH', ''),
                'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '1',
            }
            p = run_cli(['runtime', 'preflight', str(root), '--pnpm', '10.27.0'], env=env)
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            self.assertEqual(json.loads(p.stdout)['checks']['pnpm'], '10.27.0')

    def test_runtime_handshake_writes_machine_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            workflow = root / '.pipeline' / 'demo'
            p = run_cli(['runtime', 'handshake', str(root), str(workflow), '--role', 'reviewer'])
            self.assertEqual(p.returncode, 3, (p.stdout, p.stderr))
            self.assertTrue((workflow / 'capability-handshake.json').is_file())

    def test_import_opencode_session_cli(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            session = root / 'session.json'
            session.write_text('{"info":{"id":"ses_demo"},"messages":[]}', encoding='utf-8')
            p = run_cli(['metrics', 'import-opencode-session', str(root), str(session), '--task-id', 'demo'])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            self.assertIn('"imported": 0', p.stdout)

    def test_bin_wrappers_run(self):
        # AT6: wrappers must run; on Windows use .cmd via shell, on POSIX use the sh wrapper.
        import platform
        with tempfile.TemporaryDirectory() as d:
            if platform.system() == 'Windows':
                r = subprocess.run(['cmd', '/c', str(ROOT / 'bin' / 'pipeline-tools.cmd'), '--help'],
                                   capture_output=True, text=True, cwd=str(ROOT), timeout=60,
                                   env={**os.environ, 'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '1', 'PATH': os.environ.get('PATH', '') + ';C:\\Users\\alexc\\AppData\\Local\\Programs\\Python\\Python312'})
            else:
                r = subprocess.run([str(ROOT / 'bin' / 'pipeline-tools'), '--help'],
                                   capture_output=True, text=True, cwd=str(ROOT), timeout=60,
                                   env={**os.environ, 'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '1'})
            self.assertEqual(r.returncode, 0, (r.stdout, r.stderr))
            self.assertIn('task', r.stdout)

    def test_task_validate_real_sheet(self):
        p = run_cli(['task', 'validate', str(ROOT / 'docs' / 'tasks' / 'pipeline-tools-v1.md')])
        self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
        p = run_cli(['task', 'validate', str(ROOT / 'nope.md')])
        self.assertEqual(p.returncode, 2, (p.stdout, p.stderr))

    def test_planning_run_lifecycle_success_and_idempotent_finalize(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            (root / 'implement-plan.md').write_text('stable requirements\\n', encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', 'implement-plan.md'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'plan'], check=True)
            start = run_cli(['--format', 'json', 'planning', 'run', 'start', str(root), '--run-id', 'cli-lifecycle'])
            self.assertEqual(start.returncode, 0, (start.stdout, start.stderr))
            self.assertEqual(json.loads(start.stdout)['status'], 'pass')
            for phase in ('preflight', 'planned', 'generated'):
                transition = run_cli(['--format', 'json', 'planning', 'run', 'transition', str(root), '--run-id', 'cli-lifecycle', '--phase', phase])
                self.assertEqual(transition.returncode, 0, (transition.stdout, transition.stderr))
            finish = run_cli(['--format', 'json', 'planning', 'run', 'finalize', str(root), '--run-id', 'cli-lifecycle', '--success'])
            self.assertEqual(finish.returncode, 0, (finish.stdout, finish.stderr))
            value = json.loads(finish.stdout)
            self.assertEqual(value['status'], 'finalized')
            self.assertIn('run_id', value)
            self.assertIn('requirements_sha256', value)
            self.assertIn('artifacts', value)
            repeat = run_cli(['--format', 'json', 'planning', 'run', 'finalize', str(root), '--run-id', 'cli-lifecycle', '--success'])
            self.assertEqual(repeat.returncode, 0, (repeat.stdout, repeat.stderr))
            repeated = json.loads(repeat.stdout)
            self.assertEqual(repeated['status'], 'finalized')
            self.assertEqual(repeated['run_id'], value['run_id'])
            self.assertEqual(repeated['artifacts'], [])
            self.assertFalse((root / '.pipeline' / 'planning' / 'cli-lifecycle').exists())
            self.assertFalse((root / '.pipeline' / 'metrics').exists())

    def test_lifecycle_status_is_structured_and_starts_with_executor(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            evidence = root / '.pipeline' / 'demo'
            p = run_cli(['--format', 'json', 'lifecycle', 'status', str(root), '--task-id', 'demo', '--evidence', str(evidence)])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            value = json.loads(p.stdout)
            self.assertEqual(value['status'], 'ready')
            self.assertEqual(value['phase'], 'executor')
            self.assertIn('dispatch_executor', value['next_actions'])

    def test_dispatch_result_and_freshness_form_machine_closed_loop(self):
        with tempfile.TemporaryDirectory() as d:
            root, head = make_repo(d)
            dispatch = root / 'dispatch.json'
            dispatch.write_text(json.dumps({
                'schema': 1, 'task_id': 'demo', 'role': 'reviewer', 'round': 1,
                'root': '.', 'worktree': '.', 'branch': 'main',
                'evidence_dir': '.pipeline/demo',
                'permissions': {'write_workflow': True, 'write_product': False},
                'output': {'result': '.pipeline/demo/reviewer-result.json'},
            }), encoding='utf-8')
            out = root / '.pipeline' / 'demo' / 'dispatch.json'
            p = run_cli(['dispatch', 'write', str(dispatch), str(out)])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            evidence = root / '.pipeline' / 'demo' / 'evidence.log'
            evidence.write_text('observed', encoding='utf-8')
            result = root / '.pipeline' / 'demo' / 'reviewer-result.json'
            result.write_text(json.dumps({
                'schema': 1, 'task_id': 'demo', 'role': 'reviewer', 'status': 'pass',
                'identity': {'head': head}, 'acceptance': [{'id': 'AT1', 'status': 'pass', 'exit_code': 0, 'evidence_refs': ['.pipeline/demo/evidence.log']}],
                'unverified': [],
            }), encoding='utf-8')
            p = run_cli(['result', 'verify', str(result), '--task-id', 'demo', '--role', 'reviewer'])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            (root / 'implement-plan.md').write_text('frozen plan\n', encoding='utf-8')
            digest = __import__('hashlib').sha256((root / 'implement-plan.md').read_bytes()).hexdigest()
            (root / '.pipeline' / 'demo' / 'implement-plan.json').write_text(
                json.dumps({'schema': 1, 'task_id': 'demo', 'sha256': digest}), encoding='utf-8',
            )
            sheet = root / 'docs' / 'tasks' / 'demo.md'
            sheet.parent.mkdir(parents=True, exist_ok=True)
            sheet.write_text(
                '<!-- Task ID: demo -->\n```pipeline-contract\n'
                + json.dumps({
                    'schema': 1, 'task_id': 'demo',
                    'allowed_paths': ['src/**'], 'forbidden_paths': [],
                    'acceptance_tests': [{
                        'id': 'AT1', 'evidence_level': 1,
                        'test_ref': 'tests/test_cli.py', 'command_ref': 'python -m unittest',
                    }],
                })
                + '\n```\n',
                encoding='utf-8',
            )
            p = run_cli(['--format', 'json', 'freshness', str(root), str(root / '.pipeline' / 'demo'), '--result', str(result)])
            self.assertEqual(p.returncode, 0, (p.stdout, p.stderr))
            self.assertEqual(json.loads(p.stdout)['status'], 'pass')

    def test_planning_to_dispatch_cli_contract_and_failure_boundaries(self):
        with tempfile.TemporaryDirectory() as d:
            root, head = make_repo(d)
            (root / "implement-plan.md").write_text("stable plan\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("app\n", encoding="utf-8")
            project = {"schema": 1, "sources": [{"id": "source", "path": "implement-plan.md"}], "resources": [{"id": "resource", "path": "src/app.py"}, {"id": "test-resource", "path": "tests/test_cli.py"}], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_cli.py", "command_ref": "python -m unittest"}], "chain": {name: ["src/app.py"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")}, "non_goals": ["本项目没有用户可见扩展"]}
            requirements = {"schema": 1, "sources": [{"id": "source", "path": "implement-plan.md"}], "requirements": [{"id": "requirement", "source_refs": ["source"]}], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": project["acceptance_tests"]}
            plan = {"schema": 1, "non_goals": ["本任务不扩展用户可见范围"], "requirements": ["requirement"], "resources": ["resource", "tests/test_cli.py"], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": project["acceptance_tests"], "tasks": [{"id": "cli-integration-task", "type": "prerequisite", "requirements": ["requirement"], "resources": ["resource", "tests/test_cli.py"], "operations": ["operate"], "depends_on": [], "non_user_completion_reason": "produces the enabling artifact consumed by later user-facing work"}]}
            paths = []
            for name, value in (("project.json", project), ("requirements.json", requirements), ("plan.json", plan)):
                path = root / name
                path.write_text(json.dumps(value), encoding="utf-8")
                paths.append(path)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "inputs"], cwd=root, check=True)
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            args = ["--format", "json", "planning", "to-dispatch", str(root), "--run-id", "cli-integration-run", "--project-facts", str(paths[0]), "--requirement-facts", str(paths[1]), "--task-plan", str(paths[2]), "--task-id", "cli-integration-task", "--branch", "cli-integration-branch", "--baseline", head, "--approve"]
            completed = run_cli(args, cwd=root, env={"PYTHONPATH": str(ROOT)})
            self.assertEqual(completed.returncode, 0, (completed.stdout, completed.stderr))
            value = json.loads(completed.stdout)
            self.assertEqual(value["status"], "dispatch-ready")
            self.assertEqual(value["run_id"], "cli-integration-run")
            self.assertEqual(value["identity"]["task_id"], "cli-integration-task")
            self.assertIn("stages", value)
            self.assertEqual(value["artifacts"], [])
            self.assertFalse((root / ".pipeline" / "planning" / "cli-integration-run").exists())
            self.assertTrue((root / ".worktrees" / "cli-integration-task").is_dir())
            replay = run_cli(args, cwd=root, env={"PYTHONPATH": str(ROOT)})
            self.assertEqual(replay.returncode, 3, (replay.stdout, replay.stderr))
            blocked = json.loads(replay.stdout)
            self.assertEqual(blocked["status"], "blocked")
            self.assertTrue(blocked["errors"])

    def test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan = root / 'plan.json'
            sheet = root / 'task.md'
            implement_plan = root / 'implement-plan.md'
            implement_plan.write_text('stable plan\\n', encoding='utf-8')
            digest = __import__('hashlib').sha256(implement_plan.read_bytes()).hexdigest()
            chain = {name: ['not-applicable'] for name in ('entry', 'interaction', 'application', 'domain', 'persistence', 'readback', 'recovery')}
            acceptance = [{'id': 'acceptance-test-1', 'evidence_level': 2, 'test_ref': 'tests/test_cli.py', 'command_ref': 'python -m unittest'}]
            operation = {'id': 'op', 'kind': 'validate', 'scope': 'task', 'resources': ['pipeline_tools/planning.py'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}
            value = {'schema': 1, 'non_goals': ['本任务不扩展范围'], 'requirements': ['req'], 'resources': ['pipeline_tools/planning.py', 'tests/test_cli.py'], 'operations': [operation], 'acceptance_tests': acceptance, 'tasks': [{'id': 'demo', 'type': 'prerequisite', 'requirements': ['req'], 'resources': ['pipeline_tools/planning.py', 'tests/test_cli.py'], 'operations': ['op'], 'chain': chain, 'depends_on': []}]}
            plan.write_text(json.dumps(value), encoding='utf-8')
            contract = {'schema': 2, 'task_id': 'demo', 'task_type': 'prerequisite', 'implement_plan': {'path': 'implement-plan.md', 'sha256': digest, 'planning_run_id': 'run-1'}, 'allowed_paths': ['pipeline_tools/planning.py', 'tests/test_cli.py'], 'forbidden_paths': ['implement-plan.md'], 'requirements': ['req'], 'resources': ['pipeline_tools/planning.py', 'tests/test_cli.py'], 'operations': [{key: value for key, value in operation.items() if key != 'resource_mode'}], 'chain': chain, 'acceptance_tests': acceptance, 'dependencies': [], 'required_evidence_levels': [2]}
            sheet.write_text('<!-- Task ID: demo -->\n```pipeline-contract\n' + json.dumps(contract) + '\n```\n', encoding='utf-8')
            result = run_cli(['--format', 'json', 'planning', 'task-plan-contract-consistency', str(plan), str(sheet), '--root', str(root), '--expected-requirements-sha256', digest, '--expected-run-id', 'run-1'])
            self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
            self.assertEqual(json.loads(result.stdout)['status'], 'pass')


    def _dispatch_inputs(self, root, head):
        (root / 'implement-plan.md').write_text('stable planning requirements\n', encoding='utf-8')
        chain_value = {name: ['ok.txt'] for name in ('entry', 'interaction', 'application', 'domain', 'persistence', 'readback', 'recovery')}
        acceptance = [{'id': 'acceptance-test-1', 'evidence_level': 2, 'test_ref': 'tests/test_cli.py', 'command_ref': 'python -m unittest'}]
        project = {'schema': 1, 'sources': [{'id': 'source', 'path': 'implement-plan.md'}], 'resources': [{'id': 'resource', 'path': 'ok.txt'}, {'id': 'test-resource', 'path': 'tests/test_cli.py'}], 'operations': [{'id': 'op', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}], 'acceptance_tests': acceptance, 'chain': chain_value, 'facts': [], 'assumptions': [], 'unknowns': [], 'conflicts': [], 'non_goals': ['本项目没有用户可见扩展'], 'decision_blockers': []}
        requirements = {'schema': 1, 'sources': [{'id': 'source', 'path': 'implement-plan.md'}], 'requirements': [{'id': 'requirement', 'source_refs': ['source']}], 'operations': [{'id': 'op', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}], 'acceptance_tests': acceptance}
        plan = {'schema': 1, 'non_goals': ['本项目没有用户可见扩展'], 'requirements': ['requirement'], 'resources': ['resource', 'tests/test_cli.py'], 'operations': [{'id': 'op', 'resources': ['resource'], 'resource_mode': 'single', 'acceptance_tests': ['acceptance-test-1']}], 'acceptance_tests': acceptance, 'tasks': [{'id': 'cli-approval-task', 'type': 'prerequisite', 'requirements': ['requirement'], 'resources': ['resource', 'tests/test_cli.py'], 'operations': ['op'], 'depends_on': [], 'non_user_completion_reason': 'produces the enabling artifact consumed by later user-facing work'}]}
        subprocess.run(['git', 'add', '.'], cwd=root, check=True)
        subprocess.run(['git', 'commit', '-qm', 'approval inputs'], cwd=root, check=True)
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
        paths = []
        for name, value in (('project.json', project), ('requirements.json', requirements), ('plan.json', plan)):
            path = root / name
            path.write_text(json.dumps(value), encoding='utf-8')
            paths.append(path)
        return paths, head

    def _to_dispatch(self, root, paths, head, run_id, *extra):
        command = ['--format', 'json', 'planning', 'to-dispatch', str(root), '--run-id', run_id,
                   '--project-facts', str(paths[0]), '--requirement-facts', str(paths[1]),
                   '--task-plan', str(paths[2]), '--task-id', 'cli-approval-task',
                   '--branch', f'{run_id}-branch', '--baseline', head, *extra]
        return run_cli(command, cwd=root, env={'PYTHONPATH': str(ROOT)})

    def test_planning_run_start_cli_defaults_from_project_config(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            (root / 'implement-plan.md').write_text('stable requirements\n', encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '-qm', 'plan'], check=True)
            config = root / '.pipeline' / 'config.json'
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text(json.dumps({'approval_mode': 'manual'}), encoding='utf-8')
            started = run_cli(['--format', 'json', 'planning', 'run', 'start', str(root), '--run-id', 'cli-project-manual'])
            self.assertEqual(started.returncode, 0, (started.stdout, started.stderr))
            state = json.loads((root / '.pipeline' / 'planning' / 'cli-project-manual' / 'lifecycle.json').read_text(encoding='utf-8'))
            self.assertEqual(state['approval_mode'], 'manual')
            explicit = run_cli(['--format', 'json', 'planning', 'run', 'start', str(root), '--run-id', 'cli-explicit-automatic', '--approval-mode', 'automatic'])
            self.assertEqual(explicit.returncode, 0, (explicit.stdout, explicit.stderr))
            explicit_state = json.loads((root / '.pipeline' / 'planning' / 'cli-explicit-automatic' / 'lifecycle.json').read_text(encoding='utf-8'))
            self.assertEqual(explicit_state['approval_mode'], 'automatic')

    def test_planning_to_dispatch_cli_resolves_recorded_then_project_then_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            config = root / '.pipeline' / 'config.json'
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text(json.dumps({'approval_mode': 'manual'}), encoding='utf-8')
            paths, head = self._dispatch_inputs(root, None)
            started = run_cli(['--format', 'json', 'planning', 'run', 'start', str(root), '--run-id', 'cli-recorded', '--approval-mode', 'automatic'])
            self.assertEqual(started.returncode, 0, (started.stdout, started.stderr))
            recorded = self._to_dispatch(root, paths, head, 'cli-recorded')
            self.assertEqual(recorded.returncode, 0, (recorded.stdout, recorded.stderr))
            self.assertEqual(json.loads(recorded.stdout)['status'], 'dispatch-ready')

        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            config = root / '.pipeline' / 'config.json'
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text(json.dumps({'approval_mode': 'manual'}), encoding='utf-8')
            paths, head = self._dispatch_inputs(root, None)
            blocked = self._to_dispatch(root, paths, head, 'cli-project')
            self.assertEqual(blocked.returncode, 3, (blocked.stdout, blocked.stderr))
            value = json.loads(blocked.stdout)
            self.assertEqual(value['status'], 'blocked')
            self.assertEqual(value['stages'][-1]['name'], 'approval')
            self.assertFalse((root / '.worktrees' / 'cli-approval-task').exists())

        with tempfile.TemporaryDirectory() as d:
            root, _ = make_repo(d)
            config = root / '.pipeline' / 'config.json'
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text(json.dumps({'approval_mode': 'manual'}), encoding='utf-8')
            paths, head = self._dispatch_inputs(root, None)
            explicit = self._to_dispatch(root, paths, head, 'cli-explicit', '--approval-mode', 'automatic')
            self.assertEqual(explicit.returncode, 0, (explicit.stdout, explicit.stderr))
            self.assertEqual(json.loads(explicit.stdout)['status'], 'dispatch-ready')


if __name__ == '__main__':
    unittest.main()
