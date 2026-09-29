# planner-resource-validation — 执行报告

- task-id：planner-resource-validation
- worktree：`D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation`
- branch：planner-resource-validation
- 角色：executor
- 轮次：1
- 基线 HEAD：`5e9e754c6d3fde88f9f04348b1cfbec3b6745722`
- 关键命令：`python -m unittest discover -s tests`（303 passed 基线）

```pipeline-evidence
{
  "schema": 1,
  "task_id": "planner-resource-validation",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
  "branch": "planner-resource-validation",
  "role": "executor",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_missing_pipeline_resource_directory",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_delete_operation_without_deletable_files",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_accepts_existing_pipeline_resource_directory",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_planner_resource_checks",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_task_plan_validate_cli_forwards_root_for_derived_parent",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_known_items",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m pipeline_tools --format json task validate docs/tasks/planner-resource-validation.md",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "executor-report.md"
    }
  ],
  "assertions": [
    "planning.py 的 validate_task_plan 在传入 root 时对 .pipeline/<dir>/ 资源做机械存在性校验",
    "删除类 operation 的 .pipeline/<dir>/ 目录只含保留文件时报 blocked",
    "CLI planning task-plan-validate 转发 --root，使跨 run derived 父任务可被解析",
    "references/task-design.md 记录规划期资源存在性规则",
    "references/compat-and-migration.md 新增「已知项与后续跟进」小节",
    "全量测试 303 基线之上新增测试全绿"
  ],
  "evidence_refs": ["executor-report.md"],
  "unverified": [
    "全量测试的最终精确通过数（见本轮全量运行结果）",
    "未在真实产品仓库历史里回放旧任务单，仅验证了不追溯失效的设计约束"
  ],
  "identity": {
    "product_head": "5e9e754c6d3fde88f9f04348b1cfbec3b6745722"
  },
  "recommendation": "ready_for_review"
}
```

## 改动

1. `pipeline_tools/planning.py`
   - 新增 `DELETE_OPERATION_TOKENS`、`_is_delete_operation`、`_pipeline_resource_path`、`_deletable_evidence_files`、`_validate_pipeline_resource_existence`。
   - `validate_task_plan` 在 `root is not None` 时校验 `task.resources` 和每个 operation 的 `resources`；不硬编码目录名，只检查路径存在性与可删文件（保留集 `RETAINED_EVIDENCE_NAMES` 与 `*-progress.jsonl` 不计为可删）。
   - 未改变任何已有错误信息或返回类型。

2. `pipeline_tools/__main__.py:981` 附近
   - `task-plan-validate` 分支由 `validate_task_plan(value, project_facts, requirement_facts)` 改为 `validate_task_plan(value, project_facts, requirement_facts, root=args.root)`，与 `generate_task_sheets` 的 Python 入口一致。

3. `references/task-design.md`
   - 在「`test_ref` 的位置规则」前新增「规划期资源存在性规则」小节，说明两条规则、机械性与不追溯失效。

4. `references/compat-and-migration.md`
   - 新增「已知项与后续跟进」小节，登记 4 类已知项（两张已冻结单的 `**` 通配、`_shares_test_root` 疑似死代码、metrics-contract 删除方向缺口、`__main__.py` 其他转发缺口）。

5. 测试
   - `tests/test_task_generation.py`：新增 3 个验收测试。
   - `tests/test_cli.py`：新增 `test_task_plan_validate_cli_forwards_root_for_derived_parent`，真实走 CLI 并对比 Python API 结果。
   - `tests/test_acceptance_id_and_template_compliance.py`：新增 2 个文档契约测试。

## 未完成项

无。6 条验收测试全部通过；全量测试结果见最终运行。