import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.core import create_derived_dispatch


CONTRACT = {
    "schema": 2,
    "task_id": "parent-task",
    "task_type": "repair",
    "implement_plan": {"path": "implement-plan.md"},
    "allowed_paths": ["pipeline_tools/**"],
    "forbidden_paths": [".pipeline/**"],
    "operations": [{"id": "recover", "kind": "recover", "scope": "task", "acceptance_tests": ["acceptance-test-1"]}],
    "chain": {name: ["pipeline_tools/core.py"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")},
    "dependencies": [],
    "acceptance_tests": [{"id": "acceptance-test-1", "evidence_level": 3, "test_ref": "tests/test_derived_task_dispatch_recovery.py", "command_ref": "python -m unittest"}],
    "required_evidence_levels": [3],
}


class DerivedTaskDispatchRecoveryTests(unittest.TestCase):
    def _repo(self, directory):
        root = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "implement-plan.md").write_text("frozen plan\n", encoding="utf-8")
        sheet = root / "docs" / "tasks" / "parent-task.md"
        sheet.parent.mkdir(parents=True)
        sheet.write_text("# parent\n<!-- Task ID: parent-task -->\n```pipeline-contract\n" + json.dumps(CONTRACT) + "\n```\n", encoding="utf-8")
        (root / ".pipeline" / "parent-task").mkdir(parents=True)
        (root / ".pipeline" / "parent-task" / "executor-report.md").write_text("parent evidence\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "freeze parent"], cwd=root, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        return root, sheet, head

    def test_derived_task_binds_explicit_parent_commit_and_is_independent(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            parent_sheet_before = sheet.read_bytes()
            parent_evidence_before = (root / ".pipeline" / "parent-task" / "executor-report.md").read_bytes()
            result = create_derived_dispatch(root, sheet, "parent-task", "main", head, "child-task", "child-branch")
            self.assertEqual(result["status"], "pass", result)
            self.assertEqual(result["identity"]["baseline"], head)
            self.assertFalse(result["identity"]["parent_evidence_reused"])
            self.assertNotEqual(result["identity"]["task_id"], "parent-task")
            self.assertNotEqual(result["identity"]["branch"], "main")
            child = Path(result["worktree"])
            self.assertEqual(subprocess.check_output(["git", "branch", "--show-current"], cwd=child, text=True).strip(), "child-branch")
            self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD^"], cwd=child, text=True).strip(), head)
            subprocess.run(
                ["git", "ls-files", "--error-unmatch", "docs/tasks/child-task.md"],
                cwd=child, check=True, capture_output=True,
            )
            self.assertEqual(
                result["derived_from"],
                {"task_id": "parent-task", "commit": head, "branch": "main", "parent_task_type": "repair"},
            )
            self.assertTrue(Path(result["child_task_sheet"]).is_file())
            self.assertTrue(Path(result["evidence_dir"]).is_dir())
            self.assertEqual(sheet.read_bytes(), parent_sheet_before)
            self.assertEqual((root / ".pipeline" / "parent-task" / "executor-report.md").read_bytes(), parent_evidence_before)

    def test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            before = sheet.read_bytes()
            drifted = "0" * 40
            result = create_derived_dispatch(root, sheet, "parent-task", "main", drifted, "child-task", "child-branch")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any(item["category"] == "baseline" for item in result["blockers"]))
            self.assertFalse((root / ".worktrees" / "child-task").exists())
            self.assertEqual(sheet.read_bytes(), before)
            result = create_derived_dispatch(root, sheet, "parent-task", "main", head, "child-task-2", "child-branch-2")
            self.assertEqual(result["status"], "pass", result)
            child_evidence = Path(result["evidence_dir"])
            child_evidence.rmdir()
            self.assertTrue((root / ".pipeline" / "parent-task" / "executor-report.md").is_file())

    def test_child_sheet_is_committed_in_child_worktree_at_return(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            result = create_derived_dispatch(root, sheet, "parent-task", "main", head, "committed-child", "committed-child-branch")
            self.assertEqual(result["status"], "pass", result)
            child = Path(result["worktree"])
            tracked = subprocess.run(
                ["git", "ls-files", "--error-unmatch", "docs/tasks/committed-child.md"],
                cwd=child, capture_output=True, text=True,
            )
            self.assertEqual(tracked.returncode, 0, (tracked.stdout, tracked.stderr))
            self.assertNotEqual(
                subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=child, text=True).strip(),
                head,
            )
            self.assertEqual(
                subprocess.check_output(["git", "rev-parse", "HEAD^"], cwd=child, text=True).strip(),
                head,
            )

    def test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            before = sheet.read_bytes()
            first = create_derived_dispatch(root, sheet, "parent-task", "main", head, "parent-task-continuation-1", "continuation-branch", continuation=True)
            self.assertEqual(first["status"], "pass", first)
            second = create_derived_dispatch(root, sheet, "parent-task", "main", head, "parent-task-continuation-1", "continuation-branch", continuation=True)
            self.assertEqual(second["status"], "blocked")
            self.assertTrue(any(item["category"] in {"path", "conflict", "branch"} for item in second["blockers"]))
            self.assertEqual(sheet.read_bytes(), before)

    def test_cli_derived_create_returns_identity_and_blocks_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            environment = dict(__import__("os").environ)
            environment.update({"PYTHONPATH": str(Path(__file__).resolve().parent.parent), "PIPELINE_TOOLS_DISABLE_AUTO_METRICS": "1"})
            command = [
                "python", "-m", "pipeline_tools", "--format", "json", "dispatch", "derived-create",
                str(root), str(sheet), "--parent-task-id", "parent-task", "--parent-branch", "main",
                "--parent-commit", head, "--child-task-id", "cli-child", "--child-branch", "cli-child-branch",
            ]
            created = subprocess.run(command, cwd=root, env=environment, capture_output=True, text=True, check=False)
            self.assertEqual(created.returncode, 0, (created.stdout, created.stderr))
            value = json.loads(created.stdout)
            self.assertEqual(value["status"], "pass")
            self.assertEqual(value["identity"]["baseline"], head)
            self.assertEqual(value["identity"]["parent_evidence_reused"], False)
            self.assertTrue(Path(value["child_task_sheet"]).is_file())
            replay = subprocess.run(command, cwd=root, env=environment, capture_output=True, text=True, check=False)
            self.assertEqual(replay.returncode, 3, (replay.stdout, replay.stderr))
            blocked = json.loads(replay.stdout)
            self.assertEqual(blocked["status"], "blocked")
            self.assertTrue(blocked["blockers"])


    def test_child_creation_failure_rolls_back_worktree_and_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            # Pre-seed the child evidence directory inside the parent commit so
            # evidence.mkdir(exist_ok=False) raises after the worktree exists.
            seeded = root / ".pipeline" / "occupied-child" / "executor-report.md"
            seeded.parent.mkdir(parents=True)
            seeded.write_text("seeded\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "seed child evidence"], cwd=root, check=True)
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            before = subprocess.check_output(["git", "worktree", "list", "--porcelain"], cwd=root, text=True)

            result = create_derived_dispatch(
                root, sheet, "parent-task", "main", head, "occupied-child", "occupied-child-branch",
            )

            self.assertEqual(result["status"], "blocked", result)
            self.assertFalse((root / ".worktrees" / "occupied-child").exists())
            branches = subprocess.check_output(
                ["git", "branch", "--list", "occupied-child-branch"], cwd=root, text=True,
            ).strip()
            self.assertEqual(branches, "")
            after = subprocess.check_output(["git", "worktree", "list", "--porcelain"], cwd=root, text=True)
            self.assertEqual(len(after.splitlines()), len(before.splitlines()), after)

    def test_invalid_child_sheet_is_rejected_and_rolled_back(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            result = create_derived_dispatch(
                root, sheet, "parent-task", "main", head, "bad id", "bad-id-branch",
            )
            self.assertEqual(result["status"], "blocked", result)
            self.assertTrue(
                any(item["category"] == "contract" for item in result["blockers"]),
                result["blockers"],
            )
            self.assertTrue(any("not a valid contract" in error for error in result["errors"]), result["errors"])
            self.assertFalse((root / ".worktrees" / "bad id").exists())
            branches = subprocess.check_output(
                ["git", "branch", "--list", "bad-id-branch"], cwd=root, text=True,
            ).strip()
            self.assertEqual(branches, "")

    def test_worktree_add_failure_deletes_orphan_child_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            root, sheet, head = self._repo(directory)
            # `git worktree add -b` creates the branch first and the worktree
            # directory second. A regular file at the worktree root path makes
            # directory creation fail, so git exits non-zero with the child
            # branch already present.
            (root / ".worktrees").write_text("occupied\n", encoding="utf-8")
            result = create_derived_dispatch(
                root, sheet, "parent-task", "main", head, "failed-child", "failed-child-branch",
            )
            self.assertEqual(result["status"], "blocked", result)
            branch = subprocess.run(
                ["git", "rev-parse", "--verify", "refs/heads/failed-child-branch"],
                cwd=root, capture_output=True, text=True,
            )
            self.assertNotEqual(branch.returncode, 0, branch.stdout)
            self.assertFalse((root / ".worktrees" / "failed-child").exists())


if __name__ == "__main__":
    unittest.main()
