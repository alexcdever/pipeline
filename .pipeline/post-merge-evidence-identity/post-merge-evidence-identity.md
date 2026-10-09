# 合并后证据按任务单与修订版本识别

<!-- Task ID: post-merge-evidence-identity -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "post-merge-evidence-identity",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "pipeline_tools/core.py",
    "pipeline_tools/__main__.py",
    "pipeline_tools/reconcile.py",
    "tests/test_evidence.py",
    "tests/test_task_evidence_reconcile.py",
    "SKILL.md",
    "references/merge-and-recovery.md",
    "docs/tasks/post-merge-evidence-identity.md",
    ".pipeline/post-merge-evidence-identity/**"
  ],
  "forbidden_paths": [
    "docs/goal.md",
    ".pipeline/task-sheet-revision-and-evidence-binding/**",
    "docs/tasks/task-sheet-revision-and-evidence-binding.md",
    ".pipeline/security-scan-repair-20261001/**",
    ".pipeline/security-scan-repair-20261001-continuation-1/**",
    ".env",
    "credentials/**"
  ],
  "non_goals": [
    "不放宽 pre-merge 的提交绑定：active 阶段下 head、branch、worktree 的判定必须与改动前完全一致",
    "不删除 head、branch、worktree、observed_at_commit 字段，只把它们在 post-merge 阶段降为记录事实",
    "不接受与当前修订版本或任务单 id 不符的证据",
    "不修改任何历史任务单或历史证据"
  ],
  "operations": [
    {
      "id": "post-merge-identity-by-task-and-revision",
      "kind": "repair",
      "scope": "post-merge evidence identity is task_id plus sheet revision, not commit references",
      "resources": ["pipeline_tools/core.py", "pipeline_tools/__main__.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-3", "acceptance-test-4"]
    },
    {
      "id": "reconcile-identity-by-task-and-revision",
      "kind": "repair",
      "scope": "reconciliation compares task_id and sheet revision across reports",
      "resources": ["pipeline_tools/reconcile.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-6"]
    },
    {
      "id": "preserve-pre-merge-commit-binding",
      "kind": "validate",
      "scope": "active phase keeps head, branch and worktree equality checks fail-closed",
      "resources": ["tests/test_evidence.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-5"]
    },
    {
      "id": "documentation",
      "kind": "repair",
      "scope": "record the phase split in the skill and recovery reference",
      "resources": ["SKILL.md", "references/merge-and-recovery.md"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-7"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: gate post-merge and evidence verify phase CLI"],
    "interaction": ["pipeline_tools/core.py: phase-aware evidence identity check"],
    "application": ["pipeline_tools/core.py: post-merge gate over the merged head"],
    "domain": ["task_id plus sheet revision identity; commit references demoted to recorded facts"],
    "persistence": [".pipeline/post-merge-evidence-identity/ stage reports and machine results"],
    "readback": ["tests/test_evidence.py", "tests/test_task_evidence_reconcile.py"],
    "recovery": ["revision or task_id mismatch fails closed; active-phase commit binding unchanged"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_post_merge_identity_uses_task_id_and_revision_only",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k post_merge_identity_uses_task_id_and_revision_only"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_post_merge_rejects_revision_mismatch",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k post_merge_rejects_revision_mismatch"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_post_merge_rejects_task_id_mismatch",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k post_merge_rejects_task_id_mismatch"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_post_merge_requires_main_worktree_reverification",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k post_merge_requires_main_worktree_reverification"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_pre_merge_commit_identity_is_not_weakened",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k pre_merge_commit_identity_is_not_weakened"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 3,
      "test_ref": "tests/test_task_evidence_reconcile.py: TaskEvidenceReconcileTests.test_reconcile_identity_agrees_on_task_and_revision",
      "command_ref": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_identity_agrees_on_task_and_revision"
    },
    {
      "id": "acceptance-test-7",
      "evidence_level": 3,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract",
      "command_ref": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract"
    }
  ],
  "dependencies": ["task-sheet-revision-and-evidence-binding"],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "Merging a task branch always introduces product-path commits into the current head, so no commit-relative criterion can hold in the post-merge phase; identity there can only be the task id plus the sheet revision."},
    {"id": "assumption-2", "statement": "The active phase keeps the full commit binding and is what proves which code the evidence observed; the post-merge phase only proves that the evidence belongs to this task at this contract revision and that main-worktree re-verification was performed."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "Whether any consumer outside this repository relies on commit-level identity for post-merge evidence has not been enumerated."},
    {"id": "unknown-2", "statement": "Whether the existing --phase active/finalized values can carry this split without changing their current meaning must be confirmed during implementation; if they cannot, a new value must be added rather than redefining an existing one."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：证据身份判定（阶段分工）
- 任务类型：`repair`
- 用户结果或系统能力：post-merge 阶段的证据识别只依据任务单 id 与修订版本，合并本身不再使任何证据失效；pre-merge 的完整提交绑定逐字不变；`reconcile` 不再因混合身份判冲突
- 执行 worktree 约定：`<仓库根目录>/.worktrees/post-merge-evidence-identity`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/post-merge-evidence-identity/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- `task-sheet-revision-and-evidence-binding` 已合并：它建立了 `sheet_revision` 与 `sheet_sha256` 作为证据的有效性判据，并放宽了 post-merge 的 `head`。本任务把这件事做彻底——post-merge 不再使用任何提交相对的判据。
- 本任务是同一 worktree 内的**设计变更**：上一版契约要求"放宽 branch 与 worktree 的相等性"，现改为"post-merge 完全不用提交判据"。上一版实现（`merged_task_branch_identity`）在本版下成为死代码，应移除。

### 允许修改

- `pipeline_tools/core.py`：阶段感知的证据身份判定
- `pipeline_tools/reconcile.py`：三报告身份一致的判据改为 `task_id` 与 `sheet_revision`
- `tests/test_evidence.py`、`tests/test_task_evidence_reconcile.py`：新增用例，保持既有断言
- `SKILL.md`、`references/merge-and-recovery.md`：记录阶段分工
- 本任务单与 `.pipeline/post-merge-evidence-identity/**`

### 明确不改

- `docs/goal.md`；任何历史任务单与历史证据（含 `task-sheet-revision-and-evidence-binding` 的证据目录）
- `--phase` 既有取值的语义；若需要新取值，新增而不是改写

### 非目标

- 不放宽 pre-merge（active 阶段）的任何提交绑定判据。
- 不删除 `head`、`branch`、`worktree`、`observed_at_commit`——它们在 post-merge 降为记录事实，仍需存在且格式合法。
- 不处理 `.pipeline/**` 的换行符保护与任务单归档（属于后续任务）。
- 不为让闸门变绿而删除或放宽任何既有断言。

## 事实、假设与待决

### 已确认事实

- 合并任务分支必然在当前 HEAD 上引入产品路径提交，因此 post-merge 阶段 `head == HEAD`、`head` 仅被证据提交推进、以及 `observed_at_commit` 的路径交集失效判据**都不可能成立**。
- 真实后果已实测：`task-sheet-revision-and-evidence-binding` 合并后，其 post-merge 闸门因报告中记录的 head 之后出现了别的任务的提交而失败；该任务的最终化因此被扣住。
- `pipeline_tools/reconcile.py:121-132` 目前把 `branch`、`worktree`、`head` 一并纳入报告身份一致与完整性判据，混合"任务分支报告 + 主工作树 final-check"时会报 `report identity conflict`。
- `evidence verify` 已有 `--phase {active,finalized}` 选项，但当前不影响身份判定。
- 上一版实现新增的 `merged_task_branch_identity`（`pipeline_tools/core.py`）在 post-merge 不再使用提交判据后失去用途。

### 未验证事实

- 尚未确认真实仓库中把 post-merge 身份改为 id + 修订版本后，依赖任务能否通过其 post-merge 闸门并完成最终化。
- 尚未在实现 worktree 中运行任何新增测试。

### 禁止猜测

- 不得自行决定 `--phase` 取值如何承载这一分工；若必须改变既有取值语义，停下报告。
- 不得自行决定 post-merge 是否需要保留任何提交层面的存在性检查（例如 `head` 必须是合法提交）；遇到时按"格式合法即可、不做相等性判定"实现并记录。

## 设计与行为契约

[触发] 主代理在合并之后运行 `gate post-merge` 或 `evidence verify --phase finalized`
→ [处理] 工具按阶段选择证据身份判据
→ [状态] post-merge 只比对任务单 id 与修订版本；提交引用仅作记录
→ [可见结果] 合并带来新的产品提交不再使任何证据失效；修订版本或任务单 id 不符仍 fail-closed

| 判据 | active（pre-merge） | finalized（post-merge） |
|---|---|---|
| 证据文件齐全、角色正确、验收 ID 与契约一致、逐条 PASS、`evidence_ref` 可解析 | 保留 | 保留 |
| 报告写明所评判的 `sheet_revision` | 保留 | **升为身份的一部分** |
| `task_id` 与受验任务一致 | 保留 | **升为身份的一部分** |
| 主工作树复验命令（`cwd` = 主工作树根、退出码 0） | — | 保留 |
| `head` 等于 HEAD 或仅被证据提交推进 | 保留 | **不做判定** |
| `branch`、`worktree` 等于当前身份 | 保留 | **不做判定** |
| `observed_at_commit` 的路径交集失效判据 | 保留 | **不做判定** |
| `head`、`branch`、`worktree`、`observed_at_commit` 字段存在且格式合法 | 必需 | 必需（记录事实） |

- 合并提交、`finalization.json` 的 `identity` 与 `final-check.md` 的主工作树复验命令仍然记录"这份交付对应的合并点"；记录保留，只是不再作为相等性要求。
- fail-closed：`sheet_revision` 缺失或与当前修订版本不符、`task_id` 不符、证据目录与任务 id 不符、阶段取值无法确定——一律报错，不得默认接受。
- active 阶段的错误文本与判定必须与改动前逐字一致。
- `reconcile` 的报告身份一致与完整性判据改为 `task_id` 与 `sheet_revision`；`branch`、`worktree`、`head` 不再参与一致性比较。

## 环境前置

1. `python` 与 `git` 可执行，仓库可读写。
2. 在实现 worktree 中运行聚焦与全量测试。

## 验收测试

### 验收测试1：post-merge 只按任务单 id 与修订版本识别

- 触发：临时仓库中建任务 worktree 与任务分支，写入身份记录为"任务分支 + 任务 worktree + 实现提交 head"的三份 schema-2 报告，把该分支合并进主分支（合并提交改动产品路径），然后运行 `gate post-merge`。
- 断言：闸门通过（退出码 0）；报告文件字节未被改写；合并带来的产品提交不影响判定。
- 测试：`tests/test_evidence.py: EvidenceTests.test_post_merge_identity_uses_task_id_and_revision_only`
- 命令：`python -m pytest -q tests/test_evidence.py -k post_merge_identity_uses_task_id_and_revision_only`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；不得通过改写报告身份或刷新 head 来达标。

### 验收测试2：修订版本不符仍被拒绝

- 触发：报告的 `sheet_revision` 与当前修订版本不符。
- 断言：post-merge 判定失败并指出修订版本不符。
- 测试：`tests/test_evidence.py: EvidenceTests.test_post_merge_rejects_revision_mismatch`
- 命令：`python -m pytest -q tests/test_evidence.py -k post_merge_rejects_revision_mismatch`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；必须失败而非接受。

### 验收测试3：任务单 id 不符仍被拒绝

- 触发：证据的 `task_id` 与受验任务不符；以及证据目录名与任务 id 不符。
- 断言：post-merge 判定失败。
- 测试：`tests/test_evidence.py: EvidenceTests.test_post_merge_rejects_task_id_mismatch`
- 命令：`python -m pytest -q tests/test_evidence.py -k post_merge_rejects_task_id_mismatch`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；必须失败而非接受。

### 验收测试4：主工作树复验仍是硬要求

- 触发：`final-check.md` 中没有任何 `cwd` 为主工作树根且退出码为 0 的命令。
- 断言：post-merge 判定失败。
- 测试：`tests/test_evidence.py: EvidenceTests.test_post_merge_requires_main_worktree_reverification`
- 命令：`python -m pytest -q tests/test_evidence.py -k post_merge_requires_main_worktree_reverification`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；不得因为放宽身份而一并放宽复验要求。

### 验收测试5：pre-merge 的提交绑定未被削弱

- 触发：active 阶段下，分别构造错误 `head`（非祖先的 40 位值）、未合并分支、非规范 `worktree`。
- 断言：三种情形全部仍然报错，错误文本与改动前一致。
- 测试：`tests/test_evidence.py: EvidenceTests.test_pre_merge_commit_identity_is_not_weakened`
- 命令：`python -m pytest -q tests/test_evidence.py -k pre_merge_commit_identity_is_not_weakened`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；既有严格用例一个都不能删或弱化。

### 验收测试6：reconcile 按任务单与修订版本比对身份

- 触发：构造"任务分支身份的执行与审查报告 + 主工作树身份的终审报告"，三者 `task_id` 与 `sheet_revision` 一致。
- 断言：不再报 `report identity conflict`；当 `sheet_revision` 或 `task_id` 不一致时仍报冲突。
- 测试：`tests/test_task_evidence_reconcile.py: TaskEvidenceReconcileTests.test_reconcile_identity_agrees_on_task_and_revision`
- 命令：`python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_identity_agrees_on_task_and_revision`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；两个方向都必须被观测到。

### 验收测试7：文档记录阶段分工

- 触发：运行文档与模板一致性检查。
- 断言：`SKILL.md` 与 `references/merge-and-recovery.md` 记录"post-merge 按任务单 id 与修订版本识别，active 阶段保持完整提交绑定"；一致性检查通过。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`
- 命令：`python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；改写断言时不得删除其"文档必须描述当前状态模型"的约束意图。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 实现这一阶段分工必须改变 `--phase` 既有取值的语义。
2. pre-merge 的既有严格用例必须被实质性削弱才能通过。
3. 放宽身份判定需要同时改写已有报告或历史证据才能通过。
4. 实现必须修改契约未列出的文件。
