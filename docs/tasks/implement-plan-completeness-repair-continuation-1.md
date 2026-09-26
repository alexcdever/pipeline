# implement-plan completeness repair continuation-1：current target 隔离、decision blockers 与 resource operation coverage

<!-- Task ID: implement-plan-completeness-repair-continuation-1 -->
<!-- Contract section is frozen after commit. Lifecycle sections are maintained by the main agent; no separate progress tracker is required. -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "implement-plan-completeness-repair-continuation-1",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": [
    "pipeline_tools/**",
    "tests/**",
    "docs/tasks/implement-plan-completeness-repair-continuation-1.md",
    "references/**",
    "README.md",
    "SKILL.md"
  ],
  "forbidden_paths": [
    "implement-plan.md",
    "IDEA.md",
    "docs/tasks/implement-plan-coverage-repair-continuation-1.md",
    "docs/tasks/implement-plan-coverage-repair-continuation-2.md",
    "docs/tasks/pipeline-tools-v1.md",
    "docs/tasks/pipeline-tools-v1-continuation-1.md",
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
    "docs/tasks/repository-evidence-hygiene.md",
    "docs/tasks/task-evidence-reconcile.md",
    "docs/tasks/task-plan-contract-consistency.md",
    "docs/tasks/task-worktree-dispatch-identity.md",
    ".pipeline/metrics/**",
    "references/metrics-contract.md"
  ],
  "operations": [
    {
      "id": "repair-current-target-isolation",
      "kind": "repair",
      "scope": "pipeline_tools planning and CLI target selection, current implement-plan identity versus historical task inputs",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-7"]
    },
    {
      "id": "repair-decision-blocker-state-semantics",
      "kind": "repair",
      "scope": "pipeline_tools facts validation and planning-to-dispatch gate decision_blockers status semantics",
      "acceptance_tests": ["acceptance-test-3", "acceptance-test-4", "acceptance-test-7"]
    },
    {
      "id": "cover-single-resource-operation",
      "kind": "single-resource-operation",
      "scope": "one resource operation modeled, validated, dispatched and read back independently",
      "acceptance_tests": ["acceptance-test-5", "acceptance-test-7"]
    },
    {
      "id": "cover-batch-resource-operation",
      "kind": "batch-resource-operation",
      "scope": "multiple-resource batch operation modeled, validated, dispatched and read back independently from single operation",
      "acceptance_tests": ["acceptance-test-6", "acceptance-test-7"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: planning CLI and task-target arguments"],
    "interaction": ["pipeline_tools/__main__.py: argument parsing, JSON input/output and command runner"],
    "application": ["pipeline_tools/planning.py: planning validation, planning_to_dispatch and target selection"],
    "domain": ["pipeline_tools/planning.py: facts validation, decision_blockers status classification, single/batch operation coverage"],
    "persistence": ["pipeline_tools/planning.py: planning-run artifacts and task/dispatch artifacts in isolated temporary repositories"],
    "readback": ["tests/test_planning.py, tests/test_planning_dispatch_integration.py, tests/test_task_generation.py and tests/test_cli.py: assertions over current target, blocker state and operation results"],
    "recovery": ["pipeline_tools/planning.py and pipeline_tools/__main__.py: fail-closed gate, no historical-target leakage, and restart/readback identity checks"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 2,
      "test_ref": "tests/test_planning.py: PlanningTests.test_current_implement_plan_target_isolated_from_historical_task_inputs",
      "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_current_implement_plan_target_isolated_from_historical_task_inputs"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_planning_cli_rejects_historical_task_as_current_target",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_planning_cli_rejects_historical_task_as_current_target"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 1,
      "test_ref": "tests/test_planning_facts_conflicts.py: PlanningFactsConflictTests.test_decision_blocker_status_semantics_are_explicit_and_fail_closed",
      "command_ref": "python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_decision_blocker_status_semantics_are_explicit_and_fail_closed"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 2,
      "test_ref": "tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_decision_blocker_states_gate_dispatch_end_to_end",
      "command_ref": "python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_decision_blocker_states_gate_dispatch_end_to_end"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 2,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_single_resource_operation_has_independent_coverage_and_readback",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_single_resource_operation_has_independent_coverage_and_readback"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 2,
      "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_batch_resource_operation_has_independent_coverage_and_readback",
      "command_ref": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_batch_resource_operation_has_independent_coverage_and_readback"
    },
    {
      "id": "acceptance-test-7",
      "evidence_level": 1,
      "test_ref": "tests/: complete regression suite with the focused current-target, blocker-state and single/batch operation tests",
      "command_ref": "python -m unittest discover -s tests -v"
    }
  ],
  "dependencies": [
    "implement-plan-coverage-repair-continuation-2",
    "Existing schema2 contract validation in pipeline_tools/contract.py",
    "Existing planning facts model, task generation and planning-to-dispatch gate",
    "Existing CLI JSON command and unittest harness"
  ],
  "required_evidence_levels": [1, 2]
}
```

`pipeline-contract` is the frozen machine-readable contract for this continuation. The executor must consume the completed coverage/facts repair from dependency `implement-plan-coverage-repair-continuation-2`, then add only the missing current-target isolation, blocker-state semantics and separately modeled single/batch operation coverage. Historical task documents and historical evidence are context only; they must not become the current target or be rewritten.

## 任务身份

- 项目：programing-pipeline / pipeline-tools
- 领域或阶段：current implement-plan target identity、decision blocker gate semantics、single/batch resource-operation coverage
- 依赖任务：`implement-plan-coverage-repair-continuation-2`（仅消费其已完成契约，不改写其历史）
- 用户结果或系统能力：规划、CLI、dispatch、持久化/回读和恢复链路始终绑定当前 implement-plan target；`decision_blockers` 的 `blocking` 未解决状态阻断，`resolved` 与 `non_blocking` 不阻断，未知状态 fail-closed；single 与 batch resource operations 显式建模并分别覆盖。
- 执行 worktree 约定：`<仓库根目录>/.worktrees/implement-plan-completeness-repair-continuation-1`，由主代理在契约提交后用 `git worktree add` 创建；本任务单创建阶段不创建 worktree
- 状态：已完成，证据闭环并已合并后复验

## 依赖与范围

### 前置条件

- 依赖任务 `implement-plan-coverage-repair-continuation-2` 已提供 schema2 coverage、facts envelope 和 wrapper 边界的基线；本任务不重复改写这些已冻结结果。
- 当前代码已有规划、task generation、planning-to-dispatch、CLI JSON 和临时 Git 测试设施；executor 必须先读取实际符号与测试，再实现缺口。
- 当前 target 必须由本次规划输入和当前 implement-plan 身份确定；历史任务单、历史 planning run 或历史 evidence 不得被隐式重用。
- `decision_blockers` 状态集合必须是显式且有限的；未知状态不能按非阻断处理。

### 允许修改

- `pipeline_tools/**`：仅限 current target identity isolation、decision blocker status gate、single/batch resource-operation model and coverage 所需实现。
- `tests/**`：新增或调整直接证明本任务七条验收的单元、CLI、集成、持久化/回读和恢复测试。
- 本任务单 `docs/tasks/implement-plan-completeness-repair-continuation-1.md`：仅由主代理维护任务级进度；契约提交后冻结。
- `references/**`、`README.md`、`SKILL.md`：仅在公开行为说明需要同步时修改。
- 允许消费依赖任务留下的允许范围实现，但必须由本任务的新鲜验收重新证明，不能以旧报告代替证据。

### 明确不改

- 不修改 `implement-plan.md`、`IDEA.md`、依赖任务或任何历史任务单；不得把历史 BLOCKED、PASS 或未验证状态改写。
- 不修改 `.pipeline/metrics/**`、metrics contract、统计数据模型或通过关闭自动指标规避验收。
- 不改变 schema2 既有必填 coverage 语义、审批语义、worktree identity 规则或外部系统协议来绕过本任务。
- 不把 single operation 的测试结果计作 batch coverage，或反过来；不使用一个笼统 operation ref 替代两种显式模型。
- 本任务创建阶段只创建并验证任务单，不创建 worktree、不派发 executor/reviewer、不修改产品实现。

## 事实、假设与待决

### 已确认事实

- 依赖任务的 schema2 contract 已要求 top-level acceptance records 完整，并已建立 facts envelope 与 planning-to-dispatch gate 的测试边界。
- `implement-plan.md` 是规划需求的唯一当前目标；任务单和历史 planning artifacts 不是需求目标。
- 当前测试套件使用 Python 标准库 `unittest`，并已有 planning、CLI、task generation 和 dispatch integration 测试模块。
- 本任务必须同时验证真实 CLI 命令、unittest 用例、七段链路以及本地外部操作边界；单一层级绿色不能代替端到端证明。

### 未验证事实

- 未验证 executor 开始时 current target identity 在所有 CLI 和 library entry points 的实际字段名、存储位置及历史输入拒绝边界。
- 未验证现有 `decision_blockers` fixture 是否已区分 `blocking`、`resolved`、`non_blocking` 和未知状态；不得从旧测试名称推断语义已完成。
- 未验证 single/batch operation 的现有 schema 字段、fixture 和 readback artifact 形状；必须以代码和直接测试确定最小兼容修复。
- 未验证当前恢复路径是否会从历史 planning run 或历史任务单读取 target；需用临时目录、重启/重新读取和身份断言证明。

### 禁止猜测

- 不得把缺失或未知 `decision_blockers.status` 当作 `resolved`、`non_blocking` 或空列表；未知状态必须 fail-closed，缺失语义需由现有 contract 或测试明确。
- 不得把历史任务单路径、旧 planning run、旧 evidence 或旧 branch 当作当前 target 的等价身份。
- 不得认为单元测试通过就证明持久化、CLI、dispatch、回读和恢复链路通过；每段链路必须有直接断言。
- 不得通过放宽 operation schema、删除测试或修改禁止范围制造绿色结果。

## 设计与行为契约

[触发] 从当前仓库运行 planning/task-generation/dispatch CLI，或由库 API 启动一次新的 planning run
→ [处理] 解析并锁定当前 implement-plan target identity；隔离历史任务输入；校验 `decision_blockers` 状态；分别生成 single-resource 与 batch-resource operation coverage；贯通 CLI、应用、领域、持久化、回读和恢复
→ [状态] 当前 run 的 artifacts、task plan、dispatch facts 与回读结果只引用当前 target；未解决 `blocking` 阻断，`resolved`/`non_blocking` 不阻断，未知状态 fail-closed；single/batch 各有独立 operation、acceptance ref 和结果
→ [可见结果] 当前 target 的合法运行达到预期 ready/dispatch 状态；历史 target 泄漏、未解决 blocker、未知 blocker 状态或缺失 single/batch coverage 返回结构化非零失败；重启/重新读取保持同一 target identity 与 operation 语义

- target identity 必须在 entry、interaction、application、domain、persistence、readback、recovery 七段中可追溯，不能只在入口字符串中出现。
- blocker gate 的判定必须显式记录状态和原因；未解决 `blocking` 阻断，`resolved` 与 `non_blocking` 不阻断，未知状态 fail-closed。
- single 与 batch operation 必须分别有模型、验收引用、执行结果和回读断言；一方缺失不得由另一方补足。
- 历史输入只能作为被拒绝/隔离的 fixture，不能成为当前运行的隐式 fallback。

## 环境前置

1. 在仓库根目录运行 `python -m pipeline_tools task validate docs/tasks/implement-plan-completeness-repair-continuation-1.md`，任务单必须先通过。
2. 使用 Python 标准库测试环境；每条聚焦验收硬上限 180 秒，完整回归累计上限 600 秒。
3. 执行前记录主工作树身份、依赖任务提交、当前 target 文件身份、允许范围内未提交 diff 和历史现场；不得把历史任务或指标文件纳入实现。
4. 只允许本地 Python、临时目录、临时 Git repository、subprocess、本地测试 runner 和文件读写；不需要网络、凭据、浏览器、设备或真实生产 dispatch。

## 验收测试

### 验收测试1：库 API 隔离 current implement-plan target 与历史输入

- 触发：在临时仓库创建当前 target 与历史任务/历史 planning artifact，调用 planning entry point 并显式提供历史输入作为干扰项。
- 断言：运行只绑定当前 target 的规范路径、哈希/identity 和新 run；历史任务、历史 run、历史 artifact 不被选作 target，也不能覆盖当前 target；错误身份 fail-closed。
- 测试：`tests/test_planning.py: PlanningTests.test_current_implement_plan_target_isolated_from_historical_task_inputs`
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_current_implement_plan_target_isolated_from_historical_task_inputs`
- 验收模式：集成/持久化
- 证据等级：2
- 结果要求：退出码 0；断言当前 target identity、拒绝/隔离历史输入以及新 run artifact 的引用均独立成立。

### 验收测试2：CLI current target identity 端到端隔离

- 触发：通过真实 `python -m pipeline_tools` JSON CLI 分别提交当前 target、历史任务路径和历史 planning run 参数。
- 断言：当前 target CLI 成功时 JSON、planning artifact 和 dispatch identity 一致；历史 target 参数不能伪装成当前 target，返回非零结构化错误且不创建下游 dispatch/worktree artifact。
- 测试：`tests/test_cli.py: CLITests.test_planning_cli_rejects_historical_task_as_current_target`
- 命令：`python -m unittest tests.test_cli.CLITests.test_planning_cli_rejects_historical_task_as_current_target`
- 验收模式：协议/集成
- 证据等级：2
- 结果要求：退出码与 JSON status 一致；至少比较一次合法 current 与一次历史输入的 subprocess returncode 和 artifact 集合。

### 验收测试3：decision_blockers 状态语义单元覆盖

- 触发：构造 `decision_blockers` 分别为未解决 `blocking`、`resolved`、`non_blocking`、未知状态、缺失状态和空集合的 facts。
- 断言：未解决 `blocking` 返回阻断；`resolved` 与 `non_blocking` 不阻断；未知/缺失状态 fail-closed 并报告字段与状态；不存在隐式 truthy/falsy fallback。
- 测试：`tests/test_planning_facts_conflicts.py: PlanningFactsConflictTests.test_decision_blocker_status_semantics_are_explicit_and_fail_closed`
- 命令：`python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_decision_blocker_status_semantics_are_explicit_and_fail_closed`
- 验收模式：单元
- 证据等级：1
- 结果要求：退出码 0；每个状态有独立断言，未知和缺失状态均不能获得 pass。

### 验收测试4：decision_blockers gate 经 planning_to_dispatch 端到端贯通

- 触发：通过 `planning_to_dispatch` 和真实临时 Git 目录运行四类 blocker fixture，并读取 facts-gate、下游 stage、dispatch artifact 和 worktree 状态。
- 断言：未解决 `blocking` 停在 facts-gate 且不创建下游产物；`resolved`/`non_blocking` 到达合法下游状态；未知状态非零 fail-closed；状态语义在 JSON/readback 中保持。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_decision_blocker_states_gate_dispatch_end_to_end`
- 命令：`python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_decision_blocker_states_gate_dispatch_end_to_end`
- 验收模式：集成/持久化/恢复
- 证据等级：2
- 结果要求：退出码 0；逐类断言最后 stage、artifact、worktree 和 readback identity，且重读结果不改变 gate 语义。

### 验收测试5：single resource operation 独立建模与覆盖

- 触发：生成只包含一个 resource 的 operation，并运行 task generation、dispatch/readback 及恢复读取。
- 断言：single operation 有显式类型/范围、独立 acceptance ref、七段链路引用和独立结果；不得由 batch fixture 或批量 ref 补足；重新读取仍能识别 single 语义。
- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_single_resource_operation_has_independent_coverage_and_readback`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_single_resource_operation_has_independent_coverage_and_readback`
- 验收模式：集成/持久化/恢复
- 证据等级：2
- 结果要求：退出码 0；独立检查 model、acceptance ref、artifact、回读和恢复后的 operation kind。

### 验收测试6：batch resource operation 独立建模与覆盖

- 触发：生成包含多个 resources 的 batch operation，并运行与 single operation 分开的 task generation、dispatch/readback 及恢复读取。
- 断言：batch operation 有显式类型/成员范围、独立 acceptance ref、逐成员或批量结果的明确断言和独立恢复回读；single fixture 不能代替 batch coverage。
- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_batch_resource_operation_has_independent_coverage_and_readback`
- 命令：`python -m unittest tests.test_task_generation.TaskGenerationTests.test_batch_resource_operation_has_independent_coverage_and_readback`
- 验收模式：集成/持久化/恢复
- 证据等级：2
- 结果要求：退出码 0；独立检查 batch model、resource membership、acceptance ref、artifact、回读和恢复后的 operation kind。

### 验收测试7：完整 unittest 回归与真实 CLI 命令边界

- 触发：从仓库根目录运行完整 unittest discovery，并单独运行本任务六条聚焦用例；CLI 验收必须通过真实 subprocess，不得只调用内部函数。
- 断言：既有测试及本任务测试通过；current target、blocker state、single operation、batch operation 没有被历史证据替代；测试进程退出码为 0，未修改禁止路径。
- 测试：`tests/: complete regression suite covering current-target isolation, blocker semantics and separate single/batch operations`
- 命令：`python -m unittest discover -s tests -v`
- 验收模式：集成/回归
- 证据等级：1
- 结果要求：退出码 0；记录实际测试数量、完整命令、工作树 identity、范围检查结果和所有聚焦命令结果，累计不超过 600 秒。

## 外部操作

- 允许：本地临时目录、临时 Git repository、Python `subprocess`、本地 unittest runner、本地文件读写和重启/重新读取测试。
- 禁止：网络请求、凭据/密钥读取、遥测上传、真实生产项目、真实浏览器或设备、外部 API、修改用户 Git 远端、修改禁止路径、创建第二个 worktree。
- 真实 CLI 操作必须通过项目入口执行并检查 subprocess returncode/stdout/stderr；内部函数测试不能替代 CLI 证据。
- 本任务创建阶段只写本任务单并提交契约，不写指标文件，不清理或改写历史证据。

## 决策点

出现以下情况时，保留现场并报告主代理，不得静默改变契约：

1. current target identity 的来源或历史输入拒绝规则无法从现有 contract/code/test 唯一确定。
2. `decision_blockers` 缺失状态的兼容语义与 fail-closed 要求冲突，或需要用户裁决协议兼容性。
3. single/batch operation 的现有 schema 不支持独立建模而需要扩大数据格式、修改禁止路径或迁移历史数据。
4. 修复需要修改 `implement-plan.md`、`IDEA.md`、依赖/历史任务、metrics contract 或指标文件。
5. 外部 CLI、Git、权限或测试环境阻塞，无法取得真实 subprocess、持久化、回读或恢复证据。

---

## 任务级进度（主代理维护）

> 以下内容不是新的设计权威。契约区在提交后冻结；此处记录进度、裁决和最终结果。依赖任务和历史任务状态不可覆盖。

### 任务锚点

- 基线 HEAD：413ef362e0a0df3c4a8257e05ee6e5e0ae028ead
- 契约提交：413ef362e0a0df3c4a8257e05ee6e5e0ae028ead
- 执行分支：`implement-plan-completeness-repair-continuation-1`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/implement-plan-completeness-repair-continuation-1`
- 依赖任务：`docs/tasks/implement-plan-coverage-repair-continuation-2.md`（只读依赖，历史不改写）

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-1 | 完成 | fresh reviewer focused unittest | `.pipeline/implement-plan-completeness-repair-continuation-1/review-report.md` | current target 与历史输入隔离 |
| acceptance-test-2 | 完成 | fresh reviewer focused unittest | `.pipeline/implement-plan-completeness-repair-continuation-1/review-report.md` | CLI target identity 隔离 |
| acceptance-test-3 | 完成 | fresh reviewer focused unittest | `.pipeline/implement-plan-completeness-repair-continuation-1/review-report.md` | blocker 状态 fail-closed 语义 |
| acceptance-test-4 | 完成 | fresh reviewer focused unittest | `.pipeline/implement-plan-completeness-repair-continuation-1/review-report.md` | blocker gate 七段链路 |
| acceptance-test-5 | 完成 | fresh reviewer focused unittest | `.pipeline/implement-plan-completeness-repair-continuation-1/review-report.md` | single resource operation 独立覆盖 |
| acceptance-test-6 | 完成 | fresh reviewer focused unittest | `.pipeline/implement-plan-completeness-repair-continuation-1/review-report.md` | batch resource operation 独立覆盖 |
| acceptance-test-7 | 完成 | fresh full `python -m unittest discover -s tests -v` (168 tests) | `.pipeline/implement-plan-completeness-repair-continuation-1/final-check.md` | 完整 unittest 回归 |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| round 1 | executor implementation | PASS | `.pipeline/implement-plan-completeness-repair-continuation-1/executor-report.md` | independent review |
| round 2 | reviewer repair continuation | PASS | `.pipeline/implement-plan-completeness-repair-continuation-1/review-report.md` | main final check and merge |
| round 2 | main final check, pre-merge gate, merge | PASS | `.pipeline/implement-plan-completeness-repair-continuation-1/final-check.md` | post-merge revalidation |

### 设计变更与延续任务索引

- 依赖：`docs/tasks/implement-plan-coverage-repair-continuation-2.md`；只读消费，不覆盖其历史。
- 本任务当前无新的设计裁决。如需改变 current target、blocker 状态、single/batch 模型或范围，建立新的 continuation 任务，不覆盖本任务或依赖历史。

### 最终结果

- 状态：已完成并已合并
- 执行子代理：PASS；`.pipeline/implement-plan-completeness-repair-continuation-1/executor-result.json`
- 独立审查子代理：PASS（round 2）；`.pipeline/implement-plan-completeness-repair-continuation-1/reviewer-result.json`
- 主代理最终检查：PASS；`.pipeline/implement-plan-completeness-repair-continuation-1/final-check.md`
- 合并提交：主树 merge commit（`git merge --no-ff implement-plan-completeness-repair-continuation-1`）
- 合并后复验：PASS；主树重新执行全量 `python -m unittest discover -s tests -v`、scope、evidence verify/readiness、gate
- 遗留项：无；`.pipeline/metrics/**` 仅作为项目生成的 workflow metadata 允许进入 scope，不参与验收结论
