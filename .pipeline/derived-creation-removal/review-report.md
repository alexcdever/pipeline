# 独立审查报告（round 1）：derived-creation-removal

- 任务单：`docs/tasks/derived-creation-removal.md`，revision **2**（授权节「允许的测试改写（已授权）」生效）
- 任务单 sha256：`ad9dfd972ccd97904e9b3c031980b017e6121018f26a74e6a476ae63b36de6fc`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal`
- branch：`derived-creation-removal`
- 待审实现提交：`b4ca1179f30b054493e0c5227bcb86f3f6602e6b`
- 审查运行时分支尖端（执行者 round-2 证据）：`4251e0e09a41417620d8b15981bcd10e122f966c`
- 契约基线（revision 2）：`cac7cfd`
- 全部复验亲自执行；未动主工作树，未新建 worktree，未改任何产品/测试/文档文件，未改其它任务证据目录。

## 1. 环境检查（逐项）

| # | 检查 | 结果 |
|---|------|------|
| 1 | `git rev-parse --show-toplevel` == worktree 绝对路径 | PASS → `D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal` |
| 2 | `git branch --show-current` == `derived-creation-removal` | PASS |
| 3 | `git rev-parse HEAD` == `4251e0e09a41417620d8b15981bcd10e122f966c` | PASS |
| 4 | `git merge-base --is-ancestor b4ca117 HEAD` | PASS → 退出码 0 |
| 5 | `python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md` | PASS → 退出码 0，输出 `PASS` |
| 6 | 只读产品代码；不建 worktree；不动主工作树；不改其它任务证据目录 | PASS → 本审查只新增本节的两份证据文件 |

## 2. 第 4 节各点独立观察

### 点 1 — 新计划拒绝派生（自建夹具）

我自建 4 份计划（`/tmp/rev-fix/`，非仓库内）：`type: derived` 且带 `parent_task_id`/`derived_from`；`repair` 类型 + `parent_task_id`；`repair` 类型 + `derived_from`；正常 `repair`。经 Python API `validate_task_plan` 与 CLI `planning task-plan-validate` 双路复验：

| 夹具 | API | CLI 退出码 | 原因文本 |
|---|---|---|---|
| `type: derived` | REJECT | 2 | `task t1 declares the derived type; new tasks are never derived - start from the current head and express succession with dependencies`（另有派生形态一条） |
| `repair` + `parent_task_id` | REJECT | 2 | `task t1 declares a derived-form plan (parent_task_id/derived_from); ...` |
| `repair` + `derived_from` | REJECT | 2 | 同上（派生形态） |
| 正常 `repair` | ACCEPT | 0 | `{"status":"pass","errors":[]}` |

fail-closed 成立、原因可读、不误伤正常计划。生成路径不产出任务单：验收测试 1 用同一份派生计划跑 `generate_task_sheets`，断言 `status == "blocked"` 且 `docs/tasks/` 不存在。

### 点 2 — 生成器只产三类

`tests/test_planning.py: test_generated_sheets_never_declare_derived` 用三类计划（`vertical-feature`/`repair`/`prerequisite`）生成，逐张断言 `validate_task == []`、`task_type in {三类}`、`task_type != derived`、`assertNotIn("derived_from", contract)`；`task_ids == ['feature-task','repair-task','prereq-task']`。运行通过（见第 3 节 acceptance-test-2）。

### 点 3 — 历史读取未被波及（真实仓库只读，确定性契约输入）

- 仓库 `docs/tasks/` 中含 `derived_from` 的历史单共 **7** 张，逐张 `task validate` 全部退出码 0、输出 PASS：`derived-creation-removal.md`、`derived-generation-support.md`、`gate-deletion-semantics-continuation-1.md`、`metrics-tracking-policy-continuation-1.md`、`security-scan-repair-20261001-continuation-1.md`、`task-design-corruption-fix.md`、`task-sheet-revision-and-evidence-binding.md`。
- 扩大扫尾：`docs/tasks/` 全部 **46** 张任务单 `task validate` 全 PASS（无回归）。
- **链路收紧与 `evidence_floor` 前后一致**：我把 `cac7cfd` 的 `contract.py`（386 行）导出为独立模块，与 `b4ca117` 的当前模块并排跑同一组确定性输入：

| 输入 | floor 前→后 | full_chain 前→后 |
|---|---|---|
| `derived`，父 `vertical-feature` | 2 → 2 | True → True |
| `derived`，父 `repair` | 1 → 1 | True → True |
| `derived`，父 `prerequisite` | 1 → 1 | False → False |
| `derived`，父 `derived` | 1 → 1 | False → False |
| `repair` / `vertical-feature` / `prerequisite` | 1/2/1 → 1/2/1 | True/True/False → 相同 |

`ALL_BEHAVIOUR_IDENTICAL: True`，两侧 `TASK_TYPES` 均含 `derived`。链路收紧与证据下限行为与改动前逐项一致。

### 点 4 — `contract.py` 逐字节未改

`git diff cac7cfd b4ca117 -- pipeline_tools/contract.py` 为空。`contract.py:29 TASK_TYPES = {"vertical-feature", "prerequisite", "repair", "derived"}` 仍含 `derived`；`_validate_derived_from`、`_requires_full_chain`、`evidence_floor` 的 `parent_task_type` 分支齐备。fail-closed 由 `planning.py` 本文件私有 `TASK_TYPES`（去 `derived`）+ 新增判据实现，未触碰 `contract.py`。

### 点 5 — CLI 入口消失（自建仓库夹具）

在 `mktemp -d` 的独立 git 仓库调用 `--format json dispatch derived-create ...`：

- 退出码 **2**，输出 `status: config`，错误 `argument action: invalid choice: 'derived-create' (choose from write, worktree-create)`；无 `"status": "pass"`。
- 调用前/后 `git branch --list` 与 `git worktree list` **逐字相同**（仅 `* master` / 单条 worktree 记录），仓库内无 `.worktrees/` 目录。

子命令注册段（`__main__.py:404-412`）与分派分支（`__main__.py` `dispatch derived-create`）已删除，顶层 import 已移除。

### 点 6 — metrics 同名物未被误伤

`git diff cac7cfd b4ca117 -- pipeline_tools/` 中无任何含 `no-derived`/`include_derived`/`confidence derived` 的行被改动。当前仍在：`__main__.py:132 --no-derived`、`__main__.py:1254 include_derived=not args.no_derived`、`__main__.py:305 --confidence {observed,derived,reported}`、`__main__.py:963 "confidence": "derived"`、`core.py:43 CONFIDENCES`、`core.py:881/889/975 include_derived`。

### 点 7 — 测试改写在授权范围内（逐行核对删除行）

对 `git diff cac7cfd b4ca117 -- tests/` 的全部删除行逐条归类，结论：**除创建路径用例与契约授权的两处外，无任何既有断言被删或弱化**。

- `tests/test_derived_task_dispatch_recovery.py`：旧 8 个用例**全部**只覆盖创建路径（模块级 import 即 `create_derived_dispatch`；逐条核对：绑定父提交、子单提交副作用、`continuation` 幂等、CLI 创建重放、创建失败回滚、非法标识符回滚、孤儿分支删除、父证据保留——最后一条虽以父提交漂移开头，但随后继续调用创建函数创建 `child-task-2`，仍属创建路径）。全部删除并换成 1 个历史兼容用例 `test_historical_derived_contracts_still_validate`（= 验收测试 3）。
- `tests/test_planning.py`：删 4 个派生计划用例（`accepts_derived_parent_outside_the_run`、`rejects_derived_parent_that_cannot_be_found`、`rejects_planner_declared_parent_type_mismatch`、`accepts_same_run_derived_parent`）与只服务于它们的辅助；新增两个验收用例。
- `tests/test_task_generation.py`：删 3 个派生生成用例与辅助；保留 `test_generator_output_for_non_derived_task_is_unchanged`（含 `assertNotIn("derived_from", contract)`）。
- `tests/test_cli.py`：删 1 个派生计划 CLI 用例（跨 run 父单需 `--root`）；新增验收测试 4（逐字比较调用前后 branch/worktree 列表）。
- `tests/test_security_repairs.py`：删 `test_unsafe_derived_identifier_is_rejected` 与其在 `test_full_security_regression_suite` 中的调用（**契约授权**）。
- `tests/test_acceptance_id_and_template_compliance.py`：只改 `test_references_task_design_documents_derived_generation_support`（**契约授权**），方法名保留（历史单把它当 `test_ref`），改为正向钉住三类/不派生/`dependencies`/历史只读，并**反向** `assertNotIn` 旧措辞（`两条写入路径`、`_task_sheet_text`、`create_derived_dispatch`、`工具照抄`、`同一次 planning run`），约束意图未削弱、反而更严。

**交叉点独立确认**：`test_frozen_dispatch_acceptance_tests_remain_exact`（`test_acceptance_id_and_template_compliance.py:71`）要求历史单 `docs/tasks/acceptance-id-and-template-compliance.md` 的**文本**含 `...test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history`。我确认：该历史单在 `cac7cfd..b4ca117` 中 `git diff` 为空（未改写），文本中该串出现 4 次，断言只读文本、不要求被测方法存在。该用例本体一字未改，单独运行退出码 0、`1 passed`。**不是靠放宽断言达成**。

### 点 8 — 文档

- `references/task-design.md`：类型由四个改三个；`derived` 条目、`continuation` 命名统一、`derived` 继承规则、`derived_from` 两条写入路径四段删除；新增「历史 `derived` 契约的读取规则」（写明 `_validate_derived_from`/`_requires_full_chain`/`evidence_floor` 读取规则不变）；「派生任务的提交顺序」改写为「新任务的提交顺序」（从当前 `HEAD` 建 worktree + `dependencies` 表达接替）。符合要求。
- `SKILL.md`：`version: 0.16.0 → 0.17.0`；修订段/恢复段/失败重派段/契约冻结段/持久化段/任务规模段同步改写，「任务规模与 `derived` 任务」改名「任务规模与接替任务」。
- `references/compat-and-migration.md`：新增 `v0.16.0 → v0.17.0` 条目（仅 +1 行），写明移除创建路径、`dependencies` 接替、历史读取兼容、metrics 不受影响。既有条目（`v0.15.0 → v0.16.0`、`v0.13.0 → v0.14.0`、`v0.12.0 → v0.13.0`）**未被改写**。

### 点 9 — 无越界

`git diff --name-only cac7cfd b4ca117`（15 个路径）全部落在 revision 2 `allowed_paths` 内：`pipeline_tools/{core,planning,__main__}.py`、`tests/{test_planning,test_task_generation,test_derived_task_dispatch_recovery,test_security_repairs,test_cli,test_acceptance_id_and_template_compliance}.py`、`SKILL.md`、`README.md`、`references/{task-design,compat-and-migration}.md`、`.pipeline/derived-creation-removal/{executor-report.md,executor-result.json}`。`forbidden_paths` 零改动：`docs/goal.md`、`pipeline_tools/contract.py`、六个已完成任务证据目录均不在改动名单。`scope check` 退出码 0（PASS）。

## 3. 五条契约验收测试（cwd = worktree 根，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）

| ID | 命令 | 退出码 | 观察 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type` | 0 | `1 passed, 53 deselected` |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived` | 0 | `1 passed, 53 deselected` |
| acceptance-test-3 | `python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate` | 0 | `1 passed, 2 subtests passed` |
| acceptance-test-4 | `python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed` | 0 | `1 passed, 63 deselected` |
| acceptance-test-5 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | `1 passed, 27 deselected` |

## 4. 全量测试与其它命令

- `python -m pytest -q`（cwd = worktree 根）→ 退出码 **0**，输出 **`388 passed, 30 subtests passed`（304.38s）**。与执行者声明的 **388 / 30** **一致**。
- 独立核对逐文件收集数，与执行者报告的表**逐格一致**：`test_planning.py` 54、`test_task_generation.py` 23、`test_security_repairs.py` 7、`test_derived_task_dispatch_recovery.py` 1、`test_cli.py` 64、`test_acceptance_id_and_template_compliance.py` 28（合计 177）。
- `python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md` → 退出码 0（PASS）。
- `python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor` → 退出码 0（PASS）。
- `python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed <revision 2 allowed_paths> --forbidden <revision 2 forbidden_paths>` → 退出码 0（PASS）。
- `git diff --check cac7cfd b4ca117` → 退出码 0（无空白错误）。

## 5. 结论与 findings

**结论：PASS。** 五点高风险全部亲自复验通过；五条验收退出码 0；全量与声明一致；无越界；`contract.py` 未变；历史读取行为前后逐项确定一致；测试改写全部落在「创建路径用例 + 契约授权两处」范围内，历史兼容断言未被削弱。

findings（不阻塞）：

1. **轻微文档措辞不一致（低）**：`README.md:29` 写「任务类型 token 只有三个（`pipeline_tools/contract.py` 的 `TASK_TYPES`）」，而同段括注 `TASK_TYPES` 仍含 `four` 中的 `derived`。计数所指为「创建类型」，同段下一句已明确「`TASK_TYPES` 仍含 `derived`」，故不构成事实错误，但把它归因于 `TASK_TYPES` 易误读。`references/task-design.md` 未把三类计数归因到 `TASK_TYPES`，无此问题。
2. **被删用例原覆盖的一条保证失去测试（低，移除的必然结果）**：`test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume` 除创建路径外还断言「失败时保留父现场」。该保证随载体函数消失而失去专用断言；本轮不要求补建，交由主代理判断是否需要在新形态下另立断言。
3. **文档行号引用微偏（极低，既有问题）**：`references/task-design.md` 引 `contract.py:131-145`（实为 132-146）与 `:166`（实为 167）；该行号在改动前同样如此，非本轮引入。

## 6. 未复验（unverified）

- 被移除创建路径的运行时行为（建子 worktree、回滚、`continuation` 幂等）在入口消失后无法再被实际触发，只能验证其**不存在**。
- 决策点 1 的「历史 planning 计划文档」情形：仓库内未见仍需校验的历史 planning 计划文件，故只验证了历史**契约**（任务单）不受影响，未验证历史计划文档（若有）。

## 7. blockers

无。

```pipeline-evidence
{"schema": 2, "task_id": "derived-creation-removal", "worktree": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "branch": "derived-creation-removal", "role": "reviewer", "round": 1, "status": "PASS", "head": "b4ca1179f30b054493e0c5227bcb86f3f6602e6b", "sheet_revision": 2, "sheet_sha256": "ad9dfd972ccd97904e9b3c031980b017e6121018f26a74e6a476ae63b36de6fc", "observed_at_commit": "4251e0e09a41417620d8b15981bcd10e122f966c", "generated_at": "2026-10-09T04:11:29+00:00", "commands": [{"command": "git rev-parse --show-toplevel", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git branch --show-current", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git rev-parse HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git merge-base --is-ancestor b4ca1179f30b054493e0c5227bcb86f3f6602e6b HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git diff cac7cfd b4ca117 -- pipeline_tools/contract.py", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git diff --name-only cac7cfd b4ca117", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git diff cac7cfd b4ca117 -- tests/", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json planning task-plan-validate <own derived-type plan>", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 2, "expected_exit_code": 2, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json planning task-plan-validate <own repair+parent_task_id plan>", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 2, "expected_exit_code": 2, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json planning task-plan-validate <own valid repair plan>", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json dispatch derived-create <temp repo> ...", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 2, "expected_exit_code": 2, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "for f in $(grep -rl derived_from docs/tasks/*.md); do python -m pipeline_tools task validate \"$f\"; done", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "for f in docs/tasks/*.md; do python -m pipeline_tools task validate \"$f\"; done", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k frozen_dispatch_acceptance_tests_remain_exact", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q --collect-only tests/test_derived_task_dispatch_recovery.py tests/test_planning.py tests/test_task_generation.py tests/test_security_repairs.py tests/test_cli.py tests/test_acceptance_id_and_template_compliance.py", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "python -m pipeline_tools --format json scope check . --task-id derived-creation-removal --allowed <allowed_paths> --forbidden <forbidden_paths>", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}, {"command": "git diff --check cac7cfd b4ca117", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": ".pipeline/derived-creation-removal/review-report.md"}], "assertions": ["environment: toplevel, branch, HEAD==4251e0e, merge-base ancestor, task validate and read-only all pass", "own fixtures: a plan declaring type derived is rejected fail-closed with a readable reason via both the Python API and the CLI (exit 2), a non-derived plan declaring parent_task_id or derived_from is rejected the same way, and a valid three-type plan is accepted (exit 0)", "the generator emits only vertical-feature, prerequisite and repair sheets and never writes derived_from", "all 7 historical sheets in docs/tasks containing derived_from, and all 46 sheets overall, still pass task validate read-only", "chain tightening and evidence_floor for historical derived contracts are byte-for-byte behaviourally identical between cac7cfd and b4ca117 when both contract modules are driven with the same deterministic inputs", "pipeline_tools/contract.py diff between cac7cfd and b4ca117 is empty and TASK_TYPES still contains derived", "dispatch derived-create exits non-zero (invalid choice) and leaves git branch --list and git worktree list byte-identical, creating no .worktrees directory", "metrics include_derived, --no-derived and --confidence derived are present and no metrics-derived line changed in the diff", "every deleted assertion belongs to a creation-path case or to one of the two contract-authorized rewrites; no historical-compatibility assertion was deleted or weakened", "test_frozen_dispatch_acceptance_tests_remain_exact still passes by matching text in the unchanged historical sheet, not by relaxing an assertion", "references/task-design.md, SKILL.md (0.16.0 to 0.17.0) and the new compat-and-migration entry describe the current state model; older compat entries are unchanged", "all changed paths are inside revision 2 allowed_paths and no forbidden path changed; scope check passes", "all five contract acceptance tests exit 0; the full suite exits 0 with 388 passed, 30 subtests passed, matching the executor's claim; per-file collected counts match the executor's table", "task validate, result verify, scope check and git diff --check all exit 0"], "evidence_refs": [".pipeline/derived-creation-removal/review-report.md", ".pipeline/derived-creation-removal/reviewer-result.json"], "unverified": ["the runtime behaviour of the removed creation path cannot be re-exercised because the entry point no longer exists; only its absence is verified", "whether a historical planning plan document still requires validation was not verified because no such document was found in the repository", "whether the deleted recovery test's parent-scene-preservation guarantee should be re-asserted in the new shape is reported as a finding, not decided here"], "blockers": [], "recommendation": "ready_for_finalization"}
```
