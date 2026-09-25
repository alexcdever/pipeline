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
            self.assertEqual(repeated, finalized)
            recovered = planning_run_recover(root, "planning-test")
            self.assertEqual(recovered["status"], "pass")
            self.assertEqual(recovered["identity"]["requirements_sha256"], started["identity"]["requirements_sha256"])
            state = json.loads((root / ".pipeline" / "planning" / "planning-test" / "lifecycle.json").read_text())
            self.assertEqual(state["head"], started["identity"]["head"])
            self.assertEqual(state["root"], str(root.resolve()))

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
            (root / "implement-plan.md").write_text("drift\n", encoding="utf-8")
            recovered = planning_run_recover(root, "conflict-test")
            self.assertEqual(recovered["status"], "blocked")
            self.assertEqual(recovered["phase"], "conflict")
            duplicate = planning_run_start(root, "conflict-test")
            self.assertEqual(duplicate["status"], "blocked")
            self.assertNotEqual(conflict["identity"]["requirements_sha256"], recovered.get("identity", {}).get("requirements_sha256"))


if __name__ == "__main__":
    unittest.main()
