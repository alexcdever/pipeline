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
    (root / "docs" / "goal.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "goal.md").write_text("stable goal\n", encoding="utf-8")
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "app.py").write_text("app\n", encoding="utf-8")
    acceptance = [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_task_generation.py: test", "command_ref": "python -m unittest tests.test_task_generation -v"}]
    project = {"schema": 1, "sources": [{"id": "source", "path": "docs/goal.md"}], "facts": [{"id": "project-fact-1", "value": "src/app.py is the application entry resource"}], "resources": [{"id": "resource", "path": "src/app.py"}, {"id": "resource-tests", "path": "tests/test_task_generation.py"}], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance, "chain": CHAIN}
    requirements = {"schema": 1, "sources": [{"id": "source", "path": "docs/goal.md"}], "requirements": [{"id": "requirement", "source_refs": ["source"]}], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance}
    tasks = [{"id": task_id, "type": "prerequisite", "requirements": ["requirement"], "resources": ["resource", "resource-tests"], "operations": ["operate"], "depends_on": [], "non_user_completion_reason": "enabling groundwork; no user-facing outcome"} for task_id in task_ids]
    plan = {"schema": 1, "non_goals": ["本任务不扩展用户可见范围"], "requirements": ["requirement"], "resources": ["resource", "resource-tests"], "operations": [{"id": "operate", "resources": ["resource"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance, "tasks": tasks}
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
            self.assertEqual(result["requirements_sha256"], hashlib.sha256((root / "docs" / "goal.md").read_bytes()).hexdigest())
            self.assertFalse((root / ".worktrees").exists())
            for task_id in result["task_ids"]:
                sheet = root / "docs" / "tasks" / f"{task_id}.md"
                self.assertEqual(validate_task(sheet), [])
                text = sheet.read_text(encoding="utf-8")
                self.assertIn('"schema": 4', text)
                self.assertIn('"planning_run_id": "run-1"', text)
                self.assertIn('"operations"', text)
                self.assertIn('"chain"', text)
                self.assertIn('"dependencies"', text)
                self.assertIn('"non_goals"', text)
                self.assertIn('"risk"', text)
                self.assertIn('"project_type"', text)
                self.assertIn('"resource_mode"', text)
                for heading in ("## 事实/假设/未知", "## 设计与行为链路", "## 环境前置", "## 决策点"):
                    self.assertIn(heading, text)
                self.assertIn("project-fact-1", text)
                self.assertIn("src/app.py is the application entry resource", text)
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

    def test_generation_rejects_invalid_inputs_without_writing_failure_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root)
            make_repo(root)
            del requirements["sources"]
            result = self.run_generation(root, project, requirements, plan, run_id="invalid-run")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("sources" in error for error in result["errors"]))
            self.assertFalse((root / ".pipeline" / "planning").exists())
            self.assertFalse((root / "docs" / "tasks").exists())

    def test_generation_preflight_failure_leaves_no_planning_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root)
            make_repo(root)
            (root / "docs" / "goal.md").unlink()
            result = self.run_generation(root, project, requirements, plan, run_id="preflight-audit-run")
            self.assertEqual(result["status"], "blocked")
            self.assertFalse((root / ".pipeline" / "planning").exists())

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
            self.assertFalse((root / ".pipeline" / "planning").exists())

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
            plan["resources"] = ["resource", "resource-db", "resource-tests"]
            plan["operations"] = [operation]
            plan["tasks"][0].update({"resources": ["resource", "resource-db", "resource-tests"], "operations": ["batch-resources"]})
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="batch-run")
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "batch-task.md"
            contract = json.loads(sheet.read_text(encoding="utf-8").split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0])
            self.assertEqual(contract["operations"][0]["kind"], "batch-resource-operation")
            self.assertEqual(contract["operations"][0]["resources"], ["resource", "resource-db"])
            self.assertEqual(validate_task(sheet), [])

    def test_generation_rejects_goal_hash_drift_and_checks_plan_sheet_consistency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("consistent",))
            make_repo(root)
            expected = hashlib.sha256((root / "docs" / "goal.md").read_bytes()).hexdigest()
            (root / "docs" / "goal.md").write_text("drifted goal\n", encoding="utf-8")
            drift = self.run_generation(root, project, requirements, plan, run_id="drift-run", expected=expected)
            self.assertEqual(drift["status"], "blocked")
            self.assertTrue(any("hash" in error for error in drift["errors"]))
            self.assertFalse((root / "docs" / "tasks" / "consistent.md").exists())

            (root / "docs" / "goal.md").write_text("stable goal\n", encoding="utf-8")
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


    def test_generated_schema4_forbidden_paths_do_not_contradict_task_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("outside-task",))
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="outside-run")
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "outside-task.md"
            contract = json.loads(
                sheet.read_text(encoding="utf-8").split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0]
            )
            self.assertIn(".pipeline/** existing history", contract["forbidden_paths"])
            self.assertNotIn(".pipeline/** existing history", contract["allowed_paths"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("evidence-task",))
            plan["resources"] = [".pipeline/evidence-task/", "tests/test_task_generation.py"]
            plan["tasks"][0]["resources"] = [".pipeline/evidence-task/", "tests/test_task_generation.py"]
            plan["operations"][0]["resources"] = [".pipeline/evidence-task/"]
            project["resources"] = [{"id": ".pipeline/evidence-task/", "path": ".pipeline/evidence-task/"}, {"id": "resource-tests", "path": "tests/test_task_generation.py"}]
            (root / ".pipeline" / "evidence-task").mkdir(parents=True)
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="evidence-run")
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "evidence-task.md"
            contract = json.loads(
                sheet.read_text(encoding="utf-8").split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0]
            )
            self.assertEqual(contract["allowed_paths"], [".pipeline/evidence-task/", "tests/test_task_generation.py"])
            self.assertNotIn(".pipeline/** existing history", contract["forbidden_paths"])
            self.assertIn("docs/goal.md", contract["forbidden_paths"])
            self.assertIn("implement-plan.md", contract["forbidden_paths"])
            self.assertIn("IDEA.md", contract["forbidden_paths"])
            self.assertEqual(validate_task(sheet), [])

    def test_generate_task_sheets_blocks_out_of_scope_acceptance_test_ref(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("scope-task",))
            for collection in (project, requirements, plan):
                collection["acceptance_tests"] = [
                    dict(item, test_ref="tests/test_evidence.py: EvidenceTests.test_all_reports_require_machine_evidence")
                    for item in collection["acceptance_tests"]
                ]
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="scope-run")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("outside" in error for error in result["errors"]), result["errors"])
            self.assertFalse((root / "docs" / "tasks" / "scope-task.md").exists())

    def write_parent_sheet(self, root, task_id, task_type="prerequisite"):
        sheet = root / "docs" / "tasks" / f"{task_id}.md"
        sheet.parent.mkdir(parents=True, exist_ok=True)
        contract = {
            "schema": 4,
            "task_id": task_id,
            "task_type": task_type,
            "goal": {"path": "docs/goal.md", "sha256": "0" * 64, "planning_run_id": "parent-run"},
            "risk": "medium",
            "project_type": "service",
            "non_goals": ["parent sheet fixture"],
            "allowed_paths": ["src/app.py"],
            "forbidden_paths": ["goal.md"],
            "requirements": ["requirement"],
            "resources": ["src/app.py"],
            "operations": [{"id": "operate", "kind": "execute", "scope": "task", "resources": ["src/app.py"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}],
            "chain": {name: {"not_applicable": True, "reason": "fixture"} for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")},
            "acceptance_tests": [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_task_generation.py", "command_ref": "python -m unittest"}],
            "dependencies": [],
            "required_evidence_levels": [2],
        }
        if task_type == "prerequisite":
            contract["non_user_completion_reason"] = "parent fixture groundwork"
        sheet.write_text(
            f"# {task_id}\n\n<!-- Task ID: {task_id} -->\n\n```pipeline-contract\n"
            + json.dumps(contract, ensure_ascii=True, indent=2)
            + "\n```\n",
            encoding="utf-8",
        )
        return sheet

    def derived_task(self, task_id="derived-child", parent_task_id="parent-run", commit="a" * 40, branch="parent-run-branch", depends_on=()):
        return {
            "id": task_id,
            "type": "derived",
            "requirements": ["requirement"],
            "resources": ["resource", "resource-tests"],
            "operations": ["operate"],
            "depends_on": list(depends_on),
            "parent_task_id": parent_task_id,
            "derived_from": {"task_id": parent_task_id, "commit": commit, "branch": branch},
        }

    def parent_task(self, task_id="parent-task"):
        return {
            "id": task_id,
            "type": "prerequisite",
            "requirements": ["requirement"],
            "resources": ["resource", "resource-tests"],
            "operations": ["operate"],
            "depends_on": [],
            "non_user_completion_reason": "enabling groundwork; no user-facing outcome",
        }

    def contract_of(self, sheet):
        text = sheet.read_text(encoding="utf-8")
        return json.loads(text.split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0])

    def test_generator_emits_derived_from_for_derived_task(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("derived-child",))
            make_repo(root)
            self.write_parent_sheet(root, "parent-run")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "parent sheet"], cwd=root, check=True)
            plan["tasks"] = [self.derived_task()]
            result = self.run_generation(root, project, requirements, plan, run_id="derived-run")
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "derived-child.md"
            self.assertEqual(validate_task(sheet), [])
            contract = self.contract_of(sheet)
            self.assertEqual(
                contract["derived_from"],
                {
                    "task_id": "parent-run",
                    "commit": "a" * 40,
                    "branch": "parent-run-branch",
                    "parent_task_type": "prerequisite",
                },
            )

    def test_generator_output_for_non_derived_task_is_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("plain-task",))
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="plain-run")
            self.assertEqual(result["status"], "pass", result)
            contract = self.contract_of(root / "docs" / "tasks" / "plain-task.md")
            self.assertEqual(
                set(contract),
                {
                    "schema",
                    "task_id",
                    "task_type",
                    "goal",
                    "risk",
                    "project_type",
                    "non_goals",
                    "allowed_paths",
                    "forbidden_paths",
                    "requirements",
                    "resources",
                    "operations",
                    "chain",
                    "acceptance_tests",
                    "dependencies",
                    "required_evidence_levels",
                    "assumptions",
                    "unknowns",
                    "non_user_completion_reason",
                },
            )
            self.assertNotIn("derived_from", contract)

    def test_generate_task_sheets_emits_derived_sheet_for_same_run_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("parent-task",))
            plan["tasks"] = [self.parent_task(), self.derived_task("child-task", "parent-task", commit="b" * 40, branch="parent-task-branch", depends_on=("parent-task",))]
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="same-run")
            self.assertEqual(result["status"], "pass", result)
            self.assertEqual(result["task_ids"], ["parent-task", "child-task"])
            parent_sheet = root / "docs" / "tasks" / "parent-task.md"
            child_sheet = root / "docs" / "tasks" / "child-task.md"
            self.assertTrue(parent_sheet.is_file())
            self.assertTrue(child_sheet.is_file())
            self.assertEqual(validate_task(parent_sheet), [])
            self.assertEqual(validate_task(child_sheet), [])
            parent_contract = self.contract_of(parent_sheet)
            self.assertNotIn("derived_from", parent_contract)
            child_contract = self.contract_of(child_sheet)
            self.assertEqual(child_contract["dependencies"], ["parent-task"])
            self.assertEqual(child_contract["derived_from"]["task_id"], "parent-task")
            self.assertEqual(child_contract["derived_from"]["parent_task_type"], "prerequisite")
            self.assertEqual(child_contract["derived_from"]["commit"], "b" * 40)
            self.assertEqual(child_contract["derived_from"]["branch"], "parent-task-branch")

    def test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, requirements, plan = make_inputs(root, ("parent-task",))
            plan["tasks"] = [self.parent_task(), self.derived_task("child-task", "parent-task", depends_on=("parent-task",))]
            make_repo(root)
            existing = root / "docs" / "tasks" / "parent-task.md"
            existing.parent.mkdir(parents=True, exist_ok=True)
            existing.write_bytes(b"frozen parent sheet")
            result = self.run_generation(root, project, requirements, plan, run_id="existing-parent-run")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("already exists" in error for error in result["errors"]), result["errors"])
            self.assertEqual(existing.read_bytes(), b"frozen parent sheet")
            self.assertFalse((root / "docs" / "tasks" / "child-task.md").exists())
            self.assertFalse(list((root / "docs" / "tasks").glob("*.planning-tmp")))

    def pipeline_resource_inputs(self, root, resource_path, operation_kind=None, task_id="pipeline-task"):
        project, requirements, plan = make_inputs(root, (task_id,))
        plan["resources"] = [resource_path, "tests/test_task_generation.py"]
        plan["tasks"][0]["resources"] = [resource_path, "tests/test_task_generation.py"]
        operation = plan["operations"][0]
        operation["resources"] = [resource_path]
        if operation_kind is not None:
            operation["kind"] = operation_kind
        project["resources"] = [
            {"id": resource_path, "path": resource_path},
            {"id": "resource-tests", "path": "tests/test_task_generation.py"},
        ]
        return project, requirements, plan

    def test_task_generation_rejects_missing_pipeline_resource_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            resource = ".pipeline/pipeline-evidence/"
            project, requirements, plan = self.pipeline_resource_inputs(root, resource)
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="missing-pipeline-resource")
            self.assertEqual(result["status"], "blocked", result)
            self.assertTrue(
                any(resource in error and "does not exist" in error for error in result["errors"]),
                result["errors"],
            )
            self.assertFalse((root / "docs" / "tasks" / "pipeline-task.md").exists())

    def test_task_generation_rejects_delete_operation_without_deletable_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            resource = ".pipeline/pipeline-evidence/"
            project, requirements, plan = self.pipeline_resource_inputs(root, resource, operation_kind="delete-evidence")
            (root / ".pipeline" / "pipeline-evidence").mkdir(parents=True)
            (root / ".pipeline" / "pipeline-evidence" / "final-check.md").write_text("retained\n", encoding="utf-8")
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="delete-without-deletable")
            self.assertEqual(result["status"], "blocked", result)
            self.assertTrue(
                any("deletable files" in error for error in result["errors"]),
                result["errors"],
            )
            self.assertFalse((root / "docs" / "tasks" / "pipeline-task.md").exists())

    def test_task_generation_accepts_existing_pipeline_resource_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            resource = ".pipeline/pipeline-evidence/"
            project, requirements, plan = self.pipeline_resource_inputs(root, resource)
            (root / ".pipeline" / "pipeline-evidence").mkdir(parents=True)
            (root / ".pipeline" / "pipeline-evidence" / "raw.log").write_text("diagnostic\n", encoding="utf-8")
            make_repo(root)
            result = self.run_generation(root, project, requirements, plan, run_id="existing-pipeline-resource")
            self.assertEqual(result["status"], "pass", result)
            sheet = root / "docs" / "tasks" / "pipeline-task.md"
            self.assertEqual(validate_task(sheet), [])
            self.assertIn('".pipeline/pipeline-evidence/"', sheet.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
