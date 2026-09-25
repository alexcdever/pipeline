# derived-task-dispatch-recovery：派生任务派发与恢复

<!-- Task ID: derived-task-dispatch-recovery -->

## 任务目标

支持从父任务明确提交派生独立任务单，并在执行失败、证据缺失、身份漂移或设计变化时安全恢复；父任务现场不可覆盖，派生任务必须重新校验契约和身份。本任务是 derived prerequisite，不代表用户功能完成。

## 任务类型

`derived`

## 需求引用

- `implement-plan.md`：派生任务从父任务明确提交创建、失败现场保留和延续任务规则。
- `references/merge-and-recovery.md`、`references/task-design.md`：恢复和 continuation 规则。

## 允许修改

- `pipeline_tools/core.py`
- `pipeline_tools/planning.py`
- `pipeline_tools/__main__.py`
- `tests/test_derived_task_dispatch_recovery.py`
- `tests/test_evidence.py`
- `references/**`
- `docs/tasks/derived-task-dispatch-recovery.md`

## 明确不改

- `implement-plan.md`、`IDEA.md`
- 父任务单、既有任务单、既有 `.pipeline/**` 历史和 metrics
- Git 历史、外部项目、产品业务代码
- 不删除失败 worktree/证据，不自动合并或重写父任务历史

## 前置依赖

- `task-plan-contract-consistency` 已合并。
- `task-worktree-dispatch-identity` 已合并。
- `planning-run-lifecycle` 已合并。

## 设计与行为契约

[触发] 父任务提交失败/阻塞或设计裁决要求派生任务
→ [处理] 核对父 task-id、commit、branch、证据和新任务契约，再创建唯一派生 dispatch
→ [状态] 父现场只读保留，派生任务拥有独立 task-id/path/evidence
→ [可见结果] 成功恢复可继续；身份、证据或依赖不足则 BLOCKED 并保留现场

- derived task 必须引用父任务明确 commit，不得以工作树当前文件或代理摘要替代。
- 失败恢复不得把父任务 FAIL 改为 PASS；新设计必须新 task-id 且含 `continuation` 语义。
- 恢复重试幂等，不能覆盖既有派发或证据。

## 七段链路

entry：`pipeline_tools/__main__.py`；interaction：父任务提交/结果 JSON；application：`pipeline_tools/core.py`/`planning.py`；domain：父子关系、提交、恢复分类和状态；persistence：`.worktrees/<task-id>`、`.pipeline/<task-id>/`、新任务单；readback：result verify 与恢复 JSON；recovery：保留父现场、创建 continuation/derived 并重新核身份。

## 外部操作绑定

- `derived-task-plan`：从父提交生成派生任务输入。
- `derived-dispatch-verify`：核对父子身份、依赖和路径。
- `derived-recovery-resume`：在可恢复边界继续执行。
- `derived-recovery-preserve`：保留不可恢复现场并分类上报。

## 环境前置

1. 运行 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task preflight` 和 dispatch identity 检查。
2. 测试用临时 Git 仓库制造父提交、失败证据和子任务。

## 验收测试

### 验收测试1：从明确父提交生成独立派生任务

- 触发：提供父 task-id、父 branch、明确 commit 和冻结输入。
- 断言：生成独立 task-id/任务单/证据目录，父任务内容和现场不变。
- 测试：`tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_derived_task_binds_explicit_parent_commit_and_is_independent`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_derived_task_binds_explicit_parent_commit_and_is_independent -v`
- 验收模式：Git/集成；证据等级：3；结果要求：退出码 0，父子引用闭包完整。

### 验收测试2：失败与证据缺失安全恢复

- 触发：executor FAIL、review BLOCKED、报告缺失、commit 漂移或 worktree 不匹配。
- 断言：恢复分类为 BLOCKED/FAIL，保留父现场，不派发错误子任务，不覆盖报告。
- 测试：`tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume -v`
- 验收模式：恢复 / 安全边界；证据等级：3；结果要求：非零且父文件哈希不变。

### 验收测试3：continuation 幂等与父历史不可改写

- 触发：同一设计变更重复请求 continuation。
- 断言：产生唯一新 task-id/path，父任务最终结果不变，重复调用不覆盖。
- 测试：`tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history -v`
- 验收模式：集成；证据等级：2；结果要求：退出码 0，重复请求可识别。

### 验收测试4：回归

- 触发：完整测试和 evidence/dispatch 校验。
- 断言：原有证据生命周期无回归。
- 测试：`tests/: complete regression suite`；命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归；证据等级：1；结果要求：退出码 0。

## 决策点

1. 父任务提交不明确、分支已重写或证据无法关联时停下。
2. 是否允许重试产品实现而非创建 continuation 由主代理裁决。
3. 清理失败 worktree 或历史证据需要用户明确授权。

---

## 任务级进度（主代理维护）

- 基线 HEAD：待提交契约前确认；契约提交：待完成
- 执行分支：`derived-task-dispatch-recovery`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/derived-task-dispatch-recovery`

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
{"schema":2,"task_id":"derived-task-dispatch-recovery","task_type":"derived","implement_plan":{"path":"implement-plan.md"},"allowed_paths":["pipeline_tools/core.py","pipeline_tools/planning.py","pipeline_tools/__main__.py","tests/test_derived_task_dispatch_recovery.py","tests/test_evidence.py","references/**","docs/tasks/derived-task-dispatch-recovery.md"],"forbidden_paths":["implement-plan.md","IDEA.md","docs/tasks/** existing tasks",".pipeline/** existing history",".pipeline/metrics/**","**/*secret*","**/*token*"],"operations":[{"id":"derived-task-plan","kind":"generate","scope":"derived-task","acceptance_tests":["acceptance-test-1","acceptance-test-3"]},{"id":"derived-dispatch-verify","kind":"validate","scope":"dispatch","acceptance_tests":["acceptance-test-1","acceptance-test-2"]},{"id":"derived-recovery-resume","kind":"recover","scope":"task","acceptance_tests":["acceptance-test-2","acceptance-test-3"]},{"id":"derived-recovery-preserve","kind":"record","scope":"evidence","acceptance_tests":["acceptance-test-2"]}],"chain":{"entry":["pipeline_tools/__main__.py"],"interaction":["pipeline_tools/__main__.py"],"application":["pipeline_tools/core.py","pipeline_tools/planning.py"],"domain":["pipeline_tools/core.py"],"persistence":["docs/tasks/<task-id>.md",".pipeline/<task-id>/",".worktrees/<task-id>/"],"readback":["pipeline_tools/__main__.py"],"recovery":["pipeline_tools/core.py","pipeline_tools/planning.py"]},"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":3,"test_ref":"tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_derived_task_binds_explicit_parent_commit_and_is_independent","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_derived_task_binds_explicit_parent_commit_and_is_independent -v"},{"id":"acceptance-test-2","evidence_level":3,"test_ref":"tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume -v"},{"id":"acceptance-test-3","evidence_level":2,"test_ref":"tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history -v"},{"id":"acceptance-test-4","evidence_level":1,"test_ref":"tests/: complete regression suite","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"}],"dependencies":["task-plan-contract-consistency","task-worktree-dispatch-identity","planning-run-lifecycle"],"required_evidence_levels":[1,2,3]}
```

## 生命周期记录

过程事件写入 `.pipeline/derived-task-dispatch-recovery/`，不改冻结契约。
