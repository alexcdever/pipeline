# gate-deletion-semantics：冻结任务单

<!-- Task ID: gate-deletion-semantics -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "gate-deletion-semantics",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "gate-deletion-semantics"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "\u4e0d\u91cd\u5199 Git \u5386\u53f2\uff1b\u5df2\u5408\u5e76\u7684\u6e05\u7406\u63d0\u4ea4\u4fdd\u7559\u5728\u539f\u4f4d",
    "\u4e0d\u4fee\u6539 goal.md\u3001IDEA.md\u3001implement-plan.md",
    "\u4e0d\u6e05\u7406\u6216\u5220\u9664 .pipeline/ \u4e0b\u4efb\u4f55\u5df2\u6709\u8bc1\u636e\u76ee\u5f55",
    "\u4e0d\u589e\u5220 RETAINED_EVIDENCE_NAMES \u7684\u6210\u5458",
    "\u4e0d\u6539\u52a8 .pipeline/metrics/ \u7684\u5386\u53f2\u8c41\u514d\u89c4\u5219",
    "\u4e0d\u6539\u52a8 scope history \u7684 --since \u524d\u5411\u57fa\u7ebf\u8bed\u4e49",
    "\u4e0d\u4fee\u6539 docs/tasks/ \u4e0b\u4efb\u4f55\u5df2\u51bb\u7ed3\u4efb\u52a1\u5355"
  ],
  "allowed_paths": [
    "pipeline_tools/**",
    "tests/**",
    "references/**"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-deletion-status-semantics",
    "requirement-deletion-acceptance-coverage",
    "requirement-retention-gate-docs-aligned"
  ],
  "resources": [
    "pipeline_tools/**",
    "tests/**",
    "references/**"
  ],
  "operations": [
    {
      "id": "op-fix-deletion-status-branch",
      "kind": "fix-evidence-history-status-semantics",
      "scope": "pipeline-tools",
      "resources": [
        "pipeline_tools/**"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-delete-non-retained-evidence-not-a-violation",
        "acceptance-test-delete-retained-evidence-is-a-violation",
        "acceptance-test-add-non-retained-evidence-still-violates"
      ]
    },
    {
      "id": "op-cover-deletion-semantics-with-tests",
      "kind": "add-and-migrate-evidence-history-tests",
      "scope": "tests",
      "resources": [
        "tests/**"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-delete-non-retained-evidence-not-a-violation",
        "acceptance-test-delete-retained-evidence-is-a-violation",
        "acceptance-test-add-non-retained-evidence-still-violates",
        "acceptance-test-forward-gate-guard-migrated"
      ]
    },
    {
      "id": "op-align-retention-gate-docs",
      "kind": "align-evidence-retention-documentation",
      "scope": "references",
      "resources": [
        "references/**"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-retention-gate-docs-aligned"
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
      "id": "acceptance-test-delete-non-retained-evidence-not-a-violation",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_delete_non_retained_evidence_is_not_a_violation",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation"
    },
    {
      "id": "acceptance-test-delete-retained-evidence-is-a-violation",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_delete_retained_evidence_is_a_violation",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_delete_retained_evidence_is_a_violation"
    },
    {
      "id": "acceptance-test-add-non-retained-evidence-still-violates",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_add_non_retained_evidence_still_violates",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_add_non_retained_evidence_still_violates"
    },
    {
      "id": "acceptance-test-forward-gate-guard-migrated",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_commit_history_check_evidence_path_guard",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard"
    },
    {
      "id": "acceptance-test-retention-gate-docs-aligned",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-add-modify-path-unchanged",
      "status": "open",
      "source": "pipeline_tools/core.py",
      "note": "the existing add/modify rule (violation when the basename is outside the retained set) is the intended behaviour and must not change"
    },
    {
      "id": "assumption-metrics-exemption-unchanged",
      "status": "open",
      "source": "references/acceptance-evidence.md",
      "note": "the .pipeline/metrics exemption is orthogonal to the delete/add split"
    }
  ],
  "unknowns": [],
  "non_user_completion_reason": "\u672c\u4efb\u52a1\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u5b8c\u6210\uff1a\u5b83\u4fee\u6b63\u65e2\u6709\u524d\u5411\u8bc1\u636e\u95f8\u95e8\u5bf9 Git \u72b6\u6001\u7684\u5224\u5b9a\uff0c\u4f7f\u5220\u9664\u975e\u4fdd\u7559\u8bc1\u636e\u6587\u4ef6\u4e0d\u518d\u88ab\u8bef\u5224\u4e3a\u8fdd\u89c4\uff0c\u540c\u65f6\u4fdd\u6301\u5220\u9664\u4fdd\u7559\u6587\u4ef6\u4e0e\u65b0\u589e\u975e\u4fdd\u7559\u6587\u4ef6\u4ecd\u7136\u8fdd\u89c4\uff0c\u5e76\u540c\u6b65\u8fc1\u79fb\u53d7\u5f71\u54cd\u7684\u65e2\u6709\u6d4b\u8bd5\u4e0e references \u6587\u6863\u3002\u4ea7\u7269\u662f\u88ab\u540e\u7eed\u89c4\u5212\u3001\u6267\u884c\u4e0e\u5408\u5e76\u95f8\u95e8\u6d88\u8d39\u7684\u673a\u68b0\u5e95\u5ea7\uff0c\u6ca1\u6709\u5916\u90e8\u5165\u53e3\u3001\u6ca1\u6709\u4ea4\u4e92\u9762\u3001\u4e5f\u6ca1\u6709\u53ef\u7531\u7528\u6237\u89e6\u53d1\u5e76\u89c2\u5bdf\u7684\u7ed3\u679c\uff0c\u56e0\u6b64\u4e0d\u80fd\u6807 vertical-feature \u6216 repair\uff1b\u540e\u7eed\u6d88\u8d39\u8be5\u5e95\u5ea7\u7684\u4efb\u52a1\u53e6\u884c\u89c4\u5212\u3002"
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`gate-deletion-semantics`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `pipeline_tools/**`
- `tests/**`
- `references/**`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-deletion-status-semantics", "requirement-deletion-acceptance-coverage", "requirement-retention-gate-docs-aligned"]
- 资源：["pipeline_tools/**", "tests/**", "references/**"]
- 操作：["op-align-retention-gate-docs", "op-cover-deletion-semantics-with-tests", "op-fix-deletion-status-branch"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-delete-non-retained-evidence-not-a-violation

- 测试：`tests/test_git_checks.py: GitChecks.test_delete_non_retained_evidence_is_not_a_violation`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation`
- 证据等级：2

### 验收测试2：acceptance-test-delete-retained-evidence-is-a-violation

- 测试：`tests/test_git_checks.py: GitChecks.test_delete_retained_evidence_is_a_violation`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_delete_retained_evidence_is_a_violation`
- 证据等级：2

### 验收测试3：acceptance-test-add-non-retained-evidence-still-violates

- 测试：`tests/test_git_checks.py: GitChecks.test_add_non_retained_evidence_still_violates`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_add_non_retained_evidence_still_violates`
- 证据等级：2

### 验收测试4：acceptance-test-forward-gate-guard-migrated

- 测试：`tests/test_git_checks.py: GitChecks.test_commit_history_check_evidence_path_guard`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard`
- 证据等级：2

### 验收测试5：acceptance-test-retention-gate-docs-aligned

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics`
- 证据等级：2

