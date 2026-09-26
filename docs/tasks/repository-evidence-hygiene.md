# 任务：repository evidence hygiene continuation-5

<!-- Task ID: repository-evidence-hygiene-continuation-5 -->
<!-- Contract section is frozen after commit. This continuation preserves the parent task-evidence-reconcile history. -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "repository-evidence-hygiene-continuation-5",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": [
    "pipeline_tools/**",
    "tests/**",
    "docs/tasks/**",
    "references/**",
    ".pipeline/repository-evidence-hygiene-continuation-5/**"
  ],
  "forbidden_paths": [
    "implement-plan.md",
    "IDEA.md",
    "docs/tasks/task-evidence-reconcile.md",
    "docs/tasks/pipeline-tools-v1.md",
    "docs/tasks/pipeline-tools-v1-continuation-1.md",
    "docs/tasks/pipeline-evidence-lifecycle-migration.md",
    ".pipeline/metrics/**",
    ".pipeline/*/product/**",
    ".pipeline/*/historical/**"
  ],
  "operations": [
    {
      "id": "repair-repository-evidence-hygiene",
      "kind": "mechanical-repository-evidence-hygiene",
      "scope": "reconcile untracked metrics and task evidence directories without importing IDEA.md or historical task products",
      "acceptance_tests": [
        "acceptance-test-untracked-metrics",
        "acceptance-test-task-sheets-validate",
        "acceptance-test-full-regression",
        "acceptance-test-evidence-readiness",
        "acceptance-test-evidence-verify",
        "acceptance-test-gate"
      ]
    }
  ],
  "chain": {
    "entry": ["git status --short and repository evidence paths"],
    "interaction": ["pipeline_tools scope check and evidence commands"],
    "application": ["pipeline_tools task validation and evidence lifecycle"],
    "domain": ["tracked metrics metadata and task-scoped evidence hygiene"],
    "persistence": [".pipeline/repository-evidence-hygiene-continuation-5/**"],
    "readback": ["untracked metrics, allowed task evidence, validation, readiness, verify and gate results"],
    "recovery": ["preserve IDEA.md and historical task products; classify missing or conflicting evidence as BLOCKED/UNVERIFIED"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-untracked-metrics",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_generated_metrics_are_not_scope_drift and GitChecks.test_forbidden_metrics_pattern_still_wins",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_generated_metrics_are_not_scope_drift tests.test_git_checks.GitChecks.test_forbidden_metrics_pattern_still_wins"
    },
    {
      "id": "acceptance-test-task-sheets-validate",
      "evidence_level": 1,
      "test_ref": "scripts/validate_task_sheet.py: validate every Markdown task sheet under docs/tasks",
      "command_ref": "for task in docs/tasks/*.md; do python scripts/validate_task_sheet.py \"$task\" || exit $?; done"
    },
    {
      "id": "acceptance-test-full-regression",
      "evidence_level": 1,
      "test_ref": "tests/: complete regression suite",
      "command_ref": "python -m unittest discover -s tests -v"
    },
    {
      "id": "acceptance-test-evidence-readiness",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_evidence_readiness_reports_missing_final_check_without_gate_claim and CLITests.test_evidence_readiness_records_not_ready_feedback",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_evidence_readiness_reports_missing_final_check_without_gate_claim tests.test_cli.CLITests.test_evidence_readiness_records_not_ready_feedback"
    },
    {
      "id": "acceptance-test-evidence-verify",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_task_relative_evidence_references_resolve_from_canonical_task_directory and EvidenceTests.test_nonpassing_report_is_structurally_valid_but_gate_rejects_it",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_task_relative_evidence_references_resolve_from_canonical_task_directory tests.test_evidence.EvidenceTests.test_nonpassing_report_is_structurally_valid_but_gate_rejects_it"
    },
    {
      "id": "acceptance-test-gate",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_gate_requires_pass_statuses and EvidenceTests.test_passing_report_with_nonzero_command_is_rejected_by_gate",
      "command_ref": "python -m unittest tests.test_evidence.EvidenceTests.test_gate_requires_pass_statuses tests.test_evidence.EvidenceTests.test_passing_report_with_nonzero_command_is_rejected_by_gate"
    }
  ],
  "dependencies": ["task-evidence-reconcile"],
  "required_evidence_levels": [1, 2]
}
```

`pipeline-contract` is the machine-checkable projection of this continuation task. The continuation repairs repository evidence hygiene only; it does not rewrite the parent task, import `IDEA.md`, or treat historical task products as current evidence.

## 任务身份

- 项目：pipeline
- 领域或阶段：continuation-5 / repository evidence hygiene
- 用户结果或系统能力：精确识别未跟踪 metrics 与任务证据目录卫生问题，验证所有任务单，并以 readiness、verify、gate 结果阻止不完整或越界证据进入通过结论。
- 执行 worktree 约定：`<仓库根目录>/.worktrees/repository-evidence-hygiene-continuation-5`；由主代理按冻结契约创建；不创建仓库同级或第二个 worktree
- 状态：未开始

## 依赖与范围

### 前置条件

- `task-evidence-reconcile` 已完成其证据对账契约；本任务只在其基础上修复仓库证据目录卫生。
- `pipeline_tools` 已提供 `task validate`、`scope check`、`evidence readiness`、`evidence verify` 和 `gate pre-merge` 命令。
- `IDEA.md` 是保留输入，不属于本任务产品或证据范围；历史任务产品只作为禁止修改对象。

### 允许修改

- `pipeline_tools/**`：未跟踪 metrics 与任务证据目录卫生所需的机械逻辑。
- `tests/**`：对应的精确回归测试和验收夹具。
- `docs/tasks/repository-evidence-hygiene.md`：本任务单生命周期区。
- `references/**`：与本任务范围一致的工作流说明。
- `.pipeline/repository-evidence-hygiene-continuation-5/**`：本任务的 executor、review、final-check 和失败诊断证据。

### 明确不改

- `implement-plan.md`、`IDEA.md`。
- `docs/tasks/task-evidence-reconcile.md` 及历史任务单、历史任务产品和其证据。
- `.pipeline/metrics/**`；不得把 metrics 事件伪装成产品证据或删除既有指标。
- 不写入其他任务的 `.pipeline/<task-id>/` 目录，不跨任务搬运、覆盖或重命名证据。

## 事实、假设与待决

### 已确认事实

- `scope_check` 对未跟踪路径执行允许/禁止匹配；`.pipeline/metrics/**` 具备特殊的 workflow metadata 语义，但显式 forbidden pattern 必须优先。
- `evidence readiness` 必须先于正式 `evidence verify`，缺少 final-check 或必要报告只能产生未准备好结论。
- `gate` 只能接受当前 task-id、身份一致且报告状态为 PASS 的证据；非 PASS、非零命令或身份冲突必须拒绝。

### 未验证事实

- 当前主工作树实际存在的未跟踪 metrics、任务证据目录和历史遗留文件，待执行命令直接确认。
- 本轮实现前所有 readiness、verify、gate 结果均为 `UNVERIFIED`，不得从旧报告推导 PASS。

### 禁止猜测

- 不把 `.pipeline/metrics/**` 的存在、文件数量或指标成功率当作产品完成证据。
- 不把 `IDEA.md` 或历史任务产品纳入允许范围，不因 scope 便利而删除、移动或改写它们。
- 不以测试数量、报告存在或单个退出码替代任务身份、证据新鲜度和目录归属核对。

## 设计与行为契约

[触发] 扫描仓库未跟踪路径并运行任务单与证据生命周期检查
→ [处理] 仅将当前任务允许路径与当前任务证据目录纳入核对；分离 metrics metadata、任务证据、IDEA 和历史产品
→ [状态] 未跟踪 metrics 按既定 metadata 规则处理，跨任务/历史/禁止路径保持 BLOCKED 或 UNVERIFIED
→ [可见结果] 所有任务单可 validate，当前任务证据依次通过 readiness、verify、gate，且 IDEA 与历史任务产品保持不变

- 当前 task-id、`.pipeline/repository-evidence-hygiene-continuation-5/`、branch、worktree 和 HEAD 必须一致。
- readiness 是 verify 的前置；verify 是 gate 的前置；任一前置缺失不得报告通过。
- scope 检查必须精确区分允许的 pipeline_tools、tests、docs/tasks、references 与当前任务证据，禁止 implement-plan、IDEA、历史任务产品。
- 修复失败或证据不足时保留现场，写 BLOCKED/UNVERIFIED，不清理不属于本任务的目录。

## 环境前置

1. 从仓库根目录运行 `python -m pipeline_tools task validate docs/tasks/repository-evidence-hygiene.md`。
2. 从仓库根目录运行所有任务单校验命令；只允许写入当前任务 `.pipeline/repository-evidence-hygiene-continuation-5/`。
3. 每条单项测试命令默认 180 秒硬上限；全量测试使用明确的累计超时。

## 验收测试

### 验收测试1：未跟踪 metrics 与禁止模式精确处理

- 触发：仓库存在未跟踪 `.pipeline/metrics/**` 与显式禁止 metrics 路径。
- 断言：普通生成 metrics 不产生 scope drift；显式 forbidden pattern 仍报告该路径；不得波及 IDEA 或历史产品。
- 测试：`tests/test_git_checks.py: GitChecks.test_generated_metrics_are_not_scope_drift and GitChecks.test_forbidden_metrics_pattern_still_wins`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_generated_metrics_are_not_scope_drift tests.test_git_checks.GitChecks.test_forbidden_metrics_pattern_still_wins`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；两个断言均通过，未修改仓库外或其他任务证据。

### 验收测试2：所有任务单 validate

- 触发：从仓库根目录遍历 `docs/tasks/*.md`。
- 断言：每个任务单包含唯一有效 contract、完整验收字段、任务锚点和进度区；任何失败立即退出非零。
- 测试：`scripts/validate_task_sheet.py: validate every Markdown task sheet under docs/tasks`
- 命令：`for task in docs/tasks/*.md; do python scripts/validate_task_sheet.py "$task" || exit $?; done`
- 验收模式：其他（机械结构校验）
- 证据等级：1
- 结果要求：所有任务单逐个退出码 0；不得跳过历史任务单，也不得修改它们。

### 验收测试3：全量回归测试

- 触发：运行项目测试发现任务证据和 metrics 处理回归。
- 断言：所有既有测试通过，覆盖 contract、CLI、evidence、metrics、scope、reconcile 和 planning 行为。
- 测试：`tests/: complete regression suite`
- 命令：`python -m unittest discover -s tests -v`
- 验收模式：集成
- 证据等级：1
- 结果要求：退出码 0；无失败、错误或未执行测试。

### 验收测试4：readiness 先于正式核验

- 触发：当前任务证据缺少 final-check 或必要报告。
- 断言：readiness 报告 not ready，不声称 gate 通过，并记录 evidence blocker；补齐证据后才允许后续 verify。
- 测试：`tests/test_cli.py: CLITests.test_evidence_readiness_reports_missing_final_check_without_gate_claim and CLITests.test_evidence_readiness_records_not_ready_feedback`
- 命令：`python -m unittest tests.test_cli.CLITests.test_evidence_readiness_reports_missing_final_check_without_gate_claim tests.test_cli.CLITests.test_evidence_readiness_records_not_ready_feedback`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；缺证据状态为 not ready/BLOCKED，不生成 PASS。

### 验收测试5：当前任务证据 verify

- 触发：对当前任务证据目录执行结构和引用核验。
- 断言：canonical task directory 下的相对证据引用可解析；结构合法但非通过报告仍保留其非通过状态，不能伪造成功。
- 测试：`tests/test_evidence.py: EvidenceTests.test_task_relative_evidence_references_resolve_from_canonical_task_directory and EvidenceTests.test_nonpassing_report_is_structurally_valid_but_gate_rejects_it`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_task_relative_evidence_references_resolve_from_canonical_task_directory tests.test_evidence.EvidenceTests.test_nonpassing_report_is_structurally_valid_but_gate_rejects_it`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；引用只解析到当前任务目录，非 PASS 不被 verify/gate 改写。

### 验收测试6：gate 只接受完整通过证据

- 触发：对 readiness 和 verify 后的当前任务证据运行 pre-merge gate。
- 断言：所有角色报告 PASS、命令退出码为 0、身份和 evidence references 一致时才通过；缺失、非 PASS 或非零命令均拒绝。
- 测试：`tests/test_evidence.py: EvidenceTests.test_gate_requires_pass_statuses and EvidenceTests.test_passing_report_with_nonzero_command_is_rejected_by_gate`
- 命令：`python -m unittest tests.test_evidence.EvidenceTests.test_gate_requires_pass_statuses tests.test_evidence.EvidenceTests.test_passing_report_with_nonzero_command_is_rejected_by_gate`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；拒绝场景明确失败，真实完整证据才可产生 gate PASS。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 未跟踪 metrics 的归属无法区分 workflow metadata 与产品证据。
2. 发现 IDEA.md、历史任务单或历史产品需要修改、移动或删除。
3. readiness、verify、gate 的身份、证据目录或新鲜度不一致。
4. 任何修复需要扩大到本任务允许路径之外。

---

## 任务级进度（主代理维护）

> 契约区在提交后冻结；本任务按用户要求只新增任务单且不提交，后续状态必须以本轮直接证据更新。

### 任务锚点

- 基线 HEAD：UNVERIFIED
- 契约提交：不适用（用户明确要求不提交）
- 执行分支：UNVERIFIED
- 执行 worktree：主工作树（本轮仅新增任务单；正式执行路径待核对）

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-untracked-metrics | UNVERIFIED | - | - | 待执行子代理核对 metrics 与 scope |
| acceptance-test-task-sheets-validate | UNVERIFIED | - | - | 本轮仅要求新增任务单并运行 validate |
| acceptance-test-full-regression | UNVERIFIED | - | - | 未运行全量测试 |
| acceptance-test-evidence-readiness | UNVERIFIED | - | - | 未运行 readiness |
| acceptance-test-evidence-verify | UNVERIFIED | - | - | 未运行 verify |
| acceptance-test-gate | UNVERIFIED | - | - | 未运行 gate |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 创建轮 | 新增 continuation-5 任务单 | UNVERIFIED | `docs/tasks/repository-evidence-hygiene.md` | 运行本任务单 validate |

### 设计变更与延续任务索引

- 父任务：`docs/tasks/task-evidence-reconcile.md`
- 本任务为 continuation-5；如仍需改变设计，建立新的 continuation，不覆盖父任务或本任务历史。

### 最终结果

- 状态：未开始；本轮只新增任务单，validate 结果待记录
- 执行子代理：未开始
- 独立审查子代理：未开始
- 主代理最终检查：未开始
- 合并提交：不适用（用户明确要求不提交）
- 合并后复验：不适用
- 遗留项：按验收台账执行 metrics 卫生、全量任务单 validate、全量测试、readiness、verify 和 gate

## 外部操作

- 不执行提交、推送、合并、删除 worktree 或修改外部服务。
- 不修改 `IDEA.md`、`implement-plan.md`、历史任务产品或其他任务证据目录。
``` 
