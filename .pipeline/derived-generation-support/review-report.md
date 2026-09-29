# review-report：derived-generation-support

## 0. 审查身份

- task-id：`derived-generation-support`
- worktree：`D:\Projects\Skills\pipeline\.worktrees\derived-generation-support`
- branch：`derived-generation-support`
- 审查基线：`1e580ec`（冻结任务单）
- 被审 HEAD：`4ab97fc6105f6dab30aa1aee0740d61bd5ac1704`
- product_head：`19e19fdad58130e2338b57eab7d33aaef30e38db`
- role：reviewer，round 1

独立验证，不采信执行者自述。以下每项均实跑取证。

## A. 提交与边界

`git log --oneline -6`：

```
4ab97fc chore(evidence): point executor head at the evidence commit
a8dbdb4 chore(evidence): record executor commit hash
19e19fd feat(planning): emit derived_from and accept cross-run parents
1e580ec Freeze generated task derived-generation-support
```

- `19e19fd` 改动 17 个文件：2 个证据文件 + 12 个 metrics + `pipeline_tools/planning.py`(+136) + `references/task-design.md`(+21) + 3 个测试文件。
- `a8dbdb4` 仅改 `executor-report.md` 与 `executor-result.json`（记录执行提交哈希）。
- `4ab97fc` 仅改 `executor-result.json` 的 `identity.head`，并追加 8 个 metrics。
- `git status --short`：仅 4 个未跟踪 metrics 文件；`--untracked-files=no` 干净。
- `git diff 1e580ec HEAD --name-status`：**非证据改动恰好 5 个文件**，全部落在 6 项 `allowed_paths` 内：
  - `M pipeline_tools/planning.py`
  - `M references/task-design.md`
  - `M tests/test_acceptance_id_and_template_compliance.py`
  - `M tests/test_planning.py`
  - `M tests/test_task_generation.py`
  - 其余全部为 `.pipeline/derived-generation-support/` 与 `.pipeline/metrics/`（证据目录与工作流元数据，允许）。
- **`contract.py` 零改动**：`git diff 1e580ec HEAD --name-only -- pipeline_tools/contract.py` 为空。判断「无需改动」是否成立见 §C.5。
- **metrics 删除数 = 0**：`git diff 1e580ec HEAD --name-status -- .pipeline/metrics/ | grep -c '^D'` → `0`。
- **证据目录无 `freshness.json`**：见 §I。

## B. 任务单字节未变

```
16f776df56009bd87635a16eb0ddca04a69719292c01984138a235d8f6268135  docs/tasks/derived-generation-support.md
16f776df56009bd87635a16eb0ddca04a69719292c01984138a235d8f6268135  (git show 1e580ec:...)
```

与执行者自报一致。冻结任务单未被改动。

## C. 阻塞 1 —— `_task_sheet_text` 输出 `derived_from`

改后 derived 分支全文（`pipeline_tools/planning.py:1821-1854`）：

```python
    if task_type == "derived":
        derived_from = task.get("derived_from")
        derived_from = derived_from if isinstance(derived_from, dict) else {}
        relation_id = (
            derived_from.get("task_id")
            or derived_from.get("parent_task_id")
            or task.get("parent_task_id")
        )
        parent_task_type = next(
            (
                other.get("type")
                for other in plan.get("tasks", [])
                if isinstance(other, dict) and other.get("id") == relation_id
            ),
            None,
        )
        if not isinstance(parent_task_type, str) or not parent_task_type.strip():
            declared = derived_from.get("parent_task_type")
            parent_task_type = declared if isinstance(declared, str) and declared.strip() else None
        if not isinstance(parent_task_type, str) or not parent_task_type.strip():
            if root is not None and isinstance(relation_id, str) and relation_id:
                parent_task_type, _error = _read_parent_task_type(Path(root), relation_id)
        if not isinstance(parent_task_type, str) or not parent_task_type.strip():
            raise ValueError(...)
        contract["derived_from"] = {
            "task_id": relation_id,
            "commit": derived_from.get("commit"),
            "branch": derived_from.get("branch"),
            "parent_task_type": parent_task_type,
        }
```

**四字段来源核验**：

| 字段 | 来源 | 结论 |
|---|---|---|
| `task_id` | `derived_from.task_id` → `derived_from.parent_task_id` → `task.parent_task_id` | 机械读取，非自由填写 |
| `commit` | `derived_from.get("commit")`，**照抄 plan 声明值** | 符合用户裁决 2：工具不自动填充、不对同 run 推导 |
| `branch` | `derived_from.get("branch")`，**照抄 plan 声明值** | 同上 |
| `parent_task_type` | 同 run 取 plan task 的 `type` → plan 声明值 → 跨 run 读 `HEAD:docs/tasks/<parent-id>.md` | 优先级与执行者自述一致；机械读取优先于声明值 |

`git diff 1e580ec HEAD -- pipeline_tools/planning.py` 显示：非 derived 分支**未被触碰**——`task_type == "prerequisite"` 分支、契约字典的 18 个键、`contract.update` 逻辑都原样保留；新增仅为 1 个 `if task_type == "derived"` 块、函数签名加 `root`、调用点传 `root=root`。测试 2 断言非 derived 契约键集合恰为 19 个已知键且不含 `derived_from`，实测通过。

**C.5 `op-guard-derivation-contract` 无需改动是否正确 —— 正确。** 读 `contract.py`：

- `_validate_derived_from`（`contract.py:149-165`）：要求 `task_id`/`commit`/`branch` 非空，`parent_task_type` 非空且属于 `TASK_TYPES`。
- `_requires_full_chain`（`:167-180`）：`derived` 读 `derived_from.parent_task_type`，为 `vertical-feature`/`repair` 时要求完整链路。
- `evidence_floor`（`:132-147`）：`parent_task_type == "vertical-feature"` 抬高证据下限。

生成器一旦产出合法 `derived_from`，这三个闸门自然放行，无需放宽或新增。执行者判定成立。

## D. 阻塞 2 —— `validate_task_plan` 加可选 `root`

**D.1 签名**（`planning.py:1087-1095`）：`root` 是 `*` 之后的**可选关键字参数**，默认 `None`。既有位置参数调用不受影响。**未破坏既有调用**。

**D.2 全部调用点**（`git grep -n "validate_task_plan" -- pipeline_tools/ tests/ scripts/ bin/`）：

| 调用点 | 位置 | 传 `root`? | 是否应传 |
|---|---|---|---|
| 定义 | `planning.py:1087` | — | — |
| `compare_task_plan_contract` | `planning.py:1369` | `root=root` | 应传（该函数有 `root` 参数，需覆盖跨 run 父） |
| `generate_task_sheets` | `planning.py:1891` | `root=root` | 应传 |
| CLI `task-plan-validate` | `__main__.py:981` | 未传 | 可不传（保持可选；CLI 未提供 root 输入） |
| `tests/test_planning.py` | 261/268/278/298/299/362/363/597/599/613/615-617/633/635/637/656/662/667/681/683/685/687/763/779/795 | 多数未传（既有调用，位置参数） | 既有调用保持兼容 |
| `tests/test_planning.py` | 804/805/811/816/824/826/843/849 | `root=root` | 新测试 |
| `tests/test_acceptance_id_and_template_compliance.py:313` | 字符串字面量（文档断言） | — | — |

**执行者只列 4 个，实际生产代码调用点恰为 3 个**（`compare_task_plan_contract`、`generate_task_sheets`、CLI），无遗漏；新测试另加 8 处 `root=`。生产代码无遗漏。

**D.3 `_read_parent_task_type` 全文**（`planning.py:311-334`）：

```python
def _read_parent_task_type(root: Path, parent_id: str) -> tuple[str | None, str | None]:
    relative = f"docs/tasks/{parent_id}.md"
    rc, content, _error = _run_checked(["git", "show", f"HEAD:{relative}"], root)
    if rc != 0:
        return None, f"parent task {parent_id} has no frozen sheet at HEAD:{relative}"
    block = CONTRACT_BLOCK_RE.search(content)
    if block is None:
        return None, f"parent task {parent_id} sheet has no readable pipeline-contract block"
    try:
        contract = json.loads(block.group(1))
    except json.JSONDecodeError:
        return None, f"parent task {parent_id} sheet contract is not valid JSON"
    if not isinstance(contract, dict):
        return None, f"parent task {parent_id} sheet contract is not an object"
    task_type = contract.get("task_type")
    if not isinstance(task_type, str) or not task_type.strip():
        return None, f"parent task {parent_id} sheet declares no task_type"
    return task_type.strip(), None
```

**D.4 实际 git 命令**：`["git", "show", f"HEAD:docs/tasks/{parent_id}.md"]` —— **只接受已冻结（已提交到 HEAD）的父单**。未提交的父单读不到。E2E 中 ghost 父任务返回 `parent task ghost-parent has no frozen sheet at HEAD:docs/tasks/ghost-parent.md`。

**D.5 `_cross_run_parent_errors` 全文**（`planning.py:337-363`）：`root is None` → 返回错误（fail-closed）；`_read_parent_task_type` 报错 → 返回错误；声明值与观测值不等 → 返回错误。

**D.6 `derived_from.task_id == parent_task_id` 一致性校验未被放宽**（`planning.py:1295-1299`）：

```python
            if isinstance(derived_from, dict):
                relation_id = derived_from.get("task_id") or derived_from.get("parent_task_id")
                if relation_id != parent:
                    errors.append(f"derived task {identifier} has inconsistent derived_from")
```

原样保留，diff 中该段无删改。

**D.7 `root` 缺失时跨 run 父任务 fail-closed**：`_cross_run_parent_errors(root=None, ...)` 返回 `... is outside this run and root is unavailable to prove it exists`。测试 5 断言无 `root` 时非空错误、有 `root` 时 `[]`，实测通过。E2E ghost 反向核验也 fail-closed。

**D.8 同 run 声明值校验**（`planning.py:1268-1294`）：父在 `tasks` 内时，若声明了 `parent_task_type` 且与 plan 父 task 的 `type` 不等 → 报错。未放宽。

## E. 9 条新测试

**E.1 定位**：全部在契约指定类中——`TaskGenerationTests`（`tests/test_task_generation.py`）、`PlanningTests`（`tests/test_planning.py`）、`AcceptanceIdAndTemplateComplianceTests`（`tests/test_acceptance_id_and_template_compliance.py`）。方法体已逐条阅读。

**E.2 在 HEAD 实跑 9 条**：`Ran 9 tests in 7.615s`，`OK`，**exit 0**。9 条全绿。

**E.3 独立复现红绿分布** —— 用 `git archive 1e580ec` 解到系统 temp 得基线树，从 HEAD 取那 3 个测试文件覆盖过去（新测试 + 旧实现）：

```
Ran 9 tests in 7.473s
FAILED (failures=3, errors=4)
BASELINE_TREE_EXIT=1
```

实际分布 = **7 红 2 绿**，与执行者自报一致：

| # | 测试 | 修复前 |
|---|---|---|
| 1 | `test_generator_emits_derived_from_for_derived_task` | FAIL：`'blocked' != 'pass'`，错误 `derived task derived-child has invalid parent_task_id` |
| 2 | `test_generator_output_for_non_derived_task_is_unchanged` | 绿（回归保护） |
| 3 | `test_generate_task_sheets_emits_derived_sheet_for_same_run_parent` | FAIL：`'blocked' != 'pass'`，错误 `child-task.md: derived task requires a derived_from object` |
| 4 | `test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists` | 绿（回归保护） |
| 5 | `test_task_plan_accepts_derived_parent_outside_the_run` | ERROR：`TypeError: validate_task_plan() got an unexpected keyword argument 'root'` |
| 6 | `test_task_plan_rejects_derived_parent_that_cannot_be_found` | ERROR：同上 `TypeError` |
| 7 | `test_task_plan_rejects_planner_declared_parent_type_mismatch` | ERROR：同上 `TypeError` |
| 8 | `test_task_plan_accepts_same_run_derived_parent` | ERROR：同上 `TypeError` |
| 9 | `test_references_task_design_documents_derived_generation_support` | FAIL：`'两条写入路径' not found` |

**E.4 第 8 条 error 解释成立**：`test_task_plan_accepts_same_run_derived_parent` 方法体（`tests/test_planning.py:843`）首行即 `self.assertEqual(validate_task_plan(plan, root=root), [])`，确实用了 `root=` 关键字参数。基线实跑给出的 traceback 就是 `TypeError: validate_task_plan() got an unexpected keyword argument 'root'`。**它是 error 而非「本来就绿」**，执行者解释成立。

**E.5 既有测试未被削弱**：`git diff 1e580ec HEAD -- tests/` 的删除行数为 **0**（`grep -c '^-[^-]'` → 0）；`--stat` 为 `3 files changed, 289 insertions(+)`，**纯新增，无删改既有断言**。既有 derived 相关测试（如 `test_task_plan_rejects_derived_parent_outside_run`）原样保留。

## F. 端到端验证（独立复现）

在系统 temp（`mktemp -d`，不落仓库）建仓，复制真实的已冻结父单 `docs/tasks/evidence-retention-forward-gate.md`（`task_type=prerequisite`，schema 4）并提交，写最小 project/requirement/task-plan 输入，task-plan 含一个跨 run `derived` 任务，调用 `generate_task_sheets`：

```
STATUS: pass
ERRORS: []
TASK_IDS: ['derived-demo']
DERIVED_FROM: {"task_id": "evidence-retention-forward-gate", "commit": "7777...7777", "branch": "main", "parent_task_type": "prerequisite"}
TASK_TYPE: derived SCHEMA: 4
VALIDATE_TASK: []
```

- `derived_from` 四字段齐备；`commit`/`branch` 是规划者声明值照抄（`7`×40、`main`）；`parent_task_type` = 父单 `task_type` = `prerequisite`（机械读取自 `HEAD:docs/tasks/evidence-retention-forward-gate.md`）。
- 生成的单 `validate_task` 返回 `[]`。
- **反向核验**：构造跨 run 父任务 `ghost-parent`（HEAD 无该单），返回

```
GHOST_STATUS: blocked
GHOST_ERRORS: ["derived task derived-ghost: parent task ghost-parent has no frozen sheet at HEAD:docs/tasks/ghost-parent.md"]
GHOST_SHEET_EXISTS: False
```

**fail-closed 成立，不写任何单**。本任务核心目标达成。

## G. 全量测试

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests
Ran 303 tests in 222.258s
OK
```

准确数字：**303 项通过**，exit 0，耗时 222.3s。基线 294 + 新增 9 = 303，与执行者自报一致。

## H. `freshness` 与 `result verify`

**freshness**（对 executor 那份）：

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/derived-generation-support --result .pipeline/derived-generation-support/executor-result.json
status = pass
errors = []
observed.evidence_only = True
```

符合预期。跑完已删除其生成的 `freshness.json`（不在保留集内）。

**result verify 两种形式**（该命令实际需要 `--task-id` 与 `--role`）：

- 传**文件** + `--task-id derived-generation-support --role executor`：`status=pass`，`errors=[]`，exit 0。
- 传**目录** + 同上参数：`status=fail`，`errors=["result is missing or invalid JSON"]`，exit 2。

执行者「传目录 FAIL、传文件 PASS」的说法**成立**。这是 CLI 用法差异（`path` 被当作 JSON 文件读取，目录不可解析），**属工具用法约束而非产品缺陷**；本任务 `allowed_paths` 未包含 `__main__.py`，执行者无权修改，处理正确。

## I. 证据合规性 + gate 条数

**I.1 证据目录内容**：`executor-report.md`（14172 B）、`executor-result.json`（2136 B），无其他文件。
**I.2** `git ls-files .pipeline/derived-generation-support/` → 恰为这两个文件。**无 `.log`、无 `freshness.json`**。
**I.3 `executor-report.md`**：`grep -c '^```pipeline-evidence'` → **1**（` ```json ` 计数为 0）；块在文件末尾；JSON 合法。字段核验：`schema=1`、`task_id`、`worktree`、`branch`、`role=executor`、`round=1`、`status="PASS"`（**大写**）、`commands[]` 每条含非空 `command`、整数 `exit_code`、`evidence_ref`；**全部 `exit_code` 为 0**，无非零未声明项。`assertions` 非空、`evidence_refs` 非空。
**I.4 `executor-result.json`**：JSON 合法；`status="pass"`（**小写**）；`identity = {product_head: 19e19fd..., head: a8dbdb4}`；`acceptance` 9 条，`status` 全为小写 `pass`，均有 `exit_code`/`evidence_refs`；`unverified` 3 条。
**I.5 执行者是否如实报告失败/未完成**：**是**。明确写出第 2、4 条修复前即绿（回归保护）、第 8 条修复前为 error、`contract.py` 未改、reviewer/final 证据缺失。未见少报。

**注（非缺陷，供终审知晓）**：`executor-result.json` 的 `identity.head` 在三个提交间演进——`19e19fd` 时自指 `head=19e19fd`，`4ab97fc` 改为 `head=a8dbdb4`，而 `product_head` 始终 `19e19fd`。最终 `head=a8dbdb4` 指向证据提交而非 HEAD `4ab97fc`。这与「product_head 为产品提交、head 为执行提交」的既定约定一致（证据提交不计入产品头），判定为可接受。

**gate errors 条数核对**：

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json gate pre-merge .pipeline/derived-generation-support --task-id derived-generation-support
status = blocked
errors = ["missing review-report.md", "missing final-check.md", "missing reviewer-result.json", "missing final-result.json"]
exit_code = 3
```

**恰好 4 条**，与预期一致（缺 review/final 四件）。执行者如实报告。

## K. 文档改动

`git diff 1e580ec HEAD -- references/task-design.md`：新增 21 行（纯新增，无删改）。新增小节「`derived_from` 的两条写入路径与机械核验」写明：

- **两条写入路径**：路径一生成器（`generate_task_sheets` / `_task_sheet_text`）；路径二派发期 `create_derived_dispatch`。
- **生成器侧**：`parent_task_type` 按父任务位置机械读取（同 run 取 plan task 的 `type`，跨 run 读 `HEAD:docs/tasks/<parent-id>.md`）；`commit`/`branch` 由规划者声明、**工具照抄**。
- **规划期核验规则**（`validate_task_plan`，可选 `root`）：同 run 父须在 `tasks` 内且声明值等于父 `type`；跨 run 须 `root` 可用且父单已冻结；**声明值必须等于机械读取值**，否则 fail-closed。
- **生成器侧 fail-closed**：父单已存在则整次生成 fail-closed，不留 `*.planning-tmp`。

**未留下与实现矛盾的旧描述**：原「`derived_from.parent_task_type` 是唯一开关…必须原样写入父契约 `task_type`」表述与新增内容一致，未见冲突。测试 9 的文档断言（`两条写入路径`/`工具照抄`/`同一次 planning run`/`HEAD` 等）实测通过。

## 与执行者自述不符之处

**未发现实质性不符。** 逐项抽验（提交边界、`contract.py` 零改动、`root` 调用点、红绿分布 7:2、第 8 条 error、全量 303、freshness pass、result verify 两种形式、gate 4 条）均与自述一致。执行者在「诚实报告」小节主动披露了回归保护测试与未完成项，未出现前几轮的少报模式。

## 总体结论

**ACCEPT**。两条阻塞均已修复且有独立复现证据：生成器为 derived 任务输出合法 `derived_from` 四字段；`validate_task_plan` 接受可选的 `root` 并在跨 run 父任务上 fail-closed；同 run 与跨 run 均覆盖；`parent_task_type` 按位置机械读取且声明值必须相等。`contract.py` 零改动判定正确。全量 303 项通过。端到端与反向核验均成立。文档与实现一致。

## 无法确定项 / 需终审裁决项

- `executor-result.json` 的 `identity.head=a8dbdb4` 指向证据提交而非 worktree HEAD `4ab97fc`；若项目约定要求 `head` 等于被审 HEAD，需终审明确。按「head=执行提交」惯例判定可接受。
- `result verify` 目录形式 FAIL 属 CLI 用法而非产品缺陷；是否要在后续任务中改进 CLI（接受目录）由主代理裁决。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "derived-generation-support",
  "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\derived-generation-support",
  "branch": "derived-generation-support",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "git diff 1e580ec HEAD --name-status",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "sha256sum docs/tasks/derived-generation-support.md && git show 1e580ec:docs/tasks/derived-generation-support.md | sha256sum",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_task_generation.TaskGenerationTests.test_generator_emits_derived_from_for_derived_task tests.test_task_generation.TaskGenerationTests.test_generator_output_for_non_derived_task_is_unchanged tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_emits_derived_sheet_for_same_run_parent tests.test_task_generation.TaskGenerationTests.test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists tests.test_planning.PlanningTests.test_task_plan_accepts_derived_parent_outside_the_run tests.test_planning.PlanningTests.test_task_plan_rejects_derived_parent_that_cannot_be_found tests.test_planning.PlanningTests.test_task_plan_rejects_planner_declared_parent_type_mismatch tests.test_planning.PlanningTests.test_task_plan_accepts_same_run_derived_parent tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_derived_generation_support",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "baseline tree (git archive 1e580ec) + HEAD test files: python -m unittest <9 tests>",
      "exit_code": 1,
      "expected_exit_code": 1,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "system-temp repo E2E: generate_task_sheets with cross-run derived parent (evidence-retention-forward-gate)",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "system-temp repo E2E reverse: generate_task_sheets with ghost cross-run parent",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json freshness . .pipeline/derived-generation-support --result .pipeline/derived-generation-support/executor-result.json",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/derived-generation-support/executor-result.json --task-id derived-generation-support --role executor",
      "exit_code": 0,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json result verify .pipeline/derived-generation-support --task-id derived-generation-support --role executor",
      "exit_code": 2,
      "expected_exit_code": 2,
      "evidence_ref": "review-report.md"
    },
    {
      "command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools --format json gate pre-merge .pipeline/derived-generation-support --task-id derived-generation-support",
      "exit_code": 3,
      "expected_exit_code": 3,
      "evidence_ref": "review-report.md"
    }
  ],
  "assertions": [
    "非证据改动恰 5 个文件，全部落在 6 项 allowed_paths 内；contract.py 零改动且判定正确",
    "冻结任务单 sha256 未变：16f776df56009bd87635a16eb0ddca04a69719292c01984138a235d8f6268135",
    "_task_sheet_text 的 derived 分支输出 derived_from 四字段；commit/branch 照抄 plan 声明值；parent_task_type 按位置机械读取（同 run 取 plan type，跨 run 读 HEAD 父单）",
    "validate_task_plan 的 root 为可选关键字参数，既有位置调用兼容；生产代码 3 个调用点无遗漏",
    "_read_parent_task_type 用 git show HEAD:docs/tasks/<parent-id>.md 只接受已冻结父单；root 缺失时跨 run 父任务 fail-closed",
    "derived_from.task_id == parent_task_id 一致性校验未被放宽",
    "9 条新测试在 HEAD 全绿（Ran 9 tests OK）；基线树独立复现为 7 红 2 绿；第 8 条修复前为 TypeError error",
    "既有测试无删改（tests/ diff 纯新增 289 行）",
    "端到端：跨 run derived 生成 status=pass、derived_from 四字段正确、validate_task==[]；反向 ghost 父任务 blocked 且不写单",
    "全量测试 Ran 303 tests OK（基线 294 + 新增 9）",
    "freshness status=pass errors=[] evidence_only=True；result verify 文件形式 pass、目录形式 fail",
    "证据目录仅 executor-report.md 与 executor-result.json，无 .log 无 freshness.json；报告恰含 1 个 pipeline-evidence 块",
    "gate pre-merge 恰 4 条 errors（缺 review/final 四件），与预期一致"
  ],
  "evidence_refs": ["review-report.md"],
  "unverified": [
    "派发期 create_derived_dispatch 的运行时行为未执行（任务单 non_goals 第 3 条禁止改动该函数，仅静态阅读确认契约形状一致）",
    "executor-result.json 的 identity.head 指向证据提交 a8dbdb4 而非 HEAD 4ab97fc，是否满足项目约定需终审确认"
  ],
  "identity": {
    "product_head": "19e19fdad58130e2338b57eab7d33aaef30e38db"
  },
  "recommendation": "ready_for_final"
}
```