# executor-report：derived-creation-removal（round 2）

## 任务身份

- task-id：`derived-creation-removal`
- task-type：`repair`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal`
- branch：`derived-creation-removal`
- 分支尖端（本轮起点）：`aceeae208d4430583b2c7fd1530041e6fe4c1a9c`
- 实现提交（本轮）：`b4ca1179f30b054493e0c5227bcb86f3f6602e6b`
- role：executor，round **2**
- sheet_revision：**2**
- sheet_sha256：`ad9dfd972ccd97904e9b3c031980b017e6121018f26a74e6a476ae63b36de6fc`

round 1 在决策点 4 停下（移除创建函数会撞上不在 `allowed_paths` 的 `tests/test_security_repairs.py`）；主代理随后 `task amend` 登记 revision 2，把该文件加入 `allowed_paths` 并新增「允许的测试改写（已授权）」一节。本轮在 revision 2 下执行全部移除与改写。

## 移除清单（创建路径）

| 文件 | 移除内容 | 位置（改动前） |
|---|---|---|
| `pipeline_tools/core.py` | `create_derived_dispatch` 函数及其内部 `blocked`/`rollback` 辅助、`worktree add -b` / `branch -D` 回滚逻辑 | `:1566–1737`（含函数后两个空行，共 172 行） |
| `pipeline_tools/__main__.py` | 顶层导入 `create_derived_dispatch` | `:66` |
| `pipeline_tools/__main__.py` | `dispatch derived-create` 子命令注册（8 个参数） | `:405–413` |
| `pipeline_tools/__main__.py` | `dispatch derived-create` 分派分支 | `:1347–1357` |
| `pipeline_tools/planning.py` | 本文件私有 `TASK_TYPES` 去掉 `derived` | `:55` |
| `pipeline_tools/planning.py` | 计划校验的 derived 分支（同 run / 跨 run 父核验）→ 改为**无条件拒绝派生形态** | `:1396–1435` |
| `pipeline_tools/planning.py` | `validate_task_plan` 的 `task_type == "derived"` 显式 fail-closed 理由 | 新增于 `:1250–1256` |
| `pipeline_tools/planning.py` | 生成期产出派生任务单的分支 | `:1941–1973` |
| `pipeline_tools/planning.py` | 失去调用方的内部辅助 `_read_parent_task_type`、`_cross_run_parent_errors` | `:319–374` |
| `pipeline_tools/planning.py` | 失去调用方的模块常量 `CONTRACT_BLOCK_RE` | `:61` |
| `pipeline_tools/planning.py` | `validate_task_plan` docstring 中的英文「derivation」说明 | `:1148–1153` |

新增的 fail-closed 判据（两条，均给出可读原因）：

- `task <id> declares the derived type; new tasks are never derived - start from the current head and express succession with dependencies`（`task_type == "derived"`）
- `task <id> declares a derived-form plan (parent_task_id/derived_from); new tasks are never derived - ...`（任何任务声明 `parent_task_id`/`derived_from`）

## 保留清单（历史读取，未改动）

- `pipeline_tools/contract.py` **一字未改**（`git diff` 为空）：`TASK_TYPES` 仍含 `derived`；`_validate_derived_from`（`:149–164`）、`_requires_full_chain`（`:167–180`）、`evidence_floor` 的 `parent_task_type` 分支（`:132–146`）原样保留。
- `pipeline_tools/core.py` 保留历史读取路径：`CONTRACT_IDENTITY_FIELDS` 仍含 `derived_from`（`:1954`）；`freeze_check` 对 `task_type == "derived"` 历史契约的 `derived_from.parent_task_type` 复核（`:2747–2762`）原样保留。
- metrics 侧同名物一律未碰：`__main__.py:132` 的 `--no-derived`、`__main__.py:305` 的 `--confidence derived`、`__main__.py:963` 的 `"confidence": "derived"`、`core.py` 的 `include_derived`（`:881/889/975`）、`CONFIDENCES`（`:43`）。
- `docs/goal.md`、任何历史任务单与历史证据、其它任务证据目录：`git diff` 为空。

## 删除/改写用例逐条理由

### `tests/test_derived_task_dispatch_recovery.py`（旧 8 → 新 1）

旧文件的模块级 import 就是 `create_derived_dispatch`，**8 个用例全部只覆盖创建路径**，故全部删除，新增 1 个历史兼容用例：

| 删除的用例 | 理由 |
|---|---|
| `test_derived_task_binds_explicit_parent_commit_and_is_independent` | 只断言创建出的子 worktree/分支/子任务单/`derived_from`，创建路径已不存在 |
| `test_child_sheet_is_committed_in_child_worktree_at_return` | 只断言创建期提交子任务单的副作用 |
| `test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history` | 只覆盖 `continuation=True` 创建与重放（该参数随创建函数一起消失） |
| `test_cli_derived_create_returns_identity_and_blocks_replay` | 只覆盖 `dispatch derived-create` 的创建与重放；由验收测试 4 的「不再暴露」替换 |
| `test_child_creation_failure_rolls_back_worktree_and_branch` | 只覆盖创建失败回滚 |
| `test_invalid_child_sheet_is_rejected_and_rolled_back` | 只覆盖创建期非法标识符回滚 |
| `test_worktree_add_failure_deletes_orphan_child_branch` | 只覆盖 `worktree add` 失败时删孤儿分支 |
| `test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume` | 以父提交漂移开头，但随后**继续调用创建函数**创建 `child-task-2` 来观察父证据保留，仍依赖创建路径 |

新增 `test_historical_derived_contracts_still_validate`（= 验收测试 3）：对 schema-3 历史形态派生契约断言 (1) `validate_task` 通过；(2) 真实 `task validate` CLI 退出码 0；(3) 父类型 `vertical-feature` / `repair` 时结构化 `not_applicable` 链路被拒（`must be a non-empty array`）；(4) 父类型 `vertical-feature` + `risk: low` + `evidence_level: 1` 报 `floor 2`；(5) 父类型 `repair` 不抬高下限；(6) 父类型 `prerequisite` 允许豁免段与低证据。全部用 `contract` 侧确定性输入，不依赖创建路径。

### `tests/test_planning.py`（56 → 54）

| 删除的用例 | 理由 |
|---|---|
| `test_task_plan_accepts_derived_parent_outside_the_run` | 断言跨 run 派生计划被**接受**，与新规则（declared derived fail-closed 拒绝）直接冲突 |
| `test_task_plan_rejects_derived_parent_that_cannot_be_found` | 断言的是「父单找不到才拒绝」的派生定位规则，新规则下派生形态无条件拒绝，原断言（报 `ghost-task`/`unfrozen-task`）已无被测对象 |
| `test_task_plan_rejects_planner_declared_parent_type_mismatch` | 同 run/跨 run 的 `parent_task_type` 一致性核验已随派生校验分支移除 |
| `test_task_plan_accepts_same_run_derived_parent` | 断言同 run 派生计划被**接受**，同上冲突 |

同时删除只被上述用例使用的辅助 `_init_repo`、`_write_parent_sheet`、`_derived_task`、`_derived_plan`。新增 `_generation_fixture`/`_feature_task`/`_generation_repo` 与两个验收用例 `test_new_task_plan_rejects_the_derived_type`、`test_generated_sheets_never_declare_derived`。保留 `test_task_plan_rejects_missing_coverage_and_invalid_derived_parent`（它同时断言 coverage 错误；派生形态现在以新理由被拒，`any('derived' in error)` 仍成立），未删未放宽。

### `tests/test_task_generation.py`（26 → 23）

| 删除的用例 | 理由 |
|---|---|
| `test_generator_emits_derived_from_for_derived_task` | 断言生成器为派生任务输出 `derived_from`，生成分支已移除 |
| `test_generate_task_sheets_emits_derived_sheet_for_same_run_parent` | 只覆盖同 run 派生单生成 |
| `test_generate_task_sheets_fails_closed_when_same_run_parent_sheet_exists` | 只覆盖派生单生成时「父单已存在」的 fail-closed，随生成分支消失 |

同时删除只被它们使用的辅助 `write_parent_sheet`、`derived_task`、`parent_task`。保留 `test_generator_output_for_non_derived_task_is_unchanged`（含 `assertNotIn("derived_from", contract)`，仍是当前状态模型的守卫）。

### `tests/test_security_repairs.py`（8 → 7，revision 2 授权改写）

| 删除的用例 | 理由 |
|---|---|
| `test_unsafe_derived_identifier_is_rejected` | 顶层 import `create_derived_dispatch` 并调用它做不安全标识符校验；该创建函数已移除，用例失去被测对象 |

同步移除第 6 行 import 中的 `create_derived_dispatch`，并从 `test_full_security_regression_suite` 去掉对该用例的调用（只去掉对已删除用例的调用，其余两个回归调用与文件内其它断言一字未改）。

### `tests/test_cli.py`（64 → 64）

| 删除的用例 | 理由 |
|---|---|
| `test_task_plan_validate_cli_forwards_root_for_derived_parent` | 只覆盖「跨 run 派生父单需 `--root` 才能被接受」；派生计划现在一律被拒 |

同时删除只被它使用的 `_write_derived_parent_sheet`、`_derived_plan_for_cli`。新增 `test_dispatch_derived_create_is_no_longer_exposed`（= 验收测试 4）：调用 `--format json dispatch derived-create ...` 后 **非零退出**、输出含 `derived-create`、无 `"status": "pass"`，并逐字断言调用后 `git branch --list` 与 `git worktree list --porcelain` 与调用前完全相同、`.worktrees/` 不存在。

### `tests/test_acceptance_id_and_template_compliance.py`（28 → 28，revision 2 授权改写）

`test_references_task_design_documents_derived_generation_support`（`:379`）**方法名保留**（历史冻结任务单 `docs/tasks/derived-generation-support.md` 把它当作自己的 `test_ref`，改名会让该 test_ref 指名不存在的符号），断言改为钉住当前状态模型。needle 逐条处理：

| 原 needle | 处理 | 理由 |
|---|---|---|
| `两条写入路径` | 删 | 写入路径只剩历史读取，不再有「规划期生成器 / 派发期创建」两条 |
| `_task_sheet_text`、`create_derived_dispatch` | 删 | 生成分支与创建函数都已移除 |
| `工具照抄`、`同一次 planning run` | 删 | 描述的是已不存在的生成器派生行为 |
| `docs/tasks/<parent-id>.md`、`机械读取` | 删 | 计划期 `parent_task_type` 机械核验分支已随派生校验移除 |
| `derived_from`、`parent_task_type`、`validate_task_plan`、`fail-closed` | 保留 | 仍是历史读取与当前新规则用到的机制 |
| `root`、`commit`、`branch`、`HEAD` | 删 | 原断言只用于派生创建/生成措辞；这些词与「文档必须描述当前状态模型」无关 |
| 新增断言 | — | 文档必须写明：任务类型只有三类、新任务不再派生、接替关系用 `dependencies`、历史 `derived` 只作读取兼容；并**反向断言**已移除的派生生成措辞（`两条写入路径`/`_task_sheet_text`/`create_derived_dispatch`/`工具照抄`/同一次 planning run/派生任务的提交顺序）不得回流 |

保留其「文档必须描述当前状态模型」的约束意图：既正向钉住当前模型，又反向禁止旧的创建措辞。

### `tests/test_derived_task_dispatch_recovery.py` 顶部保留

`tests/test_derived_task_dispatch_recovery.py:...test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history` 被历史任务单 `docs/tasks/acceptance-id-and-template-compliance.md` 引用（由 `test_frozen_dispatch_acceptance_tests_remain_exact` 钉住该**字符串存在于历史单中**）。该用例已删除，但历史单本身未被改写，因此 `test_frozen_dispatch_acceptance_tests_remain_exact` 与 `docs/tasks/*.md` 的只读校验均不受影响（见「历史只读核对」）。

## 文档改写

- `references/task-design.md`：类型 token 由四个改三个；`derived` 条目、`continuation` 命名统一段、`derived` 继承规则段、`derived_from` 两条写入路径段删除；新增「历史 `derived` 契约的读取规则」（保留 `_validate_derived_from`/`_requires_full_chain`/`evidence_floor` 的完整读取规则说明）；「派生任务的提交顺序」改为「新任务的提交顺序」（从当前 `HEAD` 建 worktree + `dependencies` 表达接替）；事实冲突段与契约修订段的「开 `derived` 任务」改为 `task amend` / 新建任务。
- `SKILL.md`：修订段、恢复段、失败重派段、契约冻结段、持久化段、任务规模段同步改写；「任务规模与 `derived` 任务」改名「任务规模与接替任务」；版本号 `0.16.0` → `0.17.0`（与 compat 新条目对应；既有断言只要求 ≥ 0.16.0）。
- `README.md`：任务类型段由四个改三个，命名统一段删除，改为「新任务不再派生 + 历史 `derived` 只作读取兼容」；修订段「新建 `derived` 任务」改为「新建任务（接替关系写进 `dependencies`）」。
- `references/compat-and-migration.md`：新增 `v0.16.0 → v0.17.0` 条目，写明移除创建路径、新任务用 `dependencies`、历史读取兼容与 metrics 侧不受影响。

## 反向验证（实测）

临时从 `pipeline_tools/planning.py` 删除 `task_type == "derived"` 的 fail-closed 判据（判据块 6 行），只跑验收测试 1：

| 阶段 | 退出码 | 观察 |
|---|---|---|
| 正常 | 0 | `1 passed` |
| 去掉判据后 | **1** | `AssertionError: ... ['task feature-task has invalid task type']`（裸 `type: derived` 不再带可读的 derived 理由） |
| 还原后 | — | `planning.py` sha256 回到 `d35afdfb64abeb6cbb5a710f9bad8c2cc50fd7994a5f5e9ab2920ec309591b2d`（实验前值一致） |

判据承重成立。

## 历史 `derived` 单只读核对

命令（cwd = worktree 根，只读，未改任何文件）：

```
for f in $(grep -rln "derived_from" docs/tasks/); do python -m pipeline_tools task validate "$f"; done
```

| 历史任务单 | `task validate` 退出码 |
|---|---|
| `docs/tasks/derived-creation-removal.md` | 0 |
| `docs/tasks/derived-generation-support.md` | 0 |
| `docs/tasks/gate-deletion-semantics-continuation-1.md`（`task_type: derived`，父类型 `prerequisite`） | 0 |
| `docs/tasks/metrics-tracking-policy-continuation-1.md` | 0 |
| `docs/tasks/security-scan-repair-20261001-continuation-1.md` | 0 |
| `docs/tasks/task-design-corruption-fix.md` | 0 |
| `docs/tasks/task-sheet-revision-and-evidence-binding.md` | 0 |

## 验收测试（逐条）

| ID | 命令（cwd = worktree 根） | 退出码 | 观察 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type` | 0 | 1 passed, 53 deselected |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived` | 0 | 1 passed, 53 deselected |
| acceptance-test-3 | `python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate` | 0 | 1 passed, 2 subtests passed |
| acceptance-test-4 | `python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed` | 0 | 1 passed, 63 deselected |
| acceptance-test-5 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | 1 passed, 27 deselected |

## 全量测试

`python -m pytest -q`（cwd = worktree 根，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）→ 退出码 0，**388 passed, 30 subtests passed**。

与基线 **401 passed, 28 subtests passed** 的差异：**收集到的用例 −13**（401 → 388），子测试 **+2**（28 → 30）。

| 文件 | 基线 | 现在 | 明细 |
|---|---|---|---|
| `tests/test_planning.py` | 56 | 54 | −4 派生计划用例，+2 验收用例 |
| `tests/test_task_generation.py` | 26 | 23 | −3 派生生成用例 |
| `tests/test_security_repairs.py` | 8 | 7 | −1 派生创建路径安全用例 |
| `tests/test_derived_task_dispatch_recovery.py` | 8 | 1 | −8 创建路径用例（含 `continuation`），+1 历史兼容用例 |
| `tests/test_cli.py` | 64 | 64 | −1 派生计划 CLI 用例，+1 验收测试 4 |
| `tests/test_acceptance_id_and_template_compliance.py` | 28 | 28 | 1 个用例按授权就地改写，无增删 |
| 合计 | 401 | 388 | −13 |

子测试 +2 来自验收测试 3 里对两种父类型（`vertical-feature`、`repair`）的 `subTest` 循环。

## 其它检查（cwd = worktree 根）

- `python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md` → 退出码 0（PASS）。
- `python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor` → 退出码 0（PASS）。
- `python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed <revision 2 allowed_paths> --forbidden <revision 2 forbidden_paths>` → 退出码 0（PASS）。
- `git diff --check` → 退出码 0。
- 契约未改：`docs/tasks/derived-creation-removal.md` 未被本轮改动，sha256 = `ad9dfd972ccd97904e9b3c031980b017e6121018f26a74e6a476ae63b36de6fc`（与 revision 2 记录一致）。
- `pipeline_tools/contract.py` 与 `docs/goal.md` 的 `git diff` 均为空。
- 未新建 worktree、未动主工作树、未改历史任务单/历史证据与其它任务证据目录。

## 决策点核查

1. 让新计划拒绝 `derived` 会同时使历史计划/历史契约被拒 —— **未触发**。历史契约走未改的 `contract.py`，7 张含 `derived_from` 的历史单全部仍 PASS；仓库内无需要继续校验的历史 planning 计划文档。
2. 必须修改 `pipeline_tools/contract.py` —— **未触发**。`planning.py` 有本文件私有 `TASK_TYPES`，去 `derived` 即可 fail-closed。
3. 文档改写会撞上**未授权**的既有断言而必须削弱它 —— **未触发**。两处改写都在 revision 2「允许的测试改写」授权范围内；`test_references_task_design_contains_no_replacement_character`、`test_lifecycle_and_evidence_documentation_matches_current_contract`、`test_frozen_dispatch_acceptance_tests_remain_exact` 等既有断言一字未改。
4. 实现必须修改契约未列出的文件 —— **未触发**。本轮回合的改动全部落在 revision 2 的 `allowed_paths` 内（`scope check` PASS）。

```pipeline-evidence
{"schema": 2, "task_id": "derived-creation-removal", "worktree": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "branch": "derived-creation-removal", "role": "executor", "round": 2, "status": "PASS", "head": "b4ca1179f30b054493e0c5227bcb86f3f6602e6b", "sheet_revision": 2, "sheet_sha256": "ad9dfd972ccd97904e9b3c031980b017e6121018f26a74e6a476ae63b36de6fc", "observed_at_commit": "b4ca1179f30b054493e0c5227bcb86f3f6602e6b", "generated_at": "2026-10-09T03:52:34+00:00", "commands": [{"command": "git rev-parse --show-toplevel", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git branch --show-current", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git rev-parse HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "sha256sum docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type  # after temporarily removing the reject-derived criterion, then restored byte-identically", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 1, "expected_exit_code": 1, "evidence_ref": "executor-report.md"}, {"command": "for f in $(grep -rln derived_from docs/tasks/); do python -m pipeline_tools task validate \"$f\"; done", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed pipeline_tools/core.py pipeline_tools/planning.py pipeline_tools/__main__.py tests/test_planning.py tests/test_task_generation.py tests/test_derived_task_dispatch_recovery.py tests/test_security_repairs.py tests/test_cli.py tests/test_acceptance_id_and_template_compliance.py SKILL.md README.md references/task-design.md references/compat-and-migration.md docs/tasks/derived-creation-removal.md .pipeline/derived-creation-removal/** --forbidden docs/goal.md pipeline_tools/contract.py .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/finalization-report-reader/** .pipeline/finalization-hygiene/** .env credentials/**", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}], "assertions": ["the derived creation path is gone: create_derived_dispatch, the dispatch derived-create subcommand and its dispatch branch, the planning derived validation branch, the generator derived branch and its dead helpers were all removed", "new task plans that declare type: derived, or the derived form parent_task_id/derived_from, are rejected fail-closed with a readable reason, and generation produces no sheet for them", "the generator now emits only vertical-feature, prerequisite and repair sheets and never writes a derived_from field", "calling dispatch derived-create exits non-zero with no status pass and leaves git branch --list and git worktree list --porcelain byte-identical, with no .worktrees directory", "pipeline_tools/contract.py is byte-identical: TASK_TYPES still contains derived and _validate_derived_from, _requires_full_chain and the evidence_floor parent branch are unchanged", "all seven historical sheets containing derived_from still pass task validate", "the reverse validation shows the reject-derived criterion is load-bearing: removing it makes acceptance test 1 fail (exit 1) and it was restored byte-identically", "the metrics side include_derived and confidence derived strings are untouched", "the full suite is green at 388 passed, 30 subtests passed; the count moved from 401 to 388 by 13 deliberate test deletions and 2 additions, with 2 new subtests"], "evidence_refs": ["executor-report.md", "executor-result.json"], "unverified": ["round 1 stopped at decision point 4: fully removing the derived creation path requires modifying tests/test_security_repairs.py, which revision 1 allowed_paths excluded; round 2 executes the full removal under revision 2, which added that file and authorized the two test rewrites", "round 1 measured no post-removal suite count; round 2 records the measured 388 passed, 30 subtests passed", "the reverse-validation experiment temporarily edited pipeline_tools/planning.py in the working tree and restored it byte-identically (sha256 d35afdfb64abeb6cbb5a710f9bad8c2cc50fd7994a5f5e9ab2920ec309591b2d before and after); the experimental state was never committed", "the historical created-derived-task runtime behaviour (worktree creation, rollback) was not exercised after removal because the entry point no longer exists", "no claim is made about worktree cleanup or history migration: both are explicit non-goals"]}
```
