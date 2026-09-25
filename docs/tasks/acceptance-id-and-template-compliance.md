# acceptance-id-and-template-compliance：schema 2 验收 ID 与模板一致性修复

<!-- Task ID: acceptance-id-and-template-compliance -->
<!-- Contract section is frozen after commit. Lifecycle sections are maintained by the main agent. -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "acceptance-id-and-template-compliance",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": [
    "docs/tasks/pipeline*.md",
    "templates/**",
    "pipeline_tools/contract.py",
    "tests/test_contract.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "README.md",
    "SKILL.md",
    "references/**",
    "docs/tasks/acceptance-id-and-template-compliance.md"
  ],
  "forbidden_paths": [
    "implement-plan.md",
    "IDEA.md",
    "docs/tasks/** other new task sheets",
    ".pipeline/metrics/**",
    "metrics/**",
    ".worktrees/**",
    "**/*secret*",
    "**/*token*"
  ],
  "operations": [
    {
      "id": "schema2-acceptance-id-repair",
      "kind": "repair",
      "scope": "schema 2 contract validation and operation bindings",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-3"]
    },
    {
      "id": "dispatch-contract-repair",
      "kind": "validate",
      "scope": "dispatch prerequisites and schema 2 task identity",
      "acceptance_tests": ["acceptance-test-4", "acceptance-test-5"]
    },
    {
      "id": "template-evidence-compliance",
      "kind": "repair",
      "scope": "task-sheet and pipeline-evidence examples",
      "acceptance_tests": ["acceptance-test-6", "acceptance-test-7"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/contract.py", "templates/task-sheet.md"],
    "interaction": ["docs/tasks/acceptance-id-and-template-compliance.md"],
    "application": ["pipeline_tools/contract.py"],
    "domain": ["pipeline_tools/contract.py: schema and acceptance ID rules"],
    "persistence": ["docs/tasks/*.md", "templates/pipeline-evidence.json"],
    "readback": ["tests/test_contract.py", "scripts/validate_task_sheet.py"],
    "recovery": ["docs/tasks/acceptance-id-and-template-compliance.md"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 2,
      "test_ref": "tests/test_contract.py: ContractTests.test_schema2_planning_contract_is_valid",
      "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_contract.ContractTests.test_schema2_planning_contract_is_valid -v"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 2,
      "test_ref": "tests/test_contract.py: ContractTests.test_schema2_operation_must_bind_complete_acceptance_test",
      "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_contract.ContractTests.test_schema2_operation_must_bind_complete_acceptance_test -v"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 2,
      "test_ref": "tests/test_contract.py: ContractTests.test_valid_pipeline_contract",
      "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_contract.ContractTests.test_valid_pipeline_contract -v"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch",
      "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch -v"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 3,
      "test_ref": "tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history",
      "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history -v"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 1,
      "test_ref": "docs/tasks/acceptance-id-and-template-compliance.md: pipeline-contract schema 2 validation",
      "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/acceptance-id-and-template-compliance.md"
    },
    {
      "id": "acceptance-test-7",
      "evidence_level": 1,
      "test_ref": "tests/: complete regression suite",
      "command_ref": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"
    }
  ],
  "dependencies": ["dispatch-fail-closed-and-approval-semantics"],
  "required_evidence_levels": [1, 2, 3]
}
```

## 任务身份

- 项目：programing-pipeline
- 领域或阶段：continuation-3；schema 2 repair 与 dispatch repair 的契约补强
- 任务类型：`repair`
- 用户结果或系统能力：schema 2 强制完整 `acceptance-test-*` ID 及操作绑定；schema 1 只作为历史 deprecated 格式读取；任务单模板、pipeline-evidence 示例和实际契约保持同一 ID 规则；dispatch 只能消费已验证的 schema 2 契约。
- 前置任务：`dispatch-fail-closed-and-approval-semantics`
- 执行 worktree 约定：`<仓库根目录>/.worktrees/acceptance-id-and-template-compliance`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态：未开始

## 依赖与范围

### 前置条件

- `dispatch-fail-closed-and-approval-semantics` 已完成并提供 dispatch 的 fail-closed/identity 行为。
- 当前 contract validator 已区分 schema 1 与 schema 2；本任务不得把历史 schema 1 文件批量迁移成新任务单。
- `templates/task-sheet.md` 与 `templates/pipeline-evidence.json` 是新任务和证据示例的唯一模板来源。

### 允许修改

- `pipeline_tools/contract.py`
- `tests/test_contract.py`
- `tests/test_acceptance_id_and_template_compliance.py`（如已有测试结构不足时新建）
- `templates/**`
- `docs/tasks/pipeline*.md`（仅既有 pipeline 旧任务单中的缩写迁移，不新增任务单）
- `README.md`、`SKILL.md`、`references/**`
- 本任务单 `docs/tasks/acceptance-id-and-template-compliance.md` 的任务级进度区

### 明确不改

- `implement-plan.md`、`IDEA.md`、metrics 和 `.pipeline/metrics/**`。
- 除本任务单外的其它新任务单；不改写不相关任务单的历史、证据或生命周期结论。
- 产品业务代码、dispatch 实现范围外的模块、外部项目和 Git 历史。
- 不以自然语言或测试数量替代 schema/dispatch 的结构化验收。

## 事实、假设与待决

### 已确认事实

## 已确认事实、未验证事实与禁止猜测

### 已确认事实

- schema 2 contract 已要求操作 acceptance 引用使用完整 ID，并要求引用存在于顶层验收集合。
- schema 1 当前仍被历史测试读取，且旧 `AT1` 形式必须继续作为 deprecated read-only compatibility 保留。
- `dispatch.worktree-create` 已拒绝非 schema 2 task sheet；本任务验证其依赖契约，不扩大 dispatch API。

### 未验证事实

- 所有 `docs/tasks/pipeline*.md` 旧任务单中的 `AT1`、`AT2B` 等缩写位置及是否属于可迁移的人类文档文本，须由执行代理逐文件读取后记录。
- dispatch repair 依赖项在当前基线的完整独立证据，须由验收命令重新生成。

### 禁止猜测

- 不得把 schema 1 的历史读取兼容误写成 schema 2 放宽；schema 2 的顶层 ID、operation 引用和结果引用都必须完整。
- 不得把 `AT1`、`AT2B` 等缩写留在新 schema 2 契约、模板或 pipeline-evidence 示例中；迁移时对应为 `acceptance-test-1`、`acceptance-test-2b`。
- 不得通过改写 `implement-plan.md`、IDEA、metrics 或另建任务单解决冲突。

## 设计与行为契约

[触发] 读取任务单、模板或 dispatch 输入
→ [处理] 按 schema 分流；schema 2 严格验证完整 acceptance ID、唯一性、operation 绑定和引用闭包，schema 1 仅历史 deprecated 读取
→ [状态] 合法 schema 2 可继续 freeze/dispatch；旧 schema 1 可读取但不可作为新 schema 2 契约生成来源
→ [可见结果] validator、模板和 evidence 示例使用完整名称；不合法缩写返回结构化错误并 fail-closed

- 完整 ID 的正则语义为 `acceptance-test-` 加安全后缀，大小写和连字符按现有 validator 规则处理。
- operation 只能引用顶层已声明的完整验收 ID；未知、重复、缩写或空引用均拒绝。
- schema 1 的兼容读取不得改变历史文件内容，也不得让 dispatch 绕过 schema 2 gate。
- 模板示例必须同时满足人类说明和机器 JSON；不产生可直接通过的占位任务单。

## 环境前置

1. 从主工作树根目录确认 Python、Git、`pipeline-tools` 可执行，并确认依赖任务身份。
2. 每条验收命令设置 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`；单条命令硬上限 180 秒，全量回归使用明确累计上限。
3. 旧任务单迁移只在允许的既有 `docs/tasks/pipeline*.md` 文件范围内进行；不得写入 `.pipeline/metrics/**`。

## 验收测试

### 验收测试1：schema 2 合法完整 ID 通过

- 触发：读取包含完整顶层 acceptance ID、operation 绑定、七段链路和证据等级的 schema 2 契约。
- 断言：validator 返回空错误；完整 ID 在顶层和 operation 引用处保持一致。
- 测试：`tests/test_contract.py: ContractTests.test_schema2_planning_contract_is_valid`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_contract.ContractTests.test_schema2_planning_contract_is_valid -v`
- 验收模式：契约单元
- 证据等级：2
- 结果要求：退出码 0。

### 验收测试2：schema 2 拒绝缩写、未知和不完整绑定

- 触发：将 `acceptance-test-1` 替换为 `AT1`，或让 operation 指向未声明的完整 ID。
- 断言：validator 非空报错；错误指向 acceptance ID/unknown reference；不得返回可 dispatch 的契约。
- 测试：`tests/test_contract.py: ContractTests.test_schema2_operation_must_bind_complete_acceptance_test`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_contract.ContractTests.test_schema2_operation_must_bind_complete_acceptance_test -v`
- 验收模式：契约安全边界
- 证据等级：2
- 结果要求：退出码 0，两个变体均被拒绝。

### 验收测试3：schema 1 仅历史 deprecated 读取

- 触发：读取仍含 `AT1` 的历史 schema 1 任务单。
- 断言：历史 validator 读取通过且不改文件；同一缩写放入 schema 2 时被拒绝。
- 测试：`tests/test_contract.py: ContractTests.test_valid_pipeline_contract` 与 `ContractTests.test_schema2_operation_must_bind_complete_acceptance_test`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_contract -v`
- 验收模式：兼容读取回归
- 证据等级：2
- 结果要求：退出码 0，schema 分流边界明确。

### 验收测试4：有效 schema 2 契约可进入 dispatch identity

- 触发：以完整 schema 2 task sheet 执行规划到派发集成链路。
- 断言：contract/freeze/identity 阶段通过，dispatch-ready 只表示派发身份准备完成；worktree、branch、HEAD 和 task ID 一致。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch -v`
- 验收模式：Git/集成
- 证据等级：3
- 结果要求：退出码 0，身份闭包完整。

### 验收测试5：dispatch continuation 保留父任务并拒绝错误重放

- 触发：创建 continuation 派发并重复使用已占用身份或父任务现场。
- 断言：子任务 ID/path/evidence 独立；父任务历史不改写；冲突时 blocked，不能覆盖 worktree 或证据。
- 测试：`tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history -v`
- 验收模式：恢复/安全边界
- 证据等级：3
- 结果要求：退出码 0，父文件哈希不变。

### 验收测试6：本任务单 schema 2 结构校验

- 触发：从仓库根目录运行任务单 validator。
- 断言：唯一 contract 为 schema 2 repair；依赖为 dispatch repair；所有 ID 为完整名称；允许/禁止路径符合冻结范围。
- 测试：`docs/tasks/acceptance-id-and-template-compliance.md: pipeline-contract schema 2 validation`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/acceptance-id-and-template-compliance.md`
- 验收模式：契约/结构校验
- 证据等级：1
- 结果要求：退出码 0。

### 验收测试7：完整回归与范围检查

- 触发：运行完整测试套件，并检查任务单范围。
- 断言：契约、规划、dispatch、恢复和 evidence 现有测试通过；无 implement-plan/IDEA/metrics/其它新任务单修改。
- 测试：`tests/: complete regression suite`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归/范围
- 证据等级：1
- 结果要求：退出码 0；失败时保留现场，不标记 PASS。

## 决策点

1. 若 schema 1 历史任务单必须改写才能通过 schema 2，停止并报告，不自动迁移历史契约。
2. 若 dispatch repair 依赖未完成或身份漂移，保留现场并返回 BLOCKED，不复制或覆盖证据。
3. 若需要修改用户禁止的文件、metrics 或新增非本任务单任务单，停止并请求裁决。

---

## 任务级进度（主代理维护）

### 任务锚点

- 基线 HEAD：待提交契约前确认
- 契约提交：待完成
- 执行分支：`acceptance-id-and-template-compliance`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/acceptance-id-and-template-compliance`

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

## 缩写迁移约定

- 旧任务单中 `AT1` → `acceptance-test-1`，`AT2B` → `acceptance-test-2b`；只迁移明确属于验收 ID 的字段，不改变历史语义或测试命令。
- 新 schema 2、模板和 `pipeline-evidence` 示例禁止 `AT*`/`AT2B` 缩写。
- schema 1 旧文件只读兼容，除非本任务允许的 `docs/tasks/pipeline*.md` 迁移明确列出，不批量重写。

## 生命周期记录

过程事件写入 `.pipeline/acceptance-id-and-template-compliance/`，不改冻结契约。
