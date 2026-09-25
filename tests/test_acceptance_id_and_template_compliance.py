import json
import re
import unittest
from pathlib import Path

from pipeline_tools.contract import validate_task


ROOT = Path(__file__).parents[1]
TASKS = (
    ROOT / "docs/tasks/pipeline-tools-v1.md",
    ROOT / "docs/tasks/pipeline-evidence-lifecycle-migration.md",
    ROOT / "docs/tasks/pipeline-tools-v1-continuation-1.md",
)


class AcceptanceIdAndTemplateComplianceTests(unittest.TestCase):
    def test_migrated_pipeline_task_sheets_use_complete_ids(self):
        for path in TASKS:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\bAT[0-9][A-Z0-9]*\b", text), path)
            self.assertEqual(validate_task(path), [], path)
            self.assertIn('"schema": 1', text)
            ids = re.findall(r'"id": "(acceptance-test-[a-z0-9.-]+)"', text)
            self.assertTrue(ids, path)
            self.assertEqual(len(ids), len(set(ids)), path)

    def test_schema2_rejects_abbreviated_operation_reference(self):
        source = (ROOT / "docs/tasks/acceptance-id-and-template-compliance.md").read_text(encoding="utf-8")
        contract = re.search(r"```pipeline-contract\n(.*?)\n```", source, re.DOTALL)
        self.assertIsNotNone(contract)
        value = json.loads(contract.group(1))
        value["operations"][0]["acceptance_tests"][0] = "AT1"
        mutated = source.replace(contract.group(1), json.dumps(value, indent=2), 1)
        path = ROOT / "tests" / ".tmp-acceptance-id-invalid.md"
        try:
            path.write_text(mutated, encoding="utf-8")
            errors = validate_task(path)
            self.assertTrue(any("full names" in error for error in errors))
        finally:
            path.unlink(missing_ok=True)

    def test_legacy_schema1_acceptance_id_remains_read_only_compatible(self):
        path = ROOT / "docs/tasks/pipeline-tools-v1.md"
        before = path.read_bytes()
        self.assertEqual(validate_task(path), [])
        self.assertEqual(path.read_bytes(), before)

    def test_template_and_evidence_example_use_complete_format(self):
        for path in (ROOT / "templates/task-sheet.md", ROOT / "templates/pipeline-evidence.json"):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\bAT[0-9][A-Z0-9]*\b", text), path)
            self.assertIn("acceptance-test-", text)

    def test_frozen_dispatch_acceptance_tests_remain_exact(self):
        expected = {
            "tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch",
            "tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history",
        }
        source = (ROOT / "docs/tasks/acceptance-id-and-template-compliance.md").read_text(encoding="utf-8")
        self.assertTrue(expected.issubset(set(re.findall(r'"test_ref": "([^"]+)"', source))))

    def test_frozen_contract_paths_exclude_metrics_and_forbidden_files(self):
        source = (ROOT / "docs/tasks/acceptance-id-and-template-compliance.md").read_text(encoding="utf-8")
        contract = re.search(r"```pipeline-contract\n(.*?)\n```", source, re.DOTALL)
        self.assertIsNotNone(contract)
        value = json.loads(contract.group(1))
        self.assertIn(".pipeline/metrics/**", value["forbidden_paths"])
        self.assertIn("implement-plan.md", value["forbidden_paths"])
        self.assertIn("IDEA.md", value["forbidden_paths"])

    def test_all_frozen_acceptance_ids_have_exact_test_references(self):
        source = (ROOT / "docs/tasks/acceptance-id-and-template-compliance.md").read_text(encoding="utf-8")
        contract = re.search(r"```pipeline-contract\n(.*?)\n```", source, re.DOTALL)
        self.assertIsNotNone(contract)
        value = json.loads(contract.group(1))
        tests = value["acceptance_tests"]
        self.assertEqual([item["id"] for item in tests], [f"acceptance-test-{index}" for index in range(1, 8)])
        for item in tests:
            self.assertNotIn("<", item["test_ref"])
            self.assertNotIn("<", item["command_ref"])
            self.assertRegex(item["id"], r"^acceptance-test-[a-z0-9.-]+$")


if __name__ == "__main__":
    unittest.main()
