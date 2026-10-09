# 最终化卫生：状态文件保留与复验窗口

<!-- Task ID: finalization-hygiene -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "finalization-hygiene",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "pipeline_tools/core.py",
    "pipeline_tools/planning.py",
    "tests/test_planning.py",
    "tests/test_evidence.py",
    "references/merge-and-recovery.md",
    "references/acceptance-evidence.md",
    "references/execution-and-review.md",
    "SKILL.md",
    "docs/tasks/finalization-hygiene.md",
    ".pipeline/finalization-hygiene/**"
  ],
  "forbidden_paths": [
    "docs/goal.md",
    ".pipeline/task-sheet-revision-and-evidence-binding/**",
    ".pipeline/post-merge-evidence-identity/**",
    ".pipeline/finalization-and-reconcile-phase/**",
    ".pipeline/finalization-marker-head-tolerance/**",
    ".pipeline/finalization-report-reader/**",
    ".pipeline/security-scan-repair-20261001/**",
    ".pipeline/security-scan-repair-20261001-continuation-1/**",
    ".env",
    "credentials/**"
  ],
  "non_goals": [
    "不把仅证据提交的定义放宽到任意路径——仍严格限于 .pipeline 下的证据路径与 metrics",
    "不保留保留集之外的一般过程产物，只豁免两个具名的本地状态文件",
    "不放宽 retention 快照判据，也不放宽产品路径改动后的失效判定",
    "不修改任何历史任务单或历史证据，也不修改五个已完成任务的证据目录",
    "不为让测试变绿而删除或放宽任何既有断言"
  ],
  "operations": [
    {
      "id": "keep-local-state-files",
      "kind": "repair",
      "scope": "finalization pruning spares the local state files",
      "resources": ["pipeline_tools/planning.py", "pipeline_tools/core.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-1"]
    },
    {
      "id": "widen-evidence-only-scope",
      "kind": "repair",
      "scope": "any task evidence commit counts as evidence-only for staleness judgement",
      "resources": ["pipeline_tools/core.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-2", "acceptance-test-3"]
    },
    {
      "id": "documentation",
      "kind": "repair",
      "scope": "record the re-verification window, the retained local state files, and the widened evidence-only scope in every document that states it",
      "resources": ["references/merge-and-recovery.md", "references/acceptance-evidence.md", "references/execution-and-review.md", "SKILL.md"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-4"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: planning evidence-finalize and evidence verify CLI"],
    "interaction": ["pipeline_tools/core.py: evidence-only path judgement"],
    "application": ["pipeline_tools/planning.py: finalization pruning"],
    "domain": ["retained set versus local state files; scope of evidence-only commits"],
    "persistence": [".pipeline/finalization-hygiene/finalization.json and local state files"],
    "readback": ["tests/test_planning.py", "tests/test_evidence.py"],
    "recovery": ["unknown process artifacts are still pruned; product commits still invalidate evidence"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_finalization_keeps_local_state_files",
      "command_ref": "python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_finalized_verification_survives_another_tasks_evidence_commit",
      "command_ref": "python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_finalized_verification_still_fails_after_product_commits",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract",
      "command_ref": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract"
    }
  ],
  "dependencies": ["finalization-report-reader"],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "The freeze record and the revision chain are audit facts about the task, so finalization pruning them makes a later revision-bound check read the wrong revision."},
    {"id": "assumption-2", "statement": "A commit that only touches .pipeline evidence paths does not change the delivered product, so it should not invalidate another task's finalized verification."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "Whether any existing finalized task directory still holds a local state file whose absence changes a current check has not been enumerated for all sixteen markers."},
    {"id": "unknown-2", "statement": "Whether widening evidence-only to every .pipeline path can let a product-affecting commit slip through (for example a commit that touches both evidence and product paths) must be verified; mixed commits must stay fail-closed."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：最终化卫生（状态保留与复验窗口）
- 任务类型：`repair`
- 用户结果或系统能力：最终化不再删除任务的冻结记录与修订链；一条任务关闭后，别的任务提交自己的证据不会让它失效；产品路径改动仍然 fail-closed
- 执行 worktree 约定：`<仓库根目录>/.worktrees/finalization-hygiene`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/finalization-hygiene/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- 五条任务（`task-sheet-revision-and-evidence-binding`、`post-merge-evidence-identity`、`finalization-and-reconcile-phase`、`finalization-marker-head-tolerance`、`finalization-report-reader`）均已合并并最终化。本任务修的是收尾环节留下的两处卫生问题。
- 实测事实一：最终化后 `.pipeline/<task-id>/` 只剩七个保留文件，`goal.json` 与 `amendments.json` 被删除；对带修订链的任务，这会让工具读到的当前修订退化为 1，与其报告声明的修订号不符。
- 实测事实二：一条任务关闭后，只要**另一个任务**提交自己的证据（只动 `.pipeline/<其它任务>/**`），前者的 `evidence verify --phase finalized` 即报 `finalization head is stale`。

### 允许修改

- `pipeline_tools/planning.py`：最终化剪枝
- `pipeline_tools/core.py`：仅证据提交的判定范围
- `tests/test_planning.py`、`tests/test_evidence.py`：新增回归用例，保持既有断言
- `references/merge-and-recovery.md`、`SKILL.md`：记录复验窗口与保留的本地状态文件
- 本任务单与 `.pipeline/finalization-hygiene/**`

### 明确不改

- `docs/goal.md`；任何历史任务单与历史证据；五个已完成任务的证据目录
- retention 快照判据与产品路径失效判据；既有断言

### 非目标

- 不把"仅证据提交"放宽到任意路径。
- 不保留一般过程产物（原始日志、临时文件仍应被剪掉）。
- 不顺手实现归档、历史迁移或 worktree 清理。

## 事实、假设与待决

### 已确认事实

- `finalize_evidence` 只保留 `RETAINED_EVIDENCE_NAMES`（三份报告 + 三份机器结果 + `finalization.json`）并删除其余文件，包括未跟踪的本地状态文件 `goal.json` 与 `amendments.json`。
- `amendments.json` 是修订链的唯一载体；被删后 `sheet_revision` 读作 1。
- `head_advanced_by_evidence_only` 判定"仅证据提交"时使用**该任务自己的**证据目录，因此别的任务的证据提交被视为非证据提交。
- 五条任务在各自收尾窗口内 `evidence verify --phase finalized` 均为 PASS；之后重跑，较晚关闭的那条仍 PASS、较早的报 `finalization head is stale`。

### 未验证事实

- 尚未枚举既有 16 个最终化目录中本地状态文件的存留情况。
- 尚未在实现 worktree 中运行任何新增测试。

### 禁止猜测

- 不得自行决定"混合提交"（同时改动证据路径与产品路径）如何判定；必须 fail-closed，如遇到无法机械判定的形态停下报告。
- 不得自行决定除 `goal.json`、`amendments.json` 之外是否还要豁免别的文件。

## 设计与行为契约

[触发] 主代理对一个任务运行 `planning evidence-finalize`，或对已关闭任务运行 `evidence verify --phase finalized`
→ [处理] 工具选择要保留的文件与判定提交性质
→ [状态] 本地状态文件保留；别的任务的证据提交被认作仅证据提交
→ [可见结果] 修订链与冻结记录仍在；已关闭任务不再因别的任务的证据提交而报 stale；产品路径改动仍然失败

- **剪枝豁免**：最终化保留 `goal.json` 与 `amendments.json`（若存在），与保留集一并留下；其余非保留文件仍按现行为剪掉。
- **仅证据提交的范围**：判定某段提交区间是否"仅证据提交"时，`.pipeline/**` 下的**任意**任务证据路径与 `.pipeline/metrics/` 都算证据路径；`.pipeline` 之外的任何改动**都不算**。
- **fail-closed**：同一提交同时改动证据路径与产品路径时必须判为非仅证据提交；路径无法解析时判为非仅证据提交。
- **不得波及**：retention 快照判据、产品路径失效判据、schema 与报告结构校验一律不变。
- **文档**：`references/merge-and-recovery.md` 写清"复验窗口"的语义（关闭时校验通过即算通过；属后另有产品提交会让记录的 head 合法变旧）与保留的本地状态文件；`SKILL.md` 同步一句。

## 环境前置

1. `python` 与 `git` 可执行，仓库可读写。
2. 在实现 worktree 中运行聚焦与全量测试。

## 验收测试

### 验收测试1：最终化保留本地状态文件

- 触发：在临时仓库中走完整最终化链路，证据目录中预先放入 `goal.json` 与 `amendments.json` 以及一个无关的过程文件。
- 断言：最终化后 `goal.json` 与 `amendments.json` 仍在；无关的过程文件被剪掉；保留集七件仍在。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_keeps_local_state_files`
- 命令：`python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；两个方向都要被观测到（保留与剪除）。

### 验收测试2：别的任务的证据提交不使已关闭任务失效

- 触发：任务 A 关闭后，在 `.pipeline/<任务B>/**` 下提交一份证据提交。
- 断言：任务 A 的 `evidence verify --phase finalized` 仍通过；其标记身份不因该提交而失效。
- 测试：`tests/test_planning.py: PlanningTests.test_finalized_verification_survives_another_tasks_evidence_commit`
- 命令：`python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；不得通过删除标记或改写身份达标。

### 验收测试3：产品提交后仍失效

- 触发：任务 A 关闭后，提交一个改动产品路径的提交；以及一个同时改动证据路径与产品路径的混合提交。
- 断言：两种情形都必须让任务 A 的 finalized 校验失败。
- 测试：`tests/test_evidence.py: EvidenceTests.test_finalized_verification_still_fails_after_product_commits`
- 命令：`python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；混合提交必须 fail-closed。

### 验收测试4：文档记录复验窗口与保留文件

- 触发：运行文档与模板一致性检查。
- 断言：一致性检查通过；`references/merge-and-recovery.md` 写明复验窗口语义与保留的本地状态文件。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`
- 命令：`python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；该段由审查子代理逐句核对。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 混合提交无法机械判定性质。
2. 既有断言必须被实质性削弱才能通过。
3. 保留本地状态文件会破坏 retention 快照判据或既有最终化校验。
4. 实现必须修改契约未列出的文件。
