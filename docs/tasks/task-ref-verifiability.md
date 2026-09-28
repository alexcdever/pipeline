# task-ref-verifiability：冻结任务单

<!-- Task ID: task-ref-verifiability -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "task-ref-verifiability",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "task-ref-verifiability"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "\u4e0d\u5728\u672c\u4efb\u52a1\u91cc\u4fee\u6539\u4efb\u4f55\u5df2\u51bb\u7ed3\u7684 docs/tasks/ \u4efb\u52a1\u5355",
    "\u4e0d\u4e3a\u4fee\u7f3a\u9677 D \u4e0e E \u800c\u6539\u52a8 goal.md\u3001IDEA.md \u6216 implement-plan.md",
    "\u4e0d\u5f31\u5316 contract.py \u4e0e core.py \u5df2\u6709\u7684\u4efb\u4f55\u673a\u68b0\u95f8\u95e8",
    "\u4e0d\u628a\u4f4d\u7f6e\u6821\u9a8c\u5b9e\u73b0\u6210\u53ea\u68c0\u67e5\u6587\u4ef6\u5b58\u5728\u800c\u5ffd\u7565\u7c7b\u540d\u4e0e\u65b9\u6cd5\u540d",
    "\u4e0d\u628a\u4f4d\u7f6e\u6821\u9a8c\u5b9e\u73b0\u6210\u5bf9\u5177\u4f53\u6d4b\u8bd5\u6587\u4ef6\u540d\u7684\u786c\u7f16\u7801\u767d\u540d\u5355",
    "\u4e0d\u65b0\u589e\u7b2c\u4e09\u65b9\u4f9d\u8d56\uff0c\u53ea\u4f7f\u7528\u6807\u51c6\u5e93\u505a\u89e3\u6790\u4e0e\u6bd4\u5bf9",
    "\u4e0d\u6539\u52a8 scope history \u7684 --since \u524d\u5411\u57fa\u7ebf\u8bed\u4e49",
    "\u4e0d\u5728\u672c\u4efb\u52a1\u91cc\u56de\u6eaf\u4fee\u590d toolchain-freshness-fixes \u4efb\u52a1\u5355\u672c\u8eab"
  ],
  "allowed_paths": [
    "pipeline_tools/planning.py",
    "pipeline_tools/core.py",
    "tests/test_planning.py",
    "tests/test_task_generation.py",
    "tests/test_evidence.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "references/task-design.md",
    "references/acceptance-evidence.md"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-test-ref-inside-allowed-paths",
    "requirement-test-ref-position-verified",
    "requirement-test-ref-rules-documented"
  ],
  "resources": [
    "pipeline_tools/planning.py",
    "pipeline_tools/core.py",
    "tests/test_planning.py",
    "tests/test_task_generation.py",
    "tests/test_evidence.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "references/task-design.md",
    "references/acceptance-evidence.md"
  ],
  "operations": [
    {
      "id": "op-add-test-ref-placement-check",
      "kind": "add-planning-test-ref-placement-check",
      "scope": "planning",
      "resources": [
        "pipeline_tools/planning.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-planner-rejects-test-ref-outside-allowed-paths",
        "acceptance-test-planner-accepts-test-ref-inside-allowed-paths",
        "acceptance-test-generator-blocks-out-of-scope-test-ref"
      ]
    },
    {
      "id": "op-add-test-ref-position-check",
      "kind": "add-gate-test-ref-position-check",
      "scope": "pipeline-tools",
      "resources": [
        "pipeline_tools/core.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-gate-rejects-absent-test-ref-method"
      ]
    },
    {
      "id": "op-cover-test-ref-checks",
      "kind": "add-and-extend-test-ref-tests",
      "scope": "tests",
      "resources": [
        "tests/test_planning.py",
        "tests/test_task_generation.py",
        "tests/test_evidence.py",
        "tests/test_acceptance_id_and_template_compliance.py"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-planner-rejects-test-ref-outside-allowed-paths",
        "acceptance-test-planner-accepts-test-ref-inside-allowed-paths",
        "acceptance-test-generator-blocks-out-of-scope-test-ref",
        "acceptance-test-gate-rejects-absent-test-ref-method",
        "acceptance-test-test-ref-rules-documented"
      ]
    },
    {
      "id": "op-align-test-ref-docs",
      "kind": "align-test-ref-documentation",
      "scope": "references",
      "resources": [
        "references/task-design.md",
        "references/acceptance-evidence.md"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-test-ref-rules-documented"
      ]
    }
  ],
  "chain": {
    "entry": {
      "not_applicable": true,
      "reason": "planning and gate mechanical check has no user-visible chain"
    },
    "interaction": {
      "not_applicable": true,
      "reason": "planning and gate mechanical check has no user-visible chain"
    },
    "application": {
      "not_applicable": true,
      "reason": "planning and gate mechanical check has no user-visible chain"
    },
    "domain": {
      "not_applicable": true,
      "reason": "planning and gate mechanical check has no user-visible chain"
    },
    "persistence": {
      "not_applicable": true,
      "reason": "planning and gate mechanical check has no user-visible chain"
    },
    "readback": {
      "not_applicable": true,
      "reason": "planning and gate mechanical check has no user-visible chain"
    },
    "recovery": {
      "not_applicable": true,
      "reason": "planning and gate mechanical check has no user-visible chain"
    }
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-planner-rejects-test-ref-outside-allowed-paths",
      "evidence_level": 2,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources"
    },
    {
      "id": "acceptance-test-planner-accepts-test-ref-inside-allowed-paths",
      "evidence_level": 2,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_accepts_acceptance_test_ref_inside_task_resources",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_accepts_acceptance_test_ref_inside_task_resources"
    },
    {
      "id": "acceptance-test-generator-blocks-out-of-scope-test-ref",
      "evidence_level": 2,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generate_task_sheets_blocks_out_of_scope_acceptance_test_ref",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_blocks_out_of_scope_acceptance_test_ref"
    },
    {
      "id": "acceptance-test-gate-rejects-absent-test-ref-method",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_gate_rejects_acceptance_test_ref_method_absent_from_named_file",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_gate_rejects_acceptance_test_ref_method_absent_from_named_file"
    },
    {
      "id": "acceptance-test-test-ref-rules-documented",
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
      "id": "assumption-test-ref-grammar-stable",
      "status": "open",
      "source": "references/acceptance-evidence.md",
      "note": "test_ref \u7684\u65e2\u6709\u4e66\u5199\u683c\u5f0f\u662f \u6587\u4ef6\u8def\u5f84\u5192\u53f7\u7a7a\u683c\u7c7b\u540d\u70b9\u65b9\u6cd5\u540d\uff1b\u6587\u4ef6\u8def\u5f84\u662f\u9879\u76ee\u76f8\u5bf9\u8def\u5f84\uff0c\u4e14 test_ref \u4e0e command_ref \u90fd\u4e0d\u542b\u5c16\u62ec\u53f7"
    },
    {
      "id": "assumption-frozen-sheets-not-retroactively-invalidated",
      "status": "open",
      "source": "goal.md",
      "note": "\u65b0\u589e\u7684\u89c4\u5212\u671f\u4e0e gate \u671f\u6821\u9a8c\u53ea\u4f5c\u7528\u4e8e\u65b0\u89c4\u5212\u8f93\u5165\u548c\u5728\u9014\u4efb\u52a1\u7684 gate\uff0c\u4e0d\u56de\u6eaf\u6539\u5199\u5df2\u51bb\u7ed3\u7684\u4efb\u52a1\u5355"
    }
  ],
  "unknowns": [
    {
      "id": "unknown-non-python-test-paths",
      "source": "tests/",
      "status": "non_blocking",
      "note": "\u5f53\u524d\u4ed3\u5e93\u7684\u9a8c\u6536\u6d4b\u8bd5\u5168\u90e8\u662f Python unittest\uff1b\u4f4d\u7f6e\u6821\u9a8c\u662f\u5426\u9700\u8981\u8986\u76d6\u975e Python \u6d4b\u8bd5\u6587\u4ef6\u5c1a\u672a\u88c1\u51b3\uff0c\u672c\u4efb\u52a1\u6309 Python \u89e3\u6790\u8bbe\u8ba1\u9a8c\u6536"
    }
  ],
  "non_user_completion_reason": "\u672c\u4efb\u52a1\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u5b8c\u6210\uff1a\u5b83\u4fee\u6b63\u4e24\u6761\u89c4\u5212\u4e0e\u95f8\u95e8\u671f\u7684\u673a\u68b0\u6821\u9a8c\u7f3a\u53e3\uff0c\u4f7f\u5951\u7ea6\u65e0\u6cd5\u518d\u8981\u6c42\u4e00\u4e2a\u81ea\u5df1\u88ab\u7981\u6b62\u521b\u5efa\u7684\u6587\u4ef6\uff0c\u5e76\u4f7f test_ref \u6240\u6307\u65b9\u6cd5\u5fc5\u987b\u5728\u6307\u5b9a\u6587\u4ef6\u4e2d\u771f\u5b9e\u5b58\u5728\u3002\u4ea7\u7269\u662f\u88ab\u540e\u7eed\u89c4\u5212\u3001\u6267\u884c\u4e0e\u5408\u5e76\u95f8\u95e8\u6d88\u8d39\u7684\u673a\u68b0\u5e95\u5ea7\uff0c\u6ca1\u6709\u5916\u90e8\u5165\u53e3\u3001\u6ca1\u6709\u4ea4\u4e92\u9762\u3001\u4e5f\u6ca1\u6709\u53ef\u7531\u7528\u6237\u89e6\u53d1\u5e76\u89c2\u5bdf\u7684\u7ed3\u679c\uff0c\u56e0\u6b64\u4e0d\u80fd\u6807 vertical-feature \u6216 repair\uff1b\u540e\u7eed\u6d88\u8d39\u8be5\u5e95\u5ea7\u7684\u7528\u6237\u884c\u4e3a\u4efb\u52a1\u53e6\u884c\u89c4\u5212\u3002"
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`task-ref-verifiability`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `pipeline_tools/planning.py`
- `pipeline_tools/core.py`
- `tests/test_planning.py`
- `tests/test_task_generation.py`
- `tests/test_evidence.py`
- `tests/test_acceptance_id_and_template_compliance.py`
- `references/task-design.md`
- `references/acceptance-evidence.md`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-test-ref-inside-allowed-paths", "requirement-test-ref-position-verified", "requirement-test-ref-rules-documented"]
- 资源：["pipeline_tools/planning.py", "pipeline_tools/core.py", "tests/test_planning.py", "tests/test_task_generation.py", "tests/test_evidence.py", "tests/test_acceptance_id_and_template_compliance.py", "references/task-design.md", "references/acceptance-evidence.md"]
- 操作：["op-add-test-ref-placement-check", "op-add-test-ref-position-check", "op-align-test-ref-docs", "op-cover-test-ref-checks"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-planner-rejects-test-ref-outside-allowed-paths

- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_acceptance_test_ref_outside_task_resources`
- 证据等级：2

### 验收测试2：acceptance-test-planner-accepts-test-ref-inside-allowed-paths

- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_accepts_acceptance_test_ref_inside_task_resources`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_accepts_acceptance_test_ref_inside_task_resources`
- 证据等级：2

### 验收测试3：acceptance-test-generator-blocks-out-of-scope-test-ref

- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generate_task_sheets_blocks_out_of_scope_acceptance_test_ref`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_blocks_out_of_scope_acceptance_test_ref`
- 证据等级：2

### 验收测试4：acceptance-test-gate-rejects-absent-test-ref-method

- 测试：`tests/test_evidence.py: EvidenceTests.test_gate_rejects_acceptance_test_ref_method_absent_from_named_file`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_gate_rejects_acceptance_test_ref_method_absent_from_named_file`
- 证据等级：2

### 验收测试5：acceptance-test-test-ref-rules-documented

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_test_ref_placement_and_position_rules`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_test_ref_placement_and_position_rules`
- 证据等级：2

