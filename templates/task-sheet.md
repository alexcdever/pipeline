# 通用任务单

<!-- Task ID: <task-id> -->
<!-- Contract section is frozen after commit. The task sheet holds only the frozen contract and the human-readable design sections; task anchors, the acceptance ledger, the execution log and the final result live in .pipeline/<task-id>/ progress logs and stage reports. -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "<task-id>",
  "task_type": "repair",
  "project_type": "service",
  "risk": "medium",
  "goal": {"path": "goal.md"},
  "allowed_paths": ["<repo-relative-or-explicit-sibling-path-pattern>"],
  "forbidden_paths": ["<path-pattern>"],
  "non_goals": ["<explicit non-goal that this task must not pursue>"],
  "operations": [
    {
      "id": "<operation-id>",
      "kind": "<operation-kind>",
      "scope": "<operation-scope>",
      "resources": ["<repo-relative-resource-path>"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-1"]
    }
  ],
  "chain": {
    "entry": ["<path-or-reference>"],
    "interaction": ["<path-or-reference>"],
    "application": ["<path-or-reference>"],
    "domain": ["<path-or-reference>"],
    "persistence": ["<path-or-reference>"],
    "readback": ["<path-or-reference>"],
    "recovery": ["<path-or-reference>"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 1,
      "test_ref": "<file>: <exact test name>",
      "command_ref": "<complete command>"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [1],
  "assumptions": [],
  "unknowns": []
}
```

`pipeline-contract` is the machine-checkable projection of this task sheet. New task sheets use schema 4 with the `goal` field and complete `acceptance-test-*` IDs; schema 1-3 are retained only for deprecated historical reads (they keep the legacy `implement_plan` field). Keep it synchronized with the human-readable contract; after the contract commit it is frozen.

Schema 4 rules worth restating here:

- `non_goals` must be a non-empty array of non-empty strings.
- `risk` must be `low`, `medium` or `high`; `project_type` defaults to `service`.
- Each `acceptance_tests[].evidence_level` must meet the evidence floor derived from `risk`, `project_type` and `task_type`: `low`=1, `medium`=2, `high`=3; `web`/`desktop` at medium or high risk need at least 3, `multi-process` at medium or high risk needs at least 4, and `vertical-feature` needs at least 2.
- Every `chain` segment must be a non-empty array of references, or `{"not_applicable": true, "reason": "<non-empty>"}`. The bare string `"not-applicable"` is rejected.
- Every `operations[]` entry declares non-empty `resources` plus `resource_mode`: `single` for exactly one resource, `batch` for two or more.
- A `prerequisite` task must also declare a non-empty `non_user_completion_reason` describing why it is not user-facing completion. The value is taken from the task plan's `non_user_completion_reason`; generation fails closed when it is missing.
- `assumptions` and `unknowns` carry the project facts forward into the frozen contract; both default to empty arrays.
- A `derived` task must declare `derived_from.parent_task_type` (the parent contract's `task_type`). When the parent is `vertical-feature` or `repair`, the child must still carry a full `chain`; when the parent is `vertical-feature`, the evidence floor is at least 2.

## 任务身份

- 项目：<project name>
- 领域或阶段：<area / phase>
- 任务类型：`<vertical-feature / prerequisite / repair / derived>`
- 用户结果或系统能力：<one verifiable outcome>
- 执行 worktree 约定：`<仓库根目录>/.worktrees/<task-id>`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态：未开始

## 依赖与范围

### 前置条件

- <已合并任务、架构决策、文档、工具或环境>

### 允许修改

- <生产代码、测试、文档和任务级证据>

### 明确不改

- <禁止修改的文件、接口、行为、迁移或清理>

### 非目标

- <本任务明确不追求的目标；必须与契约中的 `non_goals` 一致>

## 事实、假设与待决

### 已确认事实

- <文件/符号/命令输出/架构决策及其来源>

### 未验证事实

- <尚未读取、运行或确认的内容；不得写成已实现或已通过>

### 禁止猜测

- <会改变产品行为、协议、数据格式、权限或验收边界的待决事项>

## 设计与行为契约

[触发] <用户动作或系统事件>
→ [处理] <前端、核心服务、领域或协议>
→ [状态] <领域事实、文档或持久化变化>
→ [可见结果] <界面、接口、文件、通知或重启后的结果>

- <必须保持的不变量>
- <失败、重试、幂等、隔离和恢复规则>

## 环境前置

1. `<命令或设置步骤>`
2. `<依赖、服务、设备或测试数据要求>`

## 验收测试

### 验收测试1：<名称>

- 触发：<真实用户动作或系统事件>
- 断言：<可观察结果、状态/持久化结果和恢复结果>
- 测试：`<文件路径>: <精确用例名>`
- 命令：`<从正确工作目录执行的完整命令>`
- 验收模式：<单元 / 组件 / 协议 / 集成 / 真实浏览器 / 真实设备 / 其他>
- 证据等级：<1 / 2 / 3 / 4 / 5>
- 结果要求：<退出码、输出、隔离、产物和超时>

### 验收测试2：<名称>

- 触发：<真实用户动作或系统事件>
- 断言：<可观察结果>
- 测试：`<文件路径>: <精确用例名>`
- 命令：`<完整命令>`
- 验收模式：<单元 / 组件 / 协议 / 集成 / 真实浏览器 / 真实设备 / 其他>
- 证据等级：<1 / 2 / 3 / 4 / 5>
- 结果要求：<当前命令的明确通过边界>

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. <产品或架构设计冲突>
2. <缺失环境、权限或外部依赖>
3. <验收要求超出当前范围>

> `prerequisite` 任务必须在任务计划中声明 `non_user_completion_reason`（生成器把它原样写入契约，不再填默认英文），说明该任务为何不是用户功能完成，并保留后续消费该底座的用户行为任务。缺失时任务单生成失败。

---

## 过程记录位置

任务锚点、验收台账、执行记录、设计裁决与最终结果不再写入任务单。它们由主代理维护在 `.pipeline/<task-id>/` 下的角色进度日志和阶段报告中；成功最终化后只保留阶段报告、机器结果和最终化标记。