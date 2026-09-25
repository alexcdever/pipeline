import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.core import create_worktree_dispatch


class WorktreeDispatchIdentityTests(unittest.TestCase):
    def _repo(self, directory):
        root = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "implement-plan.md").write_text("stable plan\n", encoding="utf-8")
        sheet = root / "docs" / "tasks" / "dispatch.md"
        sheet.parent.mkdir(parents=True)
        sheet.write_text("""# dispatch\n<!-- Task ID: dispatch-task -->\n```pipeline-contract\n{"schema":2,"task_id":"dispatch-task","task_type":"prerequisite","implement_plan":{"path":"implement-plan.md"},"allowed_paths":["src/**"],"forbidden_paths":[],"operations":[{"id":"create","kind":"create","scope":"worktree","acceptance_tests":["acceptance-test-1"]}],"chain":{"entry":["pipeline_tools/__main__.py"],"interaction":["pipeline_tools/__main__.py"],"application":["pipeline_tools/core.py"],"domain":["pipeline_tools/core.py"],"persistence":[".worktrees/<task-id>/"],"readback":["pipeline_tools/__main__.py"],"recovery":["pipeline_tools/core.py"]},"dependencies":[],"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":3,"test_ref":"tests/test_worktree_dispatch_identity.py","command_ref":"python -m unittest"}],"required_evidence_levels":[3]}\n```\n""", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "freeze"], cwd=root, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        return root, sheet, head

    def test_create_and_verify_standard_worktree_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            before = subprocess.check_output(["git", "worktree", "list", "--porcelain"], cwd=root, text=True)
            result = create_worktree_dispatch(root, sheet, "dispatch-task", "dispatch-task-branch", head)
            after = subprocess.check_output(["git", "worktree", "list", "--porcelain"], cwd=root, text=True)
            self.assertEqual(result["status"], "pass", result)
            identity = result["identity"]
            self.assertEqual(identity["task_id"], "dispatch-task")
            self.assertEqual(identity["branch"], "dispatch-task-branch")
            self.assertEqual(identity["head"], head)
            self.assertEqual(Path(identity["worktree"]), root / ".worktrees" / "dispatch-task")
            self.assertNotEqual(before, after)
            self.assertEqual(subprocess.check_output(["git", "branch", "--show-current"], cwd=identity["worktree"], text=True).strip(), "dispatch-task-branch")
            self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=identity["worktree"], text=True).strip(), head)

    def test_identity_drift_and_duplicate_worktree_are_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            self.assertEqual(create_worktree_dispatch(root, sheet, "dispatch-task", "dispatch-task-branch", head)["status"], "pass")
            registered = subprocess.check_output(["git", "worktree", "list", "--porcelain"], cwd=root, text=True)
            for kwargs, category in [
                ({"baseline": "0" * 40}, "baseline"),
                ({"branch": "dispatch-task-branch"}, "conflict"),
                ({"task_sheet": root / "missing.md"}, "freeze"),
            ]:
                value = {"task_sheet": sheet, "branch": "other-branch", "baseline": head, **kwargs}
                result = create_worktree_dispatch(root, value["task_sheet"], "dispatch-task", value["branch"], value["baseline"])
                self.assertEqual(result["status"], "blocked")
                self.assertTrue(any(item["category"] == category for item in result["blockers"]), result)
            self.assertEqual(subprocess.check_output(["git", "worktree", "list", "--porcelain"], cwd=root, text=True), registered)

    def test_uncommitted_and_unfrozen_task_sheets_are_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            sheet.write_text(sheet.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
            result = create_worktree_dispatch(root, sheet, "dispatch-task", "new-branch", head)
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["blockers"][0]["category"], "freeze")
            self.assertFalse((root / ".worktrees" / "dispatch-task").exists())


if __name__ == "__main__":
    unittest.main()
