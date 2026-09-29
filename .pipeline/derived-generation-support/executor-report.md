# executor-report：derived-generation-support

## 任务身份

- task-id：`derived-generation-support`
- task-type：`prerequisite`
- planning-run-id：`derived-generation-support`
- worktree：`D:\Projects\Skills\pipeline\.worktrees\derived-generation-support`
- branch：`derived-generation-support`
- baseline：`1e580ec`
- role：executor，round 1
- goal SHA-256（契约记录）：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`

## 两条阻塞的实际改动

### 阻塞 1 — `_task_sheet_text` 不输出 `derived_from`

`pipeline_tools/planning.py:1676` `_task_sheet_text`。改动：

- 签名新增可选 `root: Path | None = None`（关键字参数，仅供跨 run 父任务机械读取）。
- 在 `task_type == "prerequisite"` 分支之前插入 `task_type == "derived"` 分支：解析 `relation_id`（`derived_from.task_id` → `derived_from.parent_task_id` → `task.parent_task_id`），按双来源优先级取 `parent_task_type`，写入 `contract["derived_from"] = {task_id, commit, branch, parent_task_type}`。
- `commit` / `branch` 由规划者在 plan 显式声明，工具**照抄**（不自动填、不对同 run 做推导）。同 run 父任务在生成时还没有自己的提交与分支，因此由规划者给出非空值。

改前：`contract` 字典的 18 个键里没有 `derived_from`，也无 derived 分支，生成器必然产出缺 `derived_from` 的 schema 4 单。实测错误：`child-task.md: derived task requires a derived_from object`。
改后：derived 任务产出带四字段 `derived_from` 的 schema 4 单，`validate_task` 返回 `[]`。

### 阻塞 2 — 跨 run 父任务的 catch-22

`pipeline_tools/planning.py:1028` `validate_task_plan` 原签名无 `root`。改动：

- 签名新增**可选**关键字参数 `root: Path | None = None`。
- derived 分支（原 `:1197-1211`）重写：父在 `tasks` 内时按 plan 内父 task 的 `type` 校验声明值；父不在 `tasks` 内时改调 `_cross_run_parent_errors(...)`，不再直接报 `invalid parent_task_id`。
- 新增 `_read_parent_task_type(root, parent_id)`：用 `git show HEAD:docs/tasks/<parent-id>.md` 从 **HEAD** 读冻结父单，解析其中 `pipeline-contract` 块，取 `task_type`。
- 新增 `_cross_run_parent_errors(...)`：`root` 缺失 → 拒绝（无法机械证实）；父单在 HEAD 不存在 / 无契约块 / 无 `task_type` → 拒绝；声明值与机械读取值不等 → 拒绝。
- 新增模块级 `CONTRACT_BLOCK_RE`（与 `contract.py` 的 `CONTRACT_RE` 同形）用于解析父单契约块。

### 第三条耦合 — `derived_from.task_id` 必须等于 `parent_task_id`

`pipeline_tools/planning.py:1204-1209` 的既有一致性校验原样保留：`relation_id = derived_from.get("task_id") or derived_from.get("parent_task_id")`，`relation_id != parent` 时报 `inconsistent derived_from`。本次未放宽该断言。

## `validate_task_plan` 加 `root` 的调用点清单

`root` 是可选关键字参数，既有调用不受影响。

| 调用点 | 位置 | 传入 |
|---|---|---|
| `compare_task_plan_contract` | `planning.py:1278` | `root=root`（该函数本就有 `root` 参数） |
| `generate_task_sheets` | `planning.py:1766` | `root=root`（函数入参，已 `Path(root).resolve()`） |
| CLI `task-plan-validate` | `__main__.py:981` | 未传（保持可选，行为不变） |
| `generate_task_sheets` → `_task_sheet_text` | `planning.py:1788` | 新增 `root=root` |

## `parent_task_type` 机械读取的实现（双来源优先级）

生成器侧 `_task_sheet_text`：

1. **同 run**：`plan["tasks"]` 里 `id == relation_id` 的 task 的 `type`。
2. **plan 声明值**：`derived_from.parent_task_type`（回退）。
3. **跨 run**：`root` 可用时 `_read_parent_task_type(root, relation_id)` 从 `HEAD:docs/tasks/<parent-id>.md` 读。

三者都拿不到时抛 `ValueError`，由 `generate_task_sheets` 捕获为 blocked，不写任何单。

校验侧 `_cross_run_parent_errors` 只做机械读取 + 声明值比对；同 run 情形在 `validate_task_plan` 内直接比对 plan task 的 `type`。

## `op-guard-derivation-contract` 是否需要改 `contract.py`

**不需要改动。** 理由：既有闸门已经完整覆盖本任务所需约束——

- `_validate_derived_from`（`contract.py:149-165`）已要求 `task_id`/`commit`/`branch`/`parent_task_type` 四字段非空且 `parent_task_type` 属于四个类型 token。
- `_requires_full_chain`（`:167-180`）与 `evidence_floor`（`:132-147`）已按 `derived_from.parent_task_type` 收紧链路与证据下限。
- `load_contract` 在 `schema in {3,4}` 时调用 `_validate_schema3_contract`，其中已含 `_validate_derived_from`。

生成器一旦产出合法 `derived_from`，这些闸门自然放行；无需放宽或新增。`contract.py` 未做任何改动（`git status` 无该文件）。

## 9 条新测试

### `tests/test_task_generation.py` — `TaskGenerationTests`

| # | 方法 | 断言 | 修复前 |
|---|---|---|---|
| 1 | `test_generator_emits_derived_from_for_derived_task` | 生成 `pass`；`derived_from` 四字段等于 `{task_id: parent-run, commit: 40×a, branch: parent-run-branch, parent_task_type: prerequisite}`；`validate_task == []` | **红**：`blocked`，`derived task derived-child has invalid parent_task_id` |
| 2 | `test_generator_output_for_non_derived_task_is_unchanged` | 非 derived 契约的键集合恰为 19 个已知键（含 `non_user_completion_reason`），且不含 `derived_from` | 绿（回归保护） |
| 3 | `test_generate_task_sheets_emits_derived_sheet_for_same_run_parent` | 父同在本 run、父单不存在 → `pass`，`task_ids == [parent-task, child-task]`，父单无 `derived_from`，子单 `dependencies == [parent-task]` 且 `derived_from` 正确 | **红**：`blocked`，`child-task.md: derived task requires a derived_from object` |
| 4 | `test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists` | 父单已存在 → `blocked`，错误含 `already exists`，父单字节不变，子单不存在，无 `*.planning-tmp` | 绿（回归保护，既有 fail-closed 语义） |

### `tests/test_planning.py` — `PlanningTests`

| # | 方法 | 断言 | 修复前 |
|---|---|---|---|
| 5 | `test_task_plan_accepts_derived_parent_outside_the_run` | 无 `root` 时非空错误；带 `root` 且父单已冻结 → `[]` | **红**：`TypeError: validate_task_plan() got an unexpected keyword argument 'root'` |
| 6 | `test_task_plan_rejects_derived_parent_that_cannot_be_found` | 父单不存在 → 错误含 `ghost-task` 与 `parent`；父单未提交 → 错误含 `unfrozen-task` | **红**：同上 `TypeError` |
| 7 | `test_task_plan_rejects_planner_declared_parent_type_mismatch` | 声明值等于机械值 → `[]`；声明 `repair` 而父为 `prerequisite` → 错误含 `parent_task_type`，且不含 `invalid parent_task_id` | **红**：同上 `TypeError` |
| 8 | `test_task_plan_accepts_same_run_derived_parent` | 父在 `tasks` 内 → `[]`；声明值不匹配 → 错误含 `parent_task_type` | **红**：同上 `TypeError` |

### `tests/test_acceptance_id_and_template_compliance.py` — `AcceptanceIdAndTemplateComplianceTests`

| # | 方法 | 断言 | 修复前 |
|---|---|---|---|
| 9 | `test_references_task_design_documents_derived_generation_support` | 文档含「两条写入路径」及 `derived_from`/`_task_sheet_text`/`create_derived_dispatch`/`parent_task_type`/`docs/tasks/<parent-id>.md`/`validate_task_plan`/机械读取/fail-closed/root/commit/branch/工具照抄/同一次 planning run/HEAD | **红**：`'两条写入路径' not found` |

**修复前红绿状态汇总**：6 条红（1、3、5、6、7、8、9 中的 1/3 红 + 5/6/7/8 error + 9 红），2 条绿（2、4，均为回归保护）。修复后 9 条全绿。

## 端到端验证结果

在系统 temp 建仓，把 `docs/tasks/evidence-retention-forward-gate.md` 作为真实且已冻结的跨 run 父单复制进 `docs/tasks/` 并提交，再跑 `generate_task_sheets`：

```
STATUS: pass
ERRORS: []
VALIDATE_TASK: []
DERIVED_FROM: {
  "task_id": "evidence-retention-forward-gate",
  "commit": "7590f2a500c33e475788972bf6162736dce53b99",
  "branch": "main",
  "parent_task_type": "prerequisite"
}
SCHEMA: 4 TASK_TYPE: derived
```

生成的 `derived-demo.md` 是合法 schema 4 单，`derived_from.parent_task_type` 与父单 `task_type`（`prerequisite`）一致，`commit`/`branch` 为规划者声明值照抄。

## 测试结果

- 针对性（`tests.test_task_generation tests.test_planning tests.test_acceptance_id_and_template_compliance tests.test_contract tests.test_planning_dispatch_integration`）：`Ran 135 tests`，`OK`，103.6s。
- 全量（`python -m unittest discover -s tests`）：`Ran 303 tests`，`OK`，211.9s。基线 294 + 新增 9 = 303。

## 9 条验收命令

逐条实跑，全部 `exit 0`（见 `executor-result.json` 的 `commands[]`）。

## 诚实报告

- 第 2、4 条测试修复前就是绿的，它们是**回归保护**，不是本次修复的判别证据。任务单已预判第 8 条可能本来就绿；实测第 8 条修复前为 error（`root` 参数不存在），修复后转绿。
- `op-guard-derivation-contract` 判定为无需改动，`contract.py` 未触碰。
- gate pre-merge 与 freshness 结果见下方正文与 `executor-result.json`。

## 未完成 / 未验证项

- reviewer / final 两阶段证据缺失（本任务只交付 executor 阶段）。
- `op-guard-derivation-contract` 未新增测试；由第 1、7 条间接覆盖既有闸门未被破坏。
- 未改动 `create_derived_dispatch`（任务单 `non_goals` 第 3 条明确禁止），派发期路径仅做静态阅读确认契约形状一致。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "derived-generation-support",
  "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
  "branch": "derived-generation-support",
  "role": "executor",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generator_emits_derived_from_for_derived_task",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generator_output_for_non_derived_task_is_unchanged",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_emits_derived_sheet_for_same_run_parent",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_accepts_derived_parent_outside_the_run",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_derived_parent_that_cannot_be_found",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_rejects_planner_declared_parent_type_mismatch",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_planning.PlanningTests.test_task_plan_accepts_same_run_derived_parent",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_derived_generation_support",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation tests.test_planning tests.test_acceptance_id_and_template_compliance tests.test_contract tests.test_planning_dispatch_integration",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    },
    {
      "command": "python -m pipeline_tools task validate docs/tasks/derived-generation-support.md",
      "exit_code": 0,
      "evidence_ref": "executor-report.md"
    }
  ],
  "assertions": [
    "generate_task_sheets 为跨 run 父任务的 derived 任务产出 status=pass 且 derived_from 四字段齐备的 schema 4 任务单",
    "派发期 create_derived_dispatch 的 derived_from 契约形状与生成器侧一致，本任务未改动该函数",
    "validate_task_plan 新增可选 root 参数；无 root 时跨 run 父任务 fail-closed，有 root 时父单已冻结则接受",
    "父任务同在本 run 的 tasks 内时，生成器与 validate_task_plan 都接受，且父单与 derived 单在同一次生成中一并写出",
    "父单已存在时 generate_task_sheets fail-closed，不写任何单、不留 *.planning-tmp 残留",
    "derived_from.parent_task_type 按父任务位置机械读取（同 run 取 plan task 的 type，跨 run 读 HEAD:docs/tasks/<parent-id>.md），声明值必须与机械读取值相等",
    "contract.py 的既有 derived 闸门未被放宽，op-guard-derivation-contract 无需改动",
    "全量测试 303 项通过，基线 294 项未回归"
  ],
  "evidence_refs": ["executor-report.md"],
  "unverified": [
    "reviewer 阶段与 main-final 阶段证据尚未生成（本任务仅交付 executor 阶段）",
    "gate pre-merge 预期 blocked（缺 reviewer/final 证据），实际输出见 executor-result.json",
    "freshness 需在执行提交后运行，本轮报告只记录提交前状态"
  ],
  "identity": {
    "product_head": "19e19fdad58130e2338b57eab7d33aaef30e38db"
  },
  "recommendation": "ready_for_review"
}
```