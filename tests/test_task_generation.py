import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline_tools.contract import validate_task
from pipeline_tools.planning import _task_sheet_text, generate_task_sheets


CHAIN = {name: ["src/app.py"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")}


def make_inputs(root, task_ids=("task-a", "task-b")):
    (root / "implement-plan.md").write_text("stable implement plan\n", encoding="utf-8")
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "app.py").write_text("app\n", encoding="utf-8")
    acceptance = [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_task_generation.py: test", "command_ref": "python -m unittest tests.test_task_generation -v"}]
    project = {"schema": 1, "sources": [{"id": "source", "path": "implement-plan.md"}], "resources": [{"id": "resource", "path": "src/app.py"}], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance, "chain": CHAIN}
    requirements = {"schema": 1, "sources": [{"id": "source", "path": "implement-plan.md"}], "requirements": [{"id": "requirement", "source_refs": ["source"]}], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance}
    tasks = [{"id": task_id, "type": "prerequisite", "requirements": ["requirement"], "resources": ["resource"], "operations": ["operate"], "depends_on": [], "non_user_completion_reason": "enabling groundwork; no user-facing outcome"} for task_id in task_ids]
    plan = {"schema": 1, "non_goals": ["本任务不扩展用户可见范围"], "requirements": ["requirement"], "resources": ["resource"], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance, "tasks": tasks}
    return project, requirements, plan


def make_repo(root):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)


class TaskGenerationTests(unittest.TestCase):
    def run_generation(self, root, project, requirements, plan, run_id="run-1", expected=None):
        return generate_task_sheets(root, run_id, project, requirements, plan, expected_requirements_sha256=expected)

    def test_generate_valid_plan_creates_schema3_task_sheets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root)
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["task_ids"], ["task-a", "task-b"])
            self.assertEqual(result["planning_run_id"], "run-1")
            self.assertEqual(result["requirements_sha256"], hashlib.sha256((root / "implement-plan.md").read_bytes()).hexdigest())
            self.assertFalse((root / ".worktrees").exists())
            for task_id in result["task_ids"]:
                sheet = root / "docs" / "tasks" / f"{task_id}.md"
                self.assertEqual(validate_task(sheet), [])
                text = sheet.read_text(encoding="utf-8")
                self.assertIn('"schema": 3', text)
                self.assertIn('"planning_run_id": "run-1"', text)
                self.assertIn('"operations"', text)
                self.assertIn('"chain"', text)
                self.assertIn('"dependencies"', text)
                self.assertIn('"non_goals"', text)
                self.assertIn('"risk"', text)
                self.assertIn('"project_type"', text)
                self.assertIn('"resource_mode"', text)
                contract = json.loads(text.split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0])
                self.assertEqual(contract["non_goals"], ["本任务不扩展用户可见范围"])
                self.assertEqual(contract["risk"], "medium")
                self.assertEqual(contract["project_type"], "service")
                self.assertTrue(all(set(operation) >= {"resources", "resource_mode"} for operation in contract["operations"]))
                self.assertTrue(all("not_applicable" in reference for reference in contract["chain"].values()))

    def test_generated_sheet_round_trips_through_task_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("round-trip",))
            plan["risk"] = "high"
            plan["project_type"] = "web"
            plan["acceptance_tests"] = [{"id": "acceptance-test-1", "evidence_level": 3, "test_ref": "tests/test_task_generation.py: test", "command_ref": "python -m unittest tests.test_task_generation -v"}]
            project["acceptance_tests"] = plan["acceptance_tests"]
            requirements["acceptance_tests"] = plan["acceptance_tests"]
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="round-trip-run")
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "round-trip.md"
            self.assertEqual(validate_task(sheet), [])
            contract = json.loads(sheet.read_text(encoding="utf-8").split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0])
            self.assertEqual(contract["risk"], "high")
            self.assertEqual(contract["project_type"], "web")

    def test_generation_rejects_invalid_inputs_and_preserves_failure_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root)
            make_repo(root)
            del requirements["sources"]
            result = self.run_generation(root, project, requirements, plan, run_id="invalid-run")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("sources" in error for error in result["errors"]))
            audit = root / ".pipeline" / "planning" / "invalid-run" / "generation-result.json"
            self.assertTrue(audit.is_file())
            self.assertFalse((root / "docs" / "tasks").exists())

    def test_generation_is_fail_closed_for_existing_tasks_duplicate_ids_and_unsafe_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("task-a",))
            make_repo(root)
            existing = root / "docs" / "tasks" / "task-a.md"
            existing.parent.mkdir(parents=True)
            existing.write_bytes(b"sentinel")
            result = self.run_generation(root, project, requirements, plan, run_id="existing-run")
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(existing.read_bytes(), b"sentinel")

            project, requirements, plan = make_inputs(root, ("duplicate", "duplicate"))
            result = self.run_generation(root, project, requirements, plan, run_id="duplicate-run")
            self.assertEqual(result["status"], "blocked")
            self.assertIn("unique", " ".join(result["errors"]))

            project, requirements, plan = make_inputs(root, ("../escape",))
            result = self.run_generation(root, project, requirements, plan, run_id="unsafe-run")
            self.assertEqual(result["status"], "blocked")
            self.assertFalse((root.parent / "escape.md").exists())

    def test_generation_rolls_back_all_task_sheets_when_publication_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("rollback-a", "rollback-b"))
            make_repo(root)
            original_replace = os.replace
            calls = {"count": 0}

            def fail_on_second_replace(source, destination):
                calls["count"] += 1
                if calls["count"] == 2:
                    raise OSError("injected publication failure")
                return original_replace(source, destination)

            with patch("pipeline_tools.planning.os.replace", side_effect=fail_on_second_replace):
                result = self.run_generation(root, project, requirements, plan, run_id="rollback-run")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("OSError" in error for error in result["errors"]))
            self.assertFalse((root / "docs" / "tasks" / "rollback-a.md").exists())
            self.assertFalse((root / "docs" / "tasks" / "rollback-b.md").exists())
            self.assertFalse(list((root / "docs" / "tasks").glob("*.planning-tmp")))
            self.assertTrue((root / ".pipeline" / "planning" / "rollback-run" / "generation-result.json").is_file())

    def test_single_resource_operation_has_independent_coverage_and_readback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("single-task",))
            operation = {"id": "single-resource", "kind": "single-resource-operation", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}
            project["operations"] = [operation]
            requirements["operations"] = [operation]
            plan["operations"] = [operation]
            plan["tasks"][0]["operations"] = ["single-resource"]
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="single-run")
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "single-task.md"
            text = sheet.read_text(encoding="utf-8")
            self.assertIn('"kind": "single-resource-operation"', text)
            self.assertIn('"resources": [', text)
            self.assertEqual(validate_task(sheet), [])
            self.assertEqual(json.loads(text.split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0])["operations"][0]["kind"], "single-resource-operation")

    def test_batch_resource_operation_has_independent_coverage_and_readback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("batch-task",))
            (root / "src" / "db.py").write_text("db\\n", encoding="utf-8")
            project["resources"].append({"id": "resource-db", "path": "src/db.py"})
            operation = {"id": "batch-resources", "kind": "batch-resource-operation", "resources": ["resource", "resource-db"], "resource_mode": "batch", "acceptance_tests": ["acceptance-test-1"]}
            project["operations"] = [operation]
            requirements["operations"] = [operation]
            plan["resources"] = ["resource", "resource-db"]
            plan["operations"] = [operation]
            plan["tasks"][0].update({"resources": ["resource", "resource-db"], "operations": ["batch-resources"]})
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="batch-run")
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "batch-task.md"
            contract = json.loads(sheet.read_text(encoding="utf-8").split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0])
            self.assertEqual(contract["operations"][0]["kind"], "batch-resource-operation")
            self.assertEqual(contract["operations"][0]["resources"], ["resource", "resource-db"])
            self.assertEqual(validate_task(sheet), [])

    def test_generation_rejects_implement_plan_hash_drift_and_checks_plan_sheet_consistency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("consistent",))
            make_repo(root)
            expected = hashlib.sha256((root / "implement-plan.md").read_bytes()).hexdigest()
            (root / "implement-plan.md").write_text("drifted plan\n", encoding="utf-8")
            drift = self.run_generation(root, project, requirements, plan, run_id="drift-run", expected=expected)
            self.assertEqual(drift["status"], "blocked")
            self.assertTrue(any("hash" in error for error in drift["errors"]))
            self.assertFalse((root / "docs" / "tasks" / "consistent.md").exists())

            (root / "implement-plan.md").write_text("stable implement plan\n", encoding="utf-8")
            result = self.run_generation(root, project, requirements, plan, run_id="consistent-run")
            self.assertEqual(result["status"], "pass")
            sheet = root / "docs" / "tasks" / "consistent.md"
            self.assertEqual(validate_task(sheet), [])
            text = sheet.read_text(encoding="utf-8")
            self.assertIn('"task_id": "consistent"', text)
            self.assertIn('"id": "operate"', text)
            self.assertIn('"id": "acceptance-test-1"', text)
            self.assertIn('"dependencies": []', text)


    def test_generation_rejects_plan_without_non_goals_instead_of_inventing_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("no-non-goals",))
            del plan["non_goals"]
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="no-non-goals-run")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("non_goals" in error for error in result["errors"]), result["errors"])
            self.assertFalse((root / "docs" / "tasks" / "no-non-goals.md").exists())

    def test_generation_rejects_empty_non_goals_instead_of_inventing_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("empty-non-goals",))
            plan["non_goals"] = []
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="empty-non-goals-run")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("non_goals" in error for error in result["errors"]), result["errors"])

    def test_task_sheet_text_does_not_invent_non_goals(self):
        acceptance = [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_task_generation.py", "command_ref": "python -m unittest"}]
        task = {"id": "demo", "type": "prerequisite", "requirements": ["req"], "resources": ["resource"], "operations": ["operate"], "depends_on": []}
        plan = {"schema": 1, "requirements": ["requirement"], "resources": ["resource"], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance, "tasks": [task]}
        with self.assertRaises(ValueError) as raised:
            _task_sheet_text(task, plan, "0" * 64, "run-1")
        self.assertIn("non_goals", str(raised.exception))

    def test_task_sheet_text_does_not_invent_resources(self):
        acceptance = [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_task_generation.py", "command_ref": "python -m unittest"}]
        task = {"id": "demo", "type": "prerequisite", "requirements": ["req"], "resources": ["resource"], "operations": ["operate"], "depends_on": []}
        plan = {"schema": 1, "non_goals": ["explicit non-goal"], "requirements": ["requirement"], "resources": ["resource"], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance, "tasks": [task]}
        without_resources = dict(task)
        del without_resources["resources"]
        with self.assertRaises(ValueError) as raised:
            _task_sheet_text(without_resources, plan, "0" * 64, "run-1")
        self.assertIn("resources", str(raised.exception))

    def test_task_sheet_text_does_not_leak_unbound_acceptance_tests(self):
        acceptance = [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_task_generation.py", "command_ref": "python -m unittest"}]
        task = {"id": "demo", "type": "prerequisite", "requirements": ["req"], "resources": ["resource"], "operations": ["operate"], "depends_on": []}
        plan = {"schema": 1, "non_goals": ["explicit non-goal"], "requirements": ["requirement"], "resources": ["resource"], "operations": [{"id": "operate", "acceptance_tests": []}], "acceptance_tests": acceptance, "tasks": [task]}
        with self.assertRaises(ValueError) as raised:
            _task_sheet_text(task, plan, "0" * 64, "run-1")
        self.assertIn("acceptance", str(raised.exception))


    def test_prerequisite_non_user_completion_reason_comes_from_the_task_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("reason-task",))
            plan["tasks"][0]["non_user_completion_reason"] = "seeds the schema consumed by later tasks"
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="reason-run")
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "reason-task.md"
            contract = json.loads(sheet.read_text(encoding="utf-8").split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0])
            self.assertEqual(contract["non_user_completion_reason"], "seeds the schema consumed by later tasks")
            self.assertEqual(validate_task(sheet), [])

    def test_prerequisite_without_declared_reason_blocks_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("no-reason-task",))
            plan["tasks"][0].pop("non_user_completion_reason")
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="no-reason-run")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("non_user_completion_reason" in error for error in result["errors"]), result["errors"])
            self.assertFalse((root / "docs" / "tasks" / "no-reason-task.md").exists())

    def test_generated_contract_carries_assumptions_and_unknowns(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("facts-task",))
            assumptions = [{"id": "assumption-1", "source": "source"}]
            unknowns = [{"id": "unknown-1", "source": "source", "status": "non_blocking"}]
            project["assumptions"] = assumptions
            project["unknowns"] = unknowns
            make_repo(root)
            result = generate_task_sheets(
                root,
                "facts-run",
                project,
                requirements,
                plan,
                assumptions=assumptions,
                unknowns=unknowns,
            )
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "facts-task.md"
            contract = json.loads(sheet.read_text(encoding="utf-8").split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0])
            self.assertEqual(contract["assumptions"], assumptions)
            self.assertEqual(contract["unknowns"], unknowns)
            self.assertEqual(validate_task(sheet), [])


if __name__ == "__main__":
    unittest.main()
