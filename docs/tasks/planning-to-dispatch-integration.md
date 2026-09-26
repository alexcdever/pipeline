# planning-to-dispatch-integration：规划到派发集成

<!-- Task ID: planning-to-dispatch-integration -->

## 任务目标

把规划前置、事实冲突、任务生成、契约一致性、唯一 worktree、dispatch identity 与证据闸门串成一个 fail-closed 的端到端入口：只有冻结且一致的任务单才能派发，任何失败都保留可恢复现场。本任务是 vertical-feature（工具链能力），不代表外部用户功能完成。

## 任务类型

`vertical-feature`

## 需求引用

- `implement-plan.md`：完整规划到执行生命周期、默认推进/人工确认和失败边界。
- 前置任务：本任务消费全部规划、契约、identity 和 recovery 能力。

## 允许修改

- `pipeline_tools/**`
- `tests/test_planning_dispatch_integration.py`
- `tests/test_cli.py`
- `references/**`
- `SKILL.md`
- `README.md`
- `docs/tasks/planning-to-dispatch-integration.md`

## 明确不改

- `implement-plan.md`、`IDEA.md`
- 既有任务单、既有 `.pipeline/**` 历史和 metrics
- 产品业务代码、外部项目、Git 历史
- 不自动合并、不绕过人工确认配置、不在失败时清理现场

## 前置依赖

- `planning-run-lifecycle`
- `planning-facts-conflict-model`
- `planning-run-task-generation`
- `task-plan-contract-consistency`
- `task-worktree-dispatch-identity`
- `derived-task-dispatch-recovery`

## 设计与行为契约

[触发] 主代理提交有效 planning inputs 并请求 dispatch
→ [处理] preflight → facts/conflict gate → task generation → contract consistency → freeze check → unique worktree/identity → dispatch
→ [状态] 每阶段结构化结果绑定同一 run/task/HEAD/path，失败现场按阶段保留
→ [可见结果] 输出可审计的阶段图和下一步；成功只表示派发完成，不表示 executor/reviewer PASS

- 任一阶段失败立即停止后续阶段；不得把部分成功改写为完整成功。
- 自动推进与逐任务确认都必须尊重用户配置；未授权 dispatch 返回待确认。
- 真实 executor/reviewer 的测试和报告由后续执行阶段证明，本任务只验证 orchestration 边界。

## 七段链路

entry：`pipeline_tools/__main__.py`；interaction：结构化 planning/dispatch 输入与确认；application：`pipeline_tools/core.py`、`planning.py`；domain：facts、task contract、run/task identity、dispatch states；persistence：任务单、`.pipeline/planning/<run-id>/`、`.pipeline/<task-id>/`、`.worktrees/<task-id>/`；readback：阶段 JSON、dispatch verify、lifecycle status；recovery：阶段失败保留现场、derived continuation 和幂等重试。

## 外部操作绑定

- `integration-preflight`：运行规划前置。
- `integration-facts-gate`：拒绝 facts conflict。
- `integration-task-generation`：生成不可覆盖的 task sheets。
- `integration-contract-gate`：校验一致性与冻结。
- `integration-dispatch-identity`：创建/核对唯一 worktree。
- `integration-dispatch-confirm`：遵守自动/人工确认。
- `integration-recovery-route`：把失败导向 preserve 或 derived recovery。

## 环境前置

1. 运行时 preflight 必须确认 Python、Git、pipeline tool、可写 `.pipeline` 和测试能力。
2. 端到端测试使用临时 Git 仓库，executor/reviewer 通过 stub 只验证 dispatch contract，不修改真实项目。

## 验收测试

### 验收测试1：有效输入贯通规划到派发

- 触发：提交无冲突 facts、有效 task plan、确认 dispatch。
- 断言：七阶段按序运行，生成并校验任务单，创建唯一 worktree，最终状态为 dispatch-ready；每阶段引用同一 run/task identity。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch -v`
- 验收模式：端到端集成；证据等级：3；结果要求：退出码 0，阶段序列完整。


- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试2：各阶段失败 fail closed

- 触发：逐一注入 preflight、facts、generation、contract、identity 失败。
- 断言：后续阶段不执行，输出阻塞类别和现场路径，不创建错误 worktree/任务单。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts -v`
- 验收模式：端到端失败边界；证据等级：3；结果要求：每个变体非零且 artifact 哈希稳定。


- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试3：确认策略与重复派发幂等

- 触发：自动推进关闭、人工确认拒绝、重复请求和 identity drift。
- 断言：未确认不派发；重复请求不创建第二 worktree；漂移转 recovery，不伪造成功。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_confirmation_policy_and_repeated_dispatch_are_safe`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_confirmation_policy_and_repeated_dispatch_are_safe -v`
- 验收模式：端到端策略/安全；证据等级：3；结果要求：退出码和状态分类稳定。


- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试4：CLI JSON 与完整回归

- 触发：从 CLI 运行成功、阻塞和恢复路径。
- 断言：JSON 含 schema、run/task identity、阶段结果、artifacts、errors、next_actions；全量测试通过。
- 测试：`tests/test_cli.py: CLITests.test_planning_to_dispatch_cli_contract_and_failure_boundaries`；命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli.CLITests.test_planning_to_dispatch_cli_contract_and_failure_boundaries -v`
- 验收模式：CLI；证据等级：2；结果要求：退出码 0；错误路径是预期结构化失败。


- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`（历史命令未重新核验）
- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试5：全量回归与范围

- 触发：完整测试、契约校验、diff check。
- 断言：所有前置能力无回归，修改仅在允许范围。
- 测试：`tests/: complete regression suite`；命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归；证据等级：1；结果要求：退出码 0。

## 决策点

1. 任一前置任务接口无法组合时停下，建立 continuation，不绕过闸门。
2. 自动推进默认值、人工确认范围或真实代理启动方式存在产品决策时停下。
3. 需要触碰产品代码、既有任务单、metrics 或外部服务时停下。

---

## 任务级进度（主代理维护）

- 基线 HEAD：待提交契约前确认；契约提交：待完成
- 执行分支：`planning-to-dispatch-integration`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/planning-to-dispatch-integration`

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-1 | 未开始 | - | - | - |
| acceptance-test-2 | 未开始 | - | - | - |
| acceptance-test-3 | 未开始 | - | - | - |
| acceptance-test-4 | 未开始 | - | - | - |
| acceptance-test-5 | 未开始 | - | - | - |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 1 | 任务单创建 | 未开始 | - | 契约提交后按依赖派发 executor |

### 设计变更与延续任务索引

- 无。

### 最终结果

- 状态：未开始；执行子代理：未开始；独立审查子代理：未开始；主代理最终检查：未开始；合并提交：-；合并后复验：未开始；遗留项：-

```pipeline-contract
{"schema":2,"task_id":"planning-to-dispatch-integration","task_type":"vertical-feature","implement_plan":{"path":"implement-plan.md"},"allowed_paths":["pipeline_tools/**","tests/test_planning_dispatch_integration.py","tests/test_cli.py","references/**","SKILL.md","README.md","docs/tasks/planning-to-dispatch-integration.md"],"forbidden_paths":["implement-plan.md","IDEA.md","docs/tasks/** existing tasks",".pipeline/** existing history",".pipeline/metrics/**","**/*secret*","**/*token*"],"operations":[{"id":"integration-preflight","kind":"validate","scope":"planning-run","acceptance_tests":["acceptance-test-1","acceptance-test-2"]},{"id":"integration-facts-gate","kind":"gate","scope":"facts","acceptance_tests":["acceptance-test-1","acceptance-test-2"]},{"id":"integration-task-generation","kind":"generate","scope":"task-plan","acceptance_tests":["acceptance-test-1","acceptance-test-2"]},{"id":"integration-contract-gate","kind":"gate","scope":"task-sheet","acceptance_tests":["acceptance-test-1","acceptance-test-2"]},{"id":"integration-dispatch-identity","kind":"dispatch","scope":"worktree","acceptance_tests":["acceptance-test-1","acceptance-test-3"]},{"id":"integration-dispatch-confirm","kind":"confirm","scope":"dispatch","acceptance_tests":["acceptance-test-3","acceptance-test-4"]},{"id":"integration-recovery-route","kind":"recover","scope":"dispatch","acceptance_tests":["acceptance-test-2","acceptance-test-3"]}],"chain":{"entry":["pipeline_tools/__main__.py"],"interaction":["pipeline_tools/__main__.py"],"application":["pipeline_tools/core.py","pipeline_tools/planning.py"],"domain":["pipeline_tools/contract.py","pipeline_tools/planning.py"],"persistence":["docs/tasks/planning-to-dispatch-integration.md",".pipeline/planning/historical-planning-run/",".pipeline/planning-to-dispatch-integration/",".worktrees/planning-to-dispatch-integration/"],"readback":["pipeline_tools/__main__.py"],"recovery":["pipeline_tools/core.py","pipeline_tools/planning.py"]},"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":3,"test_ref":"tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch -v"},{"id":"acceptance-test-2","evidence_level":3,"test_ref":"tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts -v"},{"id":"acceptance-test-3","evidence_level":3,"test_ref":"tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_confirmation_policy_and_repeated_dispatch_are_safe","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_confirmation_policy_and_repeated_dispatch_are_safe -v"},{"id":"acceptance-test-4","evidence_level":2,"test_ref":"tests/test_cli.py: CLITests.test_planning_to_dispatch_cli_contract_and_failure_boundaries","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli.CLITests.test_planning_to_dispatch_cli_contract_and_failure_boundaries -v"},{"id":"acceptance-test-5","evidence_level":1,"test_ref":"tests/: complete regression suite","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"}],"dependencies":["planning-run-lifecycle","planning-facts-conflict-model","planning-run-task-generation","task-plan-contract-consistency","task-worktree-dispatch-identity","derived-task-dispatch-recovery"],"required_evidence_levels":[1,2,3]}
```

## 生命周期记录

过程事件写入 `.pipeline/planning-to-dispatch-integration/`，不改冻结契约。

- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`（历史命令未重新核验）
- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。


## 任务身份

- 项目：pipeline
- 领域或阶段：历史任务结构迁移
- 用户结果或系统能力：保留原任务语义并符合当前结构校验。
- 执行 worktree 约定：UNVERIFIED（历史任务单未在本轮重新核验）
- 状态：UNVERIFIED


## 依赖与范围

### 前置条件

- 原任务单、当前 schema 和校验脚本。

### 允许修改

- 本任务单结构字段。

### 明确不改

- implement-plan.md、IDEA.md、产品代码、metrics 和历史验收结论。


## 事实、假设与待决

### 已确认事实

- 本轮仅依据 task validate 输出修复结构缺口。

### 未验证事实

- 历史验收结果、提交和证据新鲜度保持 UNVERIFIED。

### 禁止猜测

- 不把结构校验通过解释为产品或验收通过。


### 任务锚点

- 基线 HEAD：UNVERIFIED
- 契约提交：UNVERIFIED
- 执行分支：UNVERIFIED
- 执行 worktree：UNVERIFIED


### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| 验收测试1 | UNVERIFIED | - | - | 历史结果未重新核验 |

- 合并提交：UNVERIFIED
