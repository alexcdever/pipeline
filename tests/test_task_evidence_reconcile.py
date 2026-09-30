import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.reconcile import reconcile_task
from pipeline_tools.layout import LegacyPipelineLayoutError

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
            "schema": 2, "task_id": task_id, "worktree": worktree, "branch": branch, "head": "0" * 40, "generated_at": "2026-01-01T00:00:00+00:00",
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
        for filename, role in (("executor-result.json", "executor"), ("reviewer-result.json", "reviewer"), ("final-result.json", "main-final")):
            (directory / filename).write_text(json.dumps({
                "schema": 1, "task_id": task_id, "role": role, "status": "pass",
                "identity": {"head": "not-a-git-head"}, "acceptance": [{"id": "acceptance-test-reconcile", "status": "pass", "exit_code": 0, "evidence_refs": ["test.log"]}], "unverified": [],
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

    def test_update_is_always_blocked_and_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            before = sheet.read_bytes()
            value = reconcile_task(root, sheet, update=True)
            self.assertEqual(value["status"], "BLOCKED")
            self.assertFalse(value["updated"])
            self.assertTrue(any("deprecated" in error for error in value["errors"]))
            self.assertEqual(sheet.read_bytes(), before)

    def test_update_never_modifies_task_sheet_even_when_uncommitted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            before = sheet.read_bytes()
            value = reconcile_task(root, sheet, update=True)
            self.assertEqual(value["status"], "BLOCKED")
            self.assertFalse(value["updated"])
            self.assertTrue(any("deprecated" in error for error in value["errors"]))
            self.assertEqual(sheet.read_bytes(), before)

    def test_invalid_machine_results_block_reconcile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            evidence = self._evidence(root)
            (evidence / "reviewer-result.json").write_text(json.dumps({
                "schema": 1, "task_id": "demo", "role": "reviewer", "status": "pass",
                "acceptance": [], "unverified": [],
            }), encoding="utf-8")
            value = reconcile_task(root, sheet)
            self.assertNotEqual(value["status"], "PASS")
            self.assertTrue(any("reviewer-result.json" in error for error in value["errors"]))

    def test_reconcile_migrates_legacy_evidence_layout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            legacy = root / ".workflow" / "demo"
            legacy.mkdir(parents=True)
            (legacy / "marker.txt").write_text("legacy", encoding="utf-8")
            reconcile_task(root, sheet)
            self.assertFalse((root / ".workflow").exists())
            self.assertTrue((root / ".pipeline" / "demo" / "marker.txt").is_file())

    def test_reconcile_blocks_legacy_and_canonical_layout_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            (root / ".workflow" / "demo").mkdir(parents=True)
            (root / ".pipeline" / "demo").mkdir(parents=True)
            value = reconcile_task(root, sheet)
            self.assertEqual(value["status"], "BLOCKED")
            self.assertTrue(any("布局冲突" in error for error in value["errors"]))

    def test_empty_reconcile_selection_is_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertNotEqual(reconcile_task(root, root / "docs" / "tasks" / "missing.md")["status"], "PASS")
            from pipeline_tools.reconcile import reconcile_tasks
            result = reconcile_tasks(root)
            self.assertEqual(result["status"], "blocked")
            self.assertNotEqual(result["exit_code"], 0)

    def test_old_head_and_worktree_are_blocked_against_current_git_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-qm", "base"], check=True)
            evidence = self._evidence(root)
            current = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            for report in ("executor-report.md", "review-report.md", "final-check.md"):
                lines = (evidence / report).read_text(encoding="utf-8").splitlines()
                value = json.loads(lines[2])
                value["head"] = "1" * 40
                value["worktree"] = str(root / "old-worktree")
                (evidence / report).write_text("report\n```pipeline-evidence\n" + json.dumps(value) + "\n```\n", encoding="utf-8")
            result = reconcile_task(root, sheet)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(any("current Git identity" in error for error in result["errors"]))
            self.assertNotEqual(current, "1" * 40)

    def test_post_merge_reverification_gap_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            self._evidence(root)
            result = reconcile_task(root, sheet)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(any("post-merge re-verification" in error for error in result["errors"]))

    def test_malformed_post_merge_cwd_is_blocked_without_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = self._sheet(root)
            evidence = self._evidence(root)
            report = json.loads((evidence / "final-check.md").read_text(encoding="utf-8").splitlines()[2])
            report["commands"] = [{"command": "test", "exit_code": 0, "cwd": {"__class__": "Path"}, "evidence_ref": "test.log"}]
            (evidence / "final-check.md").write_text("report\n```pipeline-evidence\n" + json.dumps(report) + "\n```\n", encoding="utf-8")
            result = reconcile_task(root, sheet)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(any("post-merge re-verification" in error for error in result["errors"]))

    def test_cli_reconcile_returns_machine_result_and_does_not_write_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._sheet(root)
            result = run_cli(["--format", "json", "evidence", "reconcile", str(root), "--task-id", "demo"], root)
            self.assertEqual(result.returncode, 3, result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["command"], "evidence.reconcile")
            self.assertEqual(value["status"], "blocked")
            self.assertIn(value["tasks"][0]["status"], {"UNVERIFIED", "BLOCKED"})
            self.assertFalse((root / ".pipeline" / "metrics").exists())


if __name__ == "__main__":
    unittest.main()
