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

    def test_automatic_approval_dispatches_without_explicit_approve(self):
        with tempfile.TemporaryDirectory() as directory:
            root, head = self.make_repo(directory)
            project, requirements, plan = self.inputs()
            ready = planning_to_dispatch(root, "automatic-run", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=head)
            self.assertEqual(ready["status"], "dispatch-ready", ready)
            self.assertNotIn("approval", [stage["name"] for stage in ready["stages"]])
            self.assertEqual(Path(ready["identity"]["worktree"]), root / ".worktrees" / "integration-task")

    def test_manual_approval_requires_explicit_approve_before_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root, head = self.make_repo(directory)
            project, requirements, plan = self.inputs()
            waiting = planning_to_dispatch(root, "manual-run", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=head, approval_mode="manual")
            self.assertEqual(waiting["status"], "blocked")
            self.assertIn("approval", waiting["stages"][-1]["name"])
            self.assertFalse((root / ".worktrees" / "integration-task").exists())
            with tempfile.TemporaryDirectory() as approved_directory:
                approved_root, approved_head = self.make_repo(approved_directory)
                ready = planning_to_dispatch(approved_root, "manual-approved-run", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=approved_head, approval_mode="manual", approved=True)
                self.assertEqual(ready["status"], "dispatch-ready", ready)
                self.assertEqual(len(list((approved_root / ".worktrees").iterdir())), 1)

    def test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts(self):
        for variant in ("same", "different", "hash-drift"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                root, head = self.make_repo(directory)
                project, requirements, plan = self.inputs()
                first = planning_to_dispatch(root, f"initial-{variant}", project, requirements, plan, task_id="integration-task", branch="initial-task-branch", baseline=head)
                self.assertEqual(first["status"], "dispatch-ready", first)
                sheet = root / "docs" / "tasks" / "integration-task.md"
                original = sheet.read_bytes()
                if variant == "different":
                    plan = json.loads(json.dumps(plan))
                    plan["tasks"][0]["type"] = "repair"
                elif variant == "hash-drift":
                    sheet.write_bytes(original + b"\nretained artifact\n")
                replay = planning_to_dispatch(root, f"replay-{variant}", project, requirements, plan, task_id="integration-task", branch="replay-task-branch", baseline=head)
                self.assertEqual(replay["status"], "blocked", replay)
                self.assertNotEqual(replay["status"], "dispatch-ready")
                self.assertTrue(replay["errors"])
                self.assertEqual(replay["stages"][-1]["name"], "task-generation")
                self.assertTrue(all(Path(path).is_file() for path in replay["artifacts"]))
                self.assertEqual(sheet.read_bytes(), original if variant != "hash-drift" else original + b"\nretained artifact\n")
                self.assertEqual(len(list((root / ".worktrees").iterdir())), 1)

    def test_dispatch_failure_does_not_create_or_replace_worktree(self):
        with tempfile.TemporaryDirectory() as directory:
            root, head = self.make_repo(directory)
            project, requirements, plan = self.inputs()
            first = planning_to_dispatch(root, "dispatch-failure-initial", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=head)
            self.assertEqual(first["status"], "dispatch-ready", first)
            worktree = root / ".worktrees" / "integration-task"
            retained = worktree / "retained.txt"
            retained.write_text("must remain\n", encoding="utf-8")
            before = retained.read_bytes()
            replay = planning_to_dispatch(root, "dispatch-failure-replay", project, requirements, plan, task_id="integration-task", branch="integration-task-branch", baseline=head)
            self.assertEqual(replay["status"], "blocked", replay)
            self.assertTrue(replay["errors"])
            self.assertTrue(any(stage["name"] == "task-generation" for stage in replay["stages"]))
            self.assertEqual(retained.read_bytes(), before)
            self.assertEqual(len(list((root / ".worktrees").iterdir())), 1)
            self.assertTrue(all(Path(path).is_file() for path in replay["artifacts"]))


if __name__ == "__main__":
    unittest.main()


# JSON input is intentionally assembled in Python so the end-to-end tests do not
# depend on a product fixture outside the temporary Git repository.
json.dumps({})
