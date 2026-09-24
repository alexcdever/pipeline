# planning-driven-vertical-pipeline：需求驱动的垂直任务规划与证据生命周期

<!-- Task ID: planning-driven-vertical-pipeline -->
<!-- Contract section is frozen after commit. Lifecycle records are not part of the frozen contract. -->

## 任务目标

根据项目根目录已冻结的 `implement-plan.md`，建立规划前置检查、需求事实与项目事实结构校验、垂直任务计划校验、操作覆盖和完整数据链路校验、角色进度日志以及新的阶段报告和最终化契约，使大语言模型负责语义规划、脚本负责机械闸门。

## 任务类型

`vertical-feature`（本技能自身的规划与执行能力增强，外部入口为命令行工具）

## 需求引用

- `implement-plan.md`：本任务涉及的全部目标、范围、数据状态和验收总原则。

## 允许修改

- `pipeline_tools/**`
- `tests/**`
- `templates/**`
- `scripts/**`
- `references/**`
- `SKILL.md`
- `README.md`
- `docs/tasks/planning-driven-vertical-pipeline.md`

## 禁止修改

- `IDEA.md`
- `.pipeline/**` 原有历史任务证据和 metrics
- Git 历史
- 外部项目和用户数据

## 外部操作

- `planning-preflight`
- `facts-validate`
- `task-plan-validate`
- `progress-append`
- `evidence-finalize`

## 完整数据链路

- `entry`：`pipeline_tools` 命令行入口
- `interaction`：命令参数和结构化 JSON 输入
- `application`：规划、进度、证据校验与最终化函数
- `domain`：需求事实、项目事实、任务类型、操作覆盖和生命周期状态
- `persistence`：项目内任务文档、任务证据目录和 JSONL/JSON 结果文件
- `readback`：CLI JSON 输出、报告校验和生命周期状态读取
- `recovery`：失败现场保留、重复追加幂等、最终化失败不删除原始证据

## 验收测试

### 验收测试1：规划前置检查

- 测试：`tests/test_planning.py`：缺少 `implement-plan.md`、Git/Python/工具、孤立工作树、`.workflow` 冲突、哈希稳定性和成功/失败输出。
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_planning_preflight -v`
- 断言：关键依赖缺失返回阻塞；不自动创建、安装或修改文件；通过时返回结构化结果；失败现场可保存。
- 证据等级：1

### 验收测试2：项目事实结构校验

- 测试：`tests/test_planning.py`：有效事实、来源缺失、路径越界、操作重复、空链路且无不适用原因。
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_project_facts_validation -v`
- 断言：机械结构和引用错误被拒绝；语义判断不由脚本伪造。
- 证据等级：1

### 验收测试3：任务计划覆盖和依赖校验

- 测试：`tests/test_planning.py`：需求/资源/操作覆盖、每个操作绑定验收测试、完整链路、依赖循环、任务类型和派生关系。
- 命令：`python -m unittest tests.test_planning.PlanningTests.test_task_plan_validation -v`
- 断言：遗漏、循环、非法派生关系和缺少操作验收测试均被拒绝；有效任务计划通过。
- 证据等级：1

### 验收测试4：角色进度日志

- 测试：`tests/test_progress.py`：按角色追加、身份校验、脱敏、禁止覆盖、禁止越界目录和失败保留。
- 命令：`python -m unittest tests.test_progress -v`
- 断言：进度事件追加成功且不进入任务单；非法角色、任务和路径被拒绝；日志不含凭据。
- 证据等级：2

### 验收测试5：阶段报告和最终化

- 测试：`tests/test_evidence.py`、`tests/test_cli.py`：三角色机器结果、最终化前后引用闭包、成功清理、失败保留和幂等。
- 命令：`python -m unittest tests.test_evidence tests.test_cli -v`
- 断言：成功最终化只保留三份报告、三个机器结果和 `finalization.json`；失败不删除原始证据、不生成最终化标记。
- 证据等级：2

### 验收测试6：全量回归与文档一致性

- 测试：`tests/` 全部测试，任务单、模板、参考文档和技能说明的一致性检查。
- 命令：`python -m unittest discover -s tests -v`
- 断言：现有能力无回归；完整名称验收测试编号无缩写；脚本与大语言模型职责边界和目录生命周期一致。
- 证据等级：1

```pipeline-contract
{
  "schema": 2,
  "task_id": "planning-driven-vertical-pipeline",
  "task_type": "vertical-feature",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": ["pipeline_tools/**", "tests/**", "templates/**", "scripts/**", "references/**", "SKILL.md", "README.md", "docs/tasks/planning-driven-vertical-pipeline.md"],
  "forbidden_paths": ["IDEA.md", ".env", "**/*secret*", "**/*token*"],
  "operations": [
    {"id": "planning-preflight", "kind": "validate", "scope": "project", "acceptance_tests": ["acceptance-test-1"]},
    {"id": "facts-validate", "kind": "validate", "scope": "project", "acceptance_tests": ["acceptance-test-2"]},
    {"id": "task-plan-validate", "kind": "validate", "scope": "task-plan", "acceptance_tests": ["acceptance-test-3"]},
    {"id": "progress-append", "kind": "record", "scope": "task", "acceptance_tests": ["acceptance-test-4"]},
    {"id": "evidence-finalize", "kind": "finalize", "scope": "task", "acceptance_tests": ["acceptance-test-5"]}
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py"],
    "interaction": ["pipeline_tools/__main__.py"],
    "application": ["pipeline_tools/core.py"],
    "domain": ["pipeline_tools/contract.py"],
    "persistence": [".pipeline/<task-id>/", "docs/tasks/<task-id>.md"],
    "readback": ["pipeline_tools/core.py", "pipeline_tools/__main__.py"],
    "recovery": ["pipeline_tools/core.py"]
  },
  "acceptance_tests": [
    {"id": "acceptance-test-1", "evidence_level": 1, "test_ref": "tests/test_planning.py: PlanningTests.test_planning_preflight", "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_planning_preflight"},
    {"id": "acceptance-test-2", "evidence_level": 1, "test_ref": "tests/test_planning.py: PlanningTests.test_project_facts_validation", "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_project_facts_validation"},
    {"id": "acceptance-test-3", "evidence_level": 1, "test_ref": "tests/test_planning.py: PlanningTests.test_task_plan_validation", "command_ref": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_validation"},
    {"id": "acceptance-test-4", "evidence_level": 2, "test_ref": "tests/test_progress.py: all progress append tests", "command_ref": "python -m unittest tests.test_progress -v"},
    {"id": "acceptance-test-5", "evidence_level": 2, "test_ref": "tests/test_evidence.py and tests/test_cli.py: finalization tests", "command_ref": "python -m unittest tests.test_evidence tests.test_cli -v"},
    {"id": "acceptance-test-6", "evidence_level": 1, "test_ref": "tests/: complete regression suite", "command_ref": "python -m unittest discover -s tests -v"}
  ],
  "dependencies": [],
  "required_evidence_levels": [1, 2]
}
```

## 生命周期记录

任务单提交后，过程事件写入 `.pipeline/planning-driven-vertical-pipeline/{executor,reviewer,main}-progress.jsonl`，不修改本任务单，不进入 Git。最终结果摘要和父子任务关系由主代理在生命周期阶段追加。
