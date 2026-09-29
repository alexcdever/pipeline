import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.task_lifecycle import append_event, inspect_task, list_tasks, resume_task, transition_task


class TaskLifecycleTests(unittest.TestCase):
    def make_repo(self, root):
        (root / "docs" / "tasks").mkdir(parents=True)
        contract = {
            "schema": 4, "task_id": "demo", "task_type": "repair", "project_type": "service", "risk": "medium",
            "goal": {"path": "goal.md"}, "allowed_paths": ["src/**"], "forbidden_paths": [], "non_goals": ["fixture-only"],
            "operations": [{"id": "op-demo", "kind": "validate", "scope": "project", "resources": ["src/app.py"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}],
            "chain": {name: ["src/app.py"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")},
            "acceptance_tests": [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_task_lifecycle.py", "command_ref": "python -m unittest"}],
            "dependencies": [], "required_evidence_levels": [2], "assumptions": [], "unknowns": [],
        }
        (root / "goal.md").write_text("fixture goal\n", encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("# fixture\n", encoding="utf-8")
        (root / "docs" / "tasks" / "demo.md").write_text(
            "<!-- Task ID: demo -->\n```pipeline-contract\n" + json.dumps(contract) + "\n```\n", encoding="utf-8"
        )

    def write_evidence(self, root):
        directory = root / ".pipeline" / "demo"
        directory.mkdir(parents=True, exist_ok=True)
        for role, report in (("executor", "executor-report.md"), ("reviewer", "review-report.md"), ("main-final", "final-check.md")):
            (directory / f"{role}.log").write_text("ok\n", encoding="utf-8")
            value = {"schema": 1, "task_id": "demo", "worktree": str(root), "branch": "main", "role": role, "round": 1, "status": "pass", "commands": [{"command": "python -m unittest", "exit_code": 0, "cwd": str(root), "evidence_ref": f"{role}.log"}], "assertions": ["fixture evidence is valid"], "evidence_refs": [f"{role}.log"], "unverified": []}
            (directory / report).write_text("```pipeline-evidence\n" + json.dumps(value) + "\n```\n", encoding="utf-8")
        for role in ("executor", "reviewer", "final"):
            value = {"schema": 1, "task_id": "demo", "role": role if role != "final" else "main-final", "status": "pass", "acceptance": [{"id": "acceptance-test-1", "status": "pass", "exit_code": 0, "evidence_refs": ["run.log"]}], "unverified": []}
            (directory / f"{role}-result.json").write_text(json.dumps(value), encoding="utf-8")

    def test_identity_transition_and_evidence_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-qm", "freeze"], check=True)
            self.assertEqual(resume_task(root, "demo")["status"], "blocked")
            self.assertEqual(transition_task(root, "demo", "active", role="main-agent")["state"], "active")
            self.assertEqual(transition_task(root, "demo", "ready", role="main-agent")["status"], "blocked")
            evidence = root / ".pipeline" / "demo" / "reviewer-result.json"
            evidence.write_text("{}", encoding="utf-8")
            self.assertEqual(transition_task(root, "demo", "review", role="main-agent")["state"], "review")
            self.assertEqual(transition_task(root, "demo", "ready", role="main-agent")["status"], "blocked")
            self.write_evidence(root)
            self.assertEqual(transition_task(root, "demo", "ready", role="main-agent")["state"], "ready")
            self.assertEqual(inspect_task(root, "demo")["identity"]["task_sheet_sha256"], inspect_task(root, "demo")["identity"]["task_sheet_sha256"])
            self.assertEqual(append_event(root, "demo", "note", role="main-agent")["status"], "pass")
            self.assertEqual(resume_task(root, "demo")["next_actions"], ["transition:abandoned", "transition:active", "transition:blocked", "transition:merged"])

    def test_illegal_transition_and_list(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-qm", "freeze"], check=True)
            self.assertEqual(transition_task(root, "demo", "active", role="main-agent")["state"], "active")
            self.assertEqual(list_tasks(root)["tasks"][0]["task_id"], "demo")
            self.assertEqual(transition_task(root, "demo", "merged", role="main-agent")["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
