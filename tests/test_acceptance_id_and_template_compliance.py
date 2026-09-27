import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline_tools.contract import validate_task
from scripts.validate_task_sheet import validate as validate_structure


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

    def test_all_task_sheets_validate_after_historical_schema_migration(self):
        from scripts.validate_task_sheet import validate

        task_sheets = sorted((ROOT / "docs/tasks").glob("*.md"))
        self.assertGreater(len(task_sheets), 1)
        for path in task_sheets:
            self.assertEqual(validate(path), [], path)
            text = path.read_text(encoding="utf-8")
            contract = re.search(r"```pipeline-contract\n(.*?)\n```", text, re.DOTALL)
            self.assertIsNotNone(contract, path)
            self.assertNotIn("<task-id>", contract.group(1))
            self.assertNotIn("<complete command>", contract.group(1))
            self.assertTrue("UNVERIFIED" in text or "未开始" in text or "已合并" in text, path)

    def _schema3_sheet(self, suffix):
        return (
            "# Task\n<!-- Task ID: demo -->\n```pipeline-contract\n"
            '{"schema":3,"task_id":"demo","task_type":"repair","project_type":"service",'
            '"risk":"medium","implement_plan":{"path":"implement-plan.md"},'
            '"allowed_paths":["src/**"],"forbidden_paths":[],'
            '"non_goals":["must not rewrite task history"],'
            '"operations":[{"id":"op","kind":"validate","scope":"project",'
            '"resources":["src/app.py"],"resource_mode":"single",'
            '"acceptance_tests":["acceptance-test-1"]}],'
            '"chain":{"entry":["src/app.py"],"interaction":["src/app.py"],'
            '"application":["src/app.py"],"domain":["src/app.py"],'
            '"persistence":["src/app.py"],"readback":["src/app.py"],'
            '"recovery":["src/app.py"]},'
            '"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":2,'
            '"test_ref":"tests/test_x.py: test_x","command_ref":"python -m unittest"}],'
            '"dependencies":[],"required_evidence_levels":[2]}'
            "\n```\n" + suffix
        )

    def _write_temp(self, text):
        path = ROOT / "tests" / ".tmp-schema3-compliance.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_schema3_sheet_rejects_process_record_heading(self):
        path = self._write_temp(self._schema3_sheet("## 任务级进度\n\n### 执行记录\n\n| a | b |\n"))
        try:
            errors = validate_structure(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertTrue(any("执行记录" in error for error in errors), errors)
        self.assertTrue(any("任务级进度" in error for error in errors), errors)

    def test_schema3_sheet_rejects_abbreviated_acceptance_id(self):
        text = self._schema3_sheet("## 验收测试\n\n### 验收测试1：demo\n").replace(
            '"id":"acceptance-test-1"', '"id":"AT1"'
        )
        path = self._write_temp(text)
        try:
            errors = validate_task(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertTrue(any("id" in error for error in errors), errors)

    def test_schema3_sheet_rejects_evidence_level_below_floor(self):
        text = self._schema3_sheet("## 验收测试\n\n### 验收测试1：demo\n").replace(
            '"evidence_level":2', '"evidence_level":1'
        )
        path = self._write_temp(text)
        try:
            errors = validate_task(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertTrue(any("floor" in error for error in errors), errors)

    def test_schema1_and_schema2_sheets_keep_today_outcome(self):
        for name in (
            "pipeline-tools-v1.md",
            "pipeline-evidence-lifecycle-migration.md",
            "acceptance-id-and-template-compliance.md",
            "task-worktree-dispatch-identity.md",
        ):
            path = ROOT / "docs/tasks" / name
            before = path.read_bytes()
            self.assertEqual(validate_task(path), [], name)
            self.assertEqual(validate_structure(path), [], name)
            self.assertEqual(path.read_bytes(), before, name)

    def test_template_emits_schema3_without_process_record_sections(self):
        text = (ROOT / "templates/task-sheet.md").read_text(encoding="utf-8")
        self.assertIn('"schema": 3', text)
        self.assertIn('"non_goals"', text)
        self.assertIn('"resource_mode"', text)
        for heading in ("## 任务级进度", "### 任务锚点", "### 验收台账", "### 执行记录", "### 最终结果"):
            self.assertNotIn(heading, text, heading)


if __name__ == "__main__":
    unittest.main()
