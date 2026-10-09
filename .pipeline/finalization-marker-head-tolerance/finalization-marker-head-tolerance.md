# 最终化标记的 head 判据容忍证据提交

<!-- Task ID: finalization-marker-head-tolerance -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "finalization-marker-head-tolerance",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "pipeline_tools/core.py",
    "tests/test_planning.py",
    "references/merge-and-recovery.md",
    "docs/tasks/finalization-marker-head-tolerance.md",
    ".pipeline/finalization-marker-head-tolerance/**"
  ],
  "forbidden_paths": [
    "docs/goal.md",
    ".pipeline/finalization-and-reconcile-phase/**",
    ".pipeline/post-merge-evidence-identity/**",
    ".pipeline/task-sheet-revision-and-evidence-binding/**",
    ".pipeline/security-scan-repair-20261001/**",
    ".pipeline/security-scan-repair-20261001-continuation-1/**",
    ".env",
    "credentials/**"
  ],
  "non_goals": [
    "不放宽 retention 快照判据：保留证据的哈希失配仍必须被拒绝",
    "不放宽产品路径改动后的失效判定：标记 head 之后若出现改动产品路径的提交，仍必须报 stale",
    "不修改任何历史任务单或历史证据，也不修改三个依赖任务的证据目录",
    "不为让校验通过而删除或放宽任何既有断言",
    "不实现任务单归档、历史迁移或 worktree 清理"
  ],
  "operations": [
    {
      "id": "marker-head-tolerance",
      "kind": "repair",
      "scope": "finalization marker head accepts advancement by task evidence commits only",
      "resources": ["pipeline_tools/core.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-3"]
    },
    {
      "id": "documentation",
      "kind": "repair",
      "scope": "record the marker head rule in the recovery reference",
      "resources": ["references/merge-and-recovery.md"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-4"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: evidence verify and planning evidence-finalize CLI"],
    "interaction": ["pipeline_tools/core.py: finalization snapshot verification"],
    "application": ["pipeline_tools/core.py: finalized phase verification"],
    "domain": ["marker identity across its own evidence commit; evidence-only advancement"],
    "persistence": [".pipeline/finalization-marker-head-tolerance/finalization.json"],
    "readback": ["tests/test_planning.py"],
    "recovery": ["product-path commits after the marker head still fail closed; snapshot mismatch still rejected"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_finalization_marker_head_survives_evidence_only_commits",
      "command_ref": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_survives_evidence_only_commits"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_finalization_marker_head_is_still_stale_after_product_commits",
      "command_ref": "python -m pytest -q tests/test_planning.py -k finalization_marker_head_is_still_stale_after_product_commits"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_finalization_marker_snapshot_mismatch_is_still_rejected",
      "command_ref": "python -m pytest -q tests/test_planning.py -k finalization_marker_snapshot_mismatch_is_still_rejected"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract",
      "command_ref": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract"
    }
  ],
  "dependencies": ["finalization-and-reconcile-phase"],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "Committing the finalization marker necessarily advances HEAD past the head the marker recorded, so an exact-equality check on that head is unsatisfiable by construction."},
    {"id": "assumption-2", "statement": "The same evidence-only-advance rule already used for stage report heads is the right tolerance here; it keeps product-path changes fail-closed while accepting the task's own evidence commits."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "Whether the marker's branch and worktree fields can also become unsatisfiable in practice (for example when finalization runs inside the task worktree) has not been demonstrated; if implementation shows such a case, stop and report rather than widening scope."},
    {"id": "unknown-2", "statement": "How many of the sixteen existing finalization markers would pass under the corrected rule has not been enumerated."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：最终化校验（标记身份）
- 任务类型：`repair`
- 用户结果或系统能力：提交最终化标记这一动作本身不再让标记失效；`evidence verify --phase finalized` 在标记提交后仍能通过；产品路径改动与快照失配仍然 fail-closed
- 执行 worktree 约定：`<仓库根目录>/.worktrees/finalization-marker-head-tolerance`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/finalization-marker-head-tolerance/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- `finalization-and-reconcile-phase` 已合并：它恢复了"schema 2 报告可以被最终化"这条链路。本任务修的是它之后的最后一环。
- 实测事实：对一个已合并、`gate post-merge` PASS、`evidence-finalize` 返回 `{"status":"finalized"}` 的交付，提交标记后运行 `evidence verify --phase finalized` 得到 `FAIL: finalization head is stale`。

### 允许修改

- `pipeline_tools/core.py`：最终化快照校验的 head 判据
- `tests/test_planning.py`：新增回归用例，保持既有断言
- `references/merge-and-recovery.md`：记录该规则
- 本任务单与 `.pipeline/finalization-marker-head-tolerance/**`

### 明确不改

- `docs/goal.md`；任何历史任务单与历史证据；三个依赖任务的证据目录
- retention 快照判据与产品路径失效判据
- 既有断言

### 非目标

- 不把标记校验整体放宽为"任何 head 都接受"。
- 不顺势处理 `branch`/`worktree` 的同类问题——除非实现中发现它们**同样**循环不可满足，那时按决策点停下报告。
- 不顺手实现归档、历史迁移或 worktree 清理。

## 事实、假设与待决

### 已确认事实

- `pipeline_tools/core.py:1166-1184` 的 `verify_finalization_snapshot` 要求标记的 `identity.head`、`branch`、`worktree` 与当前 Git 身份**严格相等**，不等即报 `finalization <key> is stale`。
- 提交最终化标记会推动 HEAD，因此该 head 判据**循环不可满足**。
- 后果不限于本仓库的新任务：既有 16 个 `finalization.json` 在提交后同样会报 `head is stale`，即 `finalized verify` 从未在提交后真正成立过。
- `pipeline_tools/core.py` 已有等价容忍实现 `head_advanced_by_evidence_only(root, reported_head, current_head, evidence_directory)`，用于阶段报告的 head：允许 head 被"仅任务证据提交"推进。
- `gate post-merge` 不受本缺口影响（实测 PASS）。

### 未验证事实

- 尚未确认标记的 `branch`/`worktree` 在实践中是否也会失配。
- 尚未在实现 worktree 中运行任何新增测试。

### 禁止猜测

- 不得自行决定 `branch`/`worktree` 是否也要容忍；遇到该形态停下报告。
- 不得自行决定"标记提交后是否允许出现非证据提交"——必须仍然拒绝。

## 设计与行为契约

[触发] 主代理提交最终化标记后运行 `evidence verify --phase finalized`，或对已有标记再次运行 `evidence finalize`
→ [处理] 工具校验标记身份与 retention 快照
→ [状态] 标记记录的 head 已被其自身所在的提交推进
→ [可见结果] 校验通过；产品路径改动或快照失配仍然失败

- **head 判据**：标记记录的 head 等于当前 HEAD，**或**该 head 是当前 HEAD 的祖先且两者之间只有任务证据提交（复用 `head_advanced_by_evidence_only`，证据目录取该任务的证据目录）。其余情形保持既有的 `finalization head is stale`。
- **不改动的判据**：`retained_sha256` 快照失配仍报 `finalization retained evidence hash mismatch`；`branch`、`worktree` 仍按现行严格相等判定（除非按决策点另行裁决）；产品路径在标记 head 之后被改动仍必须失败。
- fail-closed：head 不是合法提交、不是 HEAD 祖先、区间内出现非证据路径改动、证据目录无法解析——一律报错。
- `planning evidence-finalize` 对已存在标记的幂等复核必须与上述一致：提交标记后重复调用仍应返回 `finalized`，而不是 blocked。

## 环境前置

1. `python` 与 `git` 可执行，仓库可读写。
2. 在实现 worktree 中运行聚焦与全量测试。

## 验收测试

### 验收测试1：标记提交后仍可通过校验

- 触发：在临时仓库中完成"合并 → `gate post-merge` → `evidence-finalize` → 提交 `finalization.json`"整条链路。
- 断言：提交标记（HEAD 前移，且区间内只有该任务的证据路径）后，`verify_finalization_snapshot` 返回空错误表，`evidence verify --phase finalized` 通过；重复调用 `evidence-finalize` 仍返回 `finalized`。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_marker_head_survives_evidence_only_commits`
- 命令：`python -m pytest -q tests/test_planning.py -k finalization_marker_head_survives_evidence_only_commits`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；不得通过删除标记或改写标记身份来达标。

### 验收测试2：产品路径改动后仍判 stale

- 触发：标记 head 之后出现一个改动产品路径的提交。
- 断言：仍报 `finalization head is stale`。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_marker_head_is_still_stale_after_product_commits`
- 命令：`python -m pytest -q tests/test_planning.py -k finalization_marker_head_is_still_stale_after_product_commits`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；本任务的容忍不得越界到产品改动。

### 验收测试3：快照失配仍被拒绝

- 触发：篡改一份保留证据，使其与标记中的 `retained_sha256` 不符。
- 断言：仍报 `finalization retained evidence hash mismatch`，校验失败。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_marker_snapshot_mismatch_is_still_rejected`
- 命令：`python -m pytest -q tests/test_planning.py -k finalization_marker_snapshot_mismatch_is_still_rejected`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；retention 判据不得被本次改动波及。

### 验收测试4：文档记录该规则

- 触发：运行文档与模板一致性检查。
- 断言：一致性检查通过；`references/merge-and-recovery.md` 的"合并后"小节写明标记 head 允许被"仅任务证据提交"推进，且产品路径改动仍失败。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`
- 命令：`python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；该句由审查子代理逐句核对。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 标记的 `branch` 或 `worktree` 在实践中同样循环不可满足。
2. 既有断言必须被实质性削弱才能通过。
3. retention 快照判据必须被放宽才能通过。
4. 实现必须修改契约未列出的文件。
