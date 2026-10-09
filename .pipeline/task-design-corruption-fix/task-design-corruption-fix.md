# task-design-corruption-fix：冻结任务单

<!-- Task ID: task-design-corruption-fix -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "task-design-corruption-fix",
  "task_type": "derived",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "task-design-corruption-fix"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "Do not modify pipeline_tools, goal files, frozen task sheets, .pipeline evidence, or historical evidence reports.",
    "Do not rewrite task-design content beyond replacing the three U+FFFD characters with \u8bfb\u53d6.",
    "Do not fix historical U+FFFD occurrences in this task."
  ],
  "allowed_paths": [
    "references/",
    "tests/"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-task-design-utf8-clean",
    "requirement-task-design-corruption-guard"
  ],
  "resources": [
    "references/",
    "tests/"
  ],
  "operations": [
    {
      "id": "op-repair-task-design-text",
      "kind": "edit",
      "scope": "references",
      "resources": [
        "references/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-task-design-has-no-replacement-character"
      ]
    },
    {
      "id": "op-add-task-design-corruption-test",
      "kind": "edit",
      "scope": "tests",
      "resources": [
        "tests/"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-task-design-has-no-replacement-character"
      ]
    }
  ],
  "chain": {
    "entry": [
      "references/task-design.md"
    ],
    "interaction": [
      "references/task-design.md"
    ],
    "application": [
      "references/task-design.md"
    ],
    "domain": [
      "references/task-design.md"
    ],
    "persistence": [
      "references/task-design.md"
    ],
    "readback": [
      "references/task-design.md"
    ],
    "recovery": [
      "references/task-design.md"
    ]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-task-design-has-no-replacement-character",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_task_design_contains_no_replacement_character",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_contains_no_replacement_character"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-preserve-task-design-wording",
      "statement": "Only the three replacement characters are corrupted; intended wording is \u8bfb\u53d6 and surrounding wording must remain unchanged.",
      "status": "open",
      "source_id": "source-task-design"
    },
    {
      "id": "assumption-existing-test-host",
      "statement": "The named existing test module is the intended location for one regression test.",
      "status": "open",
      "source_id": "source-tests"
    }
  ],
  "unknowns": [
    {
      "id": "unknown-historical-corruption",
      "statement": "Historical U+FFFD occurrences outside the active references/task-design.md file are not in scope and are not fixed by this task.",
      "status": "non_blocking",
      "source_id": "source-task-design"
    }
  ],
  "derived_from": {
    "task_id": "metrics-tracking-policy-continuation-1",
    "commit": "b8295e9e98b96e0e1c0fda658dc57eae8075459d",
    "branch": "metrics-tracking-policy-continuation-1",
    "parent_task_type": "derived"
  }
}
```

## 任务身份

- 任务类型：`derived`
- planning-run-id：`task-design-corruption-fix`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `references/`
- `tests/`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-task-design-utf8-clean", "requirement-task-design-corruption-guard"]
- 资源：["references/", "tests/"]
- 操作：["op-add-task-design-corruption-test", "op-repair-task-design-text"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-task-design-has-no-replacement-character

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_task_design_contains_no_replacement_character`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_contains_no_replacement_character`
- 证据等级：2

