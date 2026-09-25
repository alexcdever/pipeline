# planning-facts-conflict-model：规划事实与冲突模型

<!-- Task ID: planning-facts-conflict-model -->

## 任务目标

为需求事实、项目事实、假设、未知和冲突建立可机械读取的结构模型，允许语义代理给出裁决建议但禁止工具替代产品判断；冲突必须阻止任务生成和派发。本任务是 prerequisite，不代表用户功能完成。

## 任务类型

`prerequisite`

## 需求引用

- `implement-plan.md`：事实来源、冲突暂停和脚本/语义职责边界。
- `references/task-design.md`：事实、假设与未知规则。

## 允许修改

- `pipeline_tools/planning.py`
- `pipeline_tools/contract.py`
- `pipeline_tools/__main__.py`
- `tests/test_planning_facts_conflicts.py`
- `tests/test_planning.py`
- `references/**`
- `docs/tasks/planning-facts-conflict-model.md`

## 明确不改

- `implement-plan.md`、`IDEA.md`
- 其他任务单、`.pipeline/**` 历史和 metrics
- 产品业务代码、外部项目、Git 历史
- 不自动裁决冲突、不生成 worktree

## 前置依赖

- `planning-driven-vertical-pipeline` 已合并。
- `planning-run-task-generation` 已合并，且 invalid facts 能阻止生成。

## 设计与行为契约

[触发] 接收需求/项目事实集合与规划输入
→ [处理] 校验来源、身份、路径、覆盖和冲突关系，分类事实/假设/未知
→ [状态] 生成结构化 facts result 与可审计 conflict records
→ [可见结果] 无冲突才允许继续；有冲突返回待裁决项和 next_actions，绝不伪造 PASS

- 同一实体的互斥值必须产生冲突；缺来源、过期 hash、越界路径、重复 ID 和无法验证的假设不得隐式通过。
- 语义裁决由主代理/开发者完成；工具只报告机械事实。
- 失败结果可重复、可脱敏、可关联 planning-run-id。

## 七段链路

entry：`pipeline_tools/__main__.py`；interaction：facts JSON；application：`pipeline_tools/planning.py`；domain：事实类别、来源、冲突和裁决状态；persistence：`.pipeline/planning/<planning-run-id>/`；readback：CLI facts/conflict JSON；recovery：保留冲突现场、等待裁决后重新校验。

## 外部操作绑定

- `facts-normalize`：规范事实记录。
- `facts-validate`：验证机械结构、来源和路径。
- `facts-conflict-detect`：生成冲突和待裁决记录。
- `facts-gate-planning`：有冲突时阻止后续规划。

## 环境前置

1. `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools planning preflight .` 通过。
2. 测试在临时项目中构造事实文件，不读取用户数据。

## 验收测试

### 验收测试1：事实分类与来源校验

- 触发：提交有效需求事实、项目事实、假设和未知。
- 断言：类别、来源、实体 ID 和路径保留，结构化结果可读。
- 测试：`tests/test_planning_facts_conflicts.py: PlanningFactsConflictTests.test_facts_are_classified_with_sources_and_safe_identity`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_facts_are_classified_with_sources_and_safe_identity -v`
- 验收模式：契约 / 集成；证据等级：2；结果要求：退出码 0。

### 验收测试2：冲突检测与暂停

- 触发：提供互斥事实、不同来源值、哈希漂移或未知裁决。
- 断言：输出 conflict records 和 decision required，规划/生成/dispatch 不继续。
- 测试：`tests/test_planning_facts_conflicts.py: PlanningFactsConflictTests.test_conflicts_block_planning_and_preserve_decision_records`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_conflicts_block_planning_and_preserve_decision_records -v`
- 验收模式：集成 / 安全边界；证据等级：2；结果要求：非零或 BLOCKED，现场存在且未覆盖。

### 验收测试3：恶意结构和语义越权拒绝

- 触发：缺来源、重复 ID、越界路径、占位符和“自动裁决”输入。
- 断言：机械校验拒绝；工具不选择产品值、不写项目外文件。
- 测试：`tests/test_planning_facts_conflicts.py: PlanningFactsConflictTests.test_invalid_facts_and_unauthorized_resolution_are_rejected`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_invalid_facts_and_unauthorized_resolution_are_rejected -v`
- 验收模式：安全边界；证据等级：2；结果要求：所有变体非零，输入字节不变。

### 验收测试4：回归

- 触发：facts/planning 全量测试和完整回归。
- 断言：现有事实校验无回归，契约和范围通过。
- 测试：`tests/test_planning.py: existing planning validation tests`；命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归；证据等级：1；结果要求：退出码 0。

## 决策点

1. 冲突是否可自动合并、优先级如何定义必须由用户/开发者裁决。
2. 需求事实 schema 兼容变化时停下，不自行迁移输入。
3. 需要修改 IDEA 或 implement-plan 时停下。

---

## 任务级进度（主代理维护）

- 基线 HEAD：待提交契约前确认；契约提交：待完成
- 执行分支：`planning-facts-conflict-model`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/planning-facts-conflict-model`

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
{"schema":2,"task_id":"planning-facts-conflict-model","task_type":"prerequisite","implement_plan":{"path":"implement-plan.md"},"allowed_paths":["pipeline_tools/planning.py","pipeline_tools/contract.py","pipeline_tools/__main__.py","tests/test_planning_facts_conflicts.py","tests/test_planning.py","references/**","docs/tasks/planning-facts-conflict-model.md"],"forbidden_paths":["implement-plan.md","IDEA.md","docs/tasks/** existing tasks",".pipeline/** existing history",".pipeline/metrics/**","**/*secret*","**/*token*"],"operations":[{"id":"facts-normalize","kind":"normalize","scope":"facts","acceptance_tests":["acceptance-test-1"]},{"id":"facts-validate","kind":"validate","scope":"facts","acceptance_tests":["acceptance-test-1","acceptance-test-3"]},{"id":"facts-conflict-detect","kind":"detect","scope":"facts","acceptance_tests":["acceptance-test-2"]},{"id":"facts-gate-planning","kind":"gate","scope":"planning","acceptance_tests":["acceptance-test-2","acceptance-test-3"]}],"chain":{"entry":["pipeline_tools/__main__.py"],"interaction":["pipeline_tools/__main__.py"],"application":["pipeline_tools/planning.py"],"domain":["pipeline_tools/planning.py","pipeline_tools/contract.py"],"persistence":[".pipeline/planning/<planning-run-id>/"],"readback":["pipeline_tools/__main__.py"],"recovery":["pipeline_tools/planning.py"]},"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":2,"test_ref":"tests/test_planning_facts_conflicts.py: PlanningFactsConflictTests.test_facts_are_classified_with_sources_and_safe_identity","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_facts_are_classified_with_sources_and_safe_identity -v"},{"id":"acceptance-test-2","evidence_level":2,"test_ref":"tests/test_planning_facts_conflicts.py: PlanningFactsConflictTests.test_conflicts_block_planning_and_preserve_decision_records","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_conflicts_block_planning_and_preserve_decision_records -v"},{"id":"acceptance-test-3","evidence_level":2,"test_ref":"tests/test_planning_facts_conflicts.py: PlanningFactsConflictTests.test_invalid_facts_and_unauthorized_resolution_are_rejected","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_facts_conflicts.PlanningFactsConflictTests.test_invalid_facts_and_unauthorized_resolution_are_rejected -v"},{"id":"acceptance-test-4","evidence_level":1,"test_ref":"tests/: complete regression suite","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"}],"dependencies":["planning-driven-vertical-pipeline","planning-run-task-generation"],"required_evidence_levels":[1,2]}
```

## 生命周期记录

过程事件写入 `.pipeline/planning-facts-conflict-model/`，不改冻结契约。
