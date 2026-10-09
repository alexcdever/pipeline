# metrics-tracking-policy：冻结任务单

<!-- Task ID: metrics-tracking-policy -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "metrics-tracking-policy",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "metrics-tracking-policy"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "do not change pipeline_tools/ production behaviour",
    "do not modify goal.md, IDEA.md, implement-plan.md",
    "do not delete the on-disk metrics files, only untrack them",
    "do not modify any frozen task sheet under docs/tasks/",
    "do not weaken the existing automatic-metrics collection tests beyond the policy change"
  ],
  "allowed_paths": [
    "references/",
    "tests/",
    ".gitignore"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-metrics-tracking-developer-choice",
    "requirement-repo-metrics-untracked",
    "requirement-metrics-tests-consistent"
  ],
  "resources": [
    "references/",
    "tests/",
    ".gitignore"
  ],
  "operations": [
    {
      "id": "op-neutralize-metrics-tracking-rule",
      "kind": "edit",
      "scope": "references",
      "resources": [
        "references/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-metrics-contract-tracking-optional",
        "acceptance-test-compat-doc-tracking-optional"
      ]
    },
    {
      "id": "op-untrack-repo-metrics",
      "kind": "edit",
      "scope": "repo",
      "resources": [
        ".gitignore"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-repo-metrics-untracked-and-ignored"
      ]
    },
    {
      "id": "op-align-metrics-tests",
      "kind": "edit",
      "scope": "tests",
      "resources": [
        "tests/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-suite-metrics-isolation-without-tracking"
      ]
    }
  ],
  "chain": {
    "entry": [
      "references/metrics-contract.md"
    ],
    "interaction": [
      "references/metrics-contract.md",
      "references/compat-and-migration.md"
    ],
    "application": [
      "references/metrics-contract.md"
    ],
    "domain": [
      "references/metrics-contract.md",
      "references/compat-and-migration.md"
    ],
    "persistence": [
      ".gitignore"
    ],
    "readback": [
      "tests/test_cli.py",
      "tests/test_acceptance_id_and_template_compliance.py"
    ],
    "recovery": [
      "tests/test_cli.py"
    ]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-metrics-contract-tracking-optional",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_tracking_is_developer_choice",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_tracking_is_developer_choice"
    },
    {
      "id": "acceptance-test-compat-doc-tracking-optional",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_tracking_is_developer_choice",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_tracking_is_developer_choice"
    },
    {
      "id": "acceptance-test-repo-metrics-untracked-and-ignored",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_repository_metrics_are_ignored_and_untracked",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_repository_metrics_are_ignored_and_untracked"
    },
    {
      "id": "acceptance-test-suite-metrics-isolation-without-tracking",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_cli_suite_does_not_write_repository_metrics",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_cli_suite_does_not_write_repository_metrics"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-developer-choice-applies-to-all-created-paths",
      "statement": "The developer-choice principle applies to every directory or file the pipeline creates, not only .pipeline/metrics/.",
      "status": "open",
      "source_id": "source-goal"
    },
    {
      "id": "assumption-metrics-files-stay-on-disk",
      "statement": "Untracking .pipeline/metrics/ keeps the on-disk files; only the Git index changes.",
      "status": "open",
      "source_id": "source-goal"
    }
  ],
  "unknowns": [
    {
      "id": "unknown-other-created-paths-tracking",
      "statement": "Whether other pipeline-created paths also need untracking in this repository is not yet decided; only .pipeline/metrics/ is in scope here.",
      "status": "non_blocking",
      "source_id": "source-goal"
    }
  ],
  "non_user_completion_reason": "prerequisite policy task with no user-facing step: completion is decided by the four declared automated acceptance tests plus the untracking of .pipeline/metrics/, so no interactive user approval or manual action is part of the finish line."
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`metrics-tracking-policy`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `references/`
- `tests/`
- `.gitignore`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-metrics-tracking-developer-choice", "requirement-repo-metrics-untracked", "requirement-metrics-tests-consistent"]
- 资源：["references/", "tests/", ".gitignore"]
- 操作：["op-align-metrics-tests", "op-neutralize-metrics-tracking-rule", "op-untrack-repo-metrics"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-metrics-contract-tracking-optional

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_tracking_is_developer_choice`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_tracking_is_developer_choice`
- 证据等级：2

### 验收测试2：acceptance-test-compat-doc-tracking-optional

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_tracking_is_developer_choice`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_tracking_is_developer_choice`
- 证据等级：2

### 验收测试3：acceptance-test-repo-metrics-untracked-and-ignored

- 测试：`tests/test_cli.py: CLITests.test_repository_metrics_are_ignored_and_untracked`
- 命令：`python -m unittest tests.test_cli.CLITests.test_repository_metrics_are_ignored_and_untracked`
- 证据等级：2

### 验收测试4：acceptance-test-suite-metrics-isolation-without-tracking

- 测试：`tests/test_cli.py: CLITests.test_cli_suite_does_not_write_repository_metrics`
- 命令：`python -m unittest tests.test_cli.CLITests.test_cli_suite_does_not_write_repository_metrics`
- 证据等级：2

