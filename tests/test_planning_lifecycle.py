import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.planning import (
    planning_run_finalize,
    planning_run_recover,
    planning_run_start,
    planning_run_transition,
)


class PlanningLifecycleTests(unittest.TestCase):
    def make_repo(self, root):
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "implement-plan.md").write_text("stable requirements\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=root, check=True)

    def test_run_identity_and_state_transitions_are_bound_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            started = planning_run_start(root, "planning-test")
            self.assertEqual(started["status"], "pass")
            self.assertEqual(planning_run_transition(root, "planning-test", "preflight")["status"], "pass")
            self.assertEqual(planning_run_transition(root, "planning-test", "planned")["status"], "pass")
            self.assertEqual(planning_run_transition(root, "planning-test", "generated")["status"], "pass")
            finalized = planning_run_finalize(root, "planning-test", success=True)
            self.assertEqual(finalized["status"], "finalized")
            repeated = planning_run_finalize(root, "planning-test", success=True)
            self.assertEqual(repeated["status"], "finalized")
            self.assertEqual(repeated["run_id"], finalized["run_id"])
            self.assertEqual(repeated["artifacts"], [])
            recovered = planning_run_recover(root, "planning-test")
            self.assertEqual(recovered["status"], "finalized")
            self.assertFalse((root / ".pipeline" / "planning" / "planning-test").exists())
            self.assertFalse((root / ".pipeline" / "planning").exists())

    def test_successful_finalize_cannot_bypass_generated_phase(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            planning_run_start(root, "ordered-finalize")
            for phase, next_phase in (("started", "preflight"), ("preflight", "planned"), ("planned", "generated")):
                result = planning_run_finalize(root, "ordered-finalize", success=True)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["phase"], phase)
                self.assertIn("generated", result["errors"][0])
                if next_phase != "generated":
                    self.assertEqual(planning_run_transition(root, "ordered-finalize", next_phase)["status"], "pass")
            self.assertEqual(planning_run_transition(root, "ordered-finalize", "generated")["status"], "pass")
            self.assertEqual(planning_run_finalize(root, "ordered-finalize", success=True)["status"], "finalized")

    def test_manual_finalize_requires_approval_but_automatic_finalize_does_not(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            planning_run_start(root, "automatic-finalize", approval_mode="automatic")
            for phase in ("preflight", "planned", "generated"):
                self.assertEqual(planning_run_transition(root, "automatic-finalize", phase)["status"], "pass")
            automatic = planning_run_finalize(root, "automatic-finalize", success=True)
            self.assertEqual(automatic["status"], "finalized")

            planning_run_start(root, "manual-finalize", approval_mode="manual")
            for phase in ("preflight", "planned", "generated"):
                self.assertEqual(planning_run_transition(root, "manual-finalize", phase)["status"], "pass")
            waiting = planning_run_finalize(root, "manual-finalize", success=True)
            self.assertEqual(waiting["status"], "blocked")
            self.assertIn("manual approval required", waiting["errors"])
            approved = planning_run_finalize(root, "manual-finalize", success=True, approval=True)
            self.assertEqual(approved["status"], "finalized")

    def test_failure_interruption_and_conflict_preserve_auditable_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            planning_run_start(root, "failed-test")
            interrupted = planning_run_transition(root, "failed-test", "preflight", status="interrupted", error="cancelled")
            self.assertEqual(interrupted["status"], "interrupted")
            audit = root / ".pipeline" / "planning" / "failed-test"
            self.assertTrue((audit / "lifecycle.json").is_file())
            conflict = planning_run_start(root, "conflict-test")
            (root / "goal.md").write_text("drift\n", encoding="utf-8")
            recovered = planning_run_recover(root, "conflict-test")
            self.assertEqual(recovered["status"], "blocked")
            self.assertEqual(recovered["phase"], "conflict")
            duplicate = planning_run_start(root, "conflict-test")
            self.assertEqual(duplicate["status"], "blocked")
            self.assertNotEqual(conflict["identity"]["requirements_sha256"], recovered.get("identity", {}).get("requirements_sha256"))

    def test_successful_finalize_writes_no_planning_products(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            planning_run_start(root, "no-products")
            for phase in ("preflight", "planned", "generated"):
                self.assertEqual(planning_run_transition(root, "no-products", phase)["status"], "pass")
            finalized = planning_run_finalize(root, "no-products", success=True)
            self.assertEqual(finalized["status"], "finalized")
            self.assertEqual(finalized["artifacts"], [])
            self.assertFalse((root / ".pipeline" / "planning" / "no-products").exists())
            recovered = planning_run_recover(root, "no-products")
            self.assertEqual(recovered["status"], "finalized")
            self.assertEqual(recovered["artifacts"], [])

    def test_failed_finalize_writes_lifecycle_and_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            planning_run_start(root, "failed-finalize")
            planning_run_transition(root, "failed-finalize", "preflight", status="failed", error="planning stopped")
            audit = root / ".pipeline" / "planning" / "failed-finalize"
            self.assertTrue((audit / "lifecycle.json").is_file())
            failed = planning_run_finalize(root, "failed-finalize", success=False)
            self.assertEqual(failed["status"], "failed")
            self.assertTrue((audit / "lifecycle.json").is_file())
            self.assertTrue((audit / "result.json").is_file())
            self.assertTrue(all(Path(path).is_file() for path in [audit / name for name in failed["artifacts"]]))


if __name__ == "__main__":
    unittest.main()
