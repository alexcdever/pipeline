# planning-run-lifecycle：规划运行生命周期

<!-- Task ID: planning-run-lifecycle -->
<!-- Contract section is frozen after commit. Lifecycle records are maintained by the main agent. -->

## 任务目标

为规划运行建立可恢复、可审计的生命周期：生成唯一 run identity，记录阶段状态，区分成功、失败、冲突和中断，并保证失败现场保留、成功不泄漏中间产物。本任务是 prerequisite，不代表用户功能完成。

## 任务类型

`prerequisite`

## 需求引用

- `implement-plan.md`：规划失败现场、哈希稳定性、任务单生命周期和进度规则。
- `references/task-design.md`：契约冻结、失败保留和恢复规则。

## 允许修改

- `pipeline_tools/planning.py`
- `pipeline_tools/core.py`
- `pipeline_tools/__main__.py`
- `tests/test_planning_lifecycle.py`
- `tests/test_cli.py`
- `references/**`
- `docs/tasks/planning-run-lifecycle.md`

## 明确不改

- `implement-plan.md`、`IDEA.md`
- `docs/tasks/**` 中其他任务单
- `.pipeline/metrics/**` 与既有 `.pipeline/**` 历史证据
- 产品业务代码、外部项目、Git 历史
- 不创建 worktree、不派发子代理、不自动提交或合并

## 前置依赖

- `planning-driven-vertical-pipeline` 已合并。
- `planning-run-task-generation` 已合并，且其 planning-run-id 与失败产物约定保持兼容。
- Python、Git 和 CLI 可执行；测试使用临时 Git 项目。

## 事实、假设与待决

### 已确认事实

- 规划入口位于 `pipeline_tools/__main__.py`，规划校验与生成逻辑位于 `pipeline_tools/planning.py`。
- `.pipeline/planning/<planning-run-id>/` 是规划失败审计目录；成功路径不应把中间规划写成冻结交付物。

### 未验证事实

- 生命周期状态枚举、CLI 参数名称和现有生成器的具体调用签名需由 executor 从当前代码确认。

### 禁止猜测

- 不把自然语言报告推断为 PASS；不把失败、中断或冲突改写为成功；状态迁移和清理策略若与既有 CLI 冲突必须停下报告。

## 设计与行为契约

[触发] planning CLI 启动、阶段完成、失败、中断或重复恢复
→ [处理] 校验 run identity、阶段迁移和 implement-plan 哈希
→ [状态] 记录结构化 lifecycle/result 与必要失败现场
→ [可见结果] CLI JSON 返回状态、run-id、artifacts、errors、next_actions，成功与失败清理边界明确

- run-id、requirements hash、HEAD、branch 和 root 绑定，不允许跨项目复用。
- 重复读取幂等；失败现场不覆盖、不删除；成功不得引用已删除中间产物。
- 命令超时、输入冲突、哈希漂移、写入失败均为 BLOCKED/FAIL，不得 PASS。

## 七段链路

entry：`pipeline_tools/__main__.py`；interaction：planning CLI JSON 参数；application：`pipeline_tools/planning.py` 生命周期协调；domain：run 状态、哈希、阶段迁移；persistence：`.pipeline/planning/<planning-run-id>/`；readback：CLI JSON 和状态读取；recovery：失败现场保留、重复恢复和幂等终止。

## 外部操作绑定

- `planning-run-start`：创建并绑定 planning run。
- `planning-run-transition`：校验并追加阶段状态。
- `planning-run-finalize`：按成功/失败边界固化结果。
- `planning-run-recover`：从保留现场安全恢复或拒绝漂移。

## 环境前置

1. 在仓库根目录执行 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools planning preflight .`。
2. 测试通过临时仓库、临时 `implement-plan.md` 和隔离 `.pipeline` 运行。

## 验收测试

### 验收测试1：生命周期状态与身份绑定

- 触发：启动、推进和读取同一 planning run。
- 断言：状态迁移有序、run-id/root/HEAD/hash 一致，重复读取不改变结果。
- 测试：`tests/test_planning_lifecycle.py: PlanningLifecycleTests.test_run_identity_and_state_transitions_are_bound_and_idempotent`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_lifecycle.PlanningLifecycleTests.test_run_identity_and_state_transitions_are_bound_and_idempotent -v`
- 验收模式：集成 / CLI；证据等级：2；结果要求：退出码 0，JSON 状态可回读。


- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试2：失败、中断与冲突保留现场

- 触发：注入哈希漂移、重复 run、写入失败和中断。
- 断言：返回 BLOCKED/FAIL，保留结构化现场，不生成成功标记，不删除已有文件。
- 测试：`tests/test_planning_lifecycle.py: PlanningLifecycleTests.test_failure_interruption_and_conflict_preserve_auditable_artifacts`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_lifecycle.PlanningLifecycleTests.test_failure_interruption_and_conflict_preserve_auditable_artifacts -v`
- 验收模式：集成 / 安全边界；证据等级：2；结果要求：退出码非零且错误分类稳定。


- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试3：成功终止不泄漏规划中间产物

- 触发：完成一次有效规划运行并终止。
- 断言：成功结果含 run-id、hash、artifacts 和 next_actions；不把临时输入伪装为成功证据，重复终止幂等。
- 测试：`tests/test_cli.py: CLITests.test_planning_run_lifecycle_success_and_idempotent_finalize`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli.CLITests.test_planning_run_lifecycle_success_and_idempotent_finalize -v`
- 验收模式：CLI 集成；证据等级：2；结果要求：退出码 0，输出可解析且无越界写入。


- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试4：回归与契约范围

- 触发：运行完整测试和本任务校验。
- 断言：既有行为无回归、契约通过、差异仅在允许路径。
- 测试：`tests/: complete regression suite`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归；证据等级：1；结果要求：退出码 0，另行运行 task validate 与 `git diff --check` 均为 0。

## 决策点

1. 需要改变既有 planning-run-task-generation 输出协议时停止并建立 continuation。
2. 需要删除历史 `.pipeline` 证据、自动创建 worktree 或改变 metrics 时停止。
3. 无法区分恢复现场身份时保留现场并报告 BLOCKED。

---

## 任务级进度（主代理维护）

### 任务锚点

- 基线 HEAD：待提交契约前确认
- 契约提交：待完成
- 执行分支：`planning-run-lifecycle`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/planning-run-lifecycle`

### 验收台账

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

- 状态：未开始
- 执行子代理：未开始
- 独立审查子代理：未开始
- 主代理最终检查：未开始
- 合并提交：-
- 合并后复验：未开始
- 遗留项：-

```pipeline-contract
{
  "schema": 2,
  "task_id": "planning-run-lifecycle",
  "task_type": "prerequisite",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": ["pipeline_tools/planning.py", "pipeline_tools/core.py", "pipeline_tools/__main__.py", "tests/test_planning_lifecycle.py", "tests/test_cli.py", "references/**", "docs/tasks/planning-run-lifecycle.md"],
  "forbidden_paths": ["implement-plan.md", "IDEA.md", "docs/tasks/** existing tasks", ".pipeline/** existing history", ".pipeline/metrics/**", "**/*secret*", "**/*token*"],
  "operations": [
    {"id": "planning-run-start", "kind": "create", "scope": "planning-run", "acceptance_tests": ["acceptance-test-1"]},
    {"id": "planning-run-transition", "kind": "validate", "scope": "planning-run", "acceptance_tests": ["acceptance-test-1", "acceptance-test-2"]},
    {"id": "planning-run-finalize", "kind": "finalize", "scope": "planning-run", "acceptance_tests": ["acceptance-test-2", "acceptance-test-3"]},
    {"id": "planning-run-recover", "kind": "recover", "scope": "planning-run", "acceptance_tests": ["acceptance-test-2"]}
  ],
  "chain": {"entry": ["pipeline_tools/__main__.py"], "interaction": ["pipeline_tools/__main__.py"], "application": ["pipeline_tools/planning.py"], "domain": ["pipeline_tools/planning.py", "pipeline_tools/contract.py"], "persistence": [".pipeline/planning/historical-planning-run/"], "readback": ["pipeline_tools/__main__.py"], "recovery": ["pipeline_tools/planning.py"]},
  "acceptance_tests": [
    {"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_planning_lifecycle.py: PlanningLifecycleTests.test_run_identity_and_state_transitions_are_bound_and_idempotent", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_lifecycle.PlanningLifecycleTests.test_run_identity_and_state_transitions_are_bound_and_idempotent -v"},
    {"id": "acceptance-test-2", "evidence_level": 2, "test_ref": "tests/test_planning_lifecycle.py: PlanningLifecycleTests.test_failure_interruption_and_conflict_preserve_auditable_artifacts", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_lifecycle.PlanningLifecycleTests.test_failure_interruption_and_conflict_preserve_auditable_artifacts -v"},
    {"id": "acceptance-test-3", "evidence_level": 2, "test_ref": "tests/test_cli.py: CLITests.test_planning_run_lifecycle_success_and_idempotent_finalize", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli.CLITests.test_planning_run_lifecycle_success_and_idempotent_finalize -v"},
    {"id": "acceptance-test-4", "evidence_level": 1, "test_ref": "tests/: complete regression suite", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"}
  ],
  "dependencies": ["planning-driven-vertical-pipeline", "planning-run-task-generation"],
  "required_evidence_levels": [1, 2]
}
```

## 生命周期记录

契约提交后，过程记录写入 `.pipeline/planning-run-lifecycle/`，不修改冻结契约区。

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
