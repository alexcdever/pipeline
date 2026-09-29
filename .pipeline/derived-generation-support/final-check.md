# final-check：derived-generation-support

## 0. 任务身份

- task-id：`derived-generation-support`
- task-type：`prerequisite`
- planning-run-id：`derived-generation-support`
- worktree：`D:\Projects\Skills\pipeline\.worktrees\derived-generation-support`
- branch：`derived-generation-support`
- baseline（冻结任务单）：`1e580ec`
- 被终审 HEAD：`5bcea4c36afb75600416cfb628cdc85a632aecc6`
- role：`main-final`，round 1
- goal SHA-256（契约记录）：`9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`

阶段链路：执行 `19e19fd`（产品/测试/文档）→ 证据 `a8dbdb4` / `4ab97fc` → 独立审查 `5bcea4c`（`reviewer-result.json` verdict=`ACCEPT`）→ 本次终审（本报告）。

本报告为第三层验证：§1、§5 的端到端与 fail-closed 均为本轮独立复现，未采信执行者或审查者摘要。

## 1. 任务 1：端到端验证的独立确认

在系统临时目录（`mktemp -d`，**不落仓库**）重建最小 Git 仓库，复制 `goal.md` 与真实已冻结父单 `docs/tasks/evidence-retention-forward-gate.md`（先确认 `git cat-file -e HEAD:docs/tasks/evidence-retention-forward-gate.md` 成功；其契约 `task_type=prerequisite`），提交后直接调用 `generate_task_sheets`。

`generate_task_sheets` 实际返回：

```json
{
  "schema": 1,
  "command": "planning.generate-task-sheets",
  "status": "pass",
  "run_id": "e2e-derived-run",
  "planning_run_id": "e2e-derived-run",
  "task_ids": ["derived-e2e-child"],
  "artifacts": ["docs/tasks/derived-e2e-child.md"],
  "errors": [],
  "next_actions": ["review and commit generated task sheets"]
}
```

生成的 derived 单 `docs/tasks/derived-e2e-child.md` 契约块实测：

- `schema` = `4`，`task_type` = `derived`
- `derived_from` 四字段**实际值**：
  - `task_id` = `evidence-retention-forward-gate`
  - `commit` = `19e19fdad58130e2338b57eab7d33aaef30e38db`（**照抄 plan 声明值，未自动填充**）
  - `branch` = `derived-generation-support`（**照抄 plan 声明值，未自动填充**）
  - `parent_task_type` = `prerequisite`（机械读取 `HEAD:docs/tasks/evidence-retention-forward-gate.md`）
- `validate_task(sheet)` 返回 `[]`
- `chain` 七段（entry / interaction / application / domain / persistence / readback / recovery）全部为 `{"not_applicable": true, "reason": "this task declares no chain reference for this phase"}` —— 父类型是 `prerequisite`，`contract.py:_requires_full_chain` 返回 `False`，形态正确。

**反向核验 1（ghost 父任务）**：`parent_task_id = "no-such-task-xyz"` →

- `status = blocked`
- `errors = ["derived task derived-missing-parent: parent task no-such-task-xyz has no frozen sheet at HEAD:docs/tasks/no-such-task-xyz.md"]`
- `docs/tasks/` 下仅剩父单，**未写任何 derived 单**（fail-closed 成立）

**反向核验 2（声明类型不符）**：`derived_from.parent_task_type = "vertical-feature"`（父单实际 `prerequisite`）→

- `status = blocked`
- `errors = ["derived task derived-type-mismatch derived_from.parent_task_type vertical-feature does not match the parent task type prerequisite"]`
- **未写任何单**

**结论：核心目标达成** —— 生成器首次产出经全部机械校验的合法 derived 单，且两条反向路径均 fail-closed。

## 2. 任务 2：两个待决项的裁定

### 2.1 `executor-result.json` 的 `identity.head`

实测 `identity` 全文：

```json
{"product_head": "19e19fdad58130e2338b57eab7d33aaef30e38db", "head": "a8dbdb4"}
```

提交溯源（逐提交 diff 实测）：

- `a8dbdb4`：把 `head` 从 `PENDING_EXECUTOR_COMMIT` 改为 `19e19fd...`（当时 `head == product_head`）。
- `4ab97fc`（message：`point executor head at the evidence commit`）：把 `head` 从 `19e19fd...` 改为 `a8dbdb4`。

**裁定：符合惯例，无需修正。**

依据：

1. 惯例中**有校验语义**的字段是 `product_head`；实测 `= 19e19fd`，恰为「最后一个改非证据路径的提交」——`git diff 1e580ec HEAD --name-status` 的 5 个非证据改动文件全部由 `19e19fd` 引入。此项完全正确。
2. `identity.head` **不被任何工具校验**。`core.py:1489-1523` 的 `evidence_freshness` 在 `product_head` 存在时只校验 `product_head`（可解析、是当前 HEAD 的祖先、`product_head..HEAD` 差异为证据/metrics），**完全不读 `head`**；`verify_structured_result`（`core.py:1220-1252`）根本不检查 `identity`。`head` 是纯记录字段。
3. 仓库先例支持 `head ≠ product_head`：`.pipeline/acceptance-id-and-template-compliance/executor-result.json` 为 `head=2beb5057…` / `product_head=ba7e80d8…`；`.pipeline/test-ref-narrowing-followup/final-check.md` §2.2 明确把「`identity.head` 与审查时 HEAD 不一致」判为已知自指特性、**可接受、非阻塞**。
4. `a8dbdb4` 可辩护：`19e19fd` 处 `executor-result.json` 仍带占位 `head: PENDING_EXECUTOR_COMMIT`，结果文件是在 `a8dbdb4` 才达到被报告的最终状态。

旁证：`freshness` 在 `5bcea4c` 上 `status=pass`、`errors=[]`、`observed.evidence_only=true`，说明 `19e19fd..5bcea4c` 之间仅证据与 metrics 改动，无产品漂移。

**残留歧义（低严重度，记录备查）**：若把「`head` 指向执行提交」按字面理解，执行提交应为 `19e19fd`。两种读法均可辩护，且该字段不参与任何闸门，故本次**不改动已提交的被审产物**，仅记录。本报告自身 `final-result.json` 的 `identity.head` 采用字面读法（`19e19fd`）以体现惯例原文。

### 2.2 `result verify` 的目录形式 FAIL

独立实测三次：

| 形式 | 命令 | 结果 | exit |
|---|---|---|---|
| 文件 | `result verify .pipeline/derived-generation-support/executor-result.json --task-id derived-generation-support --role executor` | `status=pass`，`errors=[]` | 0 |
| 文件 | `result verify .pipeline/derived-generation-support/reviewer-result.json --task-id derived-generation-support --role reviewer` | `status=pass`，`errors=[]` | 0 |
| 目录 | `result verify .pipeline/derived-generation-support --task-id derived-generation-support --role executor` | `status=fail`，`errors=["result is missing or invalid JSON"]` | 2 |

**裁定：CLI 用法约束，非工具缺陷。**

- `pipeline_tools/__main__.py:347-348` 把 `result verify` 的 `path` 定义为**单数 JSON 文件**位置参（`result_verify.add_argument("path", type=Path)`）。
- `verify_structured_result`（`core.py:1220-1224`）经 `_json_file(path)` 读取；传目录必然得到 `None` 并返回 `result is missing or invalid JSON`。
- 目录形式并非受支持的调用形态；「传证据目录」是调用方误用。

`pipeline_tools/__main__.py` **不在本任务 `allowed_paths` 内**（`grep -c "__main__.py" docs/tasks/derived-generation-support.md` → `0`），因此即使要改善报错文案也不得在本任务改动。仅记录为可选的后续改进项（非缺陷）。

## 3. 任务 3：里程碑记录

本任务之前，仓库中**没有任何 derived 单是经生成器产出的**。独立核验：

| 单 | 来源提交 | 契约块实测 |
|---|---|---|
| `docs/tasks/derived-task-dispatch-recovery.md` | `a818e08 docs: freeze remaining pipeline task contracts`、`ba1ac15 docs: migrate historical task sheets to current schema` | **schema 2**、`task_type=derived`、**无 `derived_from`** |
| `docs/tasks/gate-deletion-semantics-continuation-1.md` | `c92788c docs(tasks): freeze gate-deletion-semantics-continuation-1 record` | **schema 4**、`task_type=derived`、**手写** `derived_from` 四字段 |

后者单内第 5 行自述 `<!-- 本任务单为手工撰写，非 generate-task-sheets 产出；planning 审计链缺失 -->`；其正文第 195-198 行更明确指出「`_task_sheet_text` 构造的 18 个键里没有 `derived_from`，也没有 derived 分支，生成器必然产出缺 `derived_from` 的 schema 4 单」。

**本任务消除的缺口**：此前 derived 单只能手工撰写，因而绕过生成器的全部机械校验——schema 版本、`derived_from` 四字段齐备性与取值合法性、父子类型一致性、跨 run 父单存在性、`derived_from.task_id == parent_task_id` 一致性、链路形态（`not_applicable` vs 真实引用）、证据下限。现在这些校验在生成路径上强制执行；§1 的端到端实测即为该能力的直接证据。

## 4. 任务 4：两项「未改」判断的核验

### 4.1 `contract.py` 零改动 —— 成立

`git diff 1e580ec HEAD -- pipeline_tools/contract.py` 实测为空。

读三处闸门：

- `_validate_derived_from`（`contract.py:149-165`）：要求 `derived_from` 为对象，`task_id` / `commit` / `branch` 为非空字符串，`parent_task_type` 非空且属于 `TASK_TYPES`。
- `_requires_full_chain`（`:167-180`）：`vertical-feature` / `repair` 返回 `True`；`derived` 视 `derived_from.parent_task_type` 是否属于 `{vertical-feature, repair}`。
- `evidence_floor`（`:132-147`）：`parent_task_type == "vertical-feature"` 时抬升到 `VERTICAL_FEATURE_EVIDENCE_FLOOR`。

生成器现在产出的 `derived_from` 四字段齐备且 `parent_task_type=prerequisite` 合法，三个闸门自然放行——端到端实测 `validate_task(sheet) == []` 直接证明。**判断成立；该 operation 本不应有改动。**

### 4.2 `create_derived_dispatch` 未改动 —— 成立

`git diff 1e580ec HEAD -- pipeline_tools/core.py` 实测为空，符合 `non_goals` 第 3 条。

两条路径的 `derived_from` 契约形状**已一致**：

- 派发期 `create_derived_dispatch`（`core.py` 约 `:1363`）：`{"task_id": parent_task_id, "commit": parent_commit, "branch": parent_branch, "parent_task_type": parent_task_type.strip()}`
- 生成器 `_task_sheet_text`（`planning.py:1821-1854`）：`{"task_id": relation_id, "commit": derived_from.get("commit"), "branch": derived_from.get("branch"), "parent_task_type": parent_task_type}`

同一组四个键、同一命名、同一语义。

## 5. 任务 5：`root=None` 的 fail-closed 语义

同一份「跨 run 父任务」plan（父 = `evidence-retention-forward-gate`，父单已冻结在 HEAD）实测两次 `validate_task_plan`：

| 调用 | 实际 errors |
|---|---|
| **不传** `root` | `["derived task derived-root-none parent_task_id evidence-retention-forward-gate is outside this run and root is unavailable to prove it exists"]` → **拒绝** |
| **传** `root`（父单已冻结） | `[]` → **接受** |

**结论**：`root=None` 不会静默接受；跨 run 父任务在无法机械证实存在时 fail-closed，提供 `root` 且父单冻结在 HEAD 时接受。语义正确。

## 6. 核心事实独立复核

- 提交链：`1e580ec` → `19e19fd` → `a8dbdb4` → `4ab97fc` → `5bcea4c`。
- `git diff 1e580ec HEAD --name-status`：非证据改动**恰 5 个文件**，全部落在 6 项 `allowed_paths` 内 —— `pipeline_tools/planning.py`、`references/task-design.md`、`tests/test_acceptance_id_and_template_compliance.py`、`tests/test_planning.py`、`tests/test_task_generation.py`；其余全部为 `.pipeline/derived-generation-support/` 与 `.pipeline/metrics/`（允许）。
- 冻结任务单字节未变：`sha256sum docs/tasks/derived-generation-support.md` = `16f776df56009bd87635a16eb0ddca04a69719292c01984138a235d8f6268135`，与期望逐字一致。
- 9 条验收测试逐条实跑（`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`，从契约取 `command_ref`）：**9/9 exit=0**，逐条列出于 `final-result.json` 的 `acceptance`。
- 全量：`Ran 303 tests in 216.818s` → `OK`（exit 0）。基线 294 + 新增 9 = 303，与执行者、审查者报数一致。
- `freshness`（在 `5bcea4c`）：`status=pass`、`errors=[]`、`observed.evidence_only=true`；其生成的 `freshness.json` 已删除（不在保留集内）。
- `result verify`：executor 文件形式 `pass` / exit 0；reviewer 文件形式 `pass` / exit 0；目录形式 `fail` / exit 2（详见 §2.2）。
- `gate pre-merge`（**正确形式**：位置参为证据目录 `.pipeline/derived-generation-support`）：`errors=["missing final-check.md","missing final-result.json"]`、exit 3 —— 与前置状态描述一致；本报告与 `final-result.json` 落盘后应转 pass。
  - 附注：位置参若误传仓库根 `.`，会得到 6 条 missing（因为查的是 `<dir>/executor-report.md` 等）；该差异纯属调用形式，非状态差异。
- 证据目录：`git ls-files .pipeline/derived-generation-support/` 原为 4 个（executor 2 + reviewer 2），本报告与 `final-result.json` 落盘后为 6 个；**无 `.log`、无 `freshness.json`**。
- 抽查核心改动（自读代码，未抄审查者）：
  - `_task_sheet_text` 的 derived 分支：`commit` / `branch` **照抄** plan 声明值，不自动填充 —— 端到端实测值等于 plan 中的声明。
  - `_read_parent_task_type`（`planning.py:311-334`）：确用 `git show HEAD:docs/tasks/<parent-id>.md` 读取父单，解析 `pipeline-contract` 块取 `task_type`。
  - `validate_task_plan` 的 `root` 为**可选**关键字参数（`planning.py:1088-1093`），既有位置调用兼容。
  - `planning.py:1295-1299` 的 `derived_from.task_id == parent_task_id` 一致性校验**未被放宽**（`relation_id != parent` 仍报 `inconsistent derived_from`）。

## 7. 执行与审查阶段确认

- 执行阶段：`19e19fd`（`planning.py` +136、`references/task-design.md` +21、3 个测试文件 +289）+ `a8dbdb4` / `4ab97fc`（证据）。`executor-result.json` 9 条验收全 `pass`。
- 审查阶段：`5bcea4c` 由独立上下文产出 `review-report.md` + `reviewer-result.json`，`verdict=ACCEPT`；审查者独立复现了「非证据改动恰 5 文件」「7 红 2 绿分布」「端到端 derived 单」「ghost 父任务 blocked」「全量 303 OK」「freshness pass」。
- 链路完整且方向一致：执行 → 独立审查（ACCEPT）→ 终审（本报告）。终审对核心目标（生成器产出 derived 单）与两条 fail-closed 路径做了**本轮独立复现**，与审查结论独立吻合。

本报告未引用任何已删除的原始日志。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "derived-generation-support",
  "acceptance_id_format": "acceptance-test-*",
  "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
  "branch": "derived-generation-support",
  "role": "main-final",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "git log --oneline -6",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "git diff 1e580ec HEAD --name-status",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "git diff 1e580ec HEAD -- pipeline_tools/contract.py pipeline_tools/core.py",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "sha256sum docs/tasks/derived-generation-support.md",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generator_emits_derived_from_for_derived_task tests.test_task_generation.TaskGenerationTests.test_generator_output_for_non_derived_task_is_unchanged tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_emits_derived_sheet_for_same_run_parent tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists tests.test_planning.PlanningTests.test_task_plan_accepts_derived_parent_outside_the_run tests.test_planning.PlanningTests.test_task_plan_rejects_derived_parent_that_cannot_be_found tests.test_planning.PlanningTests.test_task_plan_rejects_planner_declared_parent_type_mismatch tests.test_planning.PlanningTests.test_task_plan_accepts_same_run_derived_parent tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_derived_generation_support",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/derived-generation-support --result .pipeline/derived-generation-support/executor-result.json",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/derived-generation-support/executor-result.json --task-id derived-generation-support --role executor",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/derived-generation-support/reviewer-result.json --task-id derived-generation-support --role reviewer",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/derived-generation-support --task-id derived-generation-support --role executor",
      "exit_code": 2,
      "expected_exit_code": 2,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json gate pre-merge .pipeline/derived-generation-support --task-id derived-generation-support",
      "exit_code": 3,
      "expected_exit_code": 3,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    },
    {
      "command": "python (tmp repo) generate_task_sheets with cross-run derived parent evidence-retention-forward-gate + 2 reverse fail-closed plans + validate_task_plan root=None/root provided",
      "exit_code": 0,
      "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
      "evidence_ref": "final-check.md"
    }
  ],
  "assertions": [
    "端到端独立复现：generate_task_sheets 对跨 run 父任务产出 status=pass 的 schema 4 derived 单，derived_from 四字段为 task_id=evidence-retention-forward-gate / commit=19e19fd... / branch=derived-generation-support / parent_task_type=prerequisite，validate_task==[]，chain 七段全 not_applicable",
    "derived_from.commit 与 branch 照抄 plan 声明值，工具未自动填充",
    "反向核验 1：parent_task_id 指向不存在的任务 -> blocked，errors 指明 HEAD 无冻结父单，且未写任何单",
    "反向核验 2：derived_from.parent_task_type 声明值与父单实际 task_type 不等 -> blocked，未写任何单",
    "任务 2.1 裁定：identity.product_head=19e19fd 为最后一个改非证据路径的提交，正确；identity.head=a8dbdb4 不被任何工具校验且仓库先例支持 head≠product_head，判为符合惯例、无需修正",
    "任务 2.2 裁定：result verify 目录形式 fail/exit 2 属 CLI 用法约束（path 为单数 JSON 文件位置参），非工具缺陷；__main__.py 不在 allowed_paths 内，不得改动",
    "任务 3 里程碑：两张现存 derived 单均为手工撰写（一张 schema 2 无 derived_from，一张 schema 4 手写 derived_from）；本任务首次让生成器产出经全部机械校验的 derived 单，消除该缺口",
    "任务 4.1：contract.py 零改动，_validate_derived_from / _requires_full_chain / evidence_floor 三个既有闸门对生成器产出自然放行，无需改动",
    "任务 4.2：create_derived_dispatch 未改动（core.py diff 为空）；派发期与生成器侧的 derived_from 契约形状为同一组四键、同一语义",
    "任务 5：validate_task_plan 不传 root 时跨 run 父任务被拒绝（fail-closed）；传 root 且父单已冻结时接受（errors=[]）",
    "冻结任务单 sha256 未变：16f776df56009bd87635a16eb0ddca04a69719292c01984138a235d8f6268135",
    "非证据改动恰 5 个文件，全部落在 6 项 allowed_paths 内",
    "9 条验收测试逐条实跑 9/9 exit=0",
    "全量测试 Ran 303 tests in 216.818s -> OK（基线 294 + 新增 9）",
    "freshness 在 5bcea4c 上 status=pass / errors=[] / evidence_only=true；生成的 freshness.json 已删除",
    "证据目录仅保留 executor/reviewer/final 三份报告与三份机器结果，无 .log、无 freshness.json"
  ],
  "evidence_refs": ["final-check.md"],
  "unverified": [
    "identity.head 的字面语义存在两种可辩护读法（执行提交 19e19fd vs 结果定稿提交 a8dbdb4），本轮判为低严重度残留歧义、不改动被审产物，留待人类确认",
    "create_derived_dispatch 的运行时派发行为未实际执行（任务单 non_goals 第 3 条禁止改动该函数，仅静态核对契约形状一致）"
  ]
}
```