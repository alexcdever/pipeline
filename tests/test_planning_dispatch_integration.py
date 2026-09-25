import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.planning import planning_to_dispatch


class PlanningDispatchIntegrationTests(unittest.TestCase):
    def make_repo(self, directory):
        root = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "implement-plan.md").write_text("frozen planning requirements\n", encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("app\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=root, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        return root, head

    def inputs(self, *, conflict=False):
        project = {
            "schema": 1,
            "sources": [{"id": "project-source", "path": "implement-plan.md"}],
            "resources": [{"id": "resource", "path": "src/app.py"}],
            "operations": [{"id": "operate", "acceptance_tests": ["acceptance-test-1"]}],
            "acceptance_tests": [{"id": "acceptance-test-1", "evidence_level": 3, "test_ref": "tests/test_planning_dispatch_integration.py", "command_ref": "python -m unittest"}],
            "chain": {name: ["src/app.py"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")},
        }
        if conflict:
            project["facts"] = [
                {"id": "same-a", "category": "project", "source": "project-source", "entity_id": "same", "value": "a"},
                {"id": "same-b", "category": "project", "source": "project-source", "entity_id": "same", "value": "b"},
            ]
        requirements = {
            "schema": 1,
            "sources": [{"id": "requirement-source", "path": "implement-plan.md"}],
            "requirements": [{"id": "requirement", "source_refs": ["requirement-source"]}],
            "operations": [{"id": "operate", "acceptance_tests": ["acceptance-test-1"]}],
            "acceptance_tests": project["acceptance_tests"],
        }
        plan = {
            "schema": 1,
            "requirements": ["requirement"],
            "resources": ["resource"],
            "operations": [{"id": "operate", "acceptance_tests": ["acceptance-test-1"]}],
            "acceptance_tests": project["acceptance_tests"],
            "tasks": [{"id": "integration-task", "type": "prerequisite", "requirements": ["requirement"], "resources": ["resource"], "operations": ["operate"], "depends_on": []}],
        }
        return project, requirements, plan

    def test_valid_planning_run_reaches_identity_verified_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root, head = self.make_repo(directory)
            project, requirements, plan = self.inputs()
            result = planning_to_dispatch(root, "integration-run", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=head, approved=True)
            self.assertEqual(result["status"], "dispatch-ready", result)
            self.assertEqual([stage["name"] for stage in result["stages"]], ["preflight", "facts-gate", "task-generation", "contract-consistency", "freeze", "dispatch-identity", "dispatch"])
            self.assertEqual(result["identity"]["task_id"], "integration-task")
            self.assertEqual(result["identity"]["branch"], "integration-task-branch")
            current_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            self.assertEqual(result["identity"]["head"], current_head)
            self.assertEqual(Path(result["identity"]["worktree"]), root / ".worktrees" / "integration-task")
            self.assertTrue((root / ".pipeline" / "planning" / "integration-run" / "dispatch.json").is_file())
            self.assertFalse(any("executor" in stage["name"] for stage in result["stages"]))

    def test_stage_failures_stop_downstream_and_preserve_artifacts(self):
        cases = [("preflight", {}, "preflight"), ("facts", {"conflict": True}, "facts-gate")]
        for label, options, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                root, head = self.make_repo(directory)
                project, requirements, plan = self.inputs(**options)
                if label == "preflight":
                    (root / "implement-plan.md").unlink()
                result = planning_to_dispatch(root, f"failed-{label}", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=head, approved=True)
                self.assertNotEqual(result["status"], "dispatch-ready")
                self.assertEqual(result["stages"][-1]["name"], expected)
                self.assertFalse(any(stage["name"] in {"task-generation", "dispatch-identity", "dispatch"} for stage in result["stages"]))
                self.assertTrue(all(Path(path).is_file() for path in result["artifacts"]))
                self.assertFalse((root / ".worktrees" / "integration-task").exists())

    def test_confirmation_policy_and_repeated_dispatch_are_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            root, head = self.make_repo(directory)
            project, requirements, plan = self.inputs()
            waiting = planning_to_dispatch(root, "manual-run", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=head, approval_mode="manual")
            self.assertEqual(waiting["status"], "blocked")
            self.assertIn("approval", waiting["stages"][-1]["name"])
            self.assertFalse((root / ".worktrees" / "integration-task").exists())
            ready = planning_to_dispatch(root, "automatic-run", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=head, approved=True)
            self.assertEqual(ready["status"], "dispatch-ready", ready)
            replay = planning_to_dispatch(root, "replay-run", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=head, approved=True)
            self.assertEqual(replay["status"], "blocked")
            self.assertTrue(any("duplicate" in error or "occupied" in error or "exists" in error for error in replay["errors"]))
            self.assertEqual(len(list((root / ".worktrees").iterdir())), 1)


if __name__ == "__main__":
    unittest.main()


# JSON input is intentionally assembled in Python so the end-to-end tests do not
# depend on a product fixture outside the temporary Git repository.
json.dumps({})
