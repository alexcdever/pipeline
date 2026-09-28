import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from pipeline_tools.planning import compare_task_plan_contract


class TaskPlanContractConsistencyTests(unittest.TestCase):
    def _fixture(self, root):
        plan_path = root / "implement-plan.md"
        plan_path.write_text("stable plan\n", encoding="utf-8")
        digest = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        acceptance = [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_x.py", "command_ref": "python -m unittest"}]
        plan = {"schema": 1, "non_goals": ["本任务不扩展范围"], "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": [{"id": "op", "kind": "validate", "scope": "task", "resources": ["pipeline_tools/planning.py"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance, "tasks": [{"id": "demo", "type": "prerequisite", "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": ["op"], "chain": {name: ["not-applicable"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")}, "depends_on": []}]}
        contract = {"schema": 2, "task_id": "demo", "task_type": "prerequisite", "implement_plan": {"path": "implement-plan.md", "sha256": digest, "planning_run_id": "run-1"}, "allowed_paths": ["pipeline_tools/planning.py"], "forbidden_paths": ["implement-plan.md"], "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": [{key: value for key, value in operation.items() if key != "resource_mode"} for operation in plan["operations"]], "chain": {name: ["not-applicable"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")}, "acceptance_tests": acceptance, "dependencies": [], "required_evidence_levels": [2]}
        sheet = root / "task.md"
        sheet.write_text("<!-- Task ID: demo -->\n```pipeline-contract\n" + json.dumps(contract) + "\n```\n", encoding="utf-8")
        return plan, sheet, digest

    def test_matching_plan_and_schema2_sheet_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); plan, sheet, digest = self._fixture(root)
            result = compare_task_plan_contract(plan, sheet, root=root, expected_requirements_sha256=digest, expected_run_id="run-1")
            self.assertEqual(result["status"], "pass")

    def test_field_drift_is_reported_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); plan, sheet, digest = self._fixture(root)
            text = sheet.read_text(encoding="utf-8"); value = json.loads(text.split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0]); value["task_type"] = "repair"
            sheet.write_text(value_text(value), encoding="utf-8")
            result = compare_task_plan_contract(plan, sheet, root=root, expected_requirements_sha256=digest, expected_run_id="run-1")
            self.assertEqual(result["status"], "fail"); self.assertTrue(any(item["field"] == "task_type" for item in result["conflicts"]))

    def test_missing_implement_plan_is_rejected_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); plan, sheet, digest = self._fixture(root)
            (root / "implement-plan.md").unlink()
            result = compare_task_plan_contract(plan, sheet, root=root, expected_requirements_sha256=digest, expected_run_id="run-1")
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any(item["field"] == "implement_plan.path" for item in result["conflicts"]))

    def test_unreadable_implement_plan_is_rejected_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); plan, sheet, digest = self._fixture(root)
            plan_path = root / "implement-plan.md"
            plan_path.write_bytes(bytes([0xFF, 0xFE]))
            result = compare_task_plan_contract(plan, sheet, root=root, expected_requirements_sha256=digest, expected_run_id="run-1")
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any(item["field"] == "implement_plan.path" for item in result["conflicts"]))

    def test_duplicate_missing_and_unsafe_plan_inputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); plan, sheet, _digest = self._fixture(root)
            plan["tasks"].append(dict(plan["tasks"][0])); plan["tasks"][0]["resources"] = ["../escape"]
            result = compare_task_plan_contract(plan, sheet, root=root)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(result["conflicts"])


    def _shared_acceptance_fixture(self, root):
        names = ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")
        chain_value = {name: ["not-applicable"] for name in names}
        plan_path = root / "implement-plan.md"
        plan_path.write_text("stable plan\n", encoding="utf-8")
        digest = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        acceptance = [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_x.py", "command_ref": "python -m unittest"}]
        operations = [
            {"id": "op-a", "kind": "execute", "scope": "task", "resources": ["pipeline_tools/planning.py"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]},
            {"id": "op-b", "kind": "execute", "scope": "task", "resources": ["pipeline_tools/planning.py"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]},
        ]
        plan = {"schema": 1, "non_goals": ["本任务不扩展范围"], "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": operations, "acceptance_tests": acceptance,
                "tasks": [{"id": "demo", "type": "prerequisite", "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": ["op-a", "op-b"], "chain": chain_value, "depends_on": []}]}
        contract = {"schema": 2, "task_id": "demo", "task_type": "prerequisite", "implement_plan": {"path": "implement-plan.md", "sha256": digest, "planning_run_id": "run-1"},
                    "allowed_paths": ["pipeline_tools/planning.py"], "forbidden_paths": ["implement-plan.md"], "requirements": ["req"], "resources": ["pipeline_tools/planning.py"],
                    "operations": [{key: value for key, value in operation.items() if key != "resource_mode"} for operation in operations],
                    "chain": chain_value, "acceptance_tests": acceptance, "dependencies": [], "required_evidence_levels": [2]}
        sheet = root / "task.md"
        sheet.write_text(value_text(contract), encoding="utf-8")
        return plan, sheet, digest

    def test_shared_acceptance_test_across_operations_passes_contract_consistency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); plan, sheet, digest = self._shared_acceptance_fixture(root)
            result = compare_task_plan_contract(plan, sheet, root=root, expected_requirements_sha256=digest, expected_run_id="run-1")
            self.assertEqual(result["status"], "pass", result)
            self.assertFalse(any(item["field"] == "acceptance_tests" for item in result["conflicts"]), result["conflicts"])

    def test_acceptance_test_missing_from_top_level_still_conflicts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); plan, sheet, digest = self._shared_acceptance_fixture(root)
            plan["operations"][0]["acceptance_tests"] = ["acceptance-test-missing"]
            result = compare_task_plan_contract(plan, sheet, root=root, expected_requirements_sha256=digest, expected_run_id="run-1")
            self.assertEqual(result["status"], "fail")

    def _schema3_fixture(self, root):
        names = ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")
        plan_path = root / "implement-plan.md"
        plan_path.write_text("stable plan\n", encoding="utf-8")
        digest = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        chain_value = {name: {"not_applicable": True, "reason": "no reference"} for name in names}
        acceptance = [{"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_x.py", "command_ref": "python -m unittest"}]
        operation = {"id": "op", "kind": "validate", "scope": "task", "resources": ["pipeline_tools/planning.py"], "resource_mode": "single", "acceptance_tests": ["acceptance-test-1"]}
        plan = {"schema": 1, "non_goals": ["本任务不扩展范围"], "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": [operation], "acceptance_tests": acceptance,
                "tasks": [{"id": "demo", "type": "prerequisite", "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": ["op"], "chain": chain_value, "depends_on": []}]}
        contract = {"schema": 3, "task_id": "demo", "task_type": "prerequisite", "project_type": "service", "risk": "medium",
                    "implement_plan": {"path": "implement-plan.md", "sha256": digest, "planning_run_id": "run-1"},
                    "non_goals": ["本任务不扩展范围"], "allowed_paths": ["pipeline_tools/planning.py"], "forbidden_paths": ["implement-plan.md"],
                    "non_user_completion_reason": "prerequisite task produces enabling artifacts",
                    "requirements": ["req"], "resources": ["pipeline_tools/planning.py"],
                    "operations": [dict(operation, resource_mode="single")], "chain": chain_value,
                    "acceptance_tests": acceptance, "dependencies": [], "required_evidence_levels": [2]}
        sheet = root / "task.md"
        sheet.write_text(value_text(contract), encoding="utf-8")
        return plan, sheet, digest

    def test_schema3_non_goals_and_allowed_paths_are_compared(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, sheet, digest = self._schema3_fixture(root)
            matching = compare_task_plan_contract(plan, sheet, root=root, expected_requirements_sha256=digest, expected_run_id="run-1")
            self.assertEqual(matching["status"], "pass", matching)

            text = sheet.read_text(encoding="utf-8")
            value = json.loads(text.split("```pipeline-contract\n", 1)[1].split("\n```", 1)[0])
            value["non_goals"] = ["a different non-goal"]
            sheet.write_text(value_text(value), encoding="utf-8")
            drifted_non_goals = compare_task_plan_contract(plan, sheet, root=root, expected_requirements_sha256=digest, expected_run_id="run-1")
            self.assertEqual(drifted_non_goals["status"], "fail")
            self.assertTrue(any(item["field"] == "non_goals" for item in drifted_non_goals["conflicts"]), drifted_non_goals["conflicts"])

            value["non_goals"] = ["本任务不扩展范围"]
            value["allowed_paths"] = ["src/**"]
            sheet.write_text(value_text(value), encoding="utf-8")
            drifted_paths = compare_task_plan_contract(plan, sheet, root=root, expected_requirements_sha256=digest, expected_run_id="run-1")
            self.assertEqual(drifted_paths["status"], "fail")
            self.assertTrue(any(item["field"] == "allowed_paths" for item in drifted_paths["conflicts"]), drifted_paths["conflicts"])


def value_text(value):
    return "<!-- Task ID: demo -->\n```pipeline-contract\n" + json.dumps(value) + "\n```\n"


if __name__ == "__main__":
    unittest.main()


# pipeline-evidence
# {"schema":1,"task_id":"task-plan-contract-consistency","role":"executor","status":"pass"}
