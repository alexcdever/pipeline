# evidence-retention-forward-gate：冻结任务单

<!-- Task ID: evidence-retention-forward-gate -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "evidence-retention-forward-gate",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "evidence-retention-forward-gate"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "\u4e0d\u91cd\u5199 Git \u5386\u53f2\uff1b2026-09-25 \u7684 9 \u4e2a\u8fdb\u5ea6\u65e5\u5fd7\u63d0\u4ea4\u4fdd\u7559\u5728 origin/main\uff0c\u53ea\u589e\u52a0\u524d\u5411\u57fa\u7ebf\u95f8\u95e8",
    "\u4e0d\u4fee\u6539 goal.md\u3001IDEA.md\u3001implement-plan.md",
    "\u4e0d\u81ea\u52a8\u5408\u5e76\u5206\u652f\u3001\u4e0d\u521b\u5efa\u6216\u5220\u9664 worktree\u3001\u4e0d\u6267\u884c git push",
    "\u4e0d\u5220\u9664\u6216\u6539\u5199 .pipeline/metrics/ \u4e0b\u4efb\u4f55\u5df2\u5165\u5e93\u7684\u6307\u6807\u6587\u4ef6",
    "\u4e0d\u5220\u9664\u4efb\u52a1\u8bc1\u636e\u76ee\u5f55\u4e2d\u7684 7 \u4e2a\u4fdd\u7559\u6587\u4ef6\uff1aexecutor-report.md\u3001review-report.md\u3001final-check.md\u3001executor-result.json\u3001reviewer-result.json\u3001final-result.json\u3001finalization.json",
    "\u4e0d\u4fee\u6539 .gitignore\uff1b.pipeline/metrics/ \u672c\u5c31\u4e0d\u5728\u5176\u6392\u9664\u89c4\u5219\u4e2d",
    "\u4e0d\u6539\u52a8 docs/tasks/ \u4e0b\u4efb\u4f55\u5df2\u51bb\u7ed3\u4efb\u52a1\u5355",
    "\u4e0d\u628a\u88c1\u51b3\u8bb0\u5f55\u5199\u5165 .pipeline/ \u4e0b\u4efb\u4f55\u8bc1\u636e\u76ee\u5f55\uff0c\u907f\u514d\u88ab\u540c\u4e00\u95f8\u95e8\u5224\u4e3a\u81ea\u6307\u8fdd\u89c4",
    "\u4e0d\u5f31\u5316 contract.py \u7684\u673a\u68b0\u95f8\u95e8\uff0c\u4e5f\u4e0d\u628a scripts/validate_task_sheet.py \u63d0\u5347\u4e3a\u6743\u5a01\u9a8c\u6536\u95f8\u95e8"
  ],
  "allowed_paths": [
    ".pipeline/planning-run-lifecycle/",
    ".pipeline/pipeline-tools-v1/",
    ".pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/",
    ".pipeline/implement-plan-coverage-repair-continuation-2/",
    ".pipeline/planning-driven-vertical-pipeline/",
    ".pipeline/task-evidence-reconcile/",
    "pipeline_tools/**",
    "scripts/**",
    "tests/**",
    "references/**",
    ".pipeline/metrics/"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-retained-evidence-set",
    "requirement-scope-history-baseline-gate",
    "requirement-references-contract-alignment",
    "requirement-metrics-tracked-in-git",
    "requirement-task-sheet-validator-schema4",
    "requirement-generated-forbidden-paths-consistent"
  ],
  "resources": [
    ".pipeline/planning-run-lifecycle/",
    ".pipeline/pipeline-tools-v1/",
    ".pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/",
    ".pipeline/implement-plan-coverage-repair-continuation-2/",
    ".pipeline/planning-driven-vertical-pipeline/",
    ".pipeline/task-evidence-reconcile/",
    "pipeline_tools/**",
    "scripts/**",
    "tests/**",
    "references/**",
    ".pipeline/metrics/"
  ],
  "operations": [
    {
      "id": "op-delete-drifted-evidence",
      "kind": "delete-drifted-evidence",
      "scope": "task-evidence-directories",
      "resources": [
        ".pipeline/planning-run-lifecycle/",
        ".pipeline/pipeline-tools-v1/",
        ".pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/",
        ".pipeline/implement-plan-coverage-repair-continuation-2/",
        ".pipeline/planning-driven-vertical-pipeline/",
        ".pipeline/task-evidence-reconcile/"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-retained-evidence-contract",
        "acceptance-test-repository-evidence-only-retained"
      ]
    },
    {
      "id": "op-add-since-baseline-gate",
      "kind": "add-forward-baseline-gate",
      "scope": "pipeline-tools",
      "resources": [
        "pipeline_tools/**",
        "tests/**"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-since-baseline-ignores-earlier-history",
        "acceptance-test-default-history-scan-unchanged",
        "acceptance-test-scope-history-cli-since"
      ]
    },
    {
      "id": "op-align-references-contract",
      "kind": "align-contract-documentation",
      "scope": "references",
      "resources": [
        "references/**",
        "tests/**"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-references-evidence-contract-aligned"
      ]
    },
    {
      "id": "op-commit-pipeline-metrics",
      "kind": "track-generated-metrics",
      "scope": "repository-evidence",
      "resources": [
        ".pipeline/metrics/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-metrics-tracked-not-ignored"
      ]
    },
    {
      "id": "op-update-task-sheet-validator",
      "kind": "align-validator-with-schema4",
      "scope": "scripts",
      "resources": [
        "scripts/**",
        "tests/**"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-task-sheet-script-schema4"
      ]
    },
    {
      "id": "op-decouple-generated-forbidden-paths",
      "kind": "align-generated-contract-with-scope",
      "scope": "pipeline-tools",
      "resources": [
        "pipeline_tools/**",
        "tests/**"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-forbidden-paths-scope-consistent"
      ]
    }
  ],
  "chain": {
    "entry": {
      "not_applicable": true,
      "reason": "mechanical tooling prerequisite has no user-visible chain"
    },
    "interaction": {
      "not_applicable": true,
      "reason": "mechanical tooling prerequisite has no user-visible chain"
    },
    "application": {
      "not_applicable": true,
      "reason": "mechanical tooling prerequisite has no user-visible chain"
    },
    "domain": {
      "not_applicable": true,
      "reason": "mechanical tooling prerequisite has no user-visible chain"
    },
    "persistence": {
      "not_applicable": true,
      "reason": "mechanical tooling prerequisite has no user-visible chain"
    },
    "readback": {
      "not_applicable": true,
      "reason": "mechanical tooling prerequisite has no user-visible chain"
    },
    "recovery": {
      "not_applicable": true,
      "reason": "mechanical tooling prerequisite has no user-visible chain"
    }
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-retained-evidence-contract",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_commit_history_check_keeps_exactly_the_documented_retained_names",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_keeps_exactly_the_documented_retained_names"
    },
    {
      "id": "acceptance-test-repository-evidence-only-retained",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_tracked_pipeline_evidence_contains_only_retained_names",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_tracked_pipeline_evidence_contains_only_retained_names"
    },
    {
      "id": "acceptance-test-since-baseline-ignores-earlier-history",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_scope_history_since_baseline_ignores_earlier_violations",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_scope_history_since_baseline_ignores_earlier_violations"
    },
    {
      "id": "acceptance-test-default-history-scan-unchanged",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_commit_history_check_evidence_path_guard",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard"
    },
    {
      "id": "acceptance-test-scope-history-cli-since",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_scope_history_cli_since_passes_baseline_and_reports_drift",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_scope_history_cli_since_passes_baseline_and_reports_drift"
    },
    {
      "id": "acceptance-test-references-evidence-contract-aligned",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_evidence_retention_contract_matches_forward_gate",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_evidence_retention_contract_matches_forward_gate"
    },
    {
      "id": "acceptance-test-metrics-tracked-not-ignored",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_tracked_metrics_are_workflow_metadata and GitChecks.test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_tracked_metrics_are_workflow_metadata tests.test_git_checks.GitChecks.test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt"
    },
    {
      "id": "acceptance-test-task-sheet-script-schema4",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_validate_task_sheet_script_accepts_schema4_sheet",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_validate_task_sheet_script_accepts_schema4_sheet"
    },
    {
      "id": "acceptance-test-forbidden-paths-scope-consistent",
      "evidence_level": 2,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generated_schema4_forbidden_paths_do_not_contradict_task_scope",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generated_schema4_forbidden_paths_do_not_contradict_task_scope"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-drifted-evidence-enumerated-at-execution",
      "status": "open",
      "source": "goal.md"
    },
    {
      "id": "assumption-metrics-untracked-count-grows",
      "status": "open",
      "source": "references/metrics-contract.md"
    },
    {
      "id": "assumption-nine-progress-log-commits-remain",
      "status": "open",
      "source": "goal.md"
    }
  ],
  "unknowns": [],
  "non_user_completion_reason": "\u672c\u4efb\u52a1\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u5b8c\u6210\uff1a\u5b83\u6e05\u7406\u4ed3\u5e93\u91cc\u5df2\u6f02\u79fb\u7684\u6d41\u7a0b\u8bc1\u636e\u3001\u7ed9\u65e2\u6709 scope history \u5b50\u547d\u4ee4\u8865\u4e00\u4e2a\u53ef\u9009 --since \u524d\u5411\u57fa\u7ebf\u95f8\u95e8\u3001\u628a\u8bc1\u636e\u4fdd\u7559\u89c4\u5219\u5199\u6210 references/ \u660e\u6587\u5951\u7ea6\u3001\u4fee\u6b63\u53ea\u505a\u7ed3\u6784\u68c0\u67e5\u7684 scripts/validate_task_sheet.py \u4f7f\u5176\u4e0e schema 4 \u4e00\u81f4\u3001\u5e76\u8ba9\u751f\u6210\u5668\u5199\u51fa\u7684 forbidden_paths \u4e0e\u4efb\u52a1\u8303\u56f4\u4e0d\u518d\u81ea\u76f8\u77db\u76fe\u3002\u4ea7\u7269\u662f\u88ab\u540e\u7eed\u89c4\u5212\u3001\u6d3e\u53d1\u4e0e\u5408\u5e76\u95f8\u95e8\u6d88\u8d39\u7684\u673a\u68b0\u5e95\u5ea7\uff0c\u6ca1\u6709\u5916\u90e8\u5165\u53e3\u3001\u6ca1\u6709\u4ea4\u4e92\u9762\u3001\u4e5f\u6ca1\u6709\u53ef\u7531\u7528\u6237\u89e6\u53d1\u5e76\u89c2\u5bdf\u7684\u7ed3\u679c\uff0c\u56e0\u6b64\u4e0d\u80fd\u6807 vertical-feature \u6216 repair\uff1b\u540e\u7eed\u6d88\u8d39\u8be5\u5e95\u5ea7\u7684\u7528\u6237\u884c\u4e3a\u4efb\u52a1\u53e6\u884c\u89c4\u5212\u3002"
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`evidence-retention-forward-gate`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `.pipeline/planning-run-lifecycle/`
- `.pipeline/pipeline-tools-v1/`
- `.pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/`
- `.pipeline/implement-plan-coverage-repair-continuation-2/`
- `.pipeline/planning-driven-vertical-pipeline/`
- `.pipeline/task-evidence-reconcile/`
- `pipeline_tools/**`
- `scripts/**`
- `tests/**`
- `references/**`
- `.pipeline/metrics/`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-retained-evidence-set", "requirement-scope-history-baseline-gate", "requirement-references-contract-alignment", "requirement-metrics-tracked-in-git", "requirement-task-sheet-validator-schema4", "requirement-generated-forbidden-paths-consistent"]
- 资源：[".pipeline/planning-run-lifecycle/", ".pipeline/pipeline-tools-v1/", ".pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/", ".pipeline/implement-plan-coverage-repair-continuation-2/", ".pipeline/planning-driven-vertical-pipeline/", ".pipeline/task-evidence-reconcile/", "pipeline_tools/**", "scripts/**", "tests/**", "references/**", ".pipeline/metrics/"]
- 操作：["op-add-since-baseline-gate", "op-align-references-contract", "op-commit-pipeline-metrics", "op-decouple-generated-forbidden-paths", "op-delete-drifted-evidence", "op-update-task-sheet-validator"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-retained-evidence-contract

- 测试：`tests/test_git_checks.py: GitChecks.test_commit_history_check_keeps_exactly_the_documented_retained_names`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_keeps_exactly_the_documented_retained_names`
- 证据等级：2

### 验收测试2：acceptance-test-repository-evidence-only-retained

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_tracked_pipeline_evidence_contains_only_retained_names`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_tracked_pipeline_evidence_contains_only_retained_names`
- 证据等级：2

### 验收测试3：acceptance-test-since-baseline-ignores-earlier-history

- 测试：`tests/test_git_checks.py: GitChecks.test_scope_history_since_baseline_ignores_earlier_violations`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_scope_history_since_baseline_ignores_earlier_violations`
- 证据等级：2

### 验收测试4：acceptance-test-default-history-scan-unchanged

- 测试：`tests/test_git_checks.py: GitChecks.test_commit_history_check_evidence_path_guard`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard`
- 证据等级：2

### 验收测试5：acceptance-test-scope-history-cli-since

- 测试：`tests/test_cli.py: CLITests.test_scope_history_cli_since_passes_baseline_and_reports_drift`
- 命令：`python -m unittest tests.test_cli.CLITests.test_scope_history_cli_since_passes_baseline_and_reports_drift`
- 证据等级：2

### 验收测试6：acceptance-test-references-evidence-contract-aligned

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_evidence_retention_contract_matches_forward_gate`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_evidence_retention_contract_matches_forward_gate`
- 证据等级：2

### 验收测试7：acceptance-test-metrics-tracked-not-ignored

- 测试：`tests/test_git_checks.py: GitChecks.test_tracked_metrics_are_workflow_metadata and GitChecks.test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_tracked_metrics_are_workflow_metadata tests.test_git_checks.GitChecks.test_repository_evidence_hygiene_keeps_only_canonical_metrics_exempt`
- 证据等级：2

### 验收测试8：acceptance-test-task-sheet-script-schema4

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_validate_task_sheet_script_accepts_schema4_sheet`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_validate_task_sheet_script_accepts_schema4_sheet`
- 证据等级：2

### 验收测试9：acceptance-test-forbidden-paths-scope-consistent

- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generated_schema4_forbidden_paths_do_not_contradict_task_scope`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_generated_schema4_forbidden_paths_do_not_contradict_task_scope`
- 证据等级：2

