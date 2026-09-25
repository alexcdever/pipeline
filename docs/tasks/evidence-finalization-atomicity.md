# evidence-finalization-atomicity：证据最终化清理原子性修复

<!-- Task ID: evidence-finalization-atomicity -->
<!-- Contract section is frozen after commit. Lifecycle sections are maintained by the main agent. -->

```pipeline-contract
{"schema":2,"task_id":"evidence-finalization-atomicity","task_type":"repair","implement_plan":{"path":"implement-plan.md"},"requirements":["repair evidence finalization so cleanup failure is fail-closed and atomic: no finalization marker is left behind, raw evidence remains preserved, and retry is idempotent"],"resources":["pipeline_tools/planning.py","tests/test_planning.py","docs/tasks/evidence-finalization-atomicity.md","references/acceptance-evidence.md","references/execution-and-review.md","references/merge-and-recovery.md"],"allowed_paths":["pipeline_tools/planning.py","tests/**","docs/tasks/evidence-finalization-atomicity.md","references/**"],"forbidden_paths":["implement-plan.md","IDEA.md","pipeline_tools/** other than pipeline_tools/planning.py","docs/tasks/** other than docs/tasks/evidence-finalization-atomicity.md",".pipeline/**",".pipeline/metrics/**","metrics/**",".worktrees/**","**/*secret*","**/*token*"],"operations":[{"id":"finalization-cleanup-atomicity","kind":"repair","scope":"evidence finalization cleanup failure","acceptance_tests":["acceptance-test-cleanup-no-marker","acceptance-test-cleanup-preserves-raw","acceptance-test-cleanup-idempotence"]},{"id":"finalization-regression","kind":"validate","scope":"existing evidence finalization behavior","acceptance_tests":["acceptance-test-existing-finalization","acceptance-test-regression"]},{"id":"finalization-contract","kind":"validate","scope":"task contract and references","acceptance_tests":["acceptance-test-contract"]}],"chain":{"entry":["pipeline_tools/planning.py: finalize_evidence entry"],"interaction":["tests/test_planning.py: finalization cleanup failure fixtures"],"application":["pipeline_tools/planning.py: finalization validation and cleanup transaction"],"domain":["pipeline_tools/planning.py: finalized versus blocked state"],"persistence":[".pipeline/<task-id>/finalization.json and raw evidence files"],"readback":["pipeline_tools/planning.py: finalize_evidence result status and marker"],"recovery":["pipeline_tools/planning.py: preserve raw evidence and retry without partial marker"]},"acceptance_tests":[{"id":"acceptance-test-cleanup-no-marker","evidence_level":2,"test_ref":"tests/test_planning.py: PlanningTests.test_finalization_cleanup_failure_leaves_no_marker","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_finalization_cleanup_failure_leaves_no_marker -v"},{"id":"acceptance-test-cleanup-preserves-raw","evidence_level":2,"test_ref":"tests/test_planning.py: PlanningTests.test_finalization_cleanup_failure_preserves_raw_evidence","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_finalization_cleanup_failure_preserves_raw_evidence -v"},{"id":"acceptance-test-cleanup-idempotence","evidence_level":2,"test_ref":"tests/test_planning.py: PlanningTests.test_finalization_cleanup_failure_retry_is_idempotent","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_finalization_cleanup_failure_retry_is_idempotent -v"},{"id":"acceptance-test-existing-finalization","evidence_level":2,"test_ref":"tests/test_planning.py: PlanningTests.test_finalization_requires_main_approval_and_keeps_raw_on_failure","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_finalization_requires_main_approval_and_keeps_raw_on_failure -v"},{"id":"acceptance-test-regression","evidence_level":1,"test_ref":"tests/: complete regression suite","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"},{"id":"acceptance-test-contract","evidence_level":1,"test_ref":"docs/tasks/evidence-finalization-atomicity.md: schema 2 repair contract validation","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/evidence-finalization-atomicity.md"}],"dependencies":["dispatch-fail-closed-and-approval-semantics"],"required_evidence_levels":[1,2]}
```

## 任务身份

- 项目：programing-pipeline
- 领域或阶段：证据生命周期最终化修复 / continuation-2
- 任务类型：`repair`
- 用户结果或系统能力：证据最终化的清理阶段失败时保持 fail-closed，不留下表示成功的 marker，不删除或损坏 raw evidence，重复重试可安全识别并保持一致。
- 前置任务：`dispatch-fail-closed-and-approval-semantics`
- 执行 worktree 约定：`<仓库根目录>/.worktrees/evidence-finalization-atomicity`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态：未开始

## 依赖与范围

### 前置条件

- `dispatch-fail-closed-and-approval-semantics` 已完成，提供 continuation-2 所需的 fail-closed 派发与恢复语义。
- 现有 `finalize_evidence` 已实现最终化前的报告、审批和引用闭包校验；本任务只修复清理失败时的原子性。
- `implement-plan.md` 是需求权威文件；本任务不修改它。
- Python 3.11 标准库；不联网、不新增第三方依赖。

### 允许修改

- `pipeline_tools/planning.py`：证据最终化清理、marker 写入和失败恢复的原子性。
- `tests/**`：新增或调整本任务列出的精确清理失败、保留 raw 和幂等验收用例，以及必要回归 fixture。
- `references/**`：同步证据最终化失败恢复和原子性规则。
- 本任务单 `docs/tasks/evidence-finalization-atomicity.md` 的任务级进度区。

### 明确不改

- 不修改任何产品业务代码、外部消费项目、用户数据或 `implement-plan.md`/`IDEA.md`。
- 不修改其它任务单，不改写父任务历史，不扩大到其它 `pipeline_tools` 模块。
- 不修改、清理、重解释 `.pipeline/metrics/**` 或其它 metrics。
- 不删除或覆盖失败现场、既有证据、其它任务证据或 worktree；不自动提交、合并或清理。
- 不把 marker 存在、函数返回成功或测试数量当作产品语义验收；清理失败必须结构化返回 blocked/fail。

## 事实、假设与待决

### 已确认事实

- `finalize_evidence` 当前在写入 `finalization.json` 后执行 raw 清理；清理异常路径需要验证 marker 与 raw 的一致性。
- 现有测试已覆盖审批失败、报告/引用闭包失败时保留 raw 且不写 marker；本 continuation 补齐清理动作本身失败的边界。
- 任务单 schema 2 要求完整 `acceptance-test-*` ID、七段 `chain`、操作到验收测试绑定、依赖和证据等级。

### 未验证事实

- 当前基线下可注入的最小清理失败点、异常类型和文件系统行为由 executor 读取实现并以测试确认。
- 具体事务顺序和可逆临时路径以当前代码为准，不得因实现便利扩大允许范围。

### 禁止猜测

- 不得在 raw 尚未安全保留时写入 finalized marker。
- 不得把清理部分成功后的目录状态当作 finalized，也不得静默删除剩余 raw 文件。
- 不得通过吞掉异常、重试到成功或重写历史来掩盖清理失败；重试必须可识别且不破坏既有现场。

## 设计与行为契约

[触发] 主代理对已通过审批、报告和引用闭包校验的证据目录执行最终化
→ [处理] 以可回滚/可验证顺序执行清理准备与清理；只有确认清理成功后原子写入 finalized marker
→ [状态] 清理失败返回 blocked/fail，marker 不存在，所有 raw evidence 保留；重复调用不扩大损坏
→ [可见结果] 成功路径只保留允许的最终报告和 marker；失败重试保持可恢复且幂等

- marker 是成功最终化的证明，任何清理失败不得留下 marker。
- cleanup failure 必须保留 raw 文件字节和路径，不得留下部分删除造成不可恢复现场。
- 失败返回不可被 `evidence verify --phase finalized` 识别为 finalized。
- 同一失败 fixture 重试结果稳定；若外部故障解除后重试成功，必须从完整 raw 现场产生一致 finalized 结果。
- 既有审批、引用闭包、报告哈希和成功最终化行为保持不变。

## 七段链路

1. **entry**：`pipeline_tools/planning.py` 的 `finalize_evidence`。
2. **interaction**：调用方提供证据目录、task-id 和 approval 状态。
3. **application**：校验报告、结果和引用闭包，组织最终化事务。
4. **domain**：区分 blocked/fail 与 finalized，marker 仅代表完整成功。
5. **persistence**：证据目录中的保留报告、raw evidence 和 `finalization.json`。
6. **readback**：返回结构化 status/finalization，并由验证逻辑读取 marker。
7. **recovery**：清理失败保留 raw、移除/不写 marker，重复调用不覆盖现场。

## 外部操作绑定

- `evidence-finalization-prepare`：准备并校验最终化输入，对应 `acceptance-test-existing-finalization`。
- `evidence-finalization-cleanup`：执行可失败清理并证明 no-marker/raw-preserved，对应三个 cleanup 验收测试。
- `evidence-finalization-commit`：仅在清理完成后提交 marker，对应 `acceptance-test-cleanup-no-marker`、`acceptance-test-existing-finalization`。
- `evidence-finalization-retry`：重复故障调用并验证幂等恢复，对应 `acceptance-test-cleanup-idempotence`。

## 环境前置

1. 在仓库根目录确认 Python、Git 和 `pipeline-tools` 可执行；不得在契约冻结前派发实现。
2. 每条验收命令使用 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`，单条测试硬上限 180 秒；完整回归使用明确累计上限。
3. 测试使用临时目录和受控清理故障注入，不读取或修改当前仓库的 `.pipeline/metrics/**`。

## 验收测试

### 验收测试1：清理失败不留下 marker

- 触发：所有最终化前置校验通过，在 raw 清理动作中注入失败。
- 断言：结果为 `blocked` 或 `fail`；`finalization.json` 不存在；不得返回 `finalized`。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_cleanup_failure_leaves_no_marker`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_finalization_cleanup_failure_leaves_no_marker -v`
- 验收模式：本地文件系统集成测试；证据等级：2
- 结果要求：退出码 0；断言直接检查 marker 路径和结构化返回。

### 验收测试2：清理失败保留 raw evidence

- 触发：与验收测试1相同，在至少一个 raw 文件清理动作失败。
- 断言：所有 raw 文件仍存在且字节内容未改变；最终化未完成；不删除失败现场或写入替代成功证据。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_cleanup_failure_preserves_raw_evidence`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_finalization_cleanup_failure_preserves_raw_evidence -v`
- 验收模式：本地文件系统集成测试；证据等级：2
- 结果要求：退出码 0；断言保存失败前后 raw 文件哈希/字节一致。

### 验收测试3：清理失败重试幂等

- 触发：同一清理失败 fixture 连续调用最终化至少两次，再解除故障并重试。
- 断言：失败重试不写 marker、不重复删除、不覆盖 raw；解除故障后才产生唯一成功 marker，重复成功调用仍为 finalized 且不变更保留文件。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_cleanup_failure_retry_is_idempotent`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_finalization_cleanup_failure_retry_is_idempotent -v`
- 验收模式：本地文件系统集成测试；证据等级：2
- 结果要求：退出码 0；断言失败、恢复、重复成功三个状态及目录快照。

### 验收测试4：既有最终化前置失败行为不回归

- 触发：审批、报告、引用闭包失败以及正常最终化 fixture。
- 断言：前置失败仍保留 raw 且无 marker；正常路径仍只保留规定最终报告和 marker，重复成功调用安全。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_requires_main_approval_and_keeps_raw_on_failure`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning.PlanningTests.test_finalization_requires_main_approval_and_keeps_raw_on_failure -v`
- 验收模式：本地文件系统集成测试；证据等级：2
- 结果要求：退出码 0；既有断言和新原子性断言同时成立。

### 验收测试5：完整回归

- 触发：运行仓库现有完整测试套件。
- 断言：规划、dispatch、证据、契约、身份和 metrics 行为无回归；范围不漂移。
- 测试：`tests/: complete regression suite`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归；证据等级：1
- 结果要求：退出码 0；失败时保留现场并不得标记 PASS。

### 验收测试6：任务单结构与 schema 2 校验

- 触发：从仓库根目录验证本任务单。
- 断言：唯一 contract 为 schema 2、task_type 为 repair，依赖包含 `dispatch-fail-closed-and-approval-semantics`，允许/禁止范围与 cleanup 验收测试完整一致。
- 测试：`docs/tasks/evidence-finalization-atomicity.md: schema 2 repair contract validation`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/evidence-finalization-atomicity.md`
- 验收模式：契约/结构校验；证据等级：1
- 结果要求：退出码 0；无占位符、重复 ID 或缺失链路字段。

## 决策点

1. 若无法在不改产品/metrics/其它任务单的范围内注入清理失败，保留现场并报告 BLOCKED。
2. 若文件系统语义无法保证“任何部分删除”都可回滚，停下请求主代理裁决，不把弱化断言写成 PASS。
3. 是否清理历史 raw evidence、旧 marker 或其它任务目录不属于本任务，需另行授权和任务单。

---

## 任务级进度（主代理维护）

### 任务锚点

- 基线 HEAD：待提交契约前确认
- 契约提交：待完成（本轮不提交）
- 执行分支：待创建
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/evidence-finalization-atomicity`

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-cleanup-no-marker | 未开始 | - | - | - |
| acceptance-test-cleanup-preserves-raw | 未开始 | - | - | - |
| acceptance-test-cleanup-idempotence | 未开始 | - | - | - |
| acceptance-test-existing-finalization | 未开始 | - | - | - |
| acceptance-test-regression | 未开始 | - | - | - |
| acceptance-test-contract | 未开始 | - | - | - |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 1 | continuation-2 任务单创建 | 未开始 | - | 契约冻结后按 dispatch repair 依赖派发 |

### 设计变更与延续任务索引

- 父任务：`dispatch-fail-closed-and-approval-semantics`
- 本任务是 continuation-2；无新的设计变更。

### 最终结果

- 状态：未开始
- 执行子代理：未开始
- 独立审查子代理：未开始
- 主代理最终检查：未开始
- 合并提交：不执行
- 合并后复验：未开始
- 遗留项：-
