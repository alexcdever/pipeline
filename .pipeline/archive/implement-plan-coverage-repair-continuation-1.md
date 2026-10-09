# implement-plan coverage repair continuation-1：schema2 规划阻塞与 facts 传递

<!-- Task ID: implement-plan-coverage-repair-continuation-1 -->
<!-- Contract section is frozen after commit. Lifecycle sections are maintained by the main agent; no separate progress tracker is required. -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "implement-plan-coverage-repair-continuation-1",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": [
    "pipeline_tools/**",
    "tests/**",
    "docs/tasks/implement-plan-coverage-repair-continuation-1.md",
    "references/**",
    "README.md",
    "SKILL.md"
  ],
  "forbidden_paths": [
    "implement-plan.md",
    "IDEA.md",
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
    "references/metrics-contract.md",
    "tests/test_metrics.py",
    "tests/*metrics*"
  ],
  "operations": [
    {
      "id": "repair-task-plan-coverage",
      "kind": "repair",
      "scope": "pipeline_tools/planning.py task-plan validation and generation boundary",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-4"]
    },
    {
      "id": "repair-facts-envelope-dispatch",
      "kind": "repair",
      "scope": "pipeline_tools/planning.py planning_to_dispatch facts gate and downstream stages",
      "acceptance_tests": ["acceptance-test-3", "acceptance-test-4"]
    },
    {
      "id": "diagnose-cli-wrapper-exit",
      "kind": "investigate",
      "scope": "pipeline_tools/__main__.py main automatic wrapper and test-runner outer exit status",
      "acceptance_tests": ["acceptance-test-5", "acceptance-test-6"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py:_main planning task-plan-validate and planning to-dispatch CLI entry points"],
    "interaction": ["pipeline_tools/__main__.py:planning parser arguments and main wrapper"],
    "application": ["pipeline_tools/planning.py:planning_to_dispatch"],
    "domain": ["pipeline_tools/planning.py:validate_task_plan, validate_facts_model, gate_facts_for_planning"],
    "persistence": ["pipeline_tools/planning.py:_planning_run_directory and stage JSON artifacts"],
    "readback": ["tests/test_planning.py and tests/test_planning_dispatch_integration.py assertions over validation and dispatch results"],
    "recovery": ["pipeline_tools/planning.py:fail-closed stage returns; pipeline_tools/__main__.py:main finally wrapper" ]
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
      "test_ref": "tests/: complete regression suite with the automatic metrics wrapper enabled and disabled",
      "command_ref": "python -m unittest discover -s tests -v"
    }
  ],
  "dependencies": [
    "Existing schema2 contract validation in pipeline_tools/contract.py",
    "Existing planning facts model and conflict gate in pipeline_tools/planning.py",
    "Existing CLI automatic metrics wrapper behavior is diagnostic input, not a product PASS signal"
  ],
  "required_evidence_levels": [1, 2]
}
```

`pipeline-contract` is the frozen machine-readable contract for this continuation. The repair must not change `implement-plan.md`, historical task sheets, IDEA, metrics implementation/contract files, or `.pipeline/metrics/**`.

## 任务身份

- 项目：programing-pipeline / pipeline-tools
- 领域或阶段：schema2 task-plan coverage、planning-to-dispatch facts envelope、CLI wrapper diagnosis
- 用户结果或系统能力：缺少完整 top-level acceptance records 的 task plan 在生成和 dispatch 前 fail-closed；planning_to_dispatch 传递完整 facts envelope（`assumptions`、`unknowns`、`conflicts`、`non_goals`、`decision_blockers`）并让任一阻塞事实端到端阻止后续 dispatch；自动 metrics wrapper 不污染测试命令的外层退出码，或以证据明确剩余原因。
- 执行 worktree 约定：`<仓库根目录>/.worktrees/implement-plan-coverage-repair-continuation-1`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态：未开始

## 依赖与范围

### 前置条件

- 当前主工作树已包含 schema2 `pipeline-contract` 与完整 `acceptance-test-*` 命名约束。
- 当前规划链路已经有 facts 校验、conflict gate、task-plan 校验、task generation、contract consistency、freeze 和 dispatch stages；本任务修复其缺口，不重做生命周期。
- 当前 CLI 在 `main()` 的 `finally` 中调用自动 metrics wrapper；既有测试证明 metrics 失败不得替换原始命令结果，本任务补齐外层测试命令退出码调查。

### 允许修改

- `pipeline_tools/**`：仅为本任务的两个 schema2/planning 缺口和 automatic wrapper 退出码问题所需的实现。
- `tests/**`：新增或调整上述缺口的精确单元、CLI、集成和回归测试。
- 本任务单 `docs/tasks/implement-plan-coverage-repair-continuation-1.md`。
- `references/**`、`README.md`、`SKILL.md`：仅在修复后的行为需要同步公开契约时修改；不得修改 metrics 专门契约。

### 明确不改

- 不修改 `implement-plan.md`、`IDEA.md` 或任何历史任务单；不重写既有任务历史。
- 不修改 metrics 数据模型、metrics contract、`.pipeline/metrics/**` 事件或统计语义；调查 wrapper 时不得以关闭 metrics 掩盖退出码问题。
- 不放宽 schema2 要求，不从 operation-level acceptance refs 推断缺失的 top-level records，不以自然语言报告替代 facts envelope。
- 不创建或提交 worktree；不提交代码；不联网、不上传遥测、不执行外部服务或真实生产 dispatch。

## 事实、假设与待决

### 已确认事实

- `pipeline_tools/planning.py:779` 的 `validate_task_plan` 当前只在 `acceptance_tests` 存在时校验 top-level records；缺失时会回退到 operation refs，正是本任务要修复的 fail-closed 缺口。
- `pipeline_tools/planning.py:1321` 的 `planning_to_dispatch` 当前只构造 `schema`、`planning_run_id`、`facts` 三字段的 gate input，未传递 `assumptions`、`unknowns`、`conflicts`、`non_goals`、`decision_blockers`。
- `planning_to_dispatch` 按 stage 首个非 pass 返回；因此 facts envelope 的阻塞必须发生在 `facts-gate`，并且 `task-generation`、`contract-consistency`、`freeze`、`dispatch-identity`、`dispatch` 不得继续。
- `pipeline_tools/__main__.py:1182` 的 `main` 在 `finally` 调用 `_record_automatic_metrics`；现有测试 `test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity` 已覆盖 metrics 写入异常时保留业务返回值，但尚未证明外层 test command 的退出码在 wrapper 参与时保持干净。
- 七段链路是 entry → interaction → application → domain → persistence → readback → recovery；本任务是工作流/CLI repair，不声称完成用户产品 E2E。

### 未验证事实

- 未验证当前 branch 上是否已有未提交修改、活动 worktree、任务证据目录或任何新测试名称；执行前必须按 pipeline workflow 重新核对。
- 未验证 automatic wrapper 的外层退出码问题是 `SystemExit`/`finally`、subprocess wrapper、shell/cmd wrapper 还是测试 runner 集成造成；必须用最小可复现实验和本任务 acceptance-test-5/6 定位。
- 未验证 `project_facts` 输入的五个 envelope 字段在所有合法旧 fixture 中均存在；兼容策略不能猜测，若需要迁移字段默认值须以测试和当前 facts contract 为依据。

### 禁止猜测

- 不得把缺失 envelope 字段自动当成空集合而绕过 decision blocker；必须明确字段来源、缺失行为和 fail-closed 规则。
- 不得把 metrics wrapper 的 warning、报告存在或内部测试绿色视为外层命令退出码已修复；必须直接读取 subprocess returncode。
- 不得改变 approval、worktree identity、freeze 或 reviewer 语义来规避阻塞。

## 设计与行为契约

[触发] CLI 或 API 调用 task-plan validate / planning_to_dispatch，或执行带 automatic metrics wrapper 的完整测试命令
→ [处理] task-plan 校验要求完整 top-level acceptance records；planning_to_dispatch 构造并传递完整 facts envelope，facts gate 检查冲突/未知/决策阻塞；CLI wrapper 记录诊断但不接管原始退出状态
→ [状态] 失败在 facts-gate 或 task-plan validation 留下可读的结构化 stage/result artifact；被阻塞时不得创建/替换 downstream task sheet、freeze、worktree 或 dispatch
→ [可见结果] 缺 coverage 或 blocking facts 返回非零且明确错误；无阻塞时完整 envelope 可在 stage/dispatch 结果中回读；测试命令外层 returncode 与被测命令真实结果一致

- `validate_task_plan` 对 schema1 planning input 也必须要求非空完整 `acceptance_tests` top-level records，并逐条覆盖 operation refs；缺失、空、字段不完整、重复或未知 ref 都 fail-closed。
- facts envelope 至少逐字段保留 `assumptions`、`unknowns`、`conflicts`、`non_goals`、`decision_blockers`；任何 blocking conflict/unknown/decision blocker 必须阻塞 facts-gate 并阻断所有下游阶段。
- automatic metrics 是反馈，不是 acceptance gate；其异常、stderr warning 或写入失败不得替换 `_main` 已产生的退出码，也不得让外层 test command 获得虚假的 0。
- 修复不得通过删除验收、缩减测试命令、关闭 automatic metrics 或修改 metrics 文件来制造干净结果。

## 环境前置

1. 在仓库根目录运行 `python -m pipeline_tools task validate docs/tasks/implement-plan-coverage-repair-continuation-1.md`，任务单必须先通过。
2. 使用 Python 标准库测试环境；每条聚焦命令硬上限 180 秒，完整回归命令累计上限 600 秒。
3. 运行 acceptance-test-5/6 时分别记录 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=0` 与 `=1`（若测试设计需要）；必须保留直接 subprocess returncode，不依赖 shell 的模糊摘要。
4. 不需要网络、凭据、浏览器、设备、外部服务、生产数据或真实 worktree dispatch；外部操作仅包括本地 Python subprocess、临时 Git 仓库和本地文件读写。

## 验收测试

### 验收测试1：缺失 top-level acceptance records 必须 fail-closed

- 触发：构造带 operation-level acceptance ref 但省略 task-plan 顶层 `acceptance_tests` 的 plan，并调用 `validate_task_plan`。
- 断言：返回非空错误，指出缺少完整 top-level acceptance records；不得把 operation refs 当作完整 records，且不得进入 task generation/dispatch。
- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_rejects_missing_top_level_acceptance_records`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_missing_top_level_acceptance_records`
- 验收模式：单元
- 证据等级：1
- 结果要求：退出码 0；断言错误分类和 fail-closed 行为；单条命令不超过 180 秒。

### 验收测试2：top-level records 必须完整且覆盖 refs

- 触发：分别构造空顶层 records、缺字段 record、重复 ID、operation 引用不存在 record 的 task plan。
- 断言：每种输入均被拒绝；完整且覆盖所有 refs 的 records 才通过；错误不能被 operation-level fallback 隐藏。
- 测试：`tests/test_planning.py: PlanningTests.test_task_plan_requires_complete_top_level_acceptance_records`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_requires_complete_top_level_acceptance_records`
- 验收模式：单元
- 证据等级：1
- 结果要求：退出码 0；四类坏输入均有独立断言，合法对照样本通过。

### 验收测试3：planning_to_dispatch 传递完整 facts envelope 并端到端阻塞

- 触发：调用 `planning_to_dispatch`，分别使用包含五个 envelope 字段的合法 facts，以及在 `conflicts`/`decision_blockers` 中加入 blocking record 的 facts。
- 断言：合法输入的 facts-gate stage 和返回结果保留 `assumptions`、`unknowns`、`conflicts`、`non_goals`、`decision_blockers`；blocking 输入状态不是 `dispatch-ready`，最后 stage 为 `facts-gate`，且没有 task-generation、freeze、dispatch artifacts 或 worktree。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_planning_to_dispatch_preserves_complete_facts_envelope_and_blocks_conflicts_end_to_end`
- 命令：`python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_planning_to_dispatch_preserves_complete_facts_envelope_and_blocks_conflicts_end_to_end`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；同时验证 pass 和 blocked 两条路径、stage 顺序、结构化 artifact 与临时 Git 隔离。

### 验收测试4：CLI to-dispatch 同样 fail-closed

- 触发：通过 `python -m pipeline_tools --format json planning to-dispatch ...` 提供包含完整 envelope 的 JSON fixture，并提供一个 blocking facts fixture。
- 断言：合法 fixture 到达 dispatch-ready；blocking fixture 返回非零 JSON，`facts-gate` 为最后 stage，后续 dispatch/worktree 不发生，且 stdout JSON 不被 automatic wrapper 的 stderr 诊断污染。
- 测试：`tests/test_cli.py: CLITests.test_planning_to_dispatch_cli_blocks_when_facts_envelope_has_conflicts`
- 命令：`python -m unittest tests.test_cli.CLITests.test_planning_to_dispatch_cli_blocks_when_facts_envelope_has_conflicts`
- 验收模式：协议/集成
- 证据等级：2
- 结果要求：退出码边界明确（合法为 0、阻塞为非零）；JSON 可解析；单条命令不超过 180 秒。

### 验收测试5：automatic metrics 异常不改变原始命令退出码

- 触发：mock `metric_event` 失败并执行返回非零的 `command run`，同时让 automatic wrapper 参与。
- 断言：`main()` 返回被测 command 的原始非零码；stderr 只产生 bounded warning；相对 log identity 仍正确；不因 metrics 失败变成 0 或另一个业务码。
- 测试：`tests/test_cli.py: CLITests.test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity`
- 命令：`python -m unittest tests.test_cli.CLITests.test_automatic_metric_failures_preserve_original_exit_code_and_relative_log_identity`
- 验收模式：单元
- 证据等级：1
- 结果要求：退出码 0（测试本身通过）；测试内部必须断言被测 `main()` 返回码为 1 和 warning 内容。

### 验收测试6：调查并修复外层测试命令退出码不干净

- 触发：以 subprocess 方式运行 automatic metrics 开启的测试/CLI wrapper，再运行同一命令关闭 automatic metrics，对比外层 returncode、stdout、stderr 和真实内部失败码。
- 断言：wrapper 不吞掉失败、不把 warning 当失败、不以 finally 的返回覆盖原始结果；外层命令 returncode 与测试 runner 的真实结果一致。若发现问题来自 shell/cmd 或测试 runner 而非产品 wrapper，报告必须给出最小复现、调用栈/边界和未修复外部原因，不得伪造 PASS。
- 测试：`tests/test_cli.py: CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code`
- 命令：`python -m unittest tests.test_cli.CLITests.test_automatic_metrics_wrapper_preserves_outer_test_command_exit_code`
- 验收模式：协议/集成
- 证据等级：1
- 结果要求：退出码 0；直接检查至少两次 subprocess returncode；任何未解决外层原因标记 BLOCKED/未验证并留证据。

### 验收测试7：全量回归不依赖关闭 metrics

- 触发：从仓库根目录运行完整测试发现。
- 断言：所有既有测试与本任务测试通过；没有通过删除、跳过或全局关闭 automatic metrics 回避失败；测试进程退出码为 0，超时不超过累计 600 秒。
- 测试：`tests/: complete regression suite with the automatic metrics wrapper enabled and disabled`
- 命令：`python -m unittest discover -s tests -v`
- 验收模式：集成
- 证据等级：1
- 结果要求：退出码 0；记录实际测试数量、完整命令、环境变量状态和任何 wrapper stderr；不要把历史 `.pipeline/metrics` 产物纳入本任务范围。

## 外部操作

- 允许：本地临时目录、临时 Git repository、Python `subprocess`、本地测试 runner、仓库内文件读写。
- 禁止：网络请求、凭据/密钥读取、遥测上传、真实生产项目、真实浏览器或设备、外部 API、修改用户 Git 远端、提交或推送。
- 任务单验证和测试命令只读/写临时证据；不得写 `.pipeline/metrics/**`，不得清理或改写历史证据。

## 决策点

出现以下情况时，保留现场并报告主代理，不得静默改变契约：

1. 现有 facts contract 无法定义五个 envelope 字段的缺失/默认语义。
2. automatic wrapper 的不干净退出码只能由 shell/cmd、测试 runner 或外部环境修复，超出 `pipeline_tools/**`、`tests/**` 和本任务允许文档范围。
3. 修复需要修改 implement-plan、IDEA、历史任务、metrics contract/实现或 `.pipeline/metrics/**`。
4. 既有合法 fixture 因严格 fail-closed 规则需要产品决策，而不是机械补齐字段。

---

## 任务级进度（主代理维护）

> 以下内容不是新的设计权威。契约区在提交后冻结；此处记录进度、裁决和最终结果。

### 任务锚点

- 基线 HEAD：-
- 契约提交：-
- 执行分支：-
- 执行 worktree：`<仓库根目录>/.worktrees/implement-plan-coverage-repair-continuation-1`（核对后的绝对路径）

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-1 | 未开始 | - | - | - |
| acceptance-test-2 | 未开始 | - | - | - |
| acceptance-test-3 | 未开始 | - | - | - |
| acceptance-test-4 | 未开始 | - | - | - |
| acceptance-test-5 | 未开始 | - | - | - |
| acceptance-test-6 | 未开始 | - | - | - |
| acceptance-test-7 | 未开始 | - | - | - |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| - | 任务单创建 | 未开始 | - | validate 后冻结并按 pipeline 派发 |

### 设计变更与延续任务索引

- 本任务是既有规划/dispatch实现的 continuation；无新的设计裁决。如需改变五字段 envelope、fail-closed 边界或 wrapper 归因，建立新的 `docs/tasks/*continuation*.md`，不得覆盖本任务历史。

### 最终结果

- 状态：未开始
- 执行子代理：未开始
- 独立审查子代理：未开始
- 主代理最终检查：未开始
- 合并提交：-
- 合并后复验：未开始
- 遗留项：-
- 未提交：本任务按用户要求 validate 后不提交
