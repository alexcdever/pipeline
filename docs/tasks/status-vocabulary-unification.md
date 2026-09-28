# status-vocabulary-unification：冻结任务单

<!-- Task ID: status-vocabulary-unification -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "status-vocabulary-unification",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "status-vocabulary-unification"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "\u4e0d\u4fee\u6539 goal.md\u3001IDEA.md \u6216 implement-plan.md",
    "\u4e0d\u4fee\u6539 docs/tasks/ \u4e0b\u4efb\u4f55\u5df2\u51bb\u7ed3\u4efb\u52a1\u5355",
    "\u4e0d\u5f31\u5316 core.py \u4e0e contract.py \u5df2\u6709\u7684\u673a\u68b0\u95f8\u95e8",
    "\u4e0d\u91cd\u5199\u6216\u5220\u9664 .pipeline/ \u4e0b\u4efb\u4f55\u5386\u53f2\u8bc1\u636e\u4ea7\u7269",
    "\u4e0d\u65b0\u589e\u7b2c\u4e09\u65b9\u4f9d\u8d56\uff0c\u53ea\u7528\u6807\u51c6\u5e93\u505a\u5927\u5c0f\u5199\u5f52\u4e00",
    "\u4e0d\u5f15\u5165\u7b2c\u4e09\u5957\u72b6\u6001\u62fc\u5199\uff1a\u5f52\u4e00\u540e\u4ecd\u53ea\u6709\u4e00\u4e2a\u6743\u5a01\u8bcd\u8868",
    "\u4e0d\u6539\u52a8 scope history \u7684 --since \u524d\u5411\u57fa\u7ebf\u8bed\u4e49",
    "\u4e0d\u6539\u53d8 gate \u7684 phase \u8bed\u4e49\uff08pre-merge \u4e0e post-merge \u5404\u81ea\u7684\u53ef\u5408\u5e76\u96c6\u5408\uff09",
    "\u4e0d\u6539\u52a8 metrics \u4e8b\u4ef6\u7684 result \u8bcd\u8868 METRIC_RESULTS",
    "\u4e0d\u5f52\u4e00 final-result.json \u91cc\u7684 decision \u4e0e verdict \u5b57\u6bb5\uff1a\u5b83\u4eec\u4e0d\u88ab\u4efb\u4f55\u6821\u9a8c\u5668\u8bfb\u53d6\uff0c\u4e0d\u5c5e\u72b6\u6001\u8bcd\u8868"
  ],
  "allowed_paths": [
    "pipeline_tools/core.py",
    "pipeline_tools/__main__.py",
    "pipeline_tools/reconcile.py",
    "pipeline_tools/planning.py",
    "tests/test_evidence.py",
    "tests/test_cli.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "references/acceptance-evidence.md",
    "templates/pipeline-evidence.json"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-single-status-vocabulary",
    "requirement-status-normalization-backward-compatible",
    "requirement-legacy-status-values-normalized",
    "requirement-result-verify-final-role",
    "requirement-status-vocabulary-documented"
  ],
  "resources": [
    "pipeline_tools/core.py",
    "pipeline_tools/__main__.py",
    "pipeline_tools/reconcile.py",
    "pipeline_tools/planning.py",
    "tests/test_evidence.py",
    "tests/test_cli.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "references/acceptance-evidence.md",
    "templates/pipeline-evidence.json"
  ],
  "operations": [
    {
      "id": "op-unify-status-vocabulary",
      "kind": "unify-machine-status-vocabulary",
      "scope": "pipeline_tools",
      "resources": [
        "pipeline_tools/core.py",
        "pipeline_tools/reconcile.py",
        "pipeline_tools/planning.py"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-markdown-report-status-normalized",
        "acceptance-test-machine-result-status-normalized",
        "acceptance-test-legacy-status-values-normalized",
        "acceptance-test-legacy-report-status-value-normalized"
      ]
    },
    {
      "id": "op-cover-status-vocabulary",
      "kind": "add-status-vocabulary-tests",
      "scope": "tests",
      "resources": [
        "tests/test_evidence.py",
        "tests/test_cli.py"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-markdown-report-status-normalized",
        "acceptance-test-machine-result-status-normalized",
        "acceptance-test-result-verify-accepts-final-role",
        "acceptance-test-legacy-status-values-normalized",
        "acceptance-test-legacy-report-status-value-normalized"
      ]
    },
    {
      "id": "op-align-status-vocabulary-docs",
      "kind": "align-status-vocabulary-documentation",
      "scope": "references",
      "resources": [
        "references/acceptance-evidence.md",
        "templates/pipeline-evidence.json"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-status-vocabulary-documented"
      ]
    }
  ],
  "chain": {
    "entry": {
      "not_applicable": true,
      "reason": "planning-time machine contract check has no user-visible chain"
    },
    "interaction": {
      "not_applicable": true,
      "reason": "planning-time machine contract check has no user-visible chain"
    },
    "application": {
      "not_applicable": true,
      "reason": "planning-time machine contract check has no user-visible chain"
    },
    "domain": {
      "not_applicable": true,
      "reason": "planning-time machine contract check has no user-visible chain"
    },
    "persistence": {
      "not_applicable": true,
      "reason": "planning-time machine contract check has no user-visible chain"
    },
    "readback": {
      "not_applicable": true,
      "reason": "planning-time machine contract check has no user-visible chain"
    },
    "recovery": {
      "not_applicable": true,
      "reason": "planning-time machine contract check has no user-visible chain"
    }
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-markdown-report-status-normalized",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_gate_accepts_normalized_report_statuses",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_gate_accepts_normalized_report_statuses"
    },
    {
      "id": "acceptance-test-machine-result-status-normalized",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_result_verify_accepts_normalized_result_statuses",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_result_verify_accepts_normalized_result_statuses"
    },
    {
      "id": "acceptance-test-result-verify-accepts-final-role",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_result_verify_cli_accepts_final_role",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_result_verify_cli_accepts_final_role"
    },
    {
      "id": "acceptance-test-legacy-status-values-normalized",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions"
    },
    {
      "id": "acceptance-test-legacy-report-status-value-normalized",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report"
    },
    {
      "id": "acceptance-test-status-vocabulary-documented",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_document_one_status_vocabulary",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_document_one_status_vocabulary"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-existing-frozen-sheets-stay-valid",
      "status": "open",
      "source": "pipeline_tools/planning.py",
      "note": "the change applies to how statuses are read at verification time and must not retroactively invalidate already frozen task sheets or their recorded evidence"
    },
    {
      "id": "assumption-no-third-spelling",
      "status": "open",
      "source": "references/acceptance-evidence.md",
      "note": "normalization accepts the two existing legacy spellings and maps them onto pass, but must not introduce a new canonical spelling that neither side currently writes"
    },
    {
      "id": "assumption-shared-normalizer-single-source",
      "status": "open",
      "source": "pipeline_tools/core.py",
      "note": "one shared normalization table serves both the markdown-side reader (evidence_verify) and the JSON-side reader (verify_structured_result), so the two sides cannot drift apart again"
    }
  ],
  "unknowns": [],
  "non_user_completion_reason": "\u672c\u4efb\u52a1\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u5b8c\u6210\uff1a\u5b83\u628a markdown \u8bc1\u636e\u5757\u4e0e\u673a\u5668\u7ed3\u679c JSON \u4e24\u5957\u65b9\u5411\u76f8\u53cd\u7684\u72b6\u6001\u8bcd\u8868\u6536\u655b\u4e3a\u4e00\u5957\u5171\u4eab\u7684\u8bfb\u53d6\u4fa7\u5f52\u4e00\u8868\uff08\u542b\u5386\u53f2\u9057\u7559\u503c pass_with_conditions \u4e0e PASS_WITH_CONDITIONS \u5230 pass \u7684\u6620\u5c04\uff09\uff0c\u5e76\u8ba9 result verify \u80fd\u591f\u6821\u9a8c\u7ec8\u5ba1\u89d2\u8272\u7684\u673a\u5668\u7ed3\u679c\u3002\u4ea7\u7269\u662f\u88ab gate\u3001result verify\u3001evidence reconcile \u4e0e\u540e\u7eed\u6240\u6709\u4efb\u52a1\u6d88\u8d39\u7684\u673a\u68b0\u5e95\u5ea7\uff0c\u6ca1\u6709\u5916\u90e8\u5165\u53e3\u3001\u6ca1\u6709\u4ea4\u4e92\u9762\u3001\u4e5f\u6ca1\u6709\u53ef\u7531\u7528\u6237\u89e6\u53d1\u5e76\u89c2\u5bdf\u7684\u7ed3\u679c\uff0c\u56e0\u6b64\u4e0d\u80fd\u6807 vertical-feature\u3001repair \u6216 derived\uff1b\u540e\u7eed\u6d88\u8d39\u8be5\u5e95\u5ea7\u7684\u7528\u6237\u884c\u4e3a\u4efb\u52a1\u53e6\u884c\u89c4\u5212\u3002"
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`status-vocabulary-unification`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `pipeline_tools/core.py`
- `pipeline_tools/__main__.py`
- `pipeline_tools/reconcile.py`
- `pipeline_tools/planning.py`
- `tests/test_evidence.py`
- `tests/test_cli.py`
- `tests/test_acceptance_id_and_template_compliance.py`
- `references/acceptance-evidence.md`
- `templates/pipeline-evidence.json`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-single-status-vocabulary", "requirement-status-normalization-backward-compatible", "requirement-legacy-status-values-normalized", "requirement-result-verify-final-role", "requirement-status-vocabulary-documented"]
- 资源：["pipeline_tools/core.py", "pipeline_tools/__main__.py", "pipeline_tools/reconcile.py", "pipeline_tools/planning.py", "tests/test_evidence.py", "tests/test_cli.py", "tests/test_acceptance_id_and_template_compliance.py", "references/acceptance-evidence.md", "templates/pipeline-evidence.json"]
- 操作：["op-align-status-vocabulary-docs", "op-cover-status-vocabulary", "op-unify-status-vocabulary"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-markdown-report-status-normalized

- 测试：`tests/test_evidence.py: EvidenceTests.test_gate_accepts_normalized_report_statuses`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_gate_accepts_normalized_report_statuses`
- 证据等级：2

### 验收测试2：acceptance-test-machine-result-status-normalized

- 测试：`tests/test_evidence.py: EvidenceTests.test_result_verify_accepts_normalized_result_statuses`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_result_verify_accepts_normalized_result_statuses`
- 证据等级：2

### 验收测试3：acceptance-test-result-verify-accepts-final-role

- 测试：`tests/test_cli.py: CLITests.test_result_verify_cli_accepts_final_role`
- 命令：`python -m unittest tests.test_cli.CLITests.test_result_verify_cli_accepts_final_role`
- 证据等级：2

### 验收测试4：acceptance-test-legacy-status-values-normalized

- 测试：`tests/test_evidence.py: EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_result_verify_accepts_legacy_pass_with_conditions`
- 证据等级：2

### 验收测试5：acceptance-test-legacy-report-status-value-normalized

- 测试：`tests/test_evidence.py: EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_gate_accepts_legacy_pass_with_conditions_in_report`
- 证据等级：2

### 验收测试6：acceptance-test-status-vocabulary-documented

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_document_one_status_vocabulary`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_document_one_status_vocabulary`
- 证据等级：2

