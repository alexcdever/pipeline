# planning-run-task-generation：从任务计划生成冻结任务单

<!-- Task ID: planning-run-task-generation -->
<!-- Contract section is frozen after commit. Lifecycle records are maintained by the main agent. -->

## 任务目标

在已通过规划前置检查的项目中，提供一个机械可验证的任务单生成能力：主代理提供需求事实、项目事实和任务计划后，工具为每个计划任务生成独立的 schema 2 任务单，绑定 `implement-plan.md` 哈希和 planning-run-id，并在失败时 fail closed、保留可审计规划现场。该任务是 prerequisite，不代表任何用户功能已经完成。

## 任务类型

`prerequisite`

## 需求引用

- `implement-plan.md`：目标、需求事实/项目事实职责边界、任务类型、哈希稳定性、失败产物和任务单生命周期。
- `references/task-design.md`：契约冻结、任务拆分、证据和产物规则。

## 允许修改

- `pipeline_tools/**`
- `tests/**`
- `templates/**`
- `references/**`
- `SKILL.md`
- `README.md`
- `docs/tasks/planning-run-task-generation.md`

## 禁止修改

- `implement-plan.md`
- `IDEA.md`
- `.pipeline/**` 中既有历史任务证据和 metrics
- `docs/tasks/planning-driven-vertical-pipeline.md`
- 外部项目、用户数据和 Git 历史
- 不创建 worktree；不自动修改或覆盖已有任务单

## 已确认事实

- 主工作树：`D:/Projects/Skills/pipeline`，分支 `main`，规划前置检查已通过。
- `implement-plan.md` 当前 SHA-256：`f06b48cf0f95b2dfc59338ecea8e3f54025598aa5bf0d45e4bf5c1840573e88`。
- `pipeline_tools/planning.py` 已提供 `planning_preflight`、`validate_project_facts`、`validate_requirement_facts` 和 `validate_task_plan`，但尚无 task-plan 到独立任务单的转换函数。
- `pipeline_tools/contract.py` 已能校验 schema 2 的 task type、implement plan、operations、完整链路、依赖和验收绑定。
- `pipeline_tools/__main__.py` 已有 `planning` CLI 分组，但没有任务单生成命令。
- `.gitignore` 已包含 `/.worktrees/`。

## 未验证事实

- 尚未实现或运行本任务要求的新生成 CLI 和测试。
- 尚未决定是否需要对任务单正文生成更多自然语言模板字段；实现应优先保证机器契约和可审计元数据，不伪造产品语义。

## 禁止猜测与决策点

- 不从文件名或 JSON 字符串推断缺失的需求、资源、操作、链路或验收测试。
- 任务计划、需求事实或项目事实校验失败时不得生成可冻结任务单。
- 任务 ID 冲突、已有任务单、implement-plan 哈希漂移、路径越界或写入失败时必须停止并保留失败现场。
- 本任务不创建 worktree；worktree 派发属于后续独立任务。

## 设计与行为契约

[输入] 已通过 preflight 的项目根目录、planning-run-id、project-facts、requirement-facts、task-plan
→ [处理] 校验三类事实/计划，绑定 implement-plan SHA-256，逐任务生成 schema 2 contract 和可读任务单
→ [状态] 成功写入每个唯一 `docs/tasks/<task-id>.md`；失败写入 `.pipeline/planning/<planning-run-id>/` 审计结果且不产生可冻结任务单
→ [可见结果] CLI JSON 摘要列出生成任务、需求哈希、planning-run-id 和错误；生成后的每个任务单可被 `pipeline-tools task validate` 校验

- 成功生成不得覆盖已有任务单。
- 生成过程不得修改 `implement-plan.md`、事实输入或任务计划输入。
- 生成任务单的 schema 2 contract 必须包含 task type、implement plan path、operations、七段链路、acceptance tests、dependencies 和 required evidence levels。
- 成功路径不创建 worktree，也不自动提交任务单；任务单提交和 worktree 创建由主代理后续阶段完成。
- 失败路径必须可重复诊断，不能把部分成功伪装成完整成功；已生成的临时文件必须不成为可冻结任务单。

## 环境前置

1. 在项目根目录运行 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools planning preflight .` 并通过。
2. Python、Git 和 pipeline 工具可执行；本轮 runtime preflight 已确认 Python 3.12.10、Git 2.55.0、Node 22.23.2、pnpm 10.27.0。
3. 新测试必须使用临时 Git 项目和临时输入文件，不读取或修改真实用户数据。

## 验收测试

### 验收测试1：有效计划生成多个 schema 2 任务单

- 触发：提供通过校验的 project facts、requirement facts 和包含两个任务的 task plan，运行生成命令。
- 断言：为每个 task 创建独立任务单；每个任务单含正确 task ID、task type、implement-plan.path、planning-run-id、当前需求哈希、operations、七段链路、完整验收测试和依赖；每份任务单通过 `validate_task`；输出 JSON 标记成功且不创建 worktree。
- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generate_valid_plan_creates_schema2_task_sheets`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_valid_plan_creates_schema2_task_sheets -v`
- 验收模式：集成 / CLI
- 证据等级：2
- 结果要求：退出码 0；生成任务单数量等于计划任务数量；无错误；输出包含 planning-run-id 和 requirements_sha256。

### 验收测试2：事实或计划校验失败时拒绝生成

- 触发：移除来源、操作验收绑定或 vertical-feature 链路后运行生成命令。
- 断言：返回结构化失败；不生成任何可冻结任务单；失败原因包含具体校验错误；规划现场写入 `.pipeline/planning/<planning-run-id>/`。
- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generation_rejects_invalid_inputs_and_preserves_failure_artifacts`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generation_rejects_invalid_inputs_and_preserves_failure_artifacts -v`
- 验收模式：集成 / CLI
- 证据等级：2
- 结果要求：退出码为配置/阻塞失败；目标任务单不存在；规划 run 目录存在且含结构化失败结果。

### 验收测试3：冲突和幂等安全

- 触发：目标任务单已存在、task ID 重复或输出路径越界时运行生成命令。
- 断言：命令拒绝覆盖和越界写入；既有任务单字节内容不变；不创建第二份任务单或 worktree。
- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generation_is_fail_closed_for_existing_tasks_duplicate_ids_and_unsafe_output`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generation_is_fail_closed_for_existing_tasks_duplicate_ids_and_unsafe_output -v`
- 验收模式：集成 / 安全边界
- 证据等级：2
- 结果要求：每种冲突退出码非零且为结构化错误；既有文件哈希保持不变；项目根外无写入。

### 验收测试4：需求哈希漂移和产物一致性

- 触发：先记录 planning-run-id 和需求哈希，再修改 `implement-plan.md` 或篡改生成任务单的机器契约后执行校验。
- 断言：哈希漂移时生成被拒绝；未漂移时每个生成任务单通过 `task validate`；任务单 contract 的任务类型、操作、链路、验收测试和依赖与 task plan 一致。
- 测试：`tests/test_task_generation.py: TaskGenerationTests.test_generation_rejects_implement_plan_hash_drift_and_checks_plan_sheet_consistency`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generation_rejects_implement_plan_hash_drift_and_checks_plan_sheet_consistency -v`
- 验收模式：集成 / 契约
- 证据等级：2
- 结果要求：漂移返回阻塞且不生成新任务单；一致性检查覆盖每个生成任务；不得修改需求文件。

### 验收测试5：CLI 端到端和规划现场生命周期

- 触发：从临时项目根目录调用 `planning generate-task-sheets`，分别覆盖成功、失败和重复调用。
- 断言：CLI JSON 输出包含 schema、command、status、task_id/run_id、artifacts、errors、next_actions；成功和失败退出码稳定；规划失败只保存审计中间结果，成功不产生 worktree。
- 测试：`tests/test_cli.py: CLITests.test_planning_generate_task_sheets_cli_lifecycle`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli.CLITests.test_planning_generate_task_sheets_cli_lifecycle -v`
- 验收模式：CLI 集成
- 证据等级：2
- 结果要求：JSON 可解析；成功退出码 0；输入错误退出码 2 或 3；无未授权路径写入。

### 验收测试6：全量回归、契约和范围

- 触发：在执行 worktree 运行完整测试与任务契约校验。
- 断言：既有测试无回归；新增任务生成测试通过；本任务单契约通过；修改路径只在允许范围内；无 whitespace 错误。
- 测试：`tests/` 全部测试；`tests/test_contract.py` 任务契约测试。
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归 / 机械检查
- 证据等级：1
- 结果要求：退出码 0；所有测试通过；`python -m pipeline_tools task validate docs/tasks/planning-run-task-generation.md` 通过；`git diff --check` 通过。

## 决策点

出现以下情况时保留 worktree 并报告，不得静默扩大范围：

1. 需要从自然语言自动推断 task-plan，而非接收结构化 task-plan 输入。
2. 需要修改 schema 2 以外的协议或兼容旧任务单行为。
3. 需要创建 worktree、提交生成任务单或自动合并分支。

---

## 任务级进度（主代理维护）

### 任务锚点

- 基线 HEAD：待提交契约前确认
- 契约提交：待完成
- 执行分支：`planning-run-task-generation`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/planning-run-task-generation`

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| 验收测试1 | 未开始 | - | - | - |
| 验收测试2 | 未开始 | - | - | - |
| 验收测试3 | 未开始 | - | - | - |
| 验收测试4 | 未开始 | - | - | - |
| 验收测试5 | 未开始 | - | - | - |
| 验收测试6 | 未开始 | - | - | - |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 1 | 任务单设计 | 已完成 | implement-plan.md、planning preflight、runtime preflight | 提交契约并创建 worktree |

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
  "task_id": "planning-run-task-generation",
  "task_type": "prerequisite",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": ["pipeline_tools/**", "tests/**", "templates/**", "references/**", "SKILL.md", "README.md", "docs/tasks/planning-run-task-generation.md"],
  "forbidden_paths": ["implement-plan.md", "IDEA.md", ".env", "**/*secret*", "**/*token*", ".pipeline/** existing history"],
  "operations": [
    {"id": "planning-generate-task-sheets", "kind": "generate", "scope": "project", "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-3", "acceptance-test-4", "acceptance-test-5"]},
    {"id": "planning-generation-validate", "kind": "validate", "scope": "task-plan", "acceptance_tests": ["acceptance-test-2", "acceptance-test-4", "acceptance-test-6"]},
    {"id": "planning-generation-audit", "kind": "record", "scope": "planning-run", "acceptance_tests": ["acceptance-test-2", "acceptance-test-3", "acceptance-test-5"]}
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py"],
    "interaction": ["pipeline_tools/__main__.py"],
    "application": ["pipeline_tools/planning.py"],
    "domain": ["pipeline_tools/contract.py", "pipeline_tools/planning.py"],
    "persistence": ["docs/tasks/planning-run-task-generation.md", ".pipeline/planning/historical-planning-run/"],
    "readback": ["pipeline_tools/__main__.py", "pipeline_tools/contract.py"],
    "recovery": ["pipeline_tools/planning.py"]
  },
  "acceptance_tests": [
    {"id": "acceptance-test-1", "evidence_level": 2, "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generate_valid_plan_creates_schema2_task_sheets", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_valid_plan_creates_schema2_task_sheets -v"},
    {"id": "acceptance-test-2", "evidence_level": 2, "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generation_rejects_invalid_inputs_and_preserves_failure_artifacts", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generation_rejects_invalid_inputs_and_preserves_failure_artifacts -v"},
    {"id": "acceptance-test-3", "evidence_level": 2, "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generation_is_fail_closed_for_existing_tasks_duplicate_ids_and_unsafe_output", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generation_is_fail_closed_for_existing_tasks_duplicate_ids_and_unsafe_output -v"},
    {"id": "acceptance-test-4", "evidence_level": 2, "test_ref": "tests/test_task_generation.py: TaskGenerationTests.test_generation_rejects_implement_plan_hash_drift_and_checks_plan_sheet_consistency", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generation_rejects_implement_plan_hash_drift_and_checks_plan_sheet_consistency -v"},
    {"id": "acceptance-test-5", "evidence_level": 2, "test_ref": "tests/test_cli.py: CLITests.test_planning_generate_task_sheets_cli_lifecycle", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli.CLITests.test_planning_generate_task_sheets_cli_lifecycle -v"},
    {"id": "acceptance-test-6", "evidence_level": 1, "test_ref": "tests/: complete regression suite", "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"}
  ],
  "dependencies": [],
  "required_evidence_levels": [1, 2]
}
```

## 生命周期记录

任务契约提交后，执行、审查和主代理过程事件写入 `.pipeline/planning-run-task-generation/{executor,reviewer,main}-progress.jsonl`，不修改本契约区。


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
