# test-metrics-isolation：冻结任务单

<!-- Task ID: test-metrics-isolation -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "test-metrics-isolation",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "test-metrics-isolation"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "\u4e0d\u6539\u52a8 pipeline_tools/ \u7684\u751f\u4ea7\u884c\u4e3a",
    "\u4e0d\u4fee\u6539 goal.md\u3001IDEA.md\u3001implement-plan.md",
    "\u4e0d\u5220\u9664 .pipeline/metrics/ \u4e0b\u4efb\u4f55\u5df2\u5165\u5e93\u6587\u4ef6",
    "\u4e0d\u6539\u52a8 .gitignore \u4e2d .pipeline/metrics/ \u7684\u8ffd\u8e2a\u72b6\u6001",
    "\u4e0d\u4fee\u6539 docs/tasks/ \u4e0b\u4efb\u4f55\u5df2\u51bb\u7ed3\u4efb\u52a1\u5355",
    "\u4e0d\u4e3a\u4e86\u9694\u79bb\u800c\u8df3\u8fc7\u6216\u5220\u9664\u4efb\u4f55\u65e2\u6709\u81ea\u52a8\u6307\u6807\u6d4b\u8bd5"
  ],
  "allowed_paths": [
    "tests/",
    "references/"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-suite-no-tracked-metrics-write",
    "requirement-enabled-auto-metrics-isolated",
    "requirement-metrics-isolation-documented"
  ],
  "resources": [
    "tests/",
    "references/"
  ],
  "operations": [
    {
      "id": "op-isolate-auto-metrics-tests",
      "kind": "isolate-test-metrics-root",
      "scope": "tests",
      "resources": [
        "tests/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-cli-suite-leaves-tracked-metrics-unchanged",
        "acceptance-test-auto-metrics-enabled-run-isolated"
      ]
    },
    {
      "id": "op-guard-tracked-metrics-in-suite",
      "kind": "add-test-suite-metrics-guard",
      "scope": "tests",
      "resources": [
        "tests/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-cli-suite-leaves-tracked-metrics-unchanged",
        "acceptance-test-auto-metrics-enabled-run-isolated",
        "acceptance-test-wrapper-exit-code-with-isolation"
      ]
    },
    {
      "id": "op-align-metrics-contract-docs",
      "kind": "align-metrics-contract-documentation",
      "scope": "references",
      "resources": [
        "references/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-metrics-contract-documents-test-isolation"
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
      "id": "acceptance-test-cli-suite-leaves-tracked-metrics-unchanged",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_cli_suite_leaves_tracked_metrics_unchanged",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_cli_suite_leaves_tracked_metrics_unchanged"
    },
    {
      "id": "acceptance-test-auto-metrics-enabled-run-isolated",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_auto_metrics_enabled_run_keeps_metrics_out_of_repository",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_auto_metrics_enabled_run_keeps_metrics_out_of_repository"
    },
    {
      "id": "acceptance-test-wrapper-exit-code-with-isolation",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code"
    },
    {
      "id": "acceptance-test-metrics-contract-documents-test-isolation",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_test_isolation",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_test_isolation"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-fix-stays-test-side",
      "status": "open",
      "source": "tests/test_cli.py",
      "note": "the isolation is expected to be achievable entirely inside the test harness by choosing a temporary metrics root or a non-repository cwd; if that turns out to be false the contract scope must be widened before dispatch"
    },
    {
      "id": "assumption-metrics-remain-tracked",
      "status": "open",
      "source": "references/metrics-contract.md",
      "note": "tracked metrics are legitimate workflow history and must stay tracked; only the test suite must stop writing into them"
    }
  ],
  "unknowns": [],
  "non_user_completion_reason": "\u672c\u4efb\u52a1\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u5b8c\u6210\uff1a\u5b83\u4fee\u6b63\u6d4b\u8bd5\u5939\u5177\uff0c\u4f7f\u663e\u5f0f\u542f\u7528\u81ea\u52a8\u6307\u6807\u6536\u96c6\u7684\u6d4b\u8bd5\u628a\u6307\u6807\u5199\u5165\u4e34\u65f6 root\uff0c\u4ece\u800c\u4e0d\u518d\u5411\u53d7\u8ffd\u8e2a\u7684 .pipeline/metrics/ \u8ffd\u52a0\u6587\u4ef6\u3001\u4e0d\u518d\u5f04\u810f\u5de5\u4f5c\u6811\u3002\u4ea7\u7269\u662f\u88ab\u540e\u7eed\u6d4b\u8bd5\u4e0e\u5408\u5e76\u95f8\u95e8\u6d88\u8d39\u7684\u673a\u68b0\u5e95\u5ea7\uff0c\u6ca1\u6709\u5916\u90e8\u5165\u53e3\u3001\u6ca1\u6709\u4ea4\u4e92\u9762\u3001\u4e5f\u6ca1\u6709\u53ef\u7531\u7528\u6237\u89e6\u53d1\u5e76\u89c2\u5bdf\u7684\u7ed3\u679c\uff0c\u56e0\u6b64\u4e0d\u80fd\u6807 vertical-feature \u6216 repair\uff1b\u540e\u7eed\u6d88\u8d39\u8be5\u5e95\u5ea7\u7684\u4efb\u52a1\u53e6\u884c\u89c4\u5212\u3002"
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`test-metrics-isolation`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `tests/`
- `references/`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-suite-no-tracked-metrics-write", "requirement-enabled-auto-metrics-isolated", "requirement-metrics-isolation-documented"]
- 资源：["tests/", "references/"]
- 操作：["op-align-metrics-contract-docs", "op-guard-tracked-metrics-in-suite", "op-isolate-auto-metrics-tests"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-cli-suite-leaves-tracked-metrics-unchanged

- 测试：`tests/test_cli.py: CLITests.test_cli_suite_leaves_tracked_metrics_unchanged`
- 命令：`python -m unittest tests.test_cli.CLITests.test_cli_suite_leaves_tracked_metrics_unchanged`
- 证据等级：2

### 验收测试2：acceptance-test-auto-metrics-enabled-run-isolated

- 测试：`tests/test_cli.py: CLITests.test_auto_metrics_enabled_run_keeps_metrics_out_of_repository`
- 命令：`python -m unittest tests.test_cli.CLITests.test_auto_metrics_enabled_run_keeps_metrics_out_of_repository`
- 证据等级：2

### 验收测试3：acceptance-test-wrapper-exit-code-with-isolation

- 测试：`tests/test_cli.py: CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code`
- 命令：`python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code`
- 证据等级：2

### 验收测试4：acceptance-test-metrics-contract-documents-test-isolation

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_test_isolation`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_test_isolation`
- 证据等级：2

