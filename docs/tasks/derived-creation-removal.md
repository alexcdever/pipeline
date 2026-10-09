# 移除派生任务的创建路径

<!-- Task ID: derived-creation-removal -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "derived-creation-removal",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "pipeline_tools/core.py",
    "pipeline_tools/planning.py",
    "pipeline_tools/__main__.py",
    "tests/test_planning.py",
    "tests/test_task_generation.py",
    "tests/test_derived_task_dispatch_recovery.py",
    "tests/test_security_repairs.py",
    "tests/test_cli.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "SKILL.md",
    "README.md",
    "references/task-design.md",
    "references/compat-and-migration.md",
    "docs/tasks/derived-creation-removal.md",
    ".pipeline/derived-creation-removal/**"
  ],
  "forbidden_paths": [
    "docs/goal.md",
    "pipeline_tools/contract.py",
    ".pipeline/task-sheet-revision-and-evidence-binding/**",
    ".pipeline/post-merge-evidence-identity/**",
    ".pipeline/finalization-and-reconcile-phase/**",
    ".pipeline/finalization-marker-head-tolerance/**",
    ".pipeline/finalization-report-reader/**",
    ".pipeline/finalization-hygiene/**",
    ".env",
    "credentials/**"
  ],
  "non_goals": [
    "不移除 derived 作为历史可读的 task_type token，也不删除 _validate_derived_from 与 _requires_full_chain、evidence_floor 的 parent 分支",
    "不修改任何历史任务单或历史证据；历史派生契约必须原样继续可读并通过校验",
    "不触碰 metrics 的 include_derived / --no-derived 与 --confidence derived——它们与任务类型无关",
    "不为让测试变绿而删除或放宽任何既有断言；历史兼容用例必须保留",
    "不实现任务单归档、历史迁移或 worktree 清理"
  ],
  "operations": [
    {
      "id": "remove-derived-creation",
      "kind": "repair",
      "scope": "remove the derived task creation path from the tool, the CLI, and the security regression test that exercises it",
      "resources": ["pipeline_tools/core.py", "pipeline_tools/__main__.py", "tests/test_security_repairs.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-2", "acceptance-test-4"]
    },
    {
      "id": "reject-derived-in-new-plans",
      "kind": "repair",
      "scope": "new task plans may not declare the derived type",
      "resources": ["pipeline_tools/planning.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2"]
    },
    {
      "id": "keep-historical-derivation-readable",
      "kind": "validate",
      "scope": "historical derived contracts keep validating and keep their tightened chain and evidence floor",
      "resources": ["tests/test_derived_task_dispatch_recovery.py", "tests/test_planning.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-3"]
    },
    {
      "id": "documentation",
      "kind": "repair",
      "scope": "record that new tasks are never derived and history stays readable",
      "resources": ["SKILL.md", "README.md", "references/task-design.md", "references/compat-and-migration.md"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-5"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: dispatch subcommands and planning generation CLI"],
    "interaction": ["pipeline_tools/planning.py: task plan validation and sheet generation"],
    "application": ["pipeline_tools/core.py: worktree dispatch"],
    "domain": ["task type tokens: new work is never derived; history stays readable"],
    "persistence": [".pipeline/derived-creation-removal/ stage reports and machine results"],
    "readback": ["tests/test_derived_task_dispatch_recovery.py"],
    "recovery": ["a plan that declares derived fails closed; historical sheets still validate"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_new_task_plan_rejects_the_derived_type",
      "command_ref": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_generated_sheets_never_declare_derived",
      "command_ref": "python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_historical_derived_contracts_still_validate",
      "command_ref": "python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_cli.py: CliTests.test_dispatch_derived_create_is_no_longer_exposed",
      "command_ref": "python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 3,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract",
      "command_ref": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract"
    }
  ],
  "dependencies": ["finalization-hygiene"],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "Amendment now covers the case derived existed for, so the creation path is obsolete; new work starts from the current head and expresses succession through dependencies."},
    {"id": "assumption-2", "statement": "The derived token and derived_from field remain part of the frozen historical contracts, so validation must keep accepting them even though nothing creates them any more."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "How many existing tests exercise the derived creation path has not been fully enumerated; only historical-compatibility tests may be kept, and any test removed must be recorded with its reason."},
    {"id": "unknown-2", "statement": "Whether tests/test_acceptance_id_and_template_compliance.py pins any string that only the derived sections provide (for example a parent sheet path in references/task-design.md) must be checked before rewriting those sections."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：任务类型与派发（收敛）
- 任务类型：`repair`
- 用户结果或系统能力：新的任务计划不再产生派生任务，工具不再暴露派生任务的创建路径；历史派生契约原样可读且校验行为不变
- 执行 worktree 约定：`<仓库根目录>/.worktrees/derived-creation-removal`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/derived-creation-removal/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- `docs/goal.md` 已规定：任务类型只有 `vertical-feature`、`prerequisite`、`repair` 三种；历史 `derived` 契约只保留读取兼容，新任务不再从父任务派生；接替关系用 `dependencies` 表达。
- 任务单修订机制（`task amend`）已合并：修正任务单不再需要开派生任务，派生创建路径因此失去用途。
- 其余收尾机制（证据版本绑定、阶段分工、最终化与读取器）均已合并并最终化。

### 允许修改

- `pipeline_tools/core.py`：派生创建函数与其调用
- `pipeline_tools/__main__.py`：`dispatch derived-create` 子命令与分派
- `pipeline_tools/planning.py`：任务计划校验与任务单生成
- `tests/test_planning.py`、`tests/test_task_generation.py`、`tests/test_derived_task_dispatch_recovery.py`、`tests/test_cli.py`、`tests/test_acceptance_id_and_template_compliance.py`
- `SKILL.md`、`README.md`、`references/task-design.md`、`references/compat-and-migration.md`
- 本任务单与 `.pipeline/derived-creation-removal/**`

### 明确不改

- `pipeline_tools/contract.py`——`TASK_TYPES` 与 `_validate_derived_from` 是历史读取路径，保持原样
- `docs/goal.md`；任何历史任务单与历史证据；六个已完成任务的证据目录
- metrics 侧的 `include_derived` / `--no-derived` / `--confidence derived`（与任务类型无关）

### 允许的测试改写（已授权，不视为放宽既有断言）

以下两处**必须**随文档模型与创建路径的移除一起改写：

- `tests/test_acceptance_id_and_template_compliance.py` 中钉住 `references/task-design.md` 派生生成措辞的用例（当前为 `test_references_task_design_documents_derived_generation_support`）：改为断言"新任务不再派生、接替关系用 `dependencies` 表达、历史 `derived` 仅作读取兼容"，并保留其"文档必须描述当前状态模型"的约束意图；被替换的措辞逐条记录理由。
- `tests/test_security_repairs.py` 中只覆盖派生创建路径的用例（顶层 import 该函数、以及调用它做不安全标识符校验的用例）随之删除或改为对保留的历史读取路径的断言；逐条记录理由。

除以上两处，其它既有断言一个都不能删除或放宽。

### 非目标

- 不删除 `derived` token；不删除父类型的链路收紧与证据下限规则。
- 不重写历史任务单，也不"迁移"历史派生契约。
- 不顺手实现归档、历史迁移或 worktree 清理。

## 事实、假设与待决

### 已确认事实

- `pipeline_tools/core.py` 存在派生创建函数（供 `dispatch derived-create` 使用），负责从父任务提交建子 worktree、复制父契约并覆盖四个字段。
- `pipeline_tools/__main__.py` 注册了 `dispatch derived-create` 子命令与其分派。
- `pipeline_tools/planning.py` 在任务计划里接受并校验 `type: derived`，并在生成期产出派生任务单。
- `pipeline_tools/contract.py` 的 `TASK_TYPES` 含 `derived`，并校验 `derived_from.parent_task_type`。
- `tests/test_derived_task_dispatch_recovery.py` 的 `DerivedTaskDispatchRecoveryTests` 共 8 个用例，其中 7 个只覆盖创建路径，1 个覆盖"失败时保留父现场"。
- `pipeline_tools/__main__.py` 里另有 `--no-derived`（metrics 的 `include_derived`）与 `--confidence derived`（metrics 置信度），二者与任务类型无关。
- 仓库中已有若干历史 `derived` 任务的冻结契约与证据。

### 未验证事实

- 尚未枚举全部只覆盖派生创建路径的用例。
- 尚未确认文档改写是否会撞上 `tests/test_acceptance_id_and_template_compliance.py` 里对 `references/task-design.md` 某些字符串的断言（该文件第 374 行附近断言过父任务单路径字符串）。
- 尚未在实现 worktree 中运行任何新增测试。

### 禁止猜测

- 不得自行决定是否让 `validate_task_plan` 对**历史**计划（已存在、含 derived）也拒绝；只对新计划拒绝。
- 不得自行删除非创建路径的历史兼容用例；若必须删除，逐条记录理由。

## 设计与行为契约

[触发] 规划器校验一份声明了 `type: derived` 的新任务计划，或调用方执行 `dispatch derived-create`
→ [处理] 工具拒绝该计划并让创建入口不可用
→ [状态] 新的任务单不再出现 `task_type: derived`；历史契约保持不变
→ [可见结果] 新任务只从当前 HEAD 建 worktree、用 `dependencies` 表达接替；历史派生任务仍能通过校验

- **计划校验 fail-closed**：新任务计划里出现 `type: derived`（或声明 `derived_from` / `parent_task_id` 的派生形态）即拒绝，并给出可读原因。
- **生成器**：不再产出 `task_type: derived` 的任务单。
- **CLI**：`dispatch derived-create` 不再可用；调用时给出明确结果（子命令不存在或返回"不再支持"），不得仍然执行创建。
- **历史读取不变**：`derived` 仍是合法 token；含 `derived_from` 的历史契约仍通过 `task validate`；父类型为 `vertical-feature` / `repair` 时链路收紧与证据下限规则原样生效。
- **不得波及**：metrics 的 `include_derived` 过滤与 `--confidence derived` 不变；`contract.py` 不变。
- **文档**：`references/task-design.md` 的派生章节改写为历史读取说明并写明新任务用 `dependencies` 表达接替；`SKILL.md`、`README.md` 同步；`references/compat-and-migration.md` 新增一条版本条目。

## 环境前置

1. `python` 与 `git` 可执行，仓库可读写。
2. 在实现 worktree 中运行聚焦与全量测试。

## 验收测试

### 验收测试1：新计划声明 derived 被拒绝

- 触发：提交一份声明 `type: derived` 的任务计划做校验。
- 断言：校验失败并给出可读原因；不生成任何任务单。
- 测试：`tests/test_planning.py: PlanningTests.test_new_task_plan_rejects_the_derived_type`
- 命令：`python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；必须失败而非接受。

### 验收测试2：生成器不再产出派生任务单

- 触发：用一份正常的三类任务计划执行任务单生成。
- 断言：产出的每张单的 `task_type` 都在三类之内；不存在 `derived_from` 字段。
- 测试：`tests/test_planning.py: PlanningTests.test_generated_sheets_never_declare_derived`
- 命令：`python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0。

### 验收测试3：历史派生契约仍可读且规则不变

- 触发：对含 `derived_from` 的历史形态契约跑校验；并核对父类型为 `vertical-feature` / `repair` 时的链路收紧与证据下限。
- 断言：校验通过；链路与证据下限行为与改动前一致。
- 测试：`tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_historical_derived_contracts_still_validate`
- 命令：`python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；不得通过放宽 `contract.py` 来达标。

### 验收测试4：创建入口不再暴露

- 触发：调用 `dispatch derived-create`。
- 断言：命令不可用或明确返回不再支持；不得创建任何 worktree、分支或任务单。
- 测试：`tests/test_cli.py: CliTests.test_dispatch_derived_create_is_no_longer_exposed`
- 命令：`python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；并断言调用后没有新增 worktree 或分支。

### 验收测试5：文档记录新规则与历史兼容

- 触发：运行文档与模板一致性检查。
- 断言：一致性检查通过；`references/task-design.md` 写明新任务不再派生、接替关系用 `dependencies`，且历史 `derived` 只作读取兼容；`compat-and-migration.md` 新增了对应版本条目。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`
- 命令：`python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；改写该测试的断言时不得删除其"文档必须描述当前状态模型"的约束意图。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 让新计划拒绝 `derived` 会同时使历史计划或历史契约被拒。
2. 必须修改 `pipeline_tools/contract.py` 才能让新计划拒绝 `derived`。
3. 文档改写会撞上既有断言而必须削弱它。
4. 实现必须修改契约未列出的文件。
