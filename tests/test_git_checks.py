import subprocess, tempfile, unittest
from pathlib import Path
from pipeline_tools.core import commit_history_check, freeze_check, scope_check

class GitChecks(unittest.TestCase):
    def test_untracked_forbidden_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); subprocess.run(['git','init'],cwd=p,capture_output=True)
            (p/'ok.txt').write_text('x'); (p/'bad.secret').write_text('x')
            self.assertEqual(scope_check(p,['ok.txt'],['*.secret']),['bad.secret'])

    def test_freeze_requires_ancestor_contract(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); subprocess.run(['git','init'],cwd=p,capture_output=True)
            subprocess.run(['git','config','user.email','test@example.invalid'],cwd=p)
            subprocess.run(['git','config','user.name','Test'],cwd=p)
            (p/'x').write_text('x'); subprocess.run(['git','add','.'],cwd=p); subprocess.run(['git','commit','-m','base'],cwd=p,capture_output=True)
            subprocess.run(['git','branch','-M','main'],cwd=p,check=True,capture_output=True)
            head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()
            self.assertEqual(freeze_check(p,head),[])
            self.assertEqual(
                freeze_check(p,head,expected_head=head,expected_branch='main',expected_worktree=p),
                [],
            )
            self.assertTrue(freeze_check(p,'deadbeef'))
            self.assertTrue(freeze_check(p,head,expected_branch='wrong'))
            self.assertTrue(freeze_check(p,head,expected_worktree=Path(d)/'other'))

    def test_freeze_check_surfaces_unverified_instead_of_a_third_semantic(self):
        import json

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            subprocess.run(['git', 'init', '-q'], cwd=p, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=p, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=p, check=True)
            (p / 'implement-plan.md').write_text('plan\n', encoding='utf-8')
            sheet = p / 'task.md'
            sheet.write_text(
                '<!-- Task ID: freeze-task -->\n```pipeline-contract\n'
                + json.dumps({
                    'schema': 2, 'task_id': 'freeze-task', 'task_type': 'prerequisite',
                    'implement_plan': {'path': 'implement-plan.md'},
                    'allowed_paths': ['src/**'], 'forbidden_paths': [],
                    'operations': [{'id': 'op', 'kind': 'validate', 'scope': 'task', 'acceptance_tests': ['acceptance-test-1']}],
                    'chain': {name: ['src/app.py'] for name in ('entry', 'interaction', 'application', 'domain', 'persistence', 'readback', 'recovery')},
                    'dependencies': [],
                    'acceptance_tests': [{'id': 'acceptance-test-1', 'evidence_level': 2, 'test_ref': 'tests/test_git_checks.py', 'command_ref': 'python -m unittest'}],
                    'required_evidence_levels': [2],
                })
                + '\n```\n',
                encoding='utf-8',
            )
            subprocess.run(['git', 'add', '.'], cwd=p, check=True)
            subprocess.run(['git', 'commit', '-qm', 'freeze'], cwd=p, check=True)
            head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=p, text=True).strip()
            unverified = []
            errors = freeze_check(p, head, task_sheet=sheet, unverified=unverified)
            self.assertEqual([error for error in errors if 'implement-plan' in error], [], errors)
            self.assertTrue(any('unrecorded' in item for item in unverified), unverified)
            self.assertTrue((p / '.pipeline' / 'freeze-task' / 'implement-plan.json').is_file())
            unverified_again = []
            freeze_check(p, head, task_sheet=sheet, unverified=unverified_again)
            self.assertEqual(unverified_again, [])

    def test_absolute_scope_pattern_matches_repository_path(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); subprocess.run(['git','init'],cwd=p,capture_output=True)
            (p/'ok.txt').write_text('x')
            absolute_pattern = str((p/'ok.txt')).replace('\\\\','/')
            self.assertEqual(scope_check(p,[absolute_pattern],[]),[])

    def test_generated_metrics_are_not_scope_drift(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); subprocess.run(['git','init'],cwd=p,capture_output=True)
            metrics = p / '.pipeline' / 'metrics'
            metrics.mkdir(parents=True)
            (metrics / 'event.json').write_text('{}')
            self.assertEqual(scope_check(p,['src/**'],[]),[])

    def test_forbidden_metrics_pattern_still_wins(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); subprocess.run(['git','init'],cwd=p,capture_output=True)
            metrics = p / '.pipeline' / 'metrics'
            metrics.mkdir(parents=True)
            (metrics / 'event.json').write_text('{}')
            self.assertEqual(scope_check(p,['src/**'],['.pipeline/metrics/**']), ['.pipeline/metrics/event.json'])

    def test_canonical_metrics_are_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); subprocess.run(['git','init'],cwd=p,capture_output=True)
            metrics = p / '.pipeline' / 'metrics'
            metrics.mkdir(parents=True)
            (metrics / 'event.json').write_text('{}')
            self.assertEqual(scope_check(p,['src/**'],[]),[])

    def test_legacy_metrics_are_migrated_before_scope_check(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); subprocess.run(['git','init'],cwd=p,capture_output=True)
            metrics = p / '.workflow' / 'metrics'
            metrics.mkdir(parents=True)
            (metrics / 'event.json').write_text('{}')
            self.assertEqual(scope_check(p,['src/**'],[]),[])
            self.assertFalse((p / '.workflow').exists())
            self.assertTrue((p / '.pipeline' / 'metrics' / 'event.json').exists())


    def test_dispatch_scope_requires_registered_task_worktree_and_role_identity(self):
        from pipeline_tools.core import create_worktree_dispatch
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
            (root / 'implement-plan.md').write_text('plan\n')
            sheet = root / 'task.md'
            sheet.write_text('''<!-- Task ID: scope-task -->\n```pipeline-contract\n{"schema":2,"task_id":"scope-task","task_type":"prerequisite","implement_plan":{"path":"implement-plan.md"},"allowed_paths":["src/**"],"forbidden_paths":[],"operations":[{"id":"op","kind":"create","scope":"worktree","acceptance_tests":["acceptance-test-1"]}],"chain":{"entry":["cli"],"interaction":["cli"],"application":["app"],"domain":["domain"],"persistence":["db"],"readback":["app"],"recovery":["app"]},"dependencies":[],"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":2,"test_ref":"tests/test_git_checks.py","command_ref":"python -m unittest"}],"required_evidence_levels":[2]}\n```\n''')
            subprocess.run(['git', 'add', '.'], cwd=root, check=True); subprocess.run(['git', 'commit', '-qm', 'freeze'], cwd=root, check=True)
            head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
            result = create_worktree_dispatch(root, sheet, 'scope-task', 'scope-branch', head, role='reviewer')
            self.assertEqual(result['status'], 'pass')
            self.assertEqual(result['identity']['role'], 'reviewer')
            self.assertTrue(any('unrecorded' in item for item in result['unverified']), result)
            wrong = create_worktree_dispatch(root, sheet, 'scope-task', 'other-branch', head, role='bad')
            self.assertEqual(wrong['status'], 'blocked')
            self.assertIn('role', wrong['errors'][0])

    def test_tracked_metrics_are_workflow_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); subprocess.run(['git','init'],cwd=p,capture_output=True)
            subprocess.run(['git','config','user.email','test@example.invalid'],cwd=p)
            subprocess.run(['git','config','user.name','Test'],cwd=p)
            metrics = p / '.pipeline' / 'metrics'
            metrics.mkdir(parents=True)
            event = metrics / 'event.json'
            event.write_text('{}')
            subprocess.run(['git','add','.'],cwd=p,check=True,capture_output=True)
            subprocess.run(['git','commit','-m','metrics'],cwd=p,check=True,capture_output=True)
            event.write_text('{"changed":true}')
            self.assertEqual(scope_check(p,['src/**'],[]),[])

    def test_commit_history_evidence_path_guard(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); subprocess.run(['git', 'init', '-q'], cwd=p, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=p, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=p, check=True)
            (p / 'src').mkdir(); (p / 'src' / 'app.py').write_text('x')
            subprocess.run(['git', 'add', '.'], cwd=p, check=True); subprocess.run(['git', 'commit', '-qm', 'base'], cwd=p, check=True)
            evidence = p / '.pipeline' / 'demo'; evidence.mkdir(parents=True)
            (evidence / 'raw.log').write_text('raw')
            subprocess.run(['git', 'add', '.'], cwd=p, check=True); subprocess.run(['git', 'commit', '-qm', 'bad evidence'], cwd=p, check=True)
            (evidence / 'raw.log').unlink(); subprocess.run(['git', 'add', '-A'], cwd=p, check=True); subprocess.run(['git', 'commit', '-qm', 'delete evidence'], cwd=p, check=True)
            metrics = p / '.pipeline' / 'metrics'; metrics.mkdir(parents=True); (metrics / 'event.json').write_text('{}')
            subprocess.run(['git', 'add', '.'], cwd=p, check=True); subprocess.run(['git', 'commit', '-qm', 'metrics'], cwd=p, check=True)
            violations = commit_history_check(p, '.pipeline/demo')
            self.assertEqual(len(violations), 2)
            self.assertTrue(all('demo' in value for value in violations))

    def test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); subprocess.run(['git', 'init'], cwd=p, capture_output=True)
            metrics = p / '.pipeline' / 'metrics'
            metrics.mkdir(parents=True)
            (metrics / 'historical.json').write_text('{}')
            subprocess.run(['git', 'add', '.'], cwd=p, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-qm', 'historical metrics'], cwd=p, check=True)
            (metrics / 'repository-task.json').write_text('{}')
            (p / '.pipeline' / 'metrics-export.json').write_text('{}')
            (p / 'IDEA.md').write_text('preserve')
            self.assertEqual(
                scope_check(
                    p,
                    ['.pipeline/repository-evidence-hygiene/**'],
                    ['IDEA.md'],
                ),
                ['.pipeline/metrics-export.json', 'IDEA.md'],
            )

    def test_freeze_check_detects_task_sheet_change_after_freeze(self):
        import json

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            subprocess.run(['git', 'init', '-q'], cwd=p, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=p, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=p, check=True)
            (p / 'implement-plan.md').write_text('plan\n', encoding='utf-8')
            contract = {
                'schema': 3,
                'task_id': 'freeze-drift',
                'task_type': 'prerequisite',
                'project_type': 'service',
                'risk': 'medium',
                'implement_plan': {'path': 'implement-plan.md'},
                'allowed_paths': ['src/**'],
                'forbidden_paths': [],
                'non_goals': ['must not rewrite history'],
                'non_user_completion_reason': 'no user-facing surface',
                'operations': [{
                    'id': 'op', 'kind': 'validate', 'scope': 'project',
                    'resources': ['src/app.py'], 'resource_mode': 'single',
                    'acceptance_tests': ['acceptance-test-1'],
                }],
                'chain': {
                    name: {'not_applicable': True, 'reason': 'prerequisite task has no user-visible chain'}
                    for name in ('entry', 'interaction', 'application', 'domain', 'persistence', 'readback', 'recovery')
                },
                'dependencies': [],
                'acceptance_tests': [{
                    'id': 'acceptance-test-1', 'evidence_level': 2,
                    'test_ref': 'tests/test_git_checks.py: test_x',
                    'command_ref': 'python -m unittest',
                }],
                'required_evidence_levels': [2],
            }
            sheet = p / 'docs' / 'tasks' / 'freeze-drift.md'
            sheet.parent.mkdir(parents=True)
            sheet.write_text(
                '<!-- Task ID: freeze-drift -->\n```pipeline-contract\n'
                + json.dumps(contract) + '\n```\n',
                encoding='utf-8',
            )
            subprocess.run(['git', 'add', '.'], cwd=p, check=True)
            subprocess.run(['git', 'commit', '-qm', 'freeze'], cwd=p, check=True, capture_output=True)
            head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=p, text=True).strip()
            first = freeze_check(p, head, task_sheet=sheet)
            self.assertNotIn('task sheet changed after freeze', first, first)
            sheet.write_text(
                sheet.read_text(encoding='utf-8').replace('must not rewrite history', 'must not rewrite task history'),
                encoding='utf-8',
            )
            second = freeze_check(p, head, task_sheet=sheet)
            self.assertIn('task sheet changed after freeze', second, second)

if __name__=='__main__': unittest.main()
