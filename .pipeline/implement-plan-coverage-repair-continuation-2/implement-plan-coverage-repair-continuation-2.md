# implement-plan coverage repair continuation-2：fail-closed coverage、facts gate 与 wrapper 边界

<!-- Task ID: implement-plan-coverage-repair-continuation-2 -->
<!-- Parent: implement-plan-coverage-repair-continuation-1 -->
<!-- Contract section is frozen after commit. Lifecycle sections are maintained by the main agent; no separate progress tracker is required. -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "implement-plan-coverage-repair-continuation-2",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": [
    "pipeline_tools/**",
    "tests/**",
    "docs/tasks/implement-plan-coverage-repair-continuation-2.md",
    "references/**",
    "README.md",
    "SKILL.md"
  ],
  "forbidden_paths": [
    "implement-plan.md",
    "IDEA.md",
    "docs/tasks/implement-plan-coverage-repair-continuation-1.md",
    "docs/tasks/pipeline-tools-v1.md",
    "docs/tasks/pipeline-tools-v1-continuation-1.md",
    "docs/tasks/pipeline-tools-v1-continuation-1-repair-continuation-1.md",
    "docs/tasks/pipeline-tools-v1-current-identity-revalidation-continuation-1.md",
    "docs/tasks/planning-driven-vertical-pipeline.md",
    "docs/tasks/planning-facts-conflict-model.md",
    "docs/tasks/planning-run-lifecycle.md",
    "docs/tasks/planning-run-task-generation.md",
    "docs/tasks/planning-to-dispatch-integration.md",
    "docs/tasks/acceptance-id-and-template-compliance.md",
    "docs/tasks/derived-task-dispatch-recovery.md",
    "docs/tasks/dispatch-fail-closed-and-approval-semantics.md",
    "docs/tasks/evidence-finalization-atomicity.md",
    "docs/tasks/pipeline-evidence-lifecycle-migration.md",
    "docs/tasks/pipeline-evidence-lifecycle-migration-continuation-1.md",
    "docs/tasks/repository-evidence-hygiene.md",
    "docs/tasks/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md",
    "docs/tasks/task-evidence-reconcile.md",
    "docs/tasks/task-plan-contract-consistency.md",
    "docs/tasks/task-worktree-dispatch-identity.md",
    ".pipeline/metrics/**",
    "references/metrics-contract.md"
  ],
  "operations": [
    {
      "id": "repair-top-level-acceptance-failclosed",
      "kind": "repair",
      "scope": "pipeline_tools/planning.py task-plan validation and generation boundary",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-7"]
    },
    {
      "id": "repair-facts-envelope-gate",
      "kind": "repair",
      "scope": "pipeline_tools/planning.py planning_to_dispatch facts envelope propagation and fail-closed downstream gate",
      "acceptance_tests": ["acceptance-test-3", "acceptance-test-4", "acceptance-test-7"]
    },
    {
      "id": "repair-metrics-wrapper-exit-boundary",
      "kind": "repair",
      "scope": "pipeline_tools/__main__.py automatic metrics wrapper and command-runner outer exit boundary",
      "acceptance_tests": ["acceptance-test-5", "acceptance-test-6", "acceptance-test-7"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py:_main planning task-plan validation and planning to-dispatch CLI entry points"],
    "interaction": ["pipeline_tools/__main__.py:argument parsing, command runner and automatic metrics wrapper"],
    "application": ["pipeline_tools/planning.py:planning_to_dispatch and task-plan generation"],
    "domain": ["pipeline_tools/planning.py:validate_task_plan, validate_facts_model, gate_facts_for_planning"],
    "persistence": ["pipeline_tools/planning.py:planning run directory and stage JSON artifacts"],
    "readback": ["tests/test_planning.py, tests/test_planning_dispatch_integration.py and tests/test_cli.py assertions over validation, facts and exit codes"],
    "recovery": ["pipeline_tools/planning.py:fail-closed stage returns; pipeline_tools/__main__.py:main/finally exit preservation"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 1,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_rejects_missing_top_level_acceptance_records",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_missing_top_level_acceptance_records"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 1,
      "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_requires_complete_top_level_acceptance_records",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_requires_complete_top_level_acceptance_records"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 2,
      "test_ref": "tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_planning_to_dispatch_preserves_complete_facts_envelope_and_blocks_conflicts_end_to_end",
      "command_ref": "python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_planning_to_dispatch_preserves_complete_facts_envelope_and_blocks_conflicts_end_to_end"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_planning_to_dispatch_cli_blocks_when_facts_envelope_has_conflicts",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_planning_to_dispatch_cli_blocks_when_facts_envelope_has_conflicts"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 1,
      "test_ref": "tests/test_cli.py: CLITests.test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 1,
      "test_ref": "tests/test_cli.py: CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code"
    },
    {
      "id": "acceptance-test-7",
      "evidence_level": 1,
      "test_ref": "tests/: complete regression suite with automatic metrics enabled and disabled",
      "command_ref": "python -m unittest discover -s tests -v"
    }
  ],
  "dependencies": [
    "Parent task implement-plan-coverage-repair-continuation-1 and its preserved BLOCKED history",
    "Existing schema2 contract validation in pipeline_tools/contract.py",
    "Existing planning facts model and conflict gate in pipeline_tools/planning.py",
    "Existing automatic metrics feedback behavior in pipeline_tools/__main__.py"
  ],
  "required_evidence_levels": [1, 2]
}
```

`pipeline-contract` is the frozen machine-readable contract for this continuation. The executor may consume an already-present implementation in the current repository state when it is inside the allowed paths and passes the same acceptance tests; otherwise it must implement the missing behavior. The parent task's BLOCKED history remains authoritative history and must not be rewritten as PASS.

## 任务身份

- 项目：programing-pipeline / pipeline-tools
- 领域或阶段：schema2 task-plan coverage、planning-to-dispatch facts envelope、CLI automatic-metrics exit boundary
- 父任务：`implement-plan-coverage-repair-continuation-1`（保留其 BLOCKED 历史，不覆盖、不改写）
- 用户结果或系统能力：task plan 缺少完整 top-level acceptance records 时 fail-closed；planning_to_dispatch 传递并门控完整 facts envelope；automatic metrics wrapper 不吞掉或伪造外层命令退出状态。
- 执行 worktree 约定：`<仓库根目录>/.worktrees/implement-plan-coverage-repair-continuation-2`，由主代理在契约提交后用 `git worktree add` 创建；本任务单创建阶段不创建 worktree
- 状态：未开始

## 依赖与范围

### 前置条件

- 父任务已记录规划覆盖、facts 传递和 wrapper 边界的阻塞历史；该历史继续保留，新的任务只修复并验证本任务列出的缺口。
- 当前规划链路已有 task-plan 校验、facts 校验、conflict gate、task generation、contract consistency、freeze 和 dispatch stages；本任务不重做生命周期。
- 当前自动 metrics 是诊断反馈，不是产品验收闸门；wrapper 的修复必须保留原始业务退出码。
- 执行前必须检查当前工作树是否已有允许范围内的未提交产品/测试实现；若有，先按相同契约和验收复核，能消费则不得无理由丢弃，不能消费才重新实现。

### 允许修改

- `pipeline_tools/**`：允许修改 task-plan 顶层 acceptance fail-closed、facts envelope gate/传播、automatic metrics wrapper 外层退出边界所需的产品实现。
- `tests/**`：允许新增或调整上述行为的单元、CLI、集成和回归测试；测试必须直接验证本任务七条验收。
- 本任务单 `docs/tasks/implement-plan-coverage-repair-continuation-2.md`：仅由主代理维护任务级进度；契约提交后冻结。
- `references/**`、`README.md`、`SKILL.md`：仅在修复后的公开行为需要同步说明时修改；不得修改 `references/metrics-contract.md`。
- 允许保留并消费当前允许范围内未提交实现；不得把未提交实现自动视为已验收，必须由本任务证据重新证明。

### 明确不改

- 不修改 `implement-plan.md`、`IDEA.md`、父任务或任何历史任务单；不得把父任务 BLOCKED 改成 PASS。
- 不修改 metrics 数据模型、metrics contract、`.pipeline/metrics/**` 事件或统计语义；不通过关闭 automatic metrics 掩盖退出码问题。
- 不放宽 schema2 要求，不从 operation-level acceptance refs 推断缺失的 top-level records，不用自然语言报告替代 facts envelope。
- 不改变 approval、worktree identity、freeze、dispatch 或 reviewer 语义来规避阻塞。
- 本阶段只创建本任务单并验证/提交契约；不创建 worktree、不派发 executor/reviewer、不修改产品代码。

## 事实、假设与待决

### 已确认事实

- 父任务 `docs/tasks/implement-plan-coverage-repair-continuation-1.md` 明确记录了三类待修复边界、七条验收和 BLOCKED/未开始历史。
- `pipeline_tools/planning.py` 当前实现仍需由 executor 以本任务 acceptance 重新证明 top-level records 的缺失、空值、字段不完整、重复和未知引用均 fail-closed；不能仅凭旧任务描述判定已完成。
- `planning_to_dispatch` 必须让 `assumptions`、`unknowns`、`conflicts`、`non_goals`、`decision_blockers` 在 facts-gate 和返回结果中可回读，并在 blocking facts 时阻断所有下游阶段。
- `pipeline_tools/__main__.py` 的 automatic metrics wrapper 必须是反馈边界，不能改变已产生的业务结果或外层测试命令的真实 returncode。
- 当前主工作树检查显示只有 `.pipeline/metrics/**` 未跟踪产物，没有已确认的 `pipeline_tools/**` 或 `tests/**` 未提交实现；这些 metrics 产物不在本任务允许范围内，不能纳入契约提交。

### 未验证事实

- 未验证 executor 开始时是否出现新的允许范围内未提交实现；必须在执行前重新读取 `git status` 和 diff，并逐项判断能否消费。
- 未验证当前 fixtures 对五个 facts envelope 字段的完整性及缺失字段语义；不得猜测默认值，需由现有 contract、代码和测试确定。
- 未验证 automatic wrapper 的外层退出边界究竟来自 `SystemExit`/`finally`、subprocess、shell/cmd wrapper 或测试 runner；必须用直接 subprocess returncode 的验收定位。

### 禁止猜测

- 不得把缺失 facts envelope 字段自动当空集合来绕过 decision blocker，除非现有 facts contract 和测试明确规定该语义。
- 不得把 metrics warning、报告存在、测试数量或内部绿色当作外层 returncode 已修复的证据。
- 不得因当前未提交实现存在就跳过测试，也不得因实现缺失而擅自扩大允许范围。

## 设计与行为契约

[触发] 调用 task-plan validate/generate、planning_to_dispatch，或运行带 automatic metrics wrapper 的 CLI/测试命令
→ [处理] task-plan 校验要求非空且完整的 top-level acceptance records；planning_to_dispatch 构造、传递并门控五字段 facts envelope；wrapper 记录诊断但保持原始业务与外层命令退出边界
→ [状态] 缺 coverage 或 blocking facts 在对应 stage 返回结构化失败；facts-gate 失败时不得进入 task-generation、contract-consistency、freeze、dispatch-identity 或 dispatch；wrapper 失败只留下 bounded diagnostic，不重写业务状态
→ [可见结果] 缺失 coverage/facts 返回非零且可读错误；合法 envelope 可在 stage/dispatch 结果中回读；外层 subprocess returncode 与被测命令真实结果一致

- schema2 和规划输入均不得以 operation-level refs 代替 top-level acceptance records；缺失、空、字段不完整、重复或未知引用必须 fail-closed。
- facts envelope 至少保留 `assumptions`、`unknowns`、`conflicts`、`non_goals`、`decision_blockers`；任一 blocking conflict/unknown/decision blocker 必须停在 facts-gate。
- automatic metrics 是反馈而非 acceptance gate；metrics 异常不得覆盖 `_main` 或 command runner 已产生的退出码，也不得把失败变成 0。
- 修复不得删除验收、缩减测试命令、关闭 automatic metrics 或修改历史证据制造干净结果。

## 环境前置

1. 在仓库根目录运行 `python -m pipeline_tools task validate docs/tasks/implement-plan-coverage-repair-continuation-2.md`，任务单必须先通过。
2. 使用 Python 标准库测试环境；聚焦验收单条硬上限 180 秒，完整回归累计上限 600 秒。
3. 执行前记录主工作树身份、基线 HEAD、允许范围内未提交 diff 和父任务 BLOCKED 历史；不得把 `.pipeline/metrics/**` 作为本任务实现。
4. 不需要网络、凭据、浏览器、设备、外部服务或真实生产 dispatch；只允许本地 Python、临时目录/Git、测试 runner 和文件读写。

## 验收测试

### 验收测试1：缺失 top-level acceptance records 必须 fail-closed

- 触发：构造带 operation-level acceptance ref 但省略 task-plan 顶层 `acceptance_tests` 的 plan，并调用 `validate_task_plan`。
- 断言：返回非空错误并明确指出缺少完整 top-level acceptance records；不得把 operation refs 当作完整 records，且不得进入 task generation/dispatch。
- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_rejects_missing_top_level_acceptance_records`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_missing_top_level_acceptance_records`
- 验收模式：单元
- 证据等级：1
- 结果要求：退出码 0；独立断言错误分类和 fail-closed 行为；单条命令不超过 180 秒。

### 验收测试2：top-level records 必须完整且覆盖 refs

- 触发：分别构造空顶层 records、缺字段 record、重复 ID、operation 引用不存在 record 的 task plan，并提供合法对照样本。
- 断言：四类坏输入均被拒绝；完整且覆盖所有 refs 的 records 才通过；错误不能被 operation-level fallback 隐藏。
- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_requires_complete_top_level_acceptance_records`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_requires_complete_top_level_acceptance_records`
- 验收模式：单元
- 证据等级：1
- 结果要求：退出码 0；坏输入和合法对照各有独立断言。

### 验收测试3：planning_to_dispatch 传递完整 facts envelope 并端到端阻塞

- 触发：调用 `planning_to_dispatch`，分别使用包含五个 envelope 字段的合法 facts，以及在 `conflicts`/`decision_blockers` 中加入 blocking record 的 facts。
- 断言：合法输入的 facts-gate 和返回结果保留五个字段；blocking 输入不是 `dispatch-ready`，最后 stage 为 `facts-gate`，且没有 task-generation、freeze、dispatch artifacts 或 worktree。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_planning_to_dispatch_preserves_complete_facts_envelope_and_blocks_conflicts_end_to_end`
- 命令：`python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_planning_to_dispatch_preserves_complete_facts_envelope_and_blocks_conflicts_end_to_end`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；同时验证 pass/blocked、stage 顺序、结构化 artifact 和临时 Git 隔离。

### 验收测试4：CLI to-dispatch 同样 fail-closed

- 触发：通过 `python -m pipeline_tools --format json planning to-dispatch ...` 提供完整 envelope fixture 和 blocking facts fixture。
- 断言：合法 fixture 到达 dispatch-ready；blocking fixture 返回非零 JSON，`facts-gate` 为最后 stage，后续 dispatch/worktree 不发生，stdout JSON 不被 automatic wrapper 的 stderr 诊断污染。
- 测试：`tests/test_cli.py: CLITests.test_planning_to_dispatch_cli_blocks_when_facts_envelope_has_conflicts`
- 命令：`python -m unittest tests.test_cli.CLITests.test_planning_to_dispatch_cli_blocks_when_facts_envelope_has_conflicts`
- 验收模式：协议/集成
- 证据等级：2
- 结果要求：合法为 0、阻塞为非零；JSON 可解析；单条命令不超过 180 秒。

### 验收测试5：automatic metrics 异常不改变原始命令退出码

- 触发：mock `metric_event` 失败并执行返回非零的 `command run`，同时让 automatic wrapper 参与。
- 断言：`main()` 返回被测 command 的原始非零码；stderr 只有 bounded warning；相对 log identity 正确；metrics 失败不变成 0 或另一个业务码。
- 测试：`tests/test_cli.py: CLITests.test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity`
- 命令：`python -m unittest tests.test_cli.CLITests.test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity`
- 验收模式：单元
- 证据等级：1
- 结果要求：测试命令退出码 0；测试内部断言被测 `main()` 返回码为 1 和 warning 内容。

### 验收测试6：外层测试命令退出码必须保持真实边界

- 触发：以 subprocess 运行 automatic metrics 开启的失败命令，再运行同一命令关闭 automatic metrics，对比两次外层 returncode、stdout、stderr 和真实内部失败码。
- 断言：wrapper 不吞掉失败、不把 warning 当失败、不以 finally 返回覆盖原始结果；外层 returncode 与测试 runner 真实结果一致。若根因在 shell/cmd 或测试 runner，必须报告最小复现和边界并标记 BLOCKED/未验证，不得伪造 PASS。
- 测试：`tests/test_cli.py: CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code`
- 命令：`python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code`
- 验收模式：协议/集成
- 证据等级：1
- 结果要求：退出码 0；直接检查至少两次 subprocess returncode；任何外部未解决原因留证据。

### 验收测试7：全量回归覆盖实现和 wrapper 两种状态

- 触发：从仓库根目录运行完整测试发现，并按项目支持的方式分别验证 automatic metrics enabled/disabled，不得用全局关闭替代修复。
- 断言：既有测试与本任务测试通过；没有删除、跳过或缩减验收；测试进程退出码为 0，wrapper 警告不改变真实失败边界。
- 测试：`tests/: complete regression suite with automatic metrics enabled and disabled`
- 命令：`python -m unittest discover -s tests -v`
- 验收模式：集成
- 证据等级：1
- 结果要求：退出码 0；记录实际测试数量、完整命令、环境变量状态和 wrapper stderr；累计不超过 600 秒，历史 `.pipeline/metrics` 不纳入本任务范围。

## 外部操作

- 允许：本地临时目录、临时 Git repository、Python `subprocess`、本地测试 runner、本地文件读写。
- 禁止：网络请求、凭据/密钥读取、遥测上传、真实生产项目、真实浏览器或设备、外部 API、修改用户 Git 远端、在本任务创建阶段创建 worktree。
- 契约验证只读任务单；本任务创建阶段只写任务单并提交该契约，不写 `.pipeline/metrics/**`，不清理或改写历史证据。

## 决策点

出现以下情况时，保留现场并报告主代理，不得静默改变契约：

1. 现有 facts contract 无法定义五个 envelope 字段的缺失/默认语义。
2. wrapper 的不干净退出码只能由 shell/cmd、测试 runner 或外部环境修复，超出允许范围。
3. 修复需要修改 implement-plan、IDEA、父任务/历史任务、metrics contract/实现或 `.pipeline/metrics/**`。
4. 允许范围内未提交实现与契约不一致、无法安全消费，或需要改变 acceptance/范围才能通过。

---

## 任务级进度（主代理维护）

> 以下内容不是新的设计权威。契约区在提交后冻结；此处记录进度、裁决和最终结果。父任务 BLOCKED 历史不可覆盖。

### 任务锚点

- 基线 HEAD：`9a94c7a489e9bb19e0a8dfec662c04b0cadba472`
- 契约提交：`9a94c7a489e9bb19e0a8dfec662c04b0cadba472`
- 执行分支：`implement-plan-coverage-repair-continuation-2`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/implement-plan-coverage-repair-continuation-2`（核对后的绝对路径）
- 父任务：`docs/tasks/implement-plan-coverage-repair-continuation-1.md`（BLOCKED 历史保留）

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-1 | PASS | `tests/test_planning.py` | `executor-report.md`, `review-report.md` | top-level acceptance 缺失 fail-closed |
| acceptance-test-2 | PASS | `tests/test_planning.py` | `executor-report.md`, `review-report.md` | records 完整性、重复及未知引用拒绝 |
| acceptance-test-3 | PASS | `tests/test_planning_dispatch_integration.py` | `executor-report.md`, `review-report.md` | facts envelope 传播及冲突阻断 |
| acceptance-test-4 | PASS | `tests/test_cli.py` | `executor-report.md`, `review-report.md` | CLI facts-gate fail-closed |
| acceptance-test-5 | PASS | `tests/test_cli.py` | `executor-report.md`, `review-report.md` | metrics 异常不覆盖业务退出码 |
| acceptance-test-6 | PASS | `tests/test_cli.py` | `executor-report.md`, `review-report.md` | 外层 subprocess returncode 保持 |
| acceptance-test-7 | PASS | `python -m unittest discover -s tests -v` | `executor-report.md`, `review-report.md`, `final-check.md` | 162 tests passed |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 2026-09-26 / continuation-2 | 契约、实现与证据闭环 | 已完成 | `4ded06b` executor；`32b1a98` review/final | 已通过聚焦验收、全量回归及 scope；继续执行 preflight/freeze、result/freshness/readiness/verify/gate |

### 设计变更与延续任务索引

- 父任务：`docs/tasks/implement-plan-coverage-repair-continuation-1.md`；其 BLOCKED 历史、验收和现场不改写。
- 本任务当前无新的设计裁决。如需改变 fail-closed、facts envelope 或 wrapper 边界，建立新的 `continuation` 任务，不覆盖本任务或父任务历史。

### 最终结果

- 状态：已完成
- 执行子代理：PASS，提交 `4ded06be486acb638040a8dd91c19b9ea555fda4`
- 独立审查子代理：PASS，证据已更新并复核
- 主代理最终检查：进行中，等待机械 gates 完成
- 合并提交：`32b1a9888b02a5c3515a56b21d67f16880b29608`
- 合并后复验：未执行（本 continuation 尚未合并主工作树）
- 遗留项：无产品遗留；需完成 preflight/freeze/result/freshness/readiness/verify/gate 机械证据
- 未提交：本任务状态段更新待提交；契约区未修改
