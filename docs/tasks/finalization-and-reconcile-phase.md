# 最终化与对账的阶段感知

<!-- Task ID: finalization-and-reconcile-phase -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "finalization-and-reconcile-phase",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "pipeline_tools/core.py",
    "pipeline_tools/planning.py",
    "pipeline_tools/reconcile.py",
    "tests/test_planning.py",
    "tests/test_evidence.py",
    "tests/test_task_evidence_reconcile.py",
    "SKILL.md",
    "references/merge-and-recovery.md",
    "docs/tasks/finalization-and-reconcile-phase.md",
    ".pipeline/finalization-and-reconcile-phase/**"
  ],
  "forbidden_paths": [
    "docs/goal.md",
    "docs/tasks/task-sheet-revision-and-evidence-binding.md",
    "docs/tasks/post-merge-evidence-identity.md",
    ".pipeline/task-sheet-revision-and-evidence-binding/**",
    ".pipeline/post-merge-evidence-identity/**",
    ".pipeline/security-scan-repair-20261001/**",
    ".pipeline/security-scan-repair-20261001-continuation-1/**",
    ".env",
    "credentials/**"
  ],
  "non_goals": [
    "不放宽 active 阶段的提交绑定：未合并任务的报告仍必须绑定当前 head、branch 与 worktree",
    "不改变 finalized 阶段的身份判据：仍为 task_id 加 sheet_revision",
    "不修改任何历史任务单或历史证据，也不修改两个依赖任务的证据目录",
    "不为让最终化通过而删除或放宽任何既有断言，含对账里钉住 active 绑定的既有用例",
    "不实现任务单归档、历史迁移或 worktree 清理"
  ],
  "operations": [
    {
      "id": "finalization-accepts-current-report-schema",
      "kind": "repair",
      "scope": "evidence finalization validates the report schema the templates actually produce",
      "resources": ["pipeline_tools/planning.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2"]
    },
    {
      "id": "reconcile-phase-awareness",
      "kind": "repair",
      "scope": "reconciliation does not impose active commit binding on a merged delivery",
      "resources": ["pipeline_tools/reconcile.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-3", "acceptance-test-4"]
    },
    {
      "id": "finalized-criteria-tolerate-legacy-evidence",
      "kind": "repair",
      "scope": "missing observed_at_commit is not an error in the finalized phase",
      "resources": ["pipeline_tools/core.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-5"]
    },
    {
      "id": "documentation",
      "kind": "repair",
      "scope": "remove the stale post-merge claim and record the phase split consistently",
      "resources": ["references/merge-and-recovery.md", "SKILL.md"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-6"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: planning evidence-finalize and evidence reconcile CLI"],
    "interaction": ["pipeline_tools/planning.py: finalization report validation"],
    "application": ["pipeline_tools/reconcile.py: reconciliation identity and phase selection"],
    "domain": ["report schema the templates produce; phase-aware identity; commit references as recorded facts"],
    "persistence": [".pipeline/finalization-and-reconcile-phase/ stage reports and machine results"],
    "readback": ["tests/test_planning.py", "tests/test_task_evidence_reconcile.py"],
    "recovery": ["incomplete or mismatched evidence still blocks finalization; unmerged tasks keep active binding"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_finalization_accepts_schema_two_reports",
      "command_ref": "python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_finalization_still_rejects_incomplete_reports",
      "command_ref": "python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_task_evidence_reconcile.py: TaskEvidenceReconcileTests.test_reconcile_reaches_pass_for_a_merged_delivery",
      "command_ref": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_task_evidence_reconcile.py: TaskEvidenceReconcileTests.test_reconcile_keeps_active_binding_for_an_unmerged_task",
      "command_ref": "python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_legacy_evidence_gains_no_new_finalized_errors",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 3,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract",
      "command_ref": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract"
    }
  ],
  "dependencies": ["task-sheet-revision-and-evidence-binding", "post-merge-evidence-identity"],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "Schema 2 is the report format the current templates and every recent task produce; a finalization validator that demands schema 1 is lagging implementation, not a deliberate contract choice."},
    {"id": "assumption-2", "statement": "Reconciliation runs both before and after a merge; its own report identity criterion is already task_id plus sheet revision, so it must not additionally impose the active commit binding on an already merged delivery."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "The evidence shapes behind the sixteen existing finalization markers have not been enumerated; this task requires both schema 1 and schema 2 reports to stay acceptable so that neither historical nor current work is broken."},
    {"id": "unknown-2", "statement": "The mechanical signal that tells reconciliation a delivery is merged (finalization marker present, or the recorded branch tip is an ancestor of HEAD) must be fixed during implementation; if the two signals can disagree, stop and report."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：合并后流程收尾（最终化与对账）
- 任务类型：`repair`
- 用户结果或系统能力：已合并且通过 post-merge 闸门的交付能够完成最终化并通过对账；未合并的任务仍然施加完整的提交绑定；历史形态证据在 finalized 阶段不新增错误
- 执行 worktree 约定：`<仓库根目录>/.worktrees/finalization-and-reconcile-phase`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/finalization-and-reconcile-phase/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- `task-sheet-revision-and-evidence-binding` 与 `post-merge-evidence-identity` 均已合并。前者建立了 `sheet_revision` 作为有效性判据，后者把 post-merge 的身份改为 `task_id` + 修订版本。这两条任务当前都**卡在最终化**，本任务的交付是它们能被关闭的前提。
- 实测事实：对已合并且 `gate post-merge` 已 PASS 的交付运行 `planning evidence-finalize`，返回 `{"status":"blocked","missing":["invalid executor-report.md","invalid review-report.md","invalid final-check.md"]}`。

### 允许修改

- `pipeline_tools/planning.py`：最终化的报告校验
- `pipeline_tools/reconcile.py`：阶段选择
- `pipeline_tools/core.py`：finalized 阶段的字段判据
- `tests/test_planning.py`、`tests/test_evidence.py`、`tests/test_task_evidence_reconcile.py`：新增用例，保持既有断言
- `SKILL.md`、`references/merge-and-recovery.md`：清理矛盾表述并记录阶段分工
- 本任务单与 `.pipeline/finalization-and-reconcile-phase/**`

### 明确不改

- `docs/goal.md`；任何历史任务单与历史证据；两个依赖任务的证据目录
- 既有断言，特别是对账里钉住 active 绑定的 `test_old_head_and_worktree_are_blocked_against_current_git_identity`

### 非目标

- 不放宽 active 阶段；不改变 finalized 阶段的身份判据。
- 不顺手实现归档、历史迁移或 worktree 清理。
- 不改动 `evidence verify` 已确立的阶段分工，只补齐尚未阶段感知的调用点。

## 事实、假设与待决

### 已确认事实

- `pipeline_tools/planning.py:2413-2422` 的 `_validate_finalization_report` 要求 `value.get("schema") == 1`，而当前模板与所有近期任务写出的报告是 schema 2，因此最终化对三份报告一律返回 `invalid`。
- `pipeline_tools/reconcile.py` 仍以默认阶段调用 `evidence_verify`，对已合并交付施加 active 提交绑定。
- `gate post-merge` 对已合并的 `post-merge-evidence-identity` 交付返回 PASS（退出码 0），说明闸门侧不受上述两处影响。
- `references/merge-and-recovery.md` 的"合并后"小节末尾有一句旧话，仍称 post-merge 施加改动路径判据，与新写的阶段分工段落矛盾。
- finalized 阶段把 `observed_at_commit` 列为必需，历史形态证据因此新增错误。

### 未验证事实

- 尚未确认既有 16 个 `finalization.json` 对应证据的 schema 分布。
- 尚未在实现 worktree 中运行任何新增测试。

### 禁止猜测

- 不得自行决定"schema 1 报告是否应继续被最终化接受"——本任务要求两种都接受；若发现必须拒绝其一会破坏既有证据，停下报告。
- 不得自行决定对账判定"已合并"的依据；两种候选依据结论不一致时停下报告。

## 设计与行为契约

[触发] 主代理对一个已合并且通过 post-merge 闸门的交付运行 `planning evidence-finalize`，或对任意交付运行 `evidence reconcile`
→ [处理] 工具按阶段与报告 schema 选择判据
→ [状态] 生成最终化标记；对账得到一致结论
→ [可见结果] 已合并交付可以完成最终化并通过对账；未合并任务仍 fail-closed；历史形态证据不新增错误

- **最终化的报告校验**：接受模板实际产出的报告 schema（1 与 2 都接受）；其余必需字段、角色、`task_id`、以及 post-merge 状态集合的校验保持不变。schema 2 报告必须仍带 `head` 且格式合法。
- **对账的阶段选择**：对**已合并**的交付（判据由实现确定并记录）不得施加 active 提交绑定；对**未合并**的任务仍必须施加，且既有用例 `test_old_head_and_worktree_are_blocked_against_current_git_identity` 必须继续通过。
- **finalized 阶段的字段容忍**：`observed_at_commit` 缺失不得计为错误（存在时仍须为非空字符串）；不含 `sheet_revision` 的历史形态证据在 finalized 阶段不得新增任何错误（这是前一任务钉住的约束）。
- **文档**：`references/merge-and-recovery.md` 中与阶段分工矛盾的旧话必须删除或改写；`SKILL.md` 的记录与实现一致。
- fail-closed：证据不齐、角色不符、`task_id` 不符、状态不在 post-merge 集合内、阶段无法确定——一律 blocked。

## 环境前置

1. `python` 与 `git` 可执行，仓库可读写。
2. 在实现 worktree 中运行聚焦与全量测试。

## 验收测试

### 验收测试1：最终化接受当前报告 schema

- 触发：构造一份完整的 schema 2 证据（三份报告 + 三份机器结果，均 schema 2），其中报告身份记录为任务分支与任务 worktree。
- 断言：`evidence-finalize` 成功产出 `finalization.json`；随后 `evidence verify --phase finalized` 通过。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_accepts_schema_two_reports`
- 命令：`python -m pytest -q tests/test_planning.py -k finalization_accepts_schema_two_reports`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；不得通过改写报告身份或放宽状态集合来达标。

### 验收测试2：不完整的证据仍被拒绝

- 触发：分别构造缺必需字段、角色不符、`task_id` 不符证据。
- 断言：最终化一律 blocked，不产出标记。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_still_rejects_incomplete_reports`
- 命令：`python -m pytest -q tests/test_planning.py -k finalization_still_rejects_incomplete_reports`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；三种情形都必须被观测到。

### 验收测试3：已合并交付的对账可达到 PASS

- 触发：构造"任务分支身份的执行与审查报告 + 主工作树身份的终审报告"的已合并交付，运行 `evidence reconcile`。
- 断言：达到 PASS，不再累积提交身份错误。
- 测试：`tests/test_task_evidence_reconcile.py: TaskEvidenceReconcileTests.test_reconcile_reaches_pass_for_a_merged_delivery`
- 命令：`python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_reaches_pass_for_a_merged_delivery`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；两个方向都要被观测到。

### 验收测试4：未合并任务的对账仍施加提交绑定

- 触发：对未合并任务运行 `evidence reconcile`。
- 断言：仍报出提交身份错误；既有用例 `test_old_head_and_worktree_are_blocked_against_current_git_identity` 继续通过。
- 测试：`tests/test_task_evidence_reconcile.py: TaskEvidenceReconcileTests.test_reconcile_keeps_active_binding_for_an_unmerged_task`
- 命令：`python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_keeps_active_binding_for_an_unmerged_task`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；不得为让已合并路径通过而一并放宽未合并路径。

### 验收测试5：历史形态证据在 finalized 下不新增错误

- 触发：构造不含 `sheet_revision` 与 `observed_at_commit` 的历史形态 schema 2 证据，运行 `evidence verify --phase finalized`。
- 断言：不新增任何错误；仅在 `unverified` 中说明未被修订判据覆盖。
- 测试：`tests/test_evidence.py: EvidenceTests.test_legacy_evidence_gains_no_new_finalized_errors`
- 命令：`python -m pytest -q tests/test_evidence.py -k legacy_evidence_gains_no_new_finalized_errors`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；同时确认携带字段时仍按新判据判定。

### 验收测试6：文档记录阶段分工且无矛盾表述

- 触发：运行文档与模板一致性检查。
- 断言：一致性检查通过；`references/merge-and-recovery.md` 不再声称 post-merge 施加改动路径判据。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`
- 命令：`python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；旧话的删除由审查子代理逐句核对，不能只以该用例通过为准。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 必须拒绝某一种 schema 才能让最终化通过，而那会破坏既有证据。
2. 对账判定"已合并"的两种候选依据给出不一致结论。
3. 既有断言（尤其钉住 active 绑定的那条）必须被实质性削弱才能通过。
4. 实现必须修改契约未列出的文件。
