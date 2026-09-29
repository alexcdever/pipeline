# planner-resource-validation：冻结任务单

<!-- Task ID: planner-resource-validation -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "planner-resource-validation",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "planner-resource-validation"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "\u4e0d\u5728\u672c\u4efb\u52a1\u91cc\u6e05\u7406\u6216\u5220\u9664 .pipeline/ \u4e0b\u4efb\u4f55\u5df2\u6709\u8bc1\u636e\u76ee\u5f55",
    "\u4e0d\u65b0\u589e\u89c4\u5212\u8005\u4e13\u7528\u7684\u679a\u4e3e\u5b50\u547d\u4ee4\uff1b\u8d44\u6e90\u5b58\u5728\u6027\u7531\u673a\u68b0\u6821\u9a8c\u4fdd\u8bc1",
    "\u4e0d\u4fee\u6539 goal.md\u3001IDEA.md\u3001implement-plan.md",
    "\u4e0d\u6539\u52a8 scope history \u7684 --since \u524d\u5411\u57fa\u7ebf\u8bed\u4e49",
    "\u4e0d\u4fee\u6539 docs/tasks/ \u4e0b\u4efb\u4f55\u5df2\u51bb\u7ed3\u4efb\u52a1\u5355",
    "\u4e0d\u5f31\u5316 contract.py \u5df2\u6709\u7684\u673a\u68b0\u95f8\u95e8",
    "\u4e0d\u628a\u6821\u9a8c\u5b9e\u73b0\u6210\u4f9d\u8d56\u67d0\u4e2a\u5177\u4f53\u76ee\u5f55\u540d\u7684\u786c\u7f16\u7801\u767d\u540d\u5355",
    "\u4e0d\u5728\u672c\u4efb\u52a1\u91cc\u91cd\u6821\u6216\u6539\u5199 evidence-retention-forward-gate \u4e0e gate-deletion-semantics \u4e24\u5f20\u5df2\u51bb\u7ed3\u5355\uff1b\u5b83\u4eec\u7684 ** \u901a\u914d\u53ea\u767b\u8bb0\u4e3a\u5df2\u77e5\u9879",
    "\u4e0d\u4fee\u590d task-plan-validate \u4e4b\u5916\u7684 __main__.py \u7f3a\u53e3\uff08\u4f8b\u5982 generate-task-sheets \u672a\u8f6c\u53d1 assumptions/unknowns\uff09\uff0c\u8fd9\u4e9b\u53ea\u767b\u8bb0\u4e3a\u5df2\u77e5\u9879"
  ],
  "allowed_paths": [
    "pipeline_tools/",
    "tests/",
    "references/",
    "pipeline_tools/__main__.py"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-planner-resource-existence",
    "requirement-planner-delete-target-verification",
    "requirement-planner-resource-docs-aligned",
    "requirement-task-plan-validate-cli-root-forwarded",
    "requirement-known-items-registered"
  ],
  "resources": [
    "pipeline_tools/",
    "tests/",
    "references/",
    "pipeline_tools/__main__.py"
  ],
  "operations": [
    {
      "id": "op-add-planner-resource-check",
      "kind": "add-planner-resource-mechanical-check",
      "scope": "planning",
      "resources": [
        "pipeline_tools/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-planner-rejects-missing-pipeline-directory",
        "acceptance-test-planner-rejects-delete-without-deletable-files",
        "acceptance-test-planner-accepts-existing-pipeline-directory"
      ]
    },
    {
      "id": "op-cover-planner-resource-check",
      "kind": "add-planner-resource-tests",
      "scope": "tests",
      "resources": [
        "tests/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-planner-rejects-missing-pipeline-directory",
        "acceptance-test-planner-rejects-delete-without-deletable-files",
        "acceptance-test-planner-accepts-existing-pipeline-directory"
      ]
    },
    {
      "id": "op-align-planner-resource-docs",
      "kind": "align-planner-resource-documentation",
      "scope": "references",
      "resources": [
        "references/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-planner-resource-rules-documented"
      ]
    },
    {
      "id": "op-forward-task-plan-validate-root",
      "kind": "forward-cli-root-to-task-plan-validate",
      "scope": "planning",
      "resources": [
        "pipeline_tools/__main__.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-task-plan-validate-cli-forwards-root"
      ]
    },
    {
      "id": "op-register-known-items",
      "kind": "register-known-items-and-follow-ups",
      "scope": "references",
      "resources": [
        "references/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-known-items-registered"
      ]
    }
  ],
  "chain": {
    "entry": {
      "not_applicable": true,
      "reason": "this task declares no chain reference for this phase"
    },
    "interaction": {
      "not_applicable": true,
      "reason": "this task declares no chain reference for this phase"
    },
    "application": {
      "not_applicable": true,
      "reason": "this task declares no chain reference for this phase"
    },
    "domain": {
      "not_applicable": true,
      "reason": "this task declares no chain reference for this phase"
    },
    "persistence": {
      "not_applicable": true,
      "reason": "this task declares no chain reference for this phase"
    },
    "readback": {
      "not_applicable": true,
      "reason": "this task declares no chain reference for this phase"
    },
    "recovery": {
      "not_applicable": true,
      "reason": "this task declares no chain reference for this phase"
    }
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-planner-rejects-missing-pipeline-directory",
      "evidence_level": 2,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_task_generation_rejects_missing_pipeline_resource_directory",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_missing_pipeline_resource_directory"
    },
    {
      "id": "acceptance-test-planner-rejects-delete-without-deletable-files",
      "evidence_level": 2,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_task_generation_rejects_delete_operation_without_deletable_files",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_delete_operation_without_deletable_files"
    },
    {
      "id": "acceptance-test-planner-accepts-existing-pipeline-directory",
      "evidence_level": 2,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_task_generation_accepts_existing_pipeline_resource_directory",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_accepts_existing_pipeline_resource_directory"
    },
    {
      "id": "acceptance-test-planner-resource-rules-documented",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_planner_resource_checks",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_planner_resource_checks"
    },
    {
      "id": "acceptance-test-task-plan-validate-cli-forwards-root",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_task_plan_validate_cli_forwards_root_for_derived_parent",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_task_plan_validate_cli_forwards_root_for_derived_parent"
    },
    {
      "id": "acceptance-test-known-items-registered",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_known_items",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_known_items"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-planning-runs-on-a-live-worktree",
      "status": "open",
      "source": "references/task-design.md",
      "note": "planning happens in a worktree where the .pipeline evidence directories under consideration are present and readable"
    },
    {
      "id": "assumption-existing-plans-stay-valid",
      "status": "open",
      "source": "pipeline_tools/planning.py",
      "note": "the new check applies to planning inputs and must not retroactively invalidate already frozen task sheets"
    }
  ],
  "unknowns": [],
  "non_user_completion_reason": "\u672c\u4efb\u52a1\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u5b8c\u6210\uff1a\u5b83\u5728\u89c4\u5212\u671f\u589e\u52a0\u4e00\u6761\u673a\u68b0\u6821\u9a8c\uff0c\u4f7f\u624b\u5199\u7684 .pipeline/<dir>/ \u8d44\u6e90\u5fc5\u987b\u771f\u5b9e\u5b58\u5728\uff0c\u4e14\u5220\u9664\u7c7b\u64cd\u4f5c\u7684\u76ee\u6807\u76ee\u5f55\u5fc5\u987b\u786e\u5b9e\u542b\u6709\u53ef\u6e05\u7406\u7684\u975e\u4fdd\u7559\u6587\u4ef6\uff0c\u4ece\u800c\u5728\u4efb\u52a1\u5355\u51bb\u7ed3\u524d\u5c31\u62d2\u7edd\u6f02\u79fb\u7684\u8d44\u6e90\u8def\u5f84\u3002\u4ea7\u7269\u662f\u88ab\u540e\u7eed\u89c4\u5212\u4e0e\u6d3e\u53d1\u6d88\u8d39\u7684\u673a\u68b0\u5e95\u5ea7\uff0c\u6ca1\u6709\u5916\u90e8\u5165\u53e3\u3001\u6ca1\u6709\u4ea4\u4e92\u9762\u3001\u4e5f\u6ca1\u6709\u53ef\u7531\u7528\u6237\u89e6\u53d1\u5e76\u89c2\u5bdf\u7684\u7ed3\u679c\uff0c\u56e0\u6b64\u4e0d\u80fd\u6807 vertical-feature \u6216 repair\uff1b\u540e\u7eed\u6d88\u8d39\u8be5\u5e95\u5ea7\u7684\u7528\u6237\u884c\u4e3a\u4efb\u52a1\u53e6\u884c\u89c4\u5212\u3002"
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`planner-resource-validation`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `pipeline_tools/`
- `tests/`
- `references/`
- `pipeline_tools/__main__.py`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-planner-resource-existence", "requirement-planner-delete-target-verification", "requirement-planner-resource-docs-aligned", "requirement-task-plan-validate-cli-root-forwarded", "requirement-known-items-registered"]
- 资源：["pipeline_tools/", "tests/", "references/", "pipeline_tools/__main__.py"]
- 操作：["op-add-planner-resource-check", "op-align-planner-resource-docs", "op-cover-planner-resource-check", "op-forward-task-plan-validate-root", "op-register-known-items"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-planner-rejects-missing-pipeline-directory

- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_task_generation_rejects_missing_pipeline_resource_directory`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_missing_pipeline_resource_directory`
- 证据等级：2

### 验收测试2：acceptance-test-planner-rejects-delete-without-deletable-files

- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_task_generation_rejects_delete_operation_without_deletable_files`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_delete_operation_without_deletable_files`
- 证据等级：2

### 验收测试3：acceptance-test-planner-accepts-existing-pipeline-directory

- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_task_generation_accepts_existing_pipeline_resource_directory`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_accepts_existing_pipeline_resource_directory`
- 证据等级：2

### 验收测试4：acceptance-test-planner-resource-rules-documented

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_planner_resource_checks`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_planner_resource_checks`
- 证据等级：2

### 验收测试5：acceptance-test-task-plan-validate-cli-forwards-root

- 测试：`tests/test_cli.py: CLITests.test_task_plan_validate_cli_forwards_root_for_derived_parent`
- 命令：`python -m unittest tests.test_cli.CLITests.test_task_plan_validate_cli_forwards_root_for_derived_parent`
- 证据等级：2

### 验收测试6：acceptance-test-known-items-registered

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_known_items`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_known_items`
- 证据等级：2

