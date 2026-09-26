# dispatch-fail-closed-and-approval-semantics：派发 fail-closed 与确认语义修复

<!-- Task ID: dispatch-fail-closed-and-approval-semantics -->
<!-- Contract section is frozen after commit. Lifecycle sections are maintained by the main agent. -->

```pipeline-contract
{"schema":2,"task_id":"dispatch-fail-closed-and-approval-semantics","task_type":"repair","implement_plan":{"path":"implement-plan.md"},"requirements":["repair dispatch stage failure handling and approval-mode semantics without weakening existing planning gates"],"resources":["pipeline_tools/planning.py","pipeline_tools/core.py","tests/test_planning_dispatch_integration.py","tests/test_planning_lifecycle.py","docs/tasks/dispatch-fail-closed-and-approval-semantics.md"],"allowed_paths":["pipeline_tools/planning.py","pipeline_tools/core.py","tests/test_planning_dispatch_integration.py","tests/test_planning_lifecycle.py","docs/tasks/dispatch-fail-closed-and-approval-semantics.md"],"forbidden_paths":["implement-plan.md","IDEA.md","docs/tasks/planning-to-dispatch-integration.md","docs/tasks/** existing tasks","tests/** other than explicitly allowed tests","pipeline_tools/** other than explicitly allowed modules",".pipeline/**",".pipeline/metrics/**",".worktrees/**","metrics/**","**/*secret*","**/*token*"],"operations":[{"id":"dispatch-fail-closed","kind":"repair","scope":"planning-to-dispatch dispatch stages","acceptance_tests":["acceptance-test-1","acceptance-test-2","acceptance-test-3"]},{"id":"dispatch-approval-semantics","kind":"repair","scope":"automatic and manual approval policy","acceptance_tests":["acceptance-test-4","acceptance-test-5"]},{"id":"dispatch-identity-preservation","kind":"validate","scope":"run/task/worktree identity and retained artifacts","acceptance_tests":["acceptance-test-2","acceptance-test-3","acceptance-test-5"]}],"chain":{"entry":["pipeline_tools/__main__.py: planning to-dispatch CLI entry"],"interaction":["pipeline_tools/__main__.py: --approval-mode and --approve inputs"],"application":["pipeline_tools/planning.py: planning_to_dispatch"],"domain":["pipeline_tools/planning.py: stage status, approval policy, conflict and recovery classification"],"persistence":[".pipeline/planning/<planning-run-id>/dispatch.json and retained stage artifacts",".worktrees/dispatch-fail-closed-and-approval-semantics/ identity when dispatch succeeds"],"readback":["pipeline_tools/__main__.py: structured dispatch JSON and stage/next_actions output"],"recovery":["pipeline_tools/planning.py: stop downstream stages, preserve artifacts, and return blocked conflict/recovery action"]},"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":3,"test_ref":"tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts -v"},{"id":"acceptance-test-2","evidence_level":3,"test_ref":"tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts -v"},{"id":"acceptance-test-3","evidence_level":3,"test_ref":"tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_dispatch_failure_does_not_create_or_replace_worktree","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_failure_does_not_create_or_replace_worktree -v"},{"id":"acceptance-test-4","evidence_level":3,"test_ref":"tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_automatic_approval_dispatches_without_explicit_approve","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_automatic_approval_dispatches_without_explicit_approve -v"},{"id":"acceptance-test-5","evidence_level":3,"test_ref":"tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_manual_approval_requires_explicit_approve_before_dispatch","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_manual_approval_requires_explicit_approve_before_dispatch -v"},{"id":"acceptance-test-6","evidence_level":2,"test_ref":"tests/test_planning_lifecycle.py: PlanningLifecycleTests.test_manual_finalize_requires_approval_but_automatic_finalize_does_not","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_lifecycle.PlanningLifecycleTests.test_manual_finalize_requires_approval_but_automatic_finalize_does_not -v"},{"id":"acceptance-test-7","evidence_level":1,"test_ref":"tests/: complete regression suite","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"},{"id":"acceptance-test-8","evidence_level":1,"test_ref":"docs/tasks/dispatch-fail-closed-and-approval-semantics.md: schema and contract validation","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/dispatch-fail-closed-and-approval-semantics.md"}],"dependencies":["planning-to-dispatch-integration"],"required_evidence_levels":[1,2,3]}
```

## 任务身份

- 项目：programing-pipeline
- 领域或阶段：规划到派发集成的修复 / continuation-1
- 任务类型：`repair`
- 用户结果或系统能力：规划到派发遇到任一阶段失败、冲突或身份漂移时立即 fail-closed 并保留可恢复现场；automatic 模式不要求显式 approve，manual 模式在创建 worktree 或进入 dispatch 前必须获得显式 approve。
- 前置任务：`planning-to-dispatch-integration`
- 执行 worktree 约定：`<仓库根目录>/.worktrees/dispatch-fail-closed-and-approval-semantics`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态：未开始

## 依赖与范围

### 前置条件

- `planning-to-dispatch-integration` 已完成并提供规划到派发七段编排、结构化阶段结果和唯一 worktree identity。
- `implement-plan.md` 是需求权威文件；其内容和 SHA-256 在本任务执行期间必须稳定。
- 现有规划、契约一致性、冻结检查和 identity gate 必须继续先于派发执行。
- 本任务只修复批准计划中的 fail-closed 与 approval policy 语义，不新增产品业务能力。

### 允许修改

- `pipeline_tools/planning.py`：派发编排、阶段失败/冲突分类、自动/人工确认策略。
- `pipeline_tools/core.py`：仅在修复需要时调整与派发 identity/保留现场直接相关的机械边界。
- `tests/test_planning_dispatch_integration.py`：新增或调整本任务列出的派发边界用例。
- `tests/test_planning_lifecycle.py`：新增本任务列出的 lifecycle approval 回归用例。
- 本任务单 `docs/tasks/dispatch-fail-closed-and-approval-semantics.md` 的任务级进度区。

### 明确不改

- `implement-plan.md`、`IDEA.md`、`metrics` 和 `.pipeline/metrics/**`。
- `planning-to-dispatch-integration` 及任何已有任务单，不改写父任务历史或既有冻结契约。
- 未列入允许范围的生产代码、测试、文档、接口、数据格式和外部项目。
- 不删除或覆盖失败现场、dispatch artifact、已有 worktree 或证据；不自动合并、不自动清理。
- 不把 executor/reviewer 的结果伪造成 dispatch 成功，也不以测试数量替代语义验收。

## 事实、假设与待决

### 已确认事实

- `planning_to_dispatch` 的成功阶段顺序必须保持 `preflight → facts-gate → task-generation → contract-consistency → freeze → dispatch-identity → dispatch`。
- 现有集成测试已覆盖部分 preflight/facts 失败、manual 等待和重复派发边界；本 continuation 补齐冲突 fail-closed 与 approval 方向性断言。
- 任务单 schema 2 要求完整 `acceptance-test-*` ID、七段 `chain`、操作到验收测试的绑定、依赖和证据等级。

### 未验证事实

- 修复前各 dispatch stage 在所有 identity conflict 和 worktree 创建失败组合下的实际返回分类，必须由 executor 读取代码并以测试确认。
- 具体实现函数和最小修改点以当前基线代码为准；不得因实现便利扩大允许路径。

### 禁止猜测

- 不得把 `approved=True` 作为 automatic 模式的必要条件；不得把 automatic 与 manual 的语义互换。
- 不得在冲突、漂移、重复占用或持久化失败时继续执行下游阶段、创建/替换 worktree 或返回 `dispatch-ready`。
- 不得通过删除 artifact、重写历史或跳过 contract/freeze/identity gate 消除失败。

## 设计与行为契约

[触发] 主代理以规划 run/task 输入请求 dispatch
→ [处理] 沿既定七段链路逐段执行；每段检查结构化结果、同一 run/task/HEAD/path identity 和 approval policy
→ [状态] 任一失败或冲突将当前运行分类为 blocked/fail，停止所有下游阶段，原子保留可读 artifact、errors 和 next_actions；成功才允许唯一 dispatch
→ [可见结果] automatic 在无显式 `--approve` 时可到达 `dispatch-ready`；manual 在显式 approve 前保持 blocked 且不创建 worktree，approve 后才 dispatch

- **冲突 fail-closed**：facts conflict、contract mismatch、freeze drift、baseline/HEAD/branch/worktree identity drift、已占用 worktree、artifact 写入/读取不一致和重复 dispatch 均为阻塞；不得降级为 warning 或成功。
- **阶段停止**：失败阶段是 `stages` 最后一段；后续 generation、identity 或 dispatch 不执行，错误路径保持可审计。
- **approval 语义**：`approval_mode=automatic` 不检查显式 approve；`approval_mode=manual` 必须有显式 approve，缺失时停在 approval gate，且 approve 前不得创建或修改 worktree。
- **幂等与隔离**：重复成功 dispatch 不创建第二 worktree；冲突/失败重试不覆盖已有 artifact，不把父任务或其他 run 的身份借入当前 run。
- **返回边界**：`dispatch-ready` 仅表示 dispatch 阶段完成，不表示 executor/reviewer PASS；任何未满足条件的路径必须返回结构化 blocked/fail 和下一步。

## 七段链路

1. **entry**：`pipeline_tools/__main__.py` 接收 `planning to-dispatch` CLI/API 输入。
2. **interaction**：读取 `--approval-mode`、`--approve` 及 run/task/baseline/branch 参数，形成结构化请求。
3. **application**：`pipeline_tools/planning.py: planning_to_dispatch` 编排阶段并停止于首个失败。
4. **domain**：验证 facts/contract/freeze/identity，区分冲突、阻塞、失败和可重试边界，实施 automatic/manual approval 规则。
5. **persistence**：写入 `.pipeline/planning/<planning-run-id>/` dispatch 和阶段 artifact；仅成功路径创建唯一 `.worktrees/<task-id>`。
6. **readback**：CLI 返回 JSON/text 中的 stage 序列、identity、artifacts、errors、next_actions 和最终 status 可被后续 gate/审查读取。
7. **recovery**：保留失败现场，指向恢复、修复输入或 continuation；不得自动清理、绕过冲突或伪造成功。

## 外部操作绑定

- `dispatch-stage-failure`：执行七段编排并证明首错停止，对应 `acceptance-test-1`、`acceptance-test-2`。
- `dispatch-conflict-gate`：检测冲突/漂移/占用并 fail-closed，对应 `acceptance-test-2`、`acceptance-test-3`。
- `dispatch-worktree-identity`：只在 identity 验证通过后创建唯一 worktree，对应 `acceptance-test-2`、`acceptance-test-3`。
- `dispatch-automatic-approval`：automatic 无显式 approve 继续派发，对应 `acceptance-test-4`。
- `dispatch-manual-approval`：manual 缺显式 approve 阻塞，approve 后才派发，对应 `acceptance-test-5`、`acceptance-test-6`。
- `dispatch-recovery-preserve`：保留 artifact、错误和 next action，不覆盖失败现场，对应 `acceptance-test-1`、`acceptance-test-2`、`acceptance-test-3`。

## 环境前置

1. 在仓库根目录确认 Python、Git、`pipeline-tools` 可执行，确认主工作树和目标 task-id 身份；不得在契约冻结前派发实现。
2. 每条验收命令使用 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`，单条测试硬上限 180 秒；完整回归使用明确累计上限。
3. 集成测试必须使用临时 Git 仓库和隔离 `.worktrees`/`.pipeline`，不修改当前仓库的产品、测试、IDEA、implement-plan、已有任务单或 metrics。

## 验收测试

### 验收测试1：首个阶段失败停止下游并保留现场

- 触发：分别注入 preflight、facts、generation、contract 或 identity 阶段失败。
- 断言：最终状态不是 `dispatch-ready`；失败阶段是最后阶段；后续阶段不执行；已有 artifact 可读且路径/identity 不被覆盖；错误包含明确 recovery/next action。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_stage_failures_stop_downstream_and_preserve_artifacts -v`
- 验收模式：端到端集成失败边界
- 证据等级：3
- 结果要求：退出码 0；每个注入变体都证明首错停止、artifact 存在且无错误 worktree。

### 验收测试2：冲突和 identity drift fail-closed

- 触发：在 facts/contract/freeze/dispatch identity 关键边界制造冲突、HEAD/branch/baseline 漂移、task/worktree 占用或 artifact identity 不匹配。
- 断言：状态为 `blocked` 或 `fail`；不得继续下游、不得创建/替换 worktree；保留当前 run/task identity 和冲突 artifact；不得返回 `dispatch-ready`。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_conflict_fails_closed_and_preserves_identity_artifacts -v`
- 验收模式：端到端冲突/安全边界
- 证据等级：3
- 结果要求：退出码 0；所有冲突变体均为预期结构化阻塞，父/既有 artifact 哈希不变。

### 验收测试3：派发失败不创建或替换 worktree

- 触发：在 identity 校验通过前或 worktree 创建/写入阶段注入失败，并重复请求同一 task。
- 断言：失败返回非成功状态；不产生第二 worktree，不替换既有 worktree，不删除失败现场；重复调用可识别 duplicate/occupied/recovery。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_dispatch_failure_does_not_create_or_replace_worktree`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_dispatch_failure_does_not_create_or_replace_worktree -v`
- 验收模式：端到端 Git/worktree/恢复
- 证据等级：3
- 结果要求：退出码 0；worktree 数量和既有内容哈希符合隔离/幂等断言。

### 验收测试4：automatic 无显式 approve 可派发

- 触发：使用 `approval_mode=automatic` 请求有效规划到派发，不传 `approved=True`/`--approve`。
- 断言：approval gate 不阻塞；七段链路完成到 `dispatch-ready`；创建的 worktree identity 与请求一致；该结果不表示 executor/reviewer PASS。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_automatic_approval_dispatches_without_explicit_approve`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_automatic_approval_dispatches_without_explicit_approve -v`
- 验收模式：端到端 approval policy
- 证据等级：3
- 结果要求：退出码 0；不依赖显式 approval 参数，不降低其他 gate。

### 验收测试5：manual 必须显式 approve

- 触发：先用 `approval_mode=manual` 且不传 approve 请求有效 dispatch，再用同一有效输入显式 approve。
- 断言：第一请求在 approval gate 返回 blocked 且不创建 worktree；第二请求通过 approval 后才完成 dispatch；其他阶段结果和 identity 保持一致。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_manual_approval_requires_explicit_approve_before_dispatch`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_manual_approval_requires_explicit_approve_before_dispatch -v`
- 验收模式：端到端 approval policy
- 证据等级：3
- 结果要求：退出码 0；缺 approval 永不创建 worktree，显式 approval 后只创建一个正确 identity 的 worktree。

### 验收测试6：lifecycle automatic/manual finalize 语义一致

- 触发：分别以 automatic 和 manual approval mode 完成 generated phase，再尝试 finalize。
- 断言：automatic finalize 无需显式 approval；manual finalize 无 approval 保持 blocked，显式 approval 后才 finalized；identity drift 仍优先 fail-closed。
- 测试：`tests/test_planning_lifecycle.py: PlanningLifecycleTests.test_manual_finalize_requires_approval_but_automatic_finalize_does_not`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_lifecycle.PlanningLifecycleTests.test_manual_finalize_requires_approval_but_automatic_finalize_does_not -v`
- 验收模式：生命周期集成
- 证据等级：2
- 结果要求：退出码 0；状态和 artifact 可重复读取，未授权 finalize 不写成功结果。

### 验收测试7：完整回归

- 触发：运行仓库现有完整测试套件。
- 断言：规划、facts conflict、task generation、contract、identity、recovery 和既有 metrics 行为无回归；本任务范围不漂移。
- 测试：`tests/: complete regression suite`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归
- 证据等级：1
- 结果要求：退出码 0；失败时保留完整现场并不得标记 PASS。

### 验收测试8：任务单结构与 schema 2 校验

- 触发：从仓库根目录验证本任务单。
- 断言：唯一 pipeline-contract 为 schema 2、task_type 为 repair、依赖包含 `planning-to-dispatch-integration`，所有 acceptance test 使用完整名称且操作/链路/路径字段完整。
- 测试：`docs/tasks/dispatch-fail-closed-and-approval-semantics.md: pipeline-contract schema 2 validation`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/dispatch-fail-closed-and-approval-semantics.md`
- 验收模式：契约/结构校验
- 证据等级：1
- 结果要求：退出码 0，输出 `OK: valid task sheet`。

## 决策点

1. 如果批准修复计划与当前实现的函数边界或 approval 默认值不一致，保留 worktree 并报告，不自行扩大范围。
2. 如果任一冲突无法区分为可恢复输入错误还是不可恢复身份漂移，保持 fail-closed，等待主代理裁决。
3. 如果测试需要修改产品、测试、IDEA、implement-plan、已有任务单或 metrics 之外的路径，停止并建立新的 continuation，不静默扩围。
4. 如果运行环境、Git worktree 权限或外部依赖不足，报告 BLOCKED，保留现场，不把环境问题改写为产品 PASS。

---

## 任务级进度（主代理维护）

> 以下内容不是新的设计权威。契约区在提交后冻结；此处记录进度、裁决和最终结果。

### 任务锚点

- 基线 HEAD：-
- 契约提交：-
- 执行分支：-
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/dispatch-fail-closed-and-approval-semantics`（核对后的绝对路径）

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
| acceptance-test-8 | 未开始 | - | - | - |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 1 | continuation-1 任务单创建 | 未开始 | - | 契约提交后按 `planning-to-dispatch-integration` 依赖派发 executor |

### 设计变更与延续任务索引

- 父任务：`docs/tasks/planning-to-dispatch-integration.md`
- 当前 continuation：`docs/tasks/dispatch-fail-closed-and-approval-semantics.md`
- 无其他延续任务。

### 最终结果

- 状态：未开始
- 执行子代理：未开始
- 独立审查子代理：未开始
- 主代理最终检查：未开始
- 合并提交：-
- 合并后复验：未开始
- 遗留项：-

## 生命周期记录

过程事件写入 `.pipeline/dispatch-fail-closed-and-approval-semantics/`，不改冻结契约；本任务单只新增，不提交。

```variant
{"task_id":"dispatch-fail-closed-and-approval-semantics","continuation_of":"planning-to-dispatch-integration","continuation_number":1,"task_type":"repair"}
```

## 外部操作与范围说明

本任务的外部操作仅指 pipeline dispatch 的可观察阶段操作，不执行真实外部服务调用。所有操作必须绑定到上述完整名称验收测试；不允许以自然语言报告、代理自述、metrics 统计或仅编译通过替代验收证据。

## 失败现场规则

冲突、身份漂移、超时、环境缺失、证据缺失和测试失败均保持 BLOCKED/FAIL 分类；不得创建最终化标记、不得清理 worktree/证据、不得修改父任务历史，必须由主代理决定重试、建立下一 continuation 或上报。

## 进度记录规则

任务级进度只由主代理在本任务单维护；executor/reviewer 的完整报告写入本任务证据目录，不能改写冻结契约。每次阶段推进必须回读本任务单、核对 task-id/branch/HEAD/worktree，并更新验收台账和执行记录。

## 交付边界

本任务单生成阶段的唯一交付物是此文件；不提交、不创建 worktree、不派发子代理、不修改产品、测试、IDEA、implement-plan、已有任务单或 metrics。

```pipeline-evidence
{"task_id":"dispatch-fail-closed-and-approval-semantics","role":"main-agent","status":"not-started","worktree":"D:/Projects/Skills/pipeline","branch":"main","head":"7848974","acceptance_results":[],"artifacts":["docs/tasks/dispatch-fail-closed-and-approval-semantics.md"]}
```

```pipeline-contract-duplicate-removed
This section is intentionally non-contract historical text; the sole machine contract is at the top of this task sheet.
```

## 任务单生成阶段核验

- 本文件是唯一新增文件；生成阶段不提交、不创建 worktree、不派发执行或审查子代理。
- `pipeline-contract` 主区块为唯一机器契约；任务执行前必须重新核对主工作树 HEAD、分支、路径和任务单冻结提交。
- 本次仅生成任务单，未执行产品修复或验收测试；下游执行必须遵循冻结契约。
