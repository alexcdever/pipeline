# derived-generation-support：冻结任务单

<!-- Task ID: derived-generation-support -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "derived-generation-support",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "derived-generation-support"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "\u4e0d\u4fee\u6539 goal.md\u3001IDEA.md \u4e0e\u4efb\u4f55\u5df2\u51bb\u7ed3\u4efb\u52a1\u5355",
    "\u4e0d\u5220\u9664\u6216\u6539\u5199 .pipeline/ \u4e0b\u7684\u65e2\u6709\u8bc1\u636e\u4e0e metrics \u5386\u53f2",
    "\u4e0d\u6539\u52a8 create_derived_dispatch \u7684\u6d3e\u53d1\u671f\u524d\u7f6e\u6761\u4ef6\u4e0e worktree \u521b\u5efa\u8bed\u4e49",
    "\u4e0d\u8ba9\u73b0\u6709\u624b\u5de5\u64b0\u5199\u7684 derived \u4efb\u52a1\u5355\u5931\u6548",
    "\u4e0d\u91cd\u5199 Git \u5386\u53f2"
  ],
  "allowed_paths": [
    "pipeline_tools/planning.py",
    "pipeline_tools/contract.py",
    "tests/test_task_generation.py",
    "tests/test_planning.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "references/task-design.md"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-generator-emits-derived-from",
    "requirement-plan-accepts-cross-run-parent",
    "requirement-derived-parent-type-read-from-parent-sheet",
    "requirement-derived-generation-documented"
  ],
  "resources": [
    "pipeline_tools/planning.py",
    "pipeline_tools/contract.py",
    "tests/test_task_generation.py",
    "tests/test_planning.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "references/task-design.md"
  ],
  "operations": [
    {
      "id": "op-emit-derived-from",
      "kind": "add-derived-contract-emission",
      "scope": "planning",
      "resources": [
        "pipeline_tools/planning.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-generator-emits-derived-from",
        "acceptance-test-generator-unchanged-for-non-derived",
        "acceptance-test-generator-emits-same-run-parent-sheets"
      ]
    },
    {
      "id": "op-relax-parent-constraint",
      "kind": "relax-cross-run-parent-validation",
      "scope": "planning",
      "resources": [
        "pipeline_tools/planning.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-plan-accepts-cross-run-parent",
        "acceptance-test-plan-rejects-missing-parent",
        "acceptance-test-plan-rejects-planner-declared-parent-type-mismatch",
        "acceptance-test-plan-accepts-same-run-derived-parent"
      ]
    },
    {
      "id": "op-guard-derivation-contract",
      "kind": "keep-derived-contract-gate-unchanged",
      "scope": "contract",
      "resources": [
        "pipeline_tools/contract.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-generator-emits-derived-from",
        "acceptance-test-plan-rejects-planner-declared-parent-type-mismatch"
      ]
    },
    {
      "id": "op-cover-generation",
      "kind": "add-generation-coverage",
      "scope": "tests",
      "resources": [
        "tests/test_task_generation.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-generator-emits-derived-from",
        "acceptance-test-generator-unchanged-for-non-derived",
        "acceptance-test-generator-emits-same-run-parent-sheets",
        "acceptance-test-generator-fails-closed-on-existing-same-run-parent-sheet"
      ]
    },
    {
      "id": "op-cover-plan-validation",
      "kind": "add-plan-validation-coverage",
      "scope": "tests",
      "resources": [
        "tests/test_planning.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-plan-accepts-cross-run-parent",
        "acceptance-test-plan-rejects-missing-parent",
        "acceptance-test-plan-rejects-planner-declared-parent-type-mismatch",
        "acceptance-test-plan-accepts-same-run-derived-parent"
      ]
    },
    {
      "id": "op-cover-docs-compliance",
      "kind": "add-documentation-compliance-coverage",
      "scope": "tests",
      "resources": [
        "tests/test_acceptance_id_and_template_compliance.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-derived-generation-rules-documented"
      ]
    },
    {
      "id": "op-align-docs",
      "kind": "align-derived-generation-documentation",
      "scope": "references",
      "resources": [
        "references/task-design.md"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-derived-generation-rules-documented"
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
      "id": "acceptance-test-generator-emits-derived-from",
      "evidence_level": 3,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generator_emits_derived_from_for_derived_task",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generator_emits_derived_from_for_derived_task"
    },
    {
      "id": "acceptance-test-generator-unchanged-for-non-derived",
      "evidence_level": 2,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generator_output_for_non_derived_task_is_unchanged",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generator_output_for_non_derived_task_is_unchanged"
    },
    {
      "id": "acceptance-test-generator-emits-same-run-parent-sheets",
      "evidence_level": 3,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generate_task_sheets_emits_derived_sheet_for_same_run_parent",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_emits_derived_sheet_for_same_run_parent"
    },
    {
      "id": "acceptance-test-generator-fails-closed-on-existing-same-run-parent-sheet",
      "evidence_level": 2,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists"
    },
    {
      "id": "acceptance-test-plan-accepts-cross-run-parent",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_accepts_derived_parent_outside_the_run",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_accepts_derived_parent_outside_the_run"
    },
    {
      "id": "acceptance-test-plan-rejects-missing-parent",
      "evidence_level": 2,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_rejects_derived_parent_that_cannot_be_found",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_derived_parent_that_cannot_be_found"
    },
    {
      "id": "acceptance-test-plan-rejects-planner-declared-parent-type-mismatch",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_rejects_planner_declared_parent_type_mismatch",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_planner_declared_parent_type_mismatch"
    },
    {
      "id": "acceptance-test-plan-accepts-same-run-derived-parent",
      "evidence_level": 2,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_accepts_same_run_derived_parent",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_accepts_same_run_derived_parent"
    },
    {
      "id": "acceptance-test-derived-generation-rules-documented",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_derived_generation_support",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_derived_generation_support"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2,
    3
  ],
  "assumptions": [
    {
      "id": "assumption-manual-sheets-stay-valid",
      "status": "open",
      "source": "docs/tasks/gate-deletion-semantics-continuation-1.md",
      "note": "the two hand-written derived sheets must keep validating; the generator change must not tighten or invalidate the existing contract gate"
    },
    {
      "id": "assumption-parent-sheet-read-is-sufficient",
      "status": "open",
      "source": "pipeline_tools/planning.py",
      "note": "for a parent outside the current run the parent sheet under docs/tasks/<parent-id>.md is the authoritative source for the parent contract's task_type and for proving the parent exists; for a same-run parent the plan task's own type is authoritative because no sheet exists yet"
    }
  ],
  "unknowns": [],
  "non_user_completion_reason": "\u672c\u4efb\u52a1\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u5b8c\u6210\uff1a\u5b83\u5728\u89c4\u5212\u671f\u6253\u901a generate_task_sheets \u7684 derived \u652f\u6301\uff0c\u4f7f\u751f\u6210\u8def\u5f84\u80fd\u591f\u4e3a derived \u4efb\u52a1\u8f93\u51fa derived_from\uff0c\u4f7f\u89c4\u5212\u671f\u80fd\u591f\u5bf9\u7236\u4efb\u52a1\u5c5e\u4e8e\u66f4\u65e9 planning run \u6216\u540c run \u7684\u60c5\u5f62\u7ed9\u51fa\u673a\u68b0\u5224\u5b9a\uff0c\u5e76\u4f7f derived_from.parent_task_type \u6309\u7236\u4efb\u52a1\u4f4d\u7f6e\uff08\u540c run \u53d6 plan\u3001\u8de8 run \u8bfb\u7236\u5355\uff09\u673a\u68b0\u8bfb\u53d6\u800c\u975e\u7531\u89c4\u5212\u8005\u81ea\u7531\u586b\u5199\uff1b\u751f\u6210\u5668\u4fa7\u7684\u7236\u5b50\u540c run \u6210\u529f\u751f\u6210\u4e0e\u7236\u5355\u5df2\u5b58\u5728\u7684 fail-closed \u4e5f\u4e00\u5e76\u8986\u76d6\u3002\u4ea7\u7269\u662f\u88ab\u540e\u7eed\u89c4\u5212\u4e0e\u6d3e\u53d1\u6d88\u8d39\u7684\u673a\u68b0\u5e95\u5ea7\uff0c\u6ca1\u6709\u5916\u90e8\u5165\u53e3\u3001\u6ca1\u6709\u4ea4\u4e92\u9762\u3001\u4e5f\u6ca1\u6709\u53ef\u7531\u7528\u6237\u89e6\u53d1\u5e76\u89c2\u5bdf\u7684\u7ed3\u679c\uff0c\u56e0\u6b64\u4e0d\u80fd\u6807 vertical-feature \u6216 repair\uff1b\u6d88\u8d39\u8be5\u5e95\u5ea7\u7684\u7528\u6237\u884c\u4e3a\u4efb\u52a1\u53e6\u884c\u89c4\u5212\u3002"
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`derived-generation-support`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `pipeline_tools/planning.py`
- `pipeline_tools/contract.py`
- `tests/test_task_generation.py`
- `tests/test_planning.py`
- `tests/test_acceptance_id_and_template_compliance.py`
- `references/task-design.md`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-generator-emits-derived-from", "requirement-plan-accepts-cross-run-parent", "requirement-derived-parent-type-read-from-parent-sheet", "requirement-derived-generation-documented"]
- 资源：["pipeline_tools/planning.py", "pipeline_tools/contract.py", "tests/test_task_generation.py", "tests/test_planning.py", "tests/test_acceptance_id_and_template_compliance.py", "references/task-design.md"]
- 操作：["op-align-docs", "op-cover-docs-compliance", "op-cover-generation", "op-cover-plan-validation", "op-emit-derived-from", "op-guard-derivation-contract", "op-relax-parent-constraint"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-generator-emits-derived-from

- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generator_emits_derived_from_for_derived_task`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_generator_emits_derived_from_for_derived_task`
- 证据等级：3

### 验收测试2：acceptance-test-generator-unchanged-for-non-derived

- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generator_output_for_non_derived_task_is_unchanged`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_generator_output_for_non_derived_task_is_unchanged`
- 证据等级：2

### 验收测试3：acceptance-test-generator-emits-same-run-parent-sheets

- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generate_task_sheets_emits_derived_sheet_for_same_run_parent`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_emits_derived_sheet_for_same_run_parent`
- 证据等级：3

### 验收测试4：acceptance-test-generator-fails-closed-on-existing-same-run-parent-sheet

- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists`
- 证据等级：2

### 验收测试5：acceptance-test-plan-accepts-cross-run-parent

- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_accepts_derived_parent_outside_the_run`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_accepts_derived_parent_outside_the_run`
- 证据等级：3

### 验收测试6：acceptance-test-plan-rejects-missing-parent

- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_rejects_derived_parent_that_cannot_be_found`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_derived_parent_that_cannot_be_found`
- 证据等级：2

### 验收测试7：acceptance-test-plan-rejects-planner-declared-parent-type-mismatch

- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_rejects_planner_declared_parent_type_mismatch`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_planner_declared_parent_type_mismatch`
- 证据等级：3

### 验收测试8：acceptance-test-plan-accepts-same-run-derived-parent

- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_accepts_same_run_derived_parent`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_accepts_same_run_derived_parent`
- 证据等级：2

### 验收测试9：acceptance-test-derived-generation-rules-documented

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_derived_generation_support`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_derived_generation_support`
- 证据等级：2

