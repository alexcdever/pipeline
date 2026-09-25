# task-plan-contract-consistency：任务计划与任务单契约一致性

<!-- Task ID: task-plan-contract-consistency -->

## 任务目标

建立 task-plan 到 schema 2 task sheet 的双向一致性校验，确保 task type、依赖、操作、七段链路、验收绑定、路径和 implement-plan hash 不漂移；冲突时 fail closed。本任务是 prerequisite，不代表用户功能完成。

## 任务类型

`prerequisite`

## 需求引用

- `implement-plan.md`：结构化任务计划、操作覆盖、依赖和哈希稳定性。
- `docs/tasks/planning-run-task-generation.md`：生成器输入输出和不覆盖规则。

## 允许修改

- `pipeline_tools/contract.py`
- `pipeline_tools/planning.py`
- `pipeline_tools/__main__.py`
- `tests/test_task_plan_contract_consistency.py`
- `tests/test_contract.py`
- `references/**`
- `docs/tasks/task-plan-contract-consistency.md`

## 明确不改

- `implement-plan.md`、`IDEA.md`
- 既有任务单、`.pipeline/**` 历史证据和 metrics
- 产品业务代码、Git 历史、外部项目
- 不生成或覆盖任务单，不创建 worktree

## 前置依赖

- `planning-run-task-generation` 已合并。
- schema 2 contract validator 和 task-plan validator 可执行。
- `planning-run-lifecycle` 不要求本任务反向依赖；若其 API 需要改变，停下报告。

## 设计与行为契约

[触发] 读取结构化 task-plan 与目标任务单
→ [处理] 规范化并逐字段比较类型、依赖、操作、链路、验收和哈希
→ [状态] 产生一致/冲突结果，不改输入
→ [可见结果] CLI JSON 列出每个冲突的字段、来源和下一步，冲突不得冻结或派发

- 比较必须是显式字段比较，禁止从文件名猜测语义。
- 缺失、重复、顺序不合法、未知 acceptance ID、路径越界和 hash 漂移均拒绝。
- 现有任务单字节内容不变；只读校验不得写 `.pipeline` 以外路径。

## 七段链路

entry：`pipeline_tools/__main__.py`；interaction：task-plan/任务单 JSON；application：`pipeline_tools/planning.py`；domain：`pipeline_tools/contract.py` 的 schema 2 字段；persistence：计划输入与 `docs/tasks/<task-id>.md`；readback：一致性 JSON 结果与 validator；recovery：保留冲突报告并阻止后续 dispatch。

## 外部操作绑定

- `task-plan-contract-compare`：比较计划和任务单。
- `task-plan-contract-hash-check`：绑定 implement-plan 与 requirements hash。
- `task-plan-contract-freeze-check`：在派发前拒绝漂移和覆盖。

## 环境前置

1. `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools planning preflight .` 必须通过。
2. 测试使用临时目录和临时任务单，禁止修改真实既有任务单。

## 验收测试

### 验收测试1：有效计划与契约一致

- 触发：提交包含完整字段的 task-plan 和对应 schema 2 task sheet。
- 断言：所有字段一致，输出 pass，任务单 validator 通过。
- 测试：`tests/test_task_plan_contract_consistency.py: TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass -v`
- 验收模式：契约 / 集成；证据等级：2；结果要求：退出码 0。

### 验收测试2：字段漂移逐项拒绝

- 触发：分别改变 task type、operations、chain、acceptance binding、dependencies 或 hash。
- 断言：每次返回明确冲突字段和非零结果，不产生可冻结状态。
- 测试：`tests/test_task_plan_contract_consistency.py: TaskPlanContractConsistencyTests.test_field_drift_is_reported_and_fail_closed`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_field_drift_is_reported_and_fail_closed -v`
- 验收模式：契约 / 安全边界；证据等级：2；结果要求：每个变体均非零且输入未改。

### 验收测试3：重复、缺失和越界安全

- 触发：重复 task ID、未知 acceptance ID、循环依赖、越界路径和既有任务单覆盖尝试。
- 断言：全部拒绝，既有文件哈希不变，不在项目外写入。
- 测试：`tests/test_task_plan_contract_consistency.py: TaskPlanContractConsistencyTests.test_duplicate_missing_and_unsafe_plan_inputs_are_rejected`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_duplicate_missing_and_unsafe_plan_inputs_are_rejected -v`
- 验收模式：安全边界；证据等级：2；结果要求：结构化错误可定位。

### 验收测试4：回归

- 触发：全量测试和契约测试。
- 断言：已有 validator 无回归，范围和 whitespace 检查通过。
- 测试：`tests/test_contract.py: complete contract regression`；命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归；证据等级：1；结果要求：退出码 0。

## 决策点

1. 需要修改 schema 2 字段语义或兼容 schema 1 时停下。
2. 计划和现有任务单无法唯一对应时保留冲突，不自动选一方。
3. 需要覆盖文件或写入 metrics 时停下。

---

## 任务级进度（主代理维护）

- 基线 HEAD：待提交契约前确认
- 契约提交：待完成
- 执行分支：`task-plan-contract-consistency`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/task-plan-contract-consistency`

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-1 | 未开始 | - | - | - |
| acceptance-test-2 | 未开始 | - | - | - |
| acceptance-test-3 | 未开始 | - | - | - |
| acceptance-test-4 | 未开始 | - | - | - |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 1 | 任务单创建 | 未开始 | - | 契约提交后派发 executor |

### 设计变更与延续任务索引

- 无。

### 最终结果

- 状态：未开始；执行子代理：未开始；独立审查子代理：未开始；主代理最终检查：未开始；合并提交：-；合并后复验：未开始；遗留项：-

```pipeline-contract
{"schema":2,"task_id":"task-plan-contract-consistency","task_type":"prerequisite","implement_plan":{"path":"implement-plan.md"},"allowed_paths":["pipeline_tools/contract.py","pipeline_tools/planning.py","pipeline_tools/__main__.py","tests/test_task_plan_contract_consistency.py","tests/test_contract.py","references/**","docs/tasks/task-plan-contract-consistency.md"],"forbidden_paths":["implement-plan.md","IDEA.md","docs/tasks/** existing tasks",".pipeline/** existing history",".pipeline/metrics/**","**/*secret*","**/*token*"],"operations":[{"id":"task-plan-contract-compare","kind":"validate","scope":"task-plan","acceptance_tests":["acceptance-test-1","acceptance-test-2"]},{"id":"task-plan-contract-hash-check","kind":"validate","scope":"requirements","acceptance_tests":["acceptance-test-2"]},{"id":"task-plan-contract-freeze-check","kind":"gate","scope":"task-sheet","acceptance_tests":["acceptance-test-2","acceptance-test-3"]}],"chain":{"entry":["pipeline_tools/__main__.py"],"interaction":["pipeline_tools/__main__.py"],"application":["pipeline_tools/planning.py"],"domain":["pipeline_tools/contract.py"],"persistence":["docs/tasks/<task-id>.md","implement-plan.md"],"readback":["pipeline_tools/contract.py"],"recovery":["pipeline_tools/planning.py"]},"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":2,"test_ref":"tests/test_task_plan_contract_consistency.py: TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_matching_plan_and_schema2_sheet_pass -v"},{"id":"acceptance-test-2","evidence_level":2,"test_ref":"tests/test_task_plan_contract_consistency.py: TaskPlanContractConsistencyTests.test_field_drift_is_reported_and_fail_closed","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_field_drift_is_reported_and_fail_closed -v"},{"id":"acceptance-test-3","evidence_level":2,"test_ref":"tests/test_task_plan_contract_consistency.py: TaskPlanContractConsistencyTests.test_duplicate_missing_and_unsafe_plan_inputs_are_rejected","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_plan_contract_consistency.TaskPlanContractConsistencyTests.test_duplicate_missing_and_unsafe_plan_inputs_are_rejected -v"},{"id":"acceptance-test-4","evidence_level":1,"test_ref":"tests/: complete regression suite","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"}],"dependencies":["planning-run-task-generation"],"required_evidence_levels":[1,2]}
```

## 生命周期记录

过程事件写入 `.pipeline/task-plan-contract-consistency/`，不改冻结契约。
