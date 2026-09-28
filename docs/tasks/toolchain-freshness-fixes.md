# toolchain-freshness-fixes：冻结任务单

<!-- Task ID: toolchain-freshness-fixes -->
<!-- Generated from task-plan; contract fields are mechanically derived. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "toolchain-freshness-fixes",
  "task_type": "prerequisite",
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f",
    "planning_run_id": "toolchain-freshness-fixes"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u529f\u80fd\u94fe\u8def\uff1b\u672c\u4efb\u52a1\u53ea\u4fee\u6b63\u5de5\u5177\u94fe freshness \u5224\u5b9a\u7684\u4e24\u4e2a\u5047\u9633\u6027\u6839\u56e0",
    "\u4e0d\u91cd\u5199 Git \u5386\u53f2\uff1b\u5df2\u5408\u5e76\u7684\u6307\u6807\u4e0e\u8bc1\u636e\u63d0\u4ea4\u4fdd\u7559\u5728\u539f\u4f4d",
    "\u4e0d\u4fee\u6539 goal.md\u3001IDEA.md\u3001implement-plan.md",
    "\u4e0d\u4fee\u6539 docs/tasks/ \u4e0b\u4efb\u4f55\u5df2\u51bb\u7ed3\u4efb\u52a1\u5355",
    "\u4e0d\u65b0\u589e\u3001\u5220\u9664\u6216\u91cd\u547d\u540d RETAINED_EVIDENCE_NAMES \u7684\u6210\u5458",
    "\u4e0d\u6539\u53d8 .pipeline/metrics/ \u7684\u5165\u5e93\u89c4\u5219\uff0c\u53ea\u8ba9 evidence_only \u4e0e\u4e4b\u53e3\u5f84\u4e00\u81f4",
    "\u4e0d\u6539\u53d8 scope history \u7684 --since \u524d\u5411\u57fa\u7ebf\u8bed\u4e49",
    "\u4e0d\u4e3a\u7f3a\u9677 E \u6539\u52a8 planning.py \u6216 core.py \u7684 scope \u6a21\u578b\uff0c\u53ea\u5728\u672c\u4efb\u52a1\u5355\u5916\u53e6\u5f00\u89c4\u5212"
  ],
  "allowed_paths": [
    "pipeline_tools/core.py",
    "tests/test_evidence.py",
    "references/acceptance-evidence.md",
    "references/execution-and-review.md"
  ],
  "forbidden_paths": [
    "goal.md",
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/** existing history"
  ],
  "requirements": [
    "requirement-freshness-evidence-ref-basis",
    "requirement-freshness-evidence-ref-safety",
    "requirement-freshness-metrics-exemption",
    "requirement-freshness-real-drift-still-blocks",
    "requirement-freshness-docs-aligned"
  ],
  "resources": [
    "pipeline_tools/core.py",
    "tests/test_evidence.py",
    "references/acceptance-evidence.md",
    "references/execution-and-review.md"
  ],
  "operations": [
    {
      "id": "op-fix-acceptance-evidence-refs-basis",
      "kind": "fix-evidence-reference-resolution",
      "scope": "pipeline-tools",
      "resources": [
        "pipeline_tools/core.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-acceptance-evidence-refs-resolve-from-evidence-directory",
        "acceptance-test-acceptance-evidence-refs-still-reject-absolute-and-traversal"
      ]
    },
    {
      "id": "op-exempt-metrics-from-evidence-only",
      "kind": "fix-freshness-evidence-only-scope",
      "scope": "pipeline-tools",
      "resources": [
        "pipeline_tools/core.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-freshness-metrics-commit-keeps-evidence-only",
        "acceptance-test-freshness-product-drift-still-blocks"
      ]
    },
    {
      "id": "op-cover-freshness-fixes-with-tests",
      "kind": "add-and-migrate-freshness-tests",
      "scope": "tests",
      "resources": [
        "tests/test_evidence.py"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-acceptance-evidence-refs-resolve-from-evidence-directory",
        "acceptance-test-acceptance-evidence-refs-still-reject-absolute-and-traversal",
        "acceptance-test-freshness-metrics-commit-keeps-evidence-only",
        "acceptance-test-freshness-product-drift-still-blocks"
      ]
    },
    {
      "id": "op-align-freshness-docs",
      "kind": "align-freshness-documentation",
      "scope": "references",
      "resources": [
        "references/acceptance-evidence.md",
        "references/execution-and-review.md"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-freshness-docs-aligned"
      ]
    }
  ],
  "chain": {
    "entry": {
      "not_applicable": true,
      "reason": "toolchain defect repair declares no chain reference for this phase"
    },
    "interaction": {
      "not_applicable": true,
      "reason": "toolchain defect repair declares no chain reference for this phase"
    },
    "application": {
      "not_applicable": true,
      "reason": "toolchain defect repair declares no chain reference for this phase"
    },
    "domain": {
      "not_applicable": true,
      "reason": "toolchain defect repair declares no chain reference for this phase"
    },
    "persistence": {
      "not_applicable": true,
      "reason": "toolchain defect repair declares no chain reference for this phase"
    },
    "readback": {
      "not_applicable": true,
      "reason": "toolchain defect repair declares no chain reference for this phase"
    },
    "recovery": {
      "not_applicable": true,
      "reason": "toolchain defect repair declares no chain reference for this phase"
    }
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-acceptance-evidence-refs-resolve-from-evidence-directory",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory"
    },
    {
      "id": "acceptance-test-acceptance-evidence-refs-still-reject-absolute-and-traversal",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal"
    },
    {
      "id": "acceptance-test-freshness-metrics-commit-keeps-evidence-only",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_freshness_allows_metrics_only_commit_after_product_head",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_freshness_allows_metrics_only_commit_after_product_head"
    },
    {
      "id": "acceptance-test-freshness-product-drift-still-blocks",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_freshness_blocks_product_drift_from_product_head",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_freshness_blocks_product_drift_from_product_head"
    },
    {
      "id": "acceptance-test-freshness-docs-aligned",
      "evidence_level": 2,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis",
      "command_ref": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-commands-evidence-ref-basis-is-correct",
      "status": "open",
      "source": "pipeline_tools/core.py",
      "note": "commands[].evidence_ref \u6309\u8bc1\u636e\u76ee\u5f55\u76f8\u5bf9\u89e3\u6790\uff08_evidence_file_exists\uff09\u662f\u5df2\u786e\u8ba4\u7684\u6b63\u786e\u57fa\u51c6\uff0cacceptance[].evidence_refs \u5e94\u4e0e\u4e4b\u4e00\u81f4"
    },
    {
      "id": "assumption-metrics-are-workflow-metadata",
      "status": "open",
      "source": "references/metrics-contract.md",
      "note": ".pipeline/metrics/ \u662f\u53ef\u5165\u5e93\u7684\u5de5\u4f5c\u6d41\u5143\u6570\u636e\uff0cscope_check \u5df2\u6309\u6b64\u8c41\u514d\uff0cevidence_only \u5e94\u5bf9\u9f50"
    }
  ],
  "unknowns": [
    {
      "id": "unknown-full-test-suite-duration",
      "source": "tests/",
      "status": "non_blocking",
      "note": "\u5168\u91cf unittest \u5957\u4ef6\u7684\u5899\u949f\u65f6\u957f\u672a\u6d4b\u91cf\uff1b\u9a8c\u6536\u53ea\u7ed1\u5b9a\u5355\u6d4b\u7c92\u5ea6\u547d\u4ee4"
    }
  ],
  "non_user_completion_reason": "\u672c\u4efb\u52a1\u4e0d\u4ea4\u4ed8\u4efb\u4f55\u7528\u6237\u53ef\u89c2\u5bdf\u7684\u5b8c\u6210\uff1a\u5b83\u4fee\u6b63\u65e2\u6709\u8bc1\u636e\u65b0\u9c9c\u5ea6\u95f8\u95e8\u7684\u4e24\u4e2a\u5047\u9633\u6027\u6839\u56e0\u2014\u2014acceptance[].evidence_refs \u7684\u89e3\u6790\u57fa\u51c6\u4e0e commands[].evidence_ref \u4e0d\u4e00\u81f4\uff08\u7f3a\u9677 C\uff09\uff0c\u4ee5\u53ca evidence_only \u5224\u5b9a\u672a\u8c41\u514d .pipeline/metrics/\uff08\u7f3a\u9677 D\uff09\u3002\u4ea7\u7269\u662f\u88ab\u540e\u7eed\u89c4\u5212\u3001\u6267\u884c\u4e0e\u5408\u5e76\u95f8\u95e8\u6d88\u8d39\u7684\u673a\u68b0\u5e95\u5ea7\uff0c\u6ca1\u6709\u5916\u90e8\u5165\u53e3\u3001\u6ca1\u6709\u4ea4\u4e92\u9762\u3001\u4e5f\u6ca1\u6709\u53ef\u7531\u7528\u6237\u89e6\u53d1\u5e76\u89c2\u5bdf\u7684\u7ed3\u679c\uff0c\u56e0\u6b64\u4e0d\u80fd\u6807 vertical-feature \u6216 repair\uff1b\u540e\u7eed\u6d88\u8d39\u8be5\u5e95\u5ea7\u7684\u4efb\u52a1\u53e6\u884c\u89c4\u5212\u3002"
}
```

## 任务身份

- 任务类型：`prerequisite`
- planning-run-id：`toolchain-freshness-fixes`
- goal SHA-256：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`
- 状态：未开始

## 依赖与范围

### 允许修改

- `pipeline_tools/core.py`
- `tests/test_evidence.py`
- `references/acceptance-evidence.md`
- `references/execution-and-review.md`

### 明确不改

- `goal.md`
- `implement-plan.md`
- `IDEA.md`
- 已有任务单和历史规划证据

## 任务计划映射

- 需求：["requirement-freshness-evidence-ref-basis", "requirement-freshness-evidence-ref-safety", "requirement-freshness-metrics-exemption", "requirement-freshness-real-drift-still-blocks", "requirement-freshness-docs-aligned"]
- 资源：["pipeline_tools/core.py", "tests/test_evidence.py", "references/acceptance-evidence.md", "references/execution-and-review.md"]
- 操作：["op-align-freshness-docs", "op-cover-freshness-fixes-with-tests", "op-exempt-metrics-from-evidence-only", "op-fix-acceptance-evidence-refs-basis"]
- 依赖：[]

## 验收测试

### 验收测试1：acceptance-test-acceptance-evidence-refs-resolve-from-evidence-directory

- 测试：`tests/test_evidence.py: EvidenceTests.test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_resolve_from_evidence_directory`
- 证据等级：2

### 验收测试2：acceptance-test-acceptance-evidence-refs-still-reject-absolute-and-traversal

- 测试：`tests/test_evidence.py: EvidenceTests.test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_freshness_acceptance_evidence_refs_still_reject_absolute_and_traversal`
- 证据等级：2

### 验收测试3：acceptance-test-freshness-metrics-commit-keeps-evidence-only

- 测试：`tests/test_evidence.py: EvidenceTests.test_freshness_allows_metrics_only_commit_after_product_head`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_freshness_allows_metrics_only_commit_after_product_head`
- 证据等级：2

### 验收测试4：acceptance-test-freshness-product-drift-still-blocks

- 测试：`tests/test_evidence.py: EvidenceTests.test_freshness_blocks_product_drift_from_product_head`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_freshness_blocks_product_drift_from_product_head`
- 证据等级：2

### 验收测试5：acceptance-test-freshness-docs-aligned

- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis`
- 命令：`python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_execution_and_review_documents_freshness_resolution_basis`
- 证据等级：2

