import json
import re
import subprocess
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

    def test_references_document_one_status_vocabulary(self):
        reference = (ROOT / "references/acceptance-evidence.md").read_text(encoding="utf-8")
        self.assertIn("归一", reference)
        self.assertIn("pass_with_conditions", reference)
        self.assertIn("pass", reference)
        self.assertIn("evidence_verify", reference)
        self.assertIn("verify_structured_result", reference)
        template = json.loads((ROOT / "templates/pipeline-evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(template["status"], "PASS")

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

    def _merged_into_head(self, text):
        """Treat a sheet whose merge commit is already in HEAD as a frozen historical record."""
        section = re.search(r"^### 最终结果$(.*?)(?=^## |\Z)", text, re.DOTALL | re.MULTILINE)
        if section is None:
            return False
        recorded = re.search(r"^- 合并提交：\s*(.+)$", section.group(1), re.MULTILINE)
        if recorded is None:
            return False
        for token in re.findall(r"[0-9a-f]{7,40}", recorded.group(1)):
            completed = subprocess.run(
                ["git", "merge-base", "--is-ancestor", token, "HEAD"],
                cwd=ROOT,
                capture_output=True,
            )
            if completed.returncode == 0:
                return True
        return False

    def test_unmerged_task_sheets_validate_after_historical_schema_migration(self):
        from scripts.validate_task_sheet import validate

        task_sheets = [
            path
            for path in sorted((ROOT / "docs" / "tasks").glob("*.md"))
            if not self._merged_into_head(path.read_text(encoding="utf-8"))
        ]
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

    def test_template_emits_schema4_without_process_record_sections(self):
        text = (ROOT / "templates/task-sheet.md").read_text(encoding="utf-8")
        self.assertIn('"schema": 4', text)
        self.assertIn('"goal"', text)
        self.assertIn('"non_goals"', text)
        self.assertIn('"resource_mode"', text)
        for heading in ("## 任务级进度", "### 任务锚点", "### 验收台账", "### 执行记录", "### 最终结果"):
            self.assertNotIn(heading, text, heading)

    def test_tracked_pipeline_evidence_contains_only_retained_names(self):
        from pipeline_tools.core import RETAINED_EVIDENCE_NAMES

        retained = set(RETAINED_EVIDENCE_NAMES)
        completed = subprocess.run(
            ["git", "ls-files", ".pipeline"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        tracked = [
            line.strip()
            for line in completed.stdout.splitlines()
            if line.strip() and not line.strip().startswith(".pipeline/metrics/")
        ]
        self.assertTrue(tracked)
        offenders = [path for path in tracked if Path(path).name not in retained]
        self.assertEqual(offenders, [], offenders)
        progress_logs = [path for path in tracked if path.endswith("-progress.jsonl")]
        self.assertEqual(progress_logs, [], progress_logs)

    def test_references_evidence_retention_contract_matches_forward_gate(self):
        from pipeline_tools.core import RETAINED_EVIDENCE_NAMES

        acceptance = (ROOT / "references/acceptance-evidence.md").read_text(encoding="utf-8")
        metrics = (ROOT / "references/metrics-contract.md").read_text(encoding="utf-8")
        for name in RETAINED_EVIDENCE_NAMES:
            self.assertIn(name, acceptance, name)
        self.assertIn("RETAINED_EVIDENCE_NAMES", acceptance)
        self.assertIn("--since", acceptance)
        self.assertIn("scope history", acceptance)
        for name in ("executor-report.md", "final-result.json", "finalization.json"):
            self.assertIn(name, metrics, name)
        self.assertIn("RETAINED_EVIDENCE_NAMES", metrics)
        self.assertIn("--since", metrics)

    def test_references_acceptance_evidence_documents_deletion_semantics(self):
        acceptance = (ROOT / "references/acceptance-evidence.md").read_text(encoding="utf-8")
        self.assertIn("commit_history_check", acceptance)
        self.assertIn("保留集", acceptance)
        self.assertIn("`A`", acceptance)
        self.assertIn("`D`", acceptance)
        deletion_rule = [line for line in acceptance.splitlines() if "`D`" in line and "保留集" in line]
        self.assertTrue(deletion_rule, acceptance)
        self.assertTrue(any("删除" in line for line in deletion_rule), deletion_rule)

    def test_validate_task_sheet_script_accepts_schema4_sheet(self):
        from scripts.validate_task_sheet import validate

        sheet = ROOT / "docs/tasks/evidence-retention-forward-gate.md"
        text = sheet.read_text(encoding="utf-8")
        self.assertIn('"schema": 4', text)
        self.assertEqual(validate(sheet), [])

        poisoned = self._write_temp(text + "\n## 任务级进度\n\n### 执行记录\n")
        try:
            errors = validate(poisoned)
        finally:
            poisoned.unlink(missing_ok=True)
        self.assertTrue(any("任务级进度" in error for error in errors), errors)

        contract = json.loads(
            re.search(r"```pipeline-contract\n(.*?)\n```", text, re.DOTALL).group(1)
        )
        self.assertNotIn("- 触发：", text)
        self.assertNotIn("- 断言：", text)
        for test in contract["acceptance_tests"]:
            self.assertIn(test["id"], text)

    def test_references_task_design_documents_test_ref_placement_and_position_rules(self):
        task_design = (ROOT / "references/task-design.md").read_text(encoding="utf-8")
        acceptance = (ROOT / "references/acceptance-evidence.md").read_text(encoding="utf-8")
        for text in (task_design, acceptance):
            self.assertIn("test_ref", text)
            self.assertIn("allowed_paths", text)
            self.assertIn("planning.py", text)
            self.assertIn("core.py", text)
        self.assertIn("`test_ref` 的位置规则", task_design)
        self.assertIn("类名.方法名", acceptance)
        self.assertIn("is outside the task's allowed paths", task_design)
        self.assertIn("absent", task_design)
        # 严格规则：规划期位置校验必须写成无条件约束。
        self.assertIn("`test_ref` 指名的文件必须落在任务的 `allowed_paths` 之内", task_design)
        self.assertIn("无条件", task_design)
        # 文档不得再保留任何收窄豁免措辞。
        self.assertNotIn("不主张归属", task_design)
        self.assertNotIn("提出归属主张", task_design)
        self.assertNotIn("位置校验不生效", task_design)

    def test_references_task_design_documents_planner_resource_checks(self):
        task_design = (ROOT / "references/task-design.md").read_text(encoding="utf-8")
        self.assertIn("规划期资源存在性规则", task_design)
        for needle in (
            "validate_task_plan",
            "root=root",
            "--root",
            "pipeline_tools/planning.py",
            ".pipeline/",
            "RETAINED_EVIDENCE_NAMES",
            "-progress.jsonl",
            "does not exist",
            "no deletable files",
            "机械",
            "白名单",
            "不会追溯地让已冻结的任务单失效",
        ):
            self.assertIn(needle, task_design, needle)

    def test_references_compat_and_migration_documents_known_items(self):
        reference = (ROOT / "references/compat-and-migration.md").read_text(encoding="utf-8")
        self.assertIn("已知项与后续跟进", reference)
        for needle in (
            "evidence-retention-forward-gate",
            "gate-deletion-semantics",
            "_shares_test_root",
            "metrics-contract.md",
            "generate-task-sheets",
            "assumptions",
            "unknowns",
            "潜在",
            "当前",
            "不要",
        ):
            self.assertIn(needle, reference, needle)

    def test_references_task_design_documents_derived_generation_support(self):
        task_design = (ROOT / "references/task-design.md").read_text(encoding="utf-8")
        self.assertIn("两条写入路径", task_design)
        for needle in (
            "derived_from",
            "_task_sheet_text",
            "create_derived_dispatch",
            "parent_task_type",
            "docs/tasks/<parent-id>.md",
            "validate_task_plan",
            "机械读取",
            "fail-closed",
            "root",
            "commit",
            "branch",
        ):
            self.assertIn(needle, task_design, needle)
        # 生成器路径照抄规划者声明的提交/分支，不自动推导。
        self.assertIn("工具照抄", task_design)
        # 跨 run 与同 run 两条来源都必须写明。
        self.assertIn("同一次 planning run", task_design)
        self.assertIn("HEAD", task_design)

    def test_references_metrics_contract_documents_test_isolation(self):
        contract = (ROOT / "references/metrics-contract.md").read_text(encoding="utf-8")
        self.assertIn("## 测试隔离规则", contract)
        for needle in (
            "临时 root",
            "非仓库目录",
            "`run_cli`",
            "`_git_root(Path.cwd())`",
            "`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`",
            "`git status --short .pipeline/metrics/`",
            "未追踪",
        ):
            self.assertIn(needle, contract, needle)
        # 隔离不变量与追踪状态无关：测试不得写入仓库的指标目录。
        self.assertIn("绝不能写入仓库的 `.pipeline/metrics/` 目录", contract)

    def test_references_metrics_contract_documents_tracking_is_developer_choice(self):
        contract = (ROOT / "references/metrics-contract.md").read_text(encoding="utf-8")
        self.assertIn("由项目开发者决定", contract)
        self.assertIn("技能既不要求也不禁止", contract)
        for stale in (
            "应纳入 Git 追踪",
            "不应加入项目 `.gitignore`",
            "加进 `.gitignore` 同样是违规",
        ):
            self.assertNotIn(stale, contract, stale)

    def test_references_compat_and_migration_documents_tracking_is_developer_choice(self):
        reference = (ROOT / "references/compat-and-migration.md").read_text(encoding="utf-8")
        self.assertIn("由项目开发者决定", reference)
        self.assertIn("技能既不要求也不禁止", reference)
        for stale in (
            "必须纳入 Git 追踪",
            "不应加入项目 `.gitignore`",
        ):
            self.assertNotIn(stale, reference, stale)

    def test_readme_documents_metrics_tracking_is_developer_choice(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("由项目开发者决定", readme)
        self.assertIn("技能既不要求也不禁止", readme)
        # 进度日志规则必须保留：过程记录不进入 Git。
        self.assertIn(".pipeline/*/*-progress.jsonl", readme)
        self.assertIn("不进入 Git", readme)
        # 每条断言缺失的字符串都曾是旧版 README 的原文，是真实回归守卫。
        for stale in (
            "纳入 Git 追踪",
            "应纳入 Git",
            "不要把该目录",
            "加入项目的",
        ):
            self.assertNotIn(stale, readme, stale)


if __name__ == "__main__":
    unittest.main()
