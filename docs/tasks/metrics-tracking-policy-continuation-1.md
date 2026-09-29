# metrics-tracking-policy-continuation-1：冻结任务单

<!-- Task ID: metrics-tracking-policy-continuation-1 -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "metrics-tracking-policy-continuation-1",
  "task_type": "derived",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "metrics-tracking-policy-continuation-1"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "do not change pipeline_tools/ production behaviour",
    "do not modify goal.md, IDEA.md, implement-plan.md",
    "do not modify any frozen task sheet under docs/tasks/",
    "do not re-add any statement that metrics must be tracked",
    "do not re-track .pipeline/metrics/"
  ],
  "allowed_paths": [
    "README.md",
    "tests/"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-readme-metrics-policy-aligned",
    "requirement-readme-metrics-guarded-by-test"
  ],
  "resources": [
    "README.md",
    "tests/"
  ],
  "operations": [
    {
      "id": "op-align-readme-metrics-policy",
      "kind": "edit",
      "scope": "docs",
      "resources": [
        "README.md"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-readme-documents-tracking-is-developer-choice"
      ]
    },
    {
      "id": "op-guard-readme-metrics-policy",
      "kind": "edit",
      "scope": "tests",
      "resources": [
        "tests/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-readme-documents-tracking-is-developer-choice"
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
      "id": "acceptance-test-readme-documents-tracking-is-developer-choice",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_readme_documents_metrics_tracking_is_developer_choice",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_readme_documents_metrics_tracking_is_developer_choice"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-readme-wording-only",
      "statement": "Only the three stale README lines need rewording; no other README statement depends on the removed mandate.",
      "status": "open",
      "source_id": "source-readme"
    },
    {
      "id": "assumption-existing-test-file-accepts-new-case",
      "statement": "tests/test_acceptance_id_and_template_compliance.py already follows the doc-contract test idiom and can host one new guarding test method.",
      "status": "open",
      "source_id": "source-tests"
    }
  ],
  "unknowns": [
    {
      "id": "unknown-other-docs-restate-mandate",
      "statement": "Whether any file outside README.md also restates the removed tracking mandate is not verified; only README.md is in scope here.",
      "status": "non_blocking",
      "source_id": "source-goal"
    }
  ],
  "derived_from": {
    "task_id": "metrics-tracking-policy",
    "commit": "cf8f00e7b0328a5ea0afe1a2e7be9ae68c1c5443",
    "branch": "metrics-tracking-policy",
    "parent_task_type": "prerequisite"
  }
}
```

## 任务身份

- 任务类型：`derived`
- planning-run-id：`metrics-tracking-policy-continuation-1`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `README.md`
- `tests/`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-readme-metrics-policy-aligned", "requirement-readme-metrics-guarded-by-test"]
- 资源：["README.md", "tests/"]
- 操作：["op-align-readme-metrics-policy", "op-guard-readme-metrics-policy"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-readme-documents-tracking-is-developer-choice

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_readme_documents_metrics_tracking_is_developer_choice`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_readme_documents_metrics_tracking_is_developer_choice`
- 证据等级：2

