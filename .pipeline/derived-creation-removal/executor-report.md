# executor-report：derived-creation-removal（round 1）

## 任务身份

- task-id：`derived-creation-removal`
- task-type：`repair`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal`
- branch：`derived-creation-removal`
- baseline HEAD（round 起点）：`168da7c4e6f488008cf3bfa7b77c12a334b9950a`
- role：executor，round **1**
- sheet_revision：**1**
- sheet_sha256：`e806e87cd4618907407986f6bf279f4936d78223f1a44cc2a7d322343a2fe4e4`

## 结论：本轮回合被决策点 4 阻断（BLOCKED），未产生任何实现改动

**决策点 4：实现必须修改契约未列出的文件。** 契约要求移除 `pipeline_tools/core.py` 的派生创建函数 `create_derived_dispatch`；但该函数被 `tests/test_security_repairs.py` 在**模块顶层 import**（第 6 行）并在两个用例中调用（第 30 行、第 67 行）。`tests/test_security_repairs.py` **不在**契约 `allowed_paths` 内（`allowed_paths` 只列了 `tests/test_planning.py`、`tests/test_task_generation.py`、`tests/test_derived_task_dispatch_recovery.py`、`tests/test_cli.py`、`tests/test_acceptance_id_and_template_compliance.py`），也不在 `forbidden_paths` 内。

要真正移除创建函数，就必须同时删掉该文件里只覆盖创建路径的用例并去掉 import；否则整份测试模块 collection 失败、全量测试转红。按 §7「若必须动未列文件，停下报 BLOCKED（决策点 4）」与 §12「立即停下、保留现场」，本轮**未改动任何文件**（含 `core.py`），停下并上报，`core.py` 逐字节保持 `168da7c4...` 的状态。

### 阻断的实测证据（不是推断）

实验：临时从 `pipeline_tools/core.py` 删除 `create_derived_dispatch` 定义（仅允许文件内的临时实验），只跑 `tests/test_security_repairs.py`，随后按字节还原。

命令（cwd = worktree 根）：

```
python -m pytest -q tests/test_security_repairs.py      # 基线
# <临时删除 core.py 的 create_derived_dispatch 定义>
python -m pytest -q tests/test_security_repairs.py      # 实验
```

结果：

| 阶段 | 退出码 | 观察 |
|---|---|---|
| 基线 | 0 | `8 passed in 0.96s` |
| 删除函数后 | **2** | `ERROR collecting tests/test_security_repairs.py` → `ImportError: cannot import name 'create_derived_dispatch' from 'pipeline_tools.core'` |
| 还原后 | — | `pipeline_tools/core.py` 的 sha256 回到 `6eab2d7dd09d7d9ac2aab8eaa6dc1d7f34220dddc1a2c6c14c9bbd714d628b73`（实验前值一致）；`git status --short` 无输出 |

`tests/test_security_repairs.py` 中被波及的两个用例：

- `test_unsafe_derived_identifier_is_rejected`（第 27–32 行）：断言 `create_derived_dispatch(root, ..., "../escape", "child")` 返回 `blocked` 且不产生 `.worktrees`。
- `test_full_security_regression_suite`（第 64–67 行）：直接调用上面这个用例。

两者都**只覆盖派生创建路径**，与 `tests/test_derived_task_dispatch_recovery.py` 里待删的 7 个用例同性质。

## 环境检查（逐项，全部通过）

| # | 检查 | 命令（cwd = worktree 根） | 结果 |
|---|---|---|---|
| 1 | worktree 根 | `git rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal` ✓ |
| 2 | 当前分支 | `git branch --show-current` | `derived-creation-removal` ✓ |
| 3 | 任务单校验 | `python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md` | 退出码 0，`PASS` ✓ |
| 4 | pytest 可用 | `python -m pytest --version` | 退出码 0，`pytest 9.1.1` ✓ |
| 5 | 证据目录可写 | `mkdir -p .pipeline/derived-creation-removal` + 探针写入/删除 | 可写 ✓ |
| 6 | 无额外 worktree / 未动主工作树 | 全程只读 `/` 本 worktree 内文件 | ✓ |

- baseline HEAD 与简报一致：`git rev-parse HEAD` = `168da7c4e6f488008cf3bfa7b77c12a334b9950a` ✓
- 基线全量测试：`python -m pytest -q`（cwd = worktree 根）→ 退出码 0，**401 passed, 28 subtests passed**（与简报基线一致）。

## 若不阻断，计划中的移除/保留清单（本轮未执行）

### 要移除（创建路径）

| 文件 | 目标 | 位置 |
|---|---|---|
| `pipeline_tools/core.py` | `create_derived_dispatch` 函数及其内部辅助（`blocked`/`rollback` 闭包与其调用的 `git worktree add`/`branch -D` 逻辑） | 定义 `core.py:1566–1735` |
| `pipeline_tools/__main__.py` | `dispatch derived-create` 子命令注册 | `__main__.py:405–413` |
| `pipeline_tools/__main__.py` | 分派分支 | `__main__.py:1347–1357` |
| `pipeline_tools/__main__.py` | 顶层导入 `create_derived_dispatch` | `__main__.py:66` |
| `pipeline_tools/planning.py` | 本文件的 `TASK_TYPES` 去掉 `derived`（新计划 fail-closed 拒绝） | `planning.py:55` |
| `pipeline_tools/planning.py` | 计划校验里的 derived 分支（同 run / 跨 run 父子核验） | `planning.py:1396–1435` |
| `pipeline_tools/planning.py` | 生成期产出派生任务单的分支 | `planning.py:2026–2058` |
| `pipeline_tools/planning.py` | 随之失去调用方的两个内部辅助 `_read_parent_task_type`、`_cross_run_parent_errors` | `planning.py:319–374` |
| `tests/test_derived_task_dispatch_recovery.py` | 8 个用例中的 7 个纯创建路径用例 + 1 个依赖创建路径的用例（删除理由见下） | 全文件 |

### 必须保住（历史读取）

- `pipeline_tools/contract.py` 一字不改：`TASK_TYPES` 仍含 `derived`；`_validate_derived_from`（`:149–164`）、`_requires_full_chain`（`:167–180`）、`evidence_floor` 的 `parent_task_type` 分支（`:132–146`）原样保留 → 含 `derived_from` 的历史契约仍通过 `task validate`，父类型 `vertical-feature`/`repair` 的链路收紧与证据下限不变。
- metrics 侧同名物一律不碰：`__main__.py:133` 的 `--no-derived`、`__main__.py:306` 的 `--confidence derived`、`__main__.py:973` 的 `"confidence": "derived"`、`core.py:881/889/975` 的 `include_derived`。

### 计划中要删除的用例（逐条理由）

`tests/test_derived_task_dispatch_recovery.py`（文件在 `allowed_paths` 内）——全部 8 个用例都调用 `create_derived_dispatch`（该文件的 import 在第 7 行），即**全部只覆盖创建路径**：

| 用例 | 删除理由 |
|---|---|
| `test_derived_task_binds_explicit_parent_commit_and_is_independent` | 只断言创建出的子 worktree/分支/子任务单/`derived_from`，创建路径移除后无被测对象 |
| `test_child_sheet_is_committed_in_child_worktree_at_return` | 只断言创建期提交子任务单的副作用 |
| `test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history` | 只覆盖 `continuation=True` 创建与重放（该参数随创建函数一起消失） |
| `test_cli_derived_create_returns_identity_and_blocks_replay` | 只覆盖 `dispatch derived-create` 的创建与重放；验收测试 4 会以「不再暴露」替换它 |
| `test_child_creation_failure_rolls_back_worktree_and_branch` | 只覆盖创建失败回滚 |
| `test_invalid_child_sheet_is_rejected_and_rolled_back` | 只覆盖创建期非法标识符回滚 |
| `test_worktree_add_failure_deletes_orphan_child_branch` | 只覆盖 `worktree add` 失败时删孤儿分支 |
| `test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume` | 该用例以「父提交漂移被拒」开头，随后**继续调用创建函数**创建 `child-task-2`（第 80–83 行）来观察父证据保留，仍依赖创建路径，故一并删除；需新增验收测试 3 的历史兼容用例补齐其「历史可读」意图 |

计划新增：`DerivedTaskDispatchRecoveryTests.test_historical_derived_contracts_still_validate`（验收测试 3），用 `contract` 侧确定性输入直接断言：含 `derived_from.parent_task_type` 的历史形态契约通过 `validate_task`；父类型 `vertical-feature`/`repair` 时链路收紧（`_requires_full_chain` → 七个段必须真实引用）与证据下限加成仍生效；父类型 `prerequisite` 时允许结构化豁免与低证据。**不依赖创建路径。**

### 计划中被同时阻断的同性质文件

`tests/test_security_repairs.py`（**不在 `allowed_paths`**）：需删除 `test_unsafe_derived_identifier_is_rejected` 并在 `test_full_security_regression_suite` 中去掉对它的调用、移除第 6 行的 import。理由与上表相同（只覆盖创建路径）。**这是本轮阻断的直接原因。**

### §6 文档断言改写计划（未执行）

`references/task-design.md` 的派生章节改写为「历史读取兼容 + 新任务用 `dependencies` 表达接替」后，`tests/test_acceptance_id_and_template_compliance.py:379` 的 `test_references_task_design_documents_derived_generation_support` 必须同步改写。计划改写的 needle 与理由：

| 现有 needle | 处理 | 理由 |
|---|---|---|
| `两条写入路径` | 删 | 写入路径只剩历史读取，不再有「规划期生成器 / 派发期创建」两条 |
| `_task_sheet_text`、`create_derived_dispatch` | 删 | 生成分支与创建函数都已移除，不再是当前状态模型 |
| `工具照抄`、`同一次 planning run` | 删 | 描述的是生成器产派生单的行为，已不存在 |
| `derived_from`、`parent_task_type`、`docs/tasks/<parent-id>.md`、`validate_task_plan`、`机械读取`、`fail-closed`、`root`、`commit`、`branch`、`HEAD` | 保留 | 这些是**历史读取**与契约校验仍在用的机制（`contract.py` 未变） |
| 新增断言 | — | 文档必须写明：新任务不再派生、接替关系用 `dependencies`、历史 `derived` 仅作读取兼容 |

必须同步保留的既有约束（不得削弱）：`tests/test_acceptance_id_and_template_compliance.py:455` 的 `test_references_task_design_contains_no_replacement_character` 要求 `task-design.md` 仍含 `_requires_full_chain` 与 `读取 \`derived_from.parent_task_type\``；line 324 的 `test_lifecycle_and_evidence_documentation_matches_current_contract`（= 验收测试 5）要求 README/SKILL/migration 等仍含 `冻结`/`修订`/`身份字段`/`lifecycle`/`.pipeline/<task-id>` 及 `v0.13.0 → v0.14.0`。

## 验收测试（本轮实跑，均为「未实现」观察，不构成验收满足）

| ID | 命令（cwd = worktree 根） | 退出码 | 观察 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type` | 5 | 无匹配用例（未实现） |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived` | 5 | 无匹配用例（未实现） |
| acceptance-test-3 | `python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate` | 5 | 无匹配用例（未实现） |
| acceptance-test-4 | `python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed` | 5 | 无匹配用例（未实现） |
| acceptance-test-5 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | 既有用例 `test_lifecycle_and_evidence_documentation_matches_current_contract`（第 324 行）通过；它不检查 `references/task-design.md` 的派生措辞，故本轮未做文档改写下仍绿 |

> 注：pytest 退出码 5 = 没有收集到用例。上述 1–4 条目前因测试方法尚不存在而返回 5；本轮未实现，故不作为验收证据。

## 未运行的验证（见 unverified）

- 反向验证（临时去掉「新计划拒绝 derived」判据、证明验收测试 1 承重）：**未运行**，因为对应实现与用例本轮均未落地。
- 全量测试在「移除后」的通过数：**未运行**（移除未执行）。基线 401 passed, 28 subtests passed，与简报一致。
- `scope check`：本轮无改动，见下「其它检查」。

## 其它检查（cwd = worktree 根）

- `python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md` → 退出码 0。
- `python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor` → 退出码 0。
- `python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed <契约 allowed_paths> --forbidden <契约 forbidden_paths>` → 退出码 0（本轮唯一改动是 `.pipeline/derived-creation-removal/**`，在允许范围内）。
- `git diff --check` → 退出码 0。
- 契约未改：`docs/tasks/derived-creation-removal.md` 未被本轮改动，sha256 = `e806e87cd4618907407986f6bf279f4936d78223f1a44cc2a7d322343a2fe4e4`。
- 未新建 worktree、未动主工作树、未改历史任务单/历史证据与其它任务证据目录（`git status` 只见本任务证据目录）。

## 决策点核查

1. 让新计划拒绝 `derived` 会同时使历史计划/历史契约被拒 —— **未触发**。历史契约走 `contract.py`（不改），仍通过；仓库内无需要继续校验的历史 planning 计划文档（`.pipeline/**` 只有报告与结果，没有 plan 文档）。
2. 必须修改 `pipeline_tools/contract.py` 才能让新计划拒绝 `derived` —— **未触发**。`planning.py:55` 有本文件私有的 `TASK_TYPES`，去掉 `derived` 即可 fail-closed，无需动 `contract.py`。
3. 文档改写会撞上既有断言而必须削弱它 —— **未触发**（本轮未改文档；§6 的改写计划已确认可在不削弱既有断言的前提下完成）。
4. 实现必须修改契约未列出的文件 —— **触发**。即 `tests/test_security_repairs.py`，见上。

## 给主代理的解除阻断选项

- **选项 A（推荐）**：`task amend docs/tasks/derived-creation-removal.md` 把 `tests/test_security_repairs.py` 加入 `allowed_paths`（并说明理由：该文件的派生用例只覆盖创建路径），然后重派 round 2。round 2 可一次性完成全部移除与改写。
- **选项 B**：授权把 `create_derived_dispatch` 保留为 fail-closed 的弃用桩（恒返回 `blocked: derived task creation is no longer supported`，不再建 worktree、不再复制契约）。这样不改未列文件、全量测试保持绿、5 条验收可达成；但函数符号仍在，与 §4「移除派生创建函数」的字面要求不完全一致，需主代理明确接受。

```pipeline-evidence
{"schema": 2, "task_id": "derived-creation-removal", "worktree": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "branch": "derived-creation-removal", "role": "executor", "round": 1, "status": "BLOCKED", "head": "168da7c4e6f488008cf3bfa7b77c12a334b9950a", "sheet_revision": 1, "sheet_sha256": "e806e87cd4618907407986f6bf279f4936d78223f1a44cc2a7d322343a2fe4e4", "observed_at_commit": "168da7c4e6f488008cf3bfa7b77c12a334b9950a", "generated_at": "2026-10-09T03:30:06+00:00", "commands": [{"command": "git rev-parse --show-toplevel", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git branch --show-current", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git rev-parse HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest --version", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 5, "expected_exit_code": 5, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 5, "expected_exit_code": 5, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 5, "expected_exit_code": 5, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 5, "expected_exit_code": 5, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_security_repairs.py", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_security_repairs.py  # after temporarily removing create_derived_dispatch from pipeline_tools/core.py, then restored byte-identically", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 2, "expected_exit_code": 2, "evidence_ref": "executor-report.md"}, {"command": "git status --short  # clean after restoring pipeline_tools/core.py", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed pipeline_tools/core.py pipeline_tools/planning.py pipeline_tools/__main__.py tests/test_planning.py tests/test_task_generation.py tests/test_derived_task_dispatch_recovery.py tests/test_cli.py tests/test_acceptance_id_and_template_compliance.py SKILL.md README.md references/task-design.md references/compat-and-migration.md docs/tasks/derived-creation-removal.md .pipeline/derived-creation-removal/** --forbidden docs/goal.md pipeline_tools/contract.py .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/finalization-report-reader/** .pipeline/finalization-hygiene/** .env credentials/**", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}], "assertions": ["environment checks 1-6 all pass: worktree root, branch, task validate exit 0, pytest 9.1.1, evidence dir writable, no extra worktree and the main worktree untouched", "removing create_derived_dispatch from pipeline_tools/core.py makes tests/test_security_repairs.py fail collection with ImportError; that file is neither in the contract allowed_paths nor forbidden_paths", "the experiment was reverted and pipeline_tools/core.py is byte-identical (sha256 6eab2d7dd09d7d9ac2aab8eaa6dc1d7f34220dddc1a2c6c14c9bbd714d628b73) with a clean git status", "decision point 4 is triggered: fully removing the derived creation path requires modifying tests/test_security_repairs.py, which the frozen contract does not allow", "no implementation, test, or documentation file was changed this round; the only working-tree change is this task's own evidence directory", "the baseline full suite is green at 401 passed, 28 subtests passed, so the removal - not the starting state - is what breaks the security test", "the plan confirms decisions 1-3 are not triggered: historical contracts still validate via the unchanged contract.py, planning.py has its own TASK_TYPES so contract.py need not change, and the task-design rewrite can keep every existing assertion intact"], "evidence_refs": ["executor-report.md", "executor-result.json"], "unverified": ["the derived creation path was not removed and tests/test_security_repairs.py was not touched, because doing so requires an allowed file the contract does not grant (decision point 4)", "acceptance tests 1-4 were not implemented, so their commands currently exit 5 (no tests collected); acceptance test 5 currently passes but is an existing unrelated test that does not check the derived wording in references/task-design.md", "the reverse validation (temporarily dropping the reject-derived rule and showing acceptance test 1 fails) was not run because neither the implementation nor the test exists yet", "the post-removal full-suite count was not measured; the baseline is 401 passed, 28 subtests passed", "no documentation, CLI, planning, or core change was made, so acceptance test 5's intended meaning (docs record the new rules) is not yet satisfied"]}
```
