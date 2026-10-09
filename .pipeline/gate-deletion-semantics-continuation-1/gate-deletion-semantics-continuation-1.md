# gate-deletion-semantics-continuation-1：派生记录（已交付扩张追补）

<!-- Task ID: gate-deletion-semantics-continuation-1 -->

<!-- 本任务单为手工撰写，非 generate-task-sheets 产出；planning 审计链缺失，详见「任务身份」。 -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "gate-deletion-semantics-continuation-1",
  "task_type": "derived",
  "derived_from": {
    "task_id": "gate-deletion-semantics",
    "commit": "1ed6c8b3d96e03fb2777b585901796da3eef1783",
    "branch": "gate-deletion-semantics",
    "parent_task_type": "prerequisite"
  },
  "goal": {
    "path": "goal.md",
    "sha256": "9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f"
  },
  "risk": "medium",
  "project_type": "cli",
  "non_goals": [
    "不重写 Git 历史；已合并的扩张提交保留在原位",
    "不修改 goal.md、IDEA.md、implement-plan.md",
    "不修改 docs/tasks/ 下任何已冻结任务单，包括父任务单 docs/tasks/gate-deletion-semantics.md",
    "不修改 pipeline_tools/ 的任何语义或实现",
    "不删除、不改写 .pipeline/metrics/ 下的历史豁免记录",
    "不删除或改写 .pipeline/gate-deletion-semantics/ 下的既有证据与终审报告",
    "本任务只读，不修改任何测试文件、参考文档或产品代码"
  ],
  "allowed_paths": [
    "docs/tasks/gate-deletion-semantics-continuation-1.md",
    "tests/test_evidence.py",
    "tests/test_git_checks.py"
  ],
  "forbidden_paths": [
    "goal.md",
    "IDEA.md",
    "implement-plan.md",
    "pipeline_tools/**",
    "docs/tasks/gate-deletion-semantics.md",
    ".pipeline/**"
  ],
  "requirements": [
    "requirement-deletion-status-semantics",
    "requirement-deletion-acceptance-coverage",
    "requirement-retention-gate-docs-aligned"
  ],
  "resources": [
    "docs/tasks/gate-deletion-semantics-continuation-1.md",
    "tests/test_evidence.py",
    "tests/test_git_checks.py"
  ],
  "operations": [
    {
      "id": "op-record-deletion-semantics-delivery",
      "kind": "record-completed-derived-delivery",
      "scope": "task-sheet",
      "resources": [
        "docs/tasks/gate-deletion-semantics-continuation-1.md"
      ],
      "resource_mode": "single",
      "acceptance_tests": [
        "acceptance-test-delete-non-retained-evidence-is-not-a-violation"
      ]
    },
    {
      "id": "op-verify-evidence-hardening",
      "kind": "verify-completed-evidence-hardening",
      "scope": "tests",
      "resources": [
        "tests/test_evidence.py",
        "tests/test_git_checks.py"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-declared-expected-exit-code-allows-nonzero-result",
        "acceptance-test-gate-rejects-boolean-expected-exit-code",
        "acceptance-test-evidence-block-parses-with-other-code-fences",
        "acceptance-test-delete-non-retained-evidence-is-not-a-violation"
      ]
    }
  ],
  "chain": {
    "entry": {
      "not_applicable": true,
      "reason": "parent task type is prerequisite, so no chain reference is required for this phase"
    },
    "interaction": {
      "not_applicable": true,
      "reason": "parent task type is prerequisite, so no chain reference is required for this phase"
    },
    "application": {
      "not_applicable": true,
      "reason": "parent task type is prerequisite, so no chain reference is required for this phase"
    },
    "domain": {
      "not_applicable": true,
      "reason": "parent task type is prerequisite, so no chain reference is required for this phase"
    },
    "persistence": {
      "not_applicable": true,
      "reason": "parent task type is prerequisite, so no chain reference is required for this phase"
    },
    "readback": {
      "not_applicable": true,
      "reason": "parent task type is prerequisite, so no chain reference is required for this phase"
    },
    "recovery": {
      "not_applicable": true,
      "reason": "parent task type is prerequisite, so no chain reference is required for this phase"
    }
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-declared-expected-exit-code-allows-nonzero-result",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_declared_expected_exit_code_allows_nonzero_result",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_declared_expected_exit_code_allows_nonzero_result"
    },
    {
      "id": "acceptance-test-gate-rejects-boolean-expected-exit-code",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_gate_rejects_boolean_expected_exit_code",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_gate_rejects_boolean_expected_exit_code"
    },
    {
      "id": "acceptance-test-evidence-block-parses-with-other-code-fences",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_evidence_block_parses_when_body_contains_other_code_fences",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_evidence_block_parses_when_body_contains_other_code_fences"
    },
    {
      "id": "acceptance-test-delete-non-retained-evidence-is-not-a-violation",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_delete_non_retained_evidence_is_not_a_violation",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [
    2
  ],
  "assumptions": [
    {
      "id": "assumption-parent-tip-is-delivery-endpoint",
      "status": "open",
      "source": "docs/tasks/gate-deletion-semantics.md",
      "note": "1ed6c8b is the parent branch tip and the completion commit of the parent task; the parent task sheet content is identical at 692ee63 and 1ed6c8b"
    },
    {
      "id": "assumption-merged-branch-retained",
      "status": "open",
      "source": ".git/refs/heads/gate-deletion-semantics",
      "note": "the parent branch gate-deletion-semantics still exists after the merge and is used verbatim as the historical derived_from.branch value"
    }
  ],
  "unknowns": [
    {
      "id": "unknown-commands-array-restoration-has-no-test",
      "status": "open",
      "source": "89835f0",
      "note": "the four restored commands[] entries have no identifiable existing test asserting their presence; item 1 is recorded as fact only"
    },
    {
      "id": "unknown-gitattributes-has-no-test",
      "status": "open",
      "source": "b7ae0cc, 8d677b0",
      "note": "no test in tests/ reads .gitattributes or asserts its LF policy; item 5 is recorded as fact only"
    },
    {
      "id": "unknown-line-ending-normalization-has-no-test",
      "status": "open",
      "source": "8d677b0",
      "note": "no test in tests/ asserts renormalization or eol of the 15 tracked .pipeline/ files; item 6 is recorded as fact only"
    }
  ],
  "non_user_completion_reason": "本任务是一张追补的派生记录单，不交付任何用户可观察的完成：它把父任务 gate-deletion-semantics 在冻结契约之外已经交付、且经终审裁定为「不违反 goal.md 但本应开派生单」的扩张，补记为一张可机械核验的 derived 任务单。产物是被后续审计消费的文档与已存在测试的只读核验，没有外部入口、没有交互面，也没有可由用户触发并观察的结果。"
}
```

## 任务身份

- 任务类型：`derived`（派生记录 / 追补）
- 父任务：`gate-deletion-semantics`（`prerequisite`，已合并）
- 状态：未开始
- 本任务是一张**追补的派生记录单**，不是新功能、不是修复，也不代表用户功能完成。

### 为什么手工撰写

本单经**手工撰写**，**非** `generate-task-sheets` 产出，**planning 审计链缺失**：契约块中没有真实的 `planning_run_id`，也没有对应的 `.pipeline/<task-id>/` 规划阶段记录。这是有意为之——生成器路径已被核验为不可行，两条机械阻塞为：

1. `pipeline_tools/planning.py:1606-1635` 的 `_task_sheet_text` 构造的 18 个键里没有 `derived_from`，也没有 derived 分支，生成器必然产出缺 `derived_from` 的 schema 4 单，`validate_task` 会拒绝。
2. `pipeline_tools/planning.py:1110` 的 `validate_task_plan` 要求 `parent_task_id` 落在同一 `tasks` 数组内；父任务属上一轮已合并，放进数组会撞 `pipeline_tools/planning.py:1701` 的 `task sheet already exists`。

先例：`docs/tasks/derived-task-dispatch-recovery.md` 同样是手工撰写（schema 2，无 `derived_from`，来自 `a818e08`）。仓库中没有任何 derived 单是经生成器产出的。

### derived_from 四字段含义

- `task_id` = `gate-deletion-semantics`：父任务的 task-id。
- `commit` = `1ed6c8b3d96e03fb2777b585901796da3eef1783`：父任务分支 tip，也是父任务交付的终点提交。父任务单在 `692ee63` 与 `1ed6c8b` 都存在且内容未变，两者都能过父单核对；取 `1ed6c8b` 语义最准。
- `branch` = `gate-deletion-semantics`：历史准确的父任务分支名，合并后仍保留。
- `parent_task_type` = `prerequisite`：父任务契约的 `task_type`。因为父类型是 `prerequisite`，`contract.py:167-180` 的 `_requires_full_chain` 返回 `False`，所以本单 `chain` 七段全部使用 `{"not_applicable": true, "reason": "..."}`。

## 依赖与范围

### 允许修改

- `docs/tasks/gate-deletion-semantics-continuation-1.md`（本单自身）
- `tests/test_evidence.py`（仅只读核验）
- `tests/test_git_checks.py`（仅只读核验）

### 明确不改

**本任务只读，不修改任何文件。** 上述 `tests/**` 条目只是被只读执行以取得核验证据，不产生任何写入；`allowed_paths` 列出它们是为了让核验 operation 的资源可追溯，并不授权改动。

- `goal.md`、`IDEA.md`、`implement-plan.md`
- `pipeline_tools/**` 的任何语义或实现
- `docs/tasks/gate-deletion-semantics.md`（父任务冻结单）及 `docs/tasks/` 下其他任何已冻结任务单
- `.pipeline/**` 下任何既有证据、终审报告与 `metrics/` 历史记录
- Git 历史（不重写、不 squash、不 rebase）

### 资源粒度说明（问题 A 的裁决）

工具把「operation 触及的资源」等同于「任务允许修改的路径」（`pipeline_tools/planning.py:1537-1548` 从 `task.resources` 派生 `allowed_paths`）。对记录型任务，核验 operation 只是**只读跑既有测试**，若把 `tests/**` 通配列为 resource，就会授权修改整个测试目录。

本单采取**收窄 resources 到具体文件**（不写 `tests/**` 通配）**并在正文显式声明只读**的组合：核验 operation 的 resources 精确到 `tests/test_evidence.py` 与 `tests/test_git_checks.py` 两个文件，`non_goals` 明确写「本任务只读，不修改任何测试文件」。残余摩擦如实保留：模型中没有「只读资源」这一概念，被列出的文件名义上仍可写；收窄到具体文件已把误授权面从整个 `tests/` 降到 2 个文件。

## 任务计划映射

- 需求：继承父任务 `["requirement-deletion-status-semantics", "requirement-deletion-acceptance-coverage", "requirement-retention-gate-docs-aligned"]`；本单不新增需求。
- 资源：`["docs/tasks/gate-deletion-semantics-continuation-1.md", "tests/test_evidence.py", "tests/test_git_checks.py"]`
- 操作：`["op-record-deletion-semantics-delivery", "op-verify-evidence-hardening"]`
- 依赖：`[]`（父任务已合并，父子关系由 `derived_from` 表达，不重复列入 dependencies）

## 已确认事实

父任务 `gate-deletion-semantics` 的冻结契约只定义了 3 个 operation，实际交付超出范围。终审（`.pipeline/gate-deletion-semantics/final-check.md` 的「范围膨胀」一节）判定「不违反 `goal.md:41`」，但指出流程缺口：这些扩张本应开 derived 任务单。用户裁决追补一张记录单。以下 6 项扩张（另加 1 项契约内核心交付）均由提交哈希确证：

| # | 交付项 | 提交 | 核验状态 |
|---|---|---|---|
| 1 | 4 条被删命令补回 `commands[]` | `89835f0` | 无既有测试，**无法确定**（见 unknown） |
| 2 | `expected_exit_code` 新字段 | `89835f0`、`b7ae0cc` | 有既有测试 |
| 3 | 证据块解析取第一个闭标记（`core.py` + `reconcile.py`） | `89835f0` | 有既有测试 |
| 4 | `gate_check` 布尔边界守卫 | `b7ae0cc` | 有既有测试 |
| 5 | `.gitattributes` 新建 | `b7ae0cc`、`8d677b0` | 无既有测试，**仅记录为事实**（问题 B 裁决 ii） |
| 6 | 15 个 `.pipeline/` 文件行尾规范化 | `8d677b0` | 无既有测试，**仅记录为事实**（问题 B 裁决 ii） |
| — | 删除语义修复（`D`/`A` 区分，契约内核心交付） | `12e302c` | 有既有测试 |

补充：第 5 项 `.gitattributes` 当前内容为 `* text=auto eol=lf`、`*.cmd text eol=crlf`、`*.bat text eol=crlf`、`docs/tasks/*.md -text`。

## 验收测试

### 验收测试1：acceptance-test-declared-expected-exit-code-allows-nonzero-result

- 测试：`tests/test_evidence.py: EvidenceTests.test_declared_expected_exit_code_allows_nonzero_result`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_declared_expected_exit_code_allows_nonzero_result`
- 证据等级：2

覆盖第 2 项扩张：`expected_exit_code` 新字段允许声明非零退出码作为预期结果。

### 验收测试2：acceptance-test-gate-rejects-boolean-expected-exit-code

- 测试：`tests/test_evidence.py: EvidenceTests.test_gate_rejects_boolean_expected_exit_code`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_gate_rejects_boolean_expected_exit_code`
- 证据等级：2

覆盖第 2 项与第 4 项扩张：`expected_exit_code` 的布尔边界守卫。

### 验收测试3：acceptance-test-evidence-block-parses-with-other-code-fences

- 测试：`tests/test_evidence.py: EvidenceTests.test_evidence_block_parses_when_body_contains_other_code_fences`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_evidence_block_parses_when_body_contains_other_code_fences`
- 证据等级：2

覆盖第 3 项扩张：证据块解析取第一个闭标记。

### 验收测试4：acceptance-test-delete-non-retained-evidence-is-not-a-violation

- 测试：`tests/test_git_checks.py: GitChecks.test_delete_non_retained_evidence_is_not_a_violation`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation`
- 证据等级：2

覆盖删除语义修复（`D`/`A` 区分），即父任务的核心契约内交付。

## 未纳入机械核验的项

- 第 1 项（4 条命令补回 `commands[]`）、第 5 项（`.gitattributes`）、第 6 项（行尾规范化）**没有既有测试**，`grep -rn "gitattributes" tests/` 与 `grep -rn "renormalize\|line ending\|eol" tests/` 均无命中。按用户「只追记已完成的扩张」的裁决，本单不为它们新建测试，只在上方「已确认事实」表里以提交哈希记录。代价是这三项扩张没有被机械核验。