# 合并后证据身份的跨合并判定

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
    "tests/test_evidence.py",
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
    "不放宽 head 的判定：报告 head 之后若出现改动产品路径的提交，仍必须判为失效",
    "不接受未合并分支的报告，也不接受非本任务规范 worktree 的报告",
    "不修改任何历史任务单或历史证据",
    "不实现任务单归档、历史迁移或 worktree 清理"
  ],
  "operations": [
    {
      "id": "relax-report-identity-across-merge",
      "kind": "repair",
      "scope": "accept task-branch report identity once that branch is merged into the current head",
      "resources": ["pipeline_tools/core.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-3", "acceptance-test-5"]
    },
    {
      "id": "preserve-strict-identity-expectations",
      "kind": "validate",
      "scope": "existing strict report identity expectations keep failing closed",
      "resources": ["tests/test_evidence.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-4"]
    },
    {
      "id": "documentation",
      "kind": "repair",
      "scope": "record the cross-merge identity rule in the skill and recovery reference",
      "resources": ["SKILL.md", "references/merge-and-recovery.md"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-6"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: gate post-merge and evidence verify CLI"],
    "interaction": ["pipeline_tools/core.py: schema-2 report identity check"],
    "application": ["pipeline_tools/core.py: post-merge gate over the merged head"],
    "domain": ["branch merged-into-head ancestry, canonical task worktree, evidence-only head advance"],
    "persistence": [".pipeline/post-merge-evidence-identity/ stage reports and machine results"],
    "readback": ["tests/test_evidence.py"],
    "recovery": ["unmerged branch or foreign worktree still fails closed; no partial acceptance"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_merged_task_branch_reports_pass_the_post_merge_gate",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k merged_task_branch_reports_pass_the_post_merge_gate"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_unmerged_branch_report_identity_is_still_rejected",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k unmerged_branch_report_identity_is_still_rejected"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_foreign_worktree_report_identity_is_still_rejected",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k foreign_worktree_report_identity_is_still_rejected"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_schema_two_report_identity_stays_strict_for_bogus_values",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k schema_two_report_identity_stays_strict"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_product_change_after_reported_head_is_still_stale",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k product_change_after_reported_head_is_still_stale"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 3,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract",
      "command_ref": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract"
    }
  ],
  "dependencies": ["task-sheet-revision-and-evidence-binding"],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "A task branch is merged when its tip is an ancestor of the current head; that ancestry is the mechanical proof that the reports written on that branch describe work now present in the current head."},
    {"id": "assumption-2", "statement": "The canonical implementation worktree for a task is that task's own directory under .worktrees/ at the repository root; any other worktree recorded in a report is not authoritative for that task."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "Whether any existing repository or downstream consumer relies on the current strict cross-worktree identity rejection of schema-2 reports has not been enumerated; the strict path must therefore stay in place for every case that is not the merged-branch one."},
    {"id": "unknown-2", "statement": "The exact report identity fields written by third-party exporters, if any, are unknown; only fields written by this repository's own stage reports are in scope."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：证据身份判定（合并后阶段）
- 任务类型：`repair`
- 用户结果或系统能力：任务分支合并进主分支后，在该任务 worktree 里写成的执行与审查报告不再因 `branch`/`worktree` 与当前身份不同而被判失效；未合并分支或非规范 worktree 的报告仍然 fail-closed；`head` 的既有严格判定保持不变
- 执行 worktree 约定：`<仓库根目录>/.worktrees/post-merge-evidence-identity`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/post-merge-evidence-identity/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- `task-sheet-revision-and-evidence-binding` 已合并：它放宽了 schema-2 报告的 `head` 判定（`head_advanced_by_evidence_only`），本任务处理同一位置上剩余的 `branch`/`worktree`。
- 该任务的 `post-merge` 闸门当前因本缺口处于未通过状态，其任务尚未最终化；本修复合并后它应当可以通过并完成最终化。

### 允许修改

- `pipeline_tools/core.py`：报告身份判定与其共享的辅助函数
- `tests/test_evidence.py`：新增跨合并用例，并保持既有严格期望
- `SKILL.md`、`references/merge-and-recovery.md`：记录该规则
- 本任务单与 `.pipeline/post-merge-evidence-identity/**`

### 明确不改

- `docs/goal.md`；任何历史任务单与历史证据（含 `task-sheet-revision-and-evidence-binding` 的证据目录，其最终化由主代理在本修复合并后处理）
- 其他任务的代码、测试与文档

### 非目标

- 不追求把身份判定整体放宽成"任何报告都接受"；放宽只针对"报告所在分支已并入当前 HEAD"这一种可机械证明的情形。
- 不处理 `.pipeline/**` 的换行符保护（属于后续归档任务）。
- 不为让闸门变绿而删除或放宽任何既有断言。

## 事实、假设与待决

### 已确认事实

- `pipeline_tools/core.py` 对 schema-2 报告要求 `head` 等于当前 HEAD 或仅被证据提交推进（`head_advanced_by_evidence_only`），但 `branch` 仍须等于 `--branch` 或当前分支、`worktree` 仍须等于当前 worktree。
- 真实后果已实测：`task-sheet-revision-and-evidence-binding` 合并到 main 后，`gate post-merge` 在 worktree 内以退出码 3 失败，六条错误全部指向执行与审查报告的 `branch`/`worktree`。
- 既有实践是合并后把执行与审查报告的 `branch`/`worktree`/`head` 改写为主工作树身份；`gate` 的这条要求正是驱动该记账的原因。
- `tests/test_evidence.py` 已覆盖"错误 head 必须报错"与"缺 product_head 时保持严格 legacy 检查"。

### 未验证事实

- 尚未确认除本仓库自己的阶段报告外，是否还有写入者依赖当前的跨 worktree 严格拒绝。
- 尚未在实现 worktree 中运行任何新增测试。

### 禁止猜测

- 不得自行决定"已合并"的判据口径之外的情形（例如分支被删除、远程分支、同一提交的两个分支）如何处置；遇到时停下报告。

## 设计与行为契约

[触发] 主代理在合并某个任务分支之后运行 `gate post-merge` 或 `evidence verify`
→ [处理] 工具逐份校验 schema-2 报告的身份字段
→ [状态] 报告的 `branch`/`worktree` 与当前身份不同，但该分支已并入当前 HEAD
→ [可见结果] 校验通过；报告无需被改写；未合并分支或非规范 worktree 仍报错

- 判定基准：对报告的 `branch`/`worktree`，除现有"等于当前身份"外，增加一条**且仅一条**可机械证明的放宽路径，三条同时满足才接受：
  1. 报告记录的 `branch` 是本地分支，且其尖端是当前 HEAD 的祖先（即已合并）；
  2. 报告记录的 `worktree` 是该任务的规范实现 worktree `<repo root>/.worktrees/<task-id>`；
  3. 报告的 `head` 已通过既有 `head_advanced_by_evidence_only` 判定。
- 不满足以上三条时，保持既有的严格判定与错误文本不变。
- `head` 的语义不得放宽：报告 head 之后若出现改动产品路径的提交，仍判失效。
- 失败必须 fail-closed：无法解析分支、无法解析 worktree、任务 id 与报告不一致时一律报错，不得默认接受。

## 环境前置

1. `python` 与 `git` 可执行，仓库可读写。
2. 在实现 worktree 中运行聚焦与全量测试。

## 验收测试

### 验收测试1：已合并分支的报告通过合并后闸门

- 触发：在临时仓库中创建任务 worktree 与任务分支，在其中写入三份身份为"任务分支 + 任务 worktree"的 schema-2 报告，随后把该分支合并进主分支并运行 `gate post-merge`。
- 断言：闸门通过（退出码 0）；报告文件字节未被改写。
- 测试：`tests/test_evidence.py: EvidenceTests.test_merged_task_branch_reports_pass_the_post_merge_gate`
- 命令：`python -m pytest -q tests/test_evidence.py -k merged_task_branch_reports_pass_the_post_merge_gate`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；断言失败即 FAIL；不得通过改写报告身份来达标。

### 验收测试2：未合并分支的报告仍被拒绝

- 触发：报告记录的 `branch` 尖端不是当前 HEAD 的祖先（未合并）。
- 断言：仍报出分支身份不匹配，校验失败；报告未被修改。
- 测试：`tests/test_evidence.py: EvidenceTests.test_unmerged_branch_report_identity_is_still_rejected`
- 命令：`python -m pytest -q tests/test_evidence.py -k unmerged_branch_report_identity_is_still_rejected`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；必须失败而非接受。

### 验收测试3：非规范 worktree 的报告仍被拒绝

- 触发：报告记录的 `worktree` 不是该任务的规范实现 worktree（例如别的任务的 worktree、仓库同级目录或不存在的路径）。
- 断言：仍报出 worktree 身份不匹配，校验失败。
- 测试：`tests/test_evidence.py: EvidenceTests.test_foreign_worktree_report_identity_is_still_rejected`
- 命令：`python -m pytest -q tests/test_evidence.py -k foreign_worktree_report_identity_is_still_rejected`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；必须失败而非接受。

### 验收测试4：既有严格期望未被削弱

- 触发：运行既有断言——错误 head（非祖先的 40 位值）、错误 branch、错误 worktree 必须报错。
- 断言：既有严格用例全部保持通过，错误文本不变。
- 测试：`tests/test_evidence.py: EvidenceTests.test_schema_two_report_identity_stays_strict_for_bogus_values`
- 命令：`python -m pytest -q tests/test_evidence.py -k schema_two_report_identity_stays_strict`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；不得删除或弱化既有断言。

### 验收测试5：`head` 的判定不被放宽

- 触发：报告 head 之后出现一个改动产品路径的提交。
- 断言：报告仍被判失效。
- 测试：`tests/test_evidence.py: EvidenceTests.test_product_change_after_reported_head_is_still_stale`
- 命令：`python -m pytest -q tests/test_evidence.py -k product_change_after_reported_head_is_still_stale`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；本任务的放宽不得越界到 `head`。

### 验收测试6：文档记录跨合并规则

- 触发：运行文档与模板一致性检查。
- 断言：`SKILL.md` 与 `references/merge-and-recovery.md` 记录"报告在其所在分支合并且 worktree 为该任务规范目录时，身份字段无需改写"；一致性检查通过。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`
- 命令：`python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；改写断言时不得删除其"文档必须描述当前状态模型"的约束意图。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 放宽某条路径需要同时改写已有报告或历史证据才能通过——这属于设计冲突，不是实现细节。
2. 既有严格用例必须被实质性削弱才能通过。
3. "已合并"的判据遇到本任务单未覆盖的形态（分支已删除、远程分支、同一提交被多个分支指向），无法在不猜测的前提下判定。
