# test-ref-narrowing-followup：冻结任务单

<!-- Task ID: test-ref-narrowing-followup -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "test-ref-narrowing-followup",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "test-ref-narrowing-followup"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "\u4e0d\u5728\u672c\u4efb\u52a1\u91cc\u6539\u52a8 goal.md\u3001IDEA.md \u6216 implement-plan.md",
    "\u4e0d\u4fee\u6539 docs/tasks/ \u4e0b\u4efb\u4f55\u5df2\u51bb\u7ed3\u4efb\u52a1\u5355",
    "\u4e0d\u5f31\u5316 contract.py \u4e0e core.py \u5df2\u6709\u7684\u673a\u68b0\u95f8\u95e8",
    "\u4e0d\u65b0\u589e\u7b2c\u4e09\u65b9\u4f9d\u8d56\uff0c\u53ea\u4f7f\u7528\u6807\u51c6\u5e93\u505a\u89e3\u6790\u4e0e\u6bd4\u5bf9",
    "\u4e0d\u628a\u4f4d\u7f6e\u6821\u9a8c\u5b9e\u73b0\u6210\u5bf9\u5177\u4f53\u6d4b\u8bd5\u6587\u4ef6\u540d\u7684\u786c\u7f16\u7801\u767d\u540d\u5355",
    "\u4e0d\u6539\u52a8 scope history \u7684 --since \u524d\u5411\u57fa\u7ebf\u8bed\u4e49",
    "\u4e0d\u5f31\u5316\u8fd9 22 \u6761\u65e2\u6709 fixture \u7684\u65ad\u8a00\u8bed\u4e49\uff1b\u8fc1\u79fb\u53ea\u5141\u8bb8\u4e3a\u5176\u5408\u6210\u4efb\u52a1\u8865\u4e0a\u5b83\u81ea\u5df1 test_ref \u6307\u5411\u7684\u6d4b\u8bd5\u6587\u4ef6\u8d44\u6e90\uff0c\u4e0d\u5f97\u653e\u5bbd\u4efb\u4f55\u65ad\u8a00"
  ],
  "allowed_paths": [
    "pipeline_tools/planning.py",
    "tests/test_planning.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "references/task-design.md",
    "tests/test_cli.py",
    "tests/test_planning_dispatch_integration.py",
    "tests/test_task_plan_contract_consistency.py"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-test-ref-strict-placement-enforced",
    "requirement-test-ref-fixtures-migrated",
    "requirement-test-ref-strict-rule-documented"
  ],
  "resources": [
    "pipeline_tools/planning.py",
    "tests/test_planning.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "references/task-design.md",
    "tests/test_cli.py",
    "tests/test_planning_dispatch_integration.py",
    "tests/test_task_plan_contract_consistency.py"
  ],
  "operations": [
    {
      "id": "op-remove-test-ref-narrowing",
      "kind": "remove-test-ref-narrowing-exemption",
      "scope": "planning",
      "resources": [
        "pipeline_tools/planning.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-planner-rejects-out-of-scope-test-ref",
        "acceptance-test-planner-rejects-unowned-test-ref-in-shared-root"
      ]
    },
    {
      "id": "op-cover-strict-test-ref-placement",
      "kind": "add-strict-test-ref-placement-tests",
      "scope": "tests",
      "resources": [
        "tests/test_planning.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-planner-rejects-out-of-scope-test-ref",
        "acceptance-test-planner-rejects-unowned-test-ref-in-shared-root"
      ]
    },
    {
      "id": "op-migrate-strict-rule-fixtures",
      "kind": "migrate-test-ref-fixtures",
      "scope": "tests",
      "resources": [
        "tests/test_cli.py",
        "tests/test_planning_dispatch_integration.py",
        "tests/test_task_plan_contract_consistency.py"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-cli-generate-task-sheets-lifecycle-passes",
        "acceptance-test-cli-contract-consistency-schema2-passes",
        "acceptance-test-dispatch-valid-run-reaches-identity-verified-dispatch",
        "acceptance-test-dispatch-conflict-fails-closed",
        "acceptance-test-contract-consistency-matching-plan-and-schema2-pass"
      ]
    },
    {
      "id": "op-document-strict-test-ref-placement",
      "kind": "align-strict-test-ref-placement-documentation",
      "scope": "references",
      "resources": [
        "references/task-design.md",
        "tests/test_acceptance_id_and_template_compliance.py"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-strict-test-ref-placement-documented"
      ]
    }
  ],
  "chain": {
    "entry": {
      "not_applicable": true,
      "reason": "planning-time mechanical check has no user-visible chain"
    },
    "interaction": {
      "not_applicable": true,
      "reason": "planning-time mechanical check has no user-visible chain"
    },
    "application": {
      "not_applicable": true,
      "reason": "planning-time mechanical check has no user-visible chain"
    },
    "domain": {
      "not_applicable": true,
      "reason": "planning-time mechanical check has no user-visible chain"
    },
    "persistence": {
      "not_applicable": true,
      "reason": "planning-time mechanical check has no user-visible chain"
    },
    "readback": {
      "not_applicable": true,
      "reason": "planning-time mechanical check has no user-visible chain"
    },
    "recovery": {
      "not_applicable": true,
      "reason": "planning-time mechanical check has no user-visible chain"
    }
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-planner-rejects-out-of-scope-test-ref",
      "evidence_level": 2,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources"
    },
    {
      "id": "acceptance-test-planner-rejects-unowned-test-ref-in-shared-root",
      "evidence_level": 2,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned"
    },
    {
      "id": "acceptance-test-cli-generate-task-sheets-lifecycle-passes",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_planning_generate_task_sheets_cli_lifecycle",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_planning_generate_task_sheets_cli_lifecycle"
    },
    {
      "id": "acceptance-test-cli-contract-consistency-schema2-passes",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet"
    },
    {
      "id": "acceptance-test-dispatch-valid-run-reaches-identity-verified-dispatch",
      "evidence_level": 2,
      "test_ref": "tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch",
      "command_ref": "python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch"
    },
    {
      "id": "acceptance-test-dispatch-conflict-fails-closed",
      "evidence_level": 2,
      "test_ref": "tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts",
      "command_ref": "python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts"
    },
    {
      "id": "acceptance-test-contract-consistency-matching-plan-and-schema2-pass",
      "evidence_level": 2,
      "test_ref": "tests/test_task_plan_contract_consistency.py: TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass",
      "command_ref": "python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass"
    },
    {
      "id": "acceptance-test-strict-test-ref-placement-documented",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_test_ref_placement_and_position_rules",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_test_ref_placement_and_position_rules"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-fixture-migration-preserves-assertions",
      "status": "open",
      "source": "tests/test_cli.py",
      "note": "\u53d7\u5f71\u54cd fixture \u53ef\u4ee5\u901a\u8fc7\u4e3a\u5176\u5408\u6210\u4efb\u52a1\u58f0\u660e test_ref \u6307\u5411\u7684\u6d4b\u8bd5\u6587\u4ef6\u8d44\u6e90\u6765\u8fc1\u79fb\uff0c\u800c\u65e0\u9700\u653e\u5bbd\u6216\u5220\u9664\u4efb\u4f55\u73b0\u6709\u65ad\u8a00"
    }
  ],
  "unknowns": [
    {
      "id": "unknown-non-python-test-paths",
      "source": "tests/",
      "status": "non_blocking",
      "note": "\u672c\u4ed3\u5e93\u9a8c\u6536\u6d4b\u8bd5\u5168\u4e3a Python unittest\uff1b\u4f4d\u7f6e\u89c4\u5219\u662f\u5426\u9700\u8986\u76d6\u975e Python \u6d4b\u8bd5\u6587\u4ef6\u5c1a\u672a\u88c1\u51b3\uff0c\u4e0d\u5c5e\u672c\u4efb\u52a1\u8303\u56f4"
    },
    {
      "id": "unknown-fixture-migration-shape",
      "source": "tests/test_planning_dispatch_integration.py",
      "status": "non_blocking",
      "note": "15 \u6761 dispatch-integration \u7528\u4f8b\u7a76\u7adf\u662f\u5404\u81ea\u65b0\u589e test_ref \u6307\u5411\u7684\u6d4b\u8bd5\u6587\u4ef6\u8d44\u6e90\uff0c\u8fd8\u662f\u628a test_ref \u6539\u6307\u5411\u5df2\u58f0\u660e\u8d44\u6e90\uff0c\u7559\u7ed9\u6267\u884c\u671f\u51b3\u5b9a\uff1b\u9a8c\u6536\u53ea\u9489\u4f4f\u8fc1\u79fb\u540e\u4ecd\u5168\u7eff\u4e14\u65ad\u8a00\u4e0d\u653e\u5bbd"
    },
    {
      "id": "unknown-historic-41-count",
      "source": ".pipeline/task-ref-verifiability/final-result.json",
      "status": "non_blocking",
      "note": "\u7ec8\u5ba1\u8bb0\u5f55\u91cc 41/22 \u4e0e 37/18 \u7684\u5dee\u5f02\u88ab\u89e3\u91ca\u4e3a subprocess \u7ea7 vs \u8fdb\u7a0b\u5185\u8ba1\u6570\uff1b\u672c\u8f6e\u5b9e\u6d4b\u53d6\u6d88\u6536\u7a84\u540e\u8fdb\u7a0b\u5185 discover \u4e3a 22 \u6761\u76f8\u5173\u5931\u8d25\uff0c\u4e0e 22 \u4e00\u81f4\uff0c41 \u8fd9\u4e2a\u6570\u5b57\u672c\u8f6e\u65e0\u6cd5\u72ec\u7acb\u590d\u73b0"
    }
  ],
  "non_user_completion_reason": "\u672c\u4efb\u52a1\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u5b8c\u6210\uff1a\u5b83\u53d6\u6d88 test_ref \u4f4d\u7f6e\u6821\u9a8c\u7684\u6536\u7a84\u8c41\u514d\uff0c\u4f7f\u89c4\u5212\u671f\u56de\u5230\u4e25\u683c\u89c4\u5219\uff08test_ref \u6307\u540d\u7684\u6587\u4ef6\u8def\u5f84\u5fc5\u987b\u843d\u5728\u672c\u4efb\u52a1 allowed_paths \u4e4b\u5185\uff09\uff0c\u540c\u6b65\u6539\u5199 references/task-design.md \u4e2d\u63cf\u8ff0\u6536\u7a84\u7684\u90a3\u6bb5\u6587\u6863\u4e0e\u9489\u4f4f\u5b83\u7684\u5408\u89c4\u65ad\u8a00\uff0c\u5e76\u628a\u56e0\u6b64\u66b4\u9732\u7684 22 \u6761\u65e2\u6709 fixture \u8fc1\u79fb\u5230\u4e0e\u65b0\u89c4\u5219\u4e00\u81f4\u3001\u4e14\u4e0d\u5f31\u5316\u4efb\u4f55\u65ad\u8a00\u7684\u5f62\u6001\u3002\u4ea7\u7269\u662f\u88ab\u540e\u7eed\u89c4\u5212\u4e0e\u6d3e\u53d1\u6d88\u8d39\u7684\u673a\u68b0\u5e95\u5ea7\uff0c\u6ca1\u6709\u5916\u90e8\u5165\u53e3\u3001\u6ca1\u6709\u4ea4\u4e92\u9762\u3001\u4e5f\u6ca1\u6709\u53ef\u7531\u7528\u6237\u89e6\u53d1\u5e76\u89c2\u5bdf\u7684\u7ed3\u679c\uff0c\u56e0\u6b64\u4e0d\u80fd\u6807 vertical-feature \u6216 repair\uff1b\u540e\u7eed\u6d88\u8d39\u8be5\u5e95\u5ea7\u7684\u7528\u6237\u884c\u4e3a\u4efb\u52a1\u53e6\u884c\u89c4\u5212\u3002"
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`test-ref-narrowing-followup`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `pipeline_tools/planning.py`
- `tests/test_planning.py`
- `tests/test_acceptance_id_and_template_compliance.py`
- `references/task-design.md`
- `tests/test_cli.py`
- `tests/test_planning_dispatch_integration.py`
- `tests/test_task_plan_contract_consistency.py`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-test-ref-strict-placement-enforced", "requirement-test-ref-fixtures-migrated", "requirement-test-ref-strict-rule-documented"]
- 资源：["pipeline_tools/planning.py", "tests/test_planning.py", "tests/test_acceptance_id_and_template_compliance.py", "references/task-design.md", "tests/test_cli.py", "tests/test_planning_dispatch_integration.py", "tests/test_task_plan_contract_consistency.py"]
- 操作：["op-cover-strict-test-ref-placement", "op-document-strict-test-ref-placement", "op-migrate-strict-rule-fixtures", "op-remove-test-ref-narrowing"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-planner-rejects-out-of-scope-test-ref

- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources`
- 证据等级：2

### 验收测试2：acceptance-test-planner-rejects-unowned-test-ref-in-shared-root

- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_test_ref_in_same_test_dir_but_not_owned`
- 证据等级：2

### 验收测试3：acceptance-test-cli-generate-task-sheets-lifecycle-passes

- 测试：`tests/test_cli.py: CLITests.test_planning_generate_task_sheets_cli_lifecycle`
- 命令：`python -m unittest tests.test_cli.CLITests.test_planning_generate_task_sheets_cli_lifecycle`
- 证据等级：2

### 验收测试4：acceptance-test-cli-contract-consistency-schema2-passes

- 测试：`tests/test_cli.py: CLITests.test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet`
- 命令：`python -m unittest tests.test_cli.CLITests.test_task_plan_contract_consistency_cli_accepts_matching_schema2_sheet`
- 证据等级：2

### 验收测试5：acceptance-test-dispatch-valid-run-reaches-identity-verified-dispatch

- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch`
- 命令：`python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch`
- 证据等级：2

### 验收测试6：acceptance-test-dispatch-conflict-fails-closed

- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts`
- 命令：`python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts`
- 证据等级：2

### 验收测试7：acceptance-test-contract-consistency-matching-plan-and-schema2-pass

- 测试：`tests/test_task_plan_contract_consistency.py: TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass`
- 命令：`python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass`
- 证据等级：2

### 验收测试8：acceptance-test-strict-test-ref-placement-documented

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_test_ref_placement_and_position_rules`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_test_ref_placement_and_position_rules`
- 证据等级：2

