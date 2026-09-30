import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class LifecycleCLITests(unittest.TestCase):
    def make_sheet(self, root):
        sheet = root / "docs" / "tasks" / "demo.md"
        sheet.parent.mkdir(parents=True)
        contract = {"schema": 4, "task_id": "demo", "task_type": "repair", "project_type": "service", "risk": "medium", "goal": {"path": "goal.md"}, "allowed_paths": ["src/**"], "forbidden_paths": [], "non_goals": ["fixture-only"], "operations": [{"id": "op-demo", "kind": "validate", "scope": "project", "resources": ["src/app.py"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "chain": {name: ["src/app.py"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")}, "acceptance_tests": [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_lifecycle_cli.py", "command_ref": "python -m unittest"}], "dependencies": [], "required_evidence_levels": [2], "assumptions": [], "unknowns": []}
        (root / "goal.md").write_text("fixture goal\n", encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("# fixture\n", encoding="utf-8")
        sheet.write_text("<!-- Task ID: demo -->\n```pipeline-contract\n" + json.dumps(contract) + "\n```\n", encoding="utf-8")
        return sheet


class LifecycleCLITests(LifecycleCLITests):
    def test_transition_and_event_require_and_forward_role(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_sheet(root)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-qm", "freeze"], check=True)
            command = [sys.executable, "-m", "pipeline_tools", "--format", "json", "lifecycle", "transition", str(root), "--task-id", "demo", "active", "--role", "main-agent"]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["state"], "active")
            event = [sys.executable, "-m", "pipeline_tools", "--format", "json", "lifecycle", "event", str(root), "--task-id", "demo", "note", "--role", "reviewer"]
            denied = subprocess.run(event, capture_output=True, text=True)
            self.assertEqual(denied.returncode, 3)
            self.assertEqual(json.loads(denied.stdout)["status"], "blocked")

    def test_json_cli_configuration_errors_are_enveloped(self):
        invalid_id = subprocess.run([sys.executable, "-m", "pipeline_tools", "--format", "json", "lifecycle", "inspect", ".", "--task-id", "bad/id"], capture_output=True, text=True)
        self.assertEqual(invalid_id.returncode, 2)
        self.assertEqual(json.loads(invalid_id.stdout)["status"], "config")
        invalid_data = subprocess.run([sys.executable, "-m", "pipeline_tools", "--format", "json", "lifecycle", "event", ".", "--task-id", "demo", "note", "--role", "main-agent", "--data", "not-json"], capture_output=True, text=True)
        self.assertEqual(invalid_data.returncode, 2)
        envelope = json.loads(invalid_data.stdout)
        self.assertEqual(envelope["status"], "config")
        self.assertIn("errors", envelope)


if __name__ == "__main__":
    unittest.main()
