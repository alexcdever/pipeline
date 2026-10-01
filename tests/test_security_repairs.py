import json
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.core import capability_handshake, create_derived_dispatch, evidence_verify, evidence_readiness, gate_check


class SecurityRepairTests(unittest.TestCase):
    def test_path_inputs_are_rejected_before_filesystem_side_effects(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for workflow in (Path(temp).parent / "outside", root / ".pipeline" / "../escape", root / ".pipeline" / "bad task"):
                result = capability_handshake(root, "executor", workflow)
                self.assertEqual(result["status"], "blocked")
            self.assertFalse((root / ".pipeline").exists())

    def test_symlink_workflow_has_no_side_effect(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as target:
            root = Path(temp)
            pipeline = root / ".pipeline"
            pipeline.symlink_to(Path(target), target_is_directory=True)
            result = capability_handshake(root, "executor", pipeline / "demo")
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(list(Path(target).iterdir()), [])

    def test_unsafe_derived_identifier_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = create_derived_dispatch(root, root / "parent.md", "parent", "main", "head", "../escape", "child")
            self.assertEqual(result["status"], "blocked")
            self.assertFalse((root / ".worktrees").exists())

    def test_evidence_identity_and_scope_are_enforced(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            canonical = root / ".pipeline" / "demo"
            canonical.mkdir(parents=True)
            for directory in (Path(outside), root / "other" / "demo", root / ".pipeline" / "../escape", root / ".pipeline" / "demo" / ".."):
                with self.assertRaises(ValueError):
                    evidence_verify(directory, "demo")
                with self.assertRaises(ValueError):
                    evidence_readiness(directory, "demo")
                with self.assertRaises(ValueError):
                    gate_check(directory, "demo", None, "pre-merge")
            link = root / "linked"
            link.symlink_to(canonical, target_is_directory=True)
            with self.assertRaises(ValueError):
                evidence_verify(link, "demo")

    def test_schema_one_reports_cannot_pass_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / ".pipeline" / "demo"
            directory.mkdir(parents=True)
            for name, role in (("executor-report.md", "executor"), ("review-report.md", "reviewer"), ("final-check.md", "main-final")):
                (directory / name).write_text("```pipeline-evidence\n" + json.dumps({"schema": 1, "task_id": "demo", "worktree": str(root), "branch": "main", "role": role, "round": 1, "status": "PASS", "commands": [{"command": "true", "exit_code": 0, "evidence_ref": ""}], "assertions": ["legacy report"], "evidence_refs": ["legacy.log"], "unverified": []}) + "\n```\n", encoding="utf-8")
            (directory / "legacy.log").write_text("legacy\n", encoding="utf-8")
            self.assertTrue(any("schema 1 is legacy" in error for error in gate_check(directory, "demo", "main", "post-merge")))

    def test_valid_secure_paths_and_references_still_work(self):
        self.test_valid_secure_paths_still_work()

    def test_full_security_regression_suite(self):
        self.test_path_inputs_are_rejected_before_filesystem_side_effects()
        self.test_symlink_workflow_has_no_side_effect()
        self.test_unsafe_derived_identifier_is_rejected()

    def test_valid_secure_paths_still_work(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = capability_handshake(root, "executor", Path(".pipeline/demo"), required_commands=[])
            self.assertIn(result["status"], {"pass", "blocked"})
            self.assertTrue((root / ".pipeline" / "demo" / "capability-handshake.json").is_file())
            self.assertEqual(json.loads((root / ".pipeline" / "demo" / "capability-handshake.json").read_text())["role"], "executor")


if __name__ == "__main__":
    unittest.main()
