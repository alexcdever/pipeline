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
        plan = {"schema": 1, "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": [{"id": "op", "kind": "validate", "scope": "task", "acceptance_tests": ["acceptance-test-1"]}], "acceptance_tests": acceptance, "tasks": [{"id": "demo", "type": "prerequisite", "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": ["op"], "chain": {name: ["not-applicable"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")}, "depends_on": []}]}
        contract = {"schema": 2, "task_id": "demo", "task_type": "prerequisite", "implement_plan": {"path": "implement-plan.md", "sha256": digest, "planning_run_id": "run-1"}, "allowed_paths": ["pipeline_tools/planning.py"], "forbidden_paths": ["implement-plan.md"], "requirements": ["req"], "resources": ["pipeline_tools/planning.py"], "operations": plan["operations"], "chain": {name: ["not-applicable"] for name in ("entry", "interaction", "application", "domain", "persistence", "readback", "recovery")}, "acceptance_tests": acceptance, "dependencies": [], "required_evidence_levels": [2]}
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


def value_text(value):
    return "<!-- Task ID: demo -->\n```pipeline-contract\n" + json.dumps(value) + "\n```\n"


if __name__ == "__main__":
    unittest.main()


# pipeline-evidence
# {"schema":1,"task_id":"task-plan-contract-consistency","role":"executor","status":"pass"}
