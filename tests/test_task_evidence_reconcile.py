import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.reconcile import reconcile_task

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run_cli(args, cwd):
    env = {**os.environ, "PIPELINE_TOOLS_DISABLE_AUTO_METRICS": "1", "PYTHONPATH": str(ROOT)}
    return subprocess.run([PY, "-m", "pipeline_tools", *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=60)


class TaskEvidenceReconcileTests(unittest.TestCase):
    def _sheet(self, root, task_id="demo"):
        path = root / "docs" / "tasks" / f"{task_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# {task_id}\n<!-- Task ID: {task_id} -->\n\n### 最终结果\n- 状态：未验证\n\n"
            "```pipeline-contract\n" + json.dumps({
                "schema": 2, "task_id": task_id, "task_type": "repair",
                "implement_plan": {"path": "implement-plan.md"},
                "allowed_paths": ["pipeline_tools/**", "tests/**", "docs/tasks/**"],
                "forbidden_paths": ["implement-plan.md", "IDEA.md", ".pipeline/**"],
                "operations": [{"id": "reconcile", "kind": "repair", "scope": "evidence", "acceptance_tests": ["acceptance-test-reconcile"]}],
                "chain": {name: ["pipeline_tools/core.py"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")},
                "dependencies": [], "required_evidence_levels": [1],
                "acceptance_tests": [{"id": "acceptance-test-reconcile", "evidence_level": 1, "test_ref": "tests/test_task_evidence_reconcile.py", "command_ref": "python -m unittest tests.test_task_evidence_reconcile"}],
            }, ensure_ascii=True) + "\n```\n", encoding="utf-8")
        return path

    def _report(self, role, task_id="demo", branch="demo-branch", worktree=".worktrees/demo"):
        return "report\n```pipeline-evidence\n" + json.dumps({
            "schema": 1, "task_id": task_id, "worktree": worktree, "branch": branch,
            "role": role, "round": 1, "status": "PASS",
            "commands": [{"command": "python -m unittest", "exit_code": 0, "evidence_ref": "test.log"}],
            "assertions": ["direct evidence is present"], "evidence_refs": ["test.log"], "unverified": [],
        }) + "\n```\n"

    def _evidence(self, root, task_id="demo", conflicting_branch=None):
        directory = root / ".pipeline" / task_id
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "test.log").write_text("direct test output\n", encoding="utf-8")
        for filename, role in (("executor-report.md", "executor"), ("review-report.md", "reviewer"), ("final-check.md", "main-final")):
            branch = conflicting_branch if filename == "review-report.md" else "demo-branch"
            (directory / filename).write_text(self._report(role, branch=branch), encoding="utf-8")
        (directory / "final-result.json").write_text(json.dumps({
            "schema": 1, "task_id": task_id, "role": "main-final", "status": "pass",
            "identity": {"head": "not-a-git-head"}, "acceptance": [], "unverified": [],
        }), encoding="utf-8")
        return directory

    def test_missing_evidence_is_unverified_or_blocked_without_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            value = reconcile_task(root, sheet)
            self.assertIn(value["status"], {"UNVERIFIED", "BLOCKED"})
            self.assertNotEqual(value["status"], "PASS")
            self.assertEqual(value["readiness"], "not_ready")
            self.assertFalse(value["updated"])

    def test_identity_conflict_is_blocked_and_does_not_claim_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            self._evidence(root, conflicting_branch="other-branch")
            value = reconcile_task(root, sheet)
            self.assertEqual(value["status"], "BLOCKED")
            self.assertIn("report identity conflict", value["errors"])
            self.assertIsNone(value["identity"]["branch"])

    def test_default_reconcile_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            before = sheet.read_bytes()
            reconcile_task(root, sheet)
            self.assertEqual(sheet.read_bytes(), before)

    def test_update_changes_only_task_status_section(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            before = sheet.read_text(encoding="utf-8")
            value = reconcile_task(root, sheet, update=True)
            after = sheet.read_text(encoding="utf-8")
            self.assertTrue(value["updated"])
            self.assertIn("### 机械对账（直接证据）", after)
            self.assertEqual(after.split("### 最终结果", 1)[0], before.split("### 最终结果", 1)[0])
            self.assertIn("pipeline-contract", after)

    def test_cli_reconcile_returns_machine_result_and_does_not_write_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._sheet(root)
            result = run_cli(["--format", "json", "evidence", "reconcile", str(root), "--task-id", "demo"], root)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["command"], "evidence.reconcile")
            self.assertIn(value["tasks"][0]["status"], {"UNVERIFIED", "BLOCKED"})
            self.assertFalse((root / ".pipeline" / "metrics").exists())


if __name__ == "__main__":
    unittest.main()
