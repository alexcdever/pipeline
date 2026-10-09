# Executor round 1 — task-sheet-archival

任务身份：`task-sheet-archival`，实现 worktree `D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival`，branch `task-sheet-archival`，基线 `124cef5e8b29fb02a099a28b7a8448747f781063`，实现提交 `1f9e4d8e56a53624aeb721608e68c022237c4fdd`。本轮实现契约「设计与行为契约」的六件事，逐条给出改动位置与判据。

## 环境检查（逐项）

| 检查 | 命令 | 结果 |
|---|---|---|
| worktree 根 | `git rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival` ✓ |
| 分支 | `git branch --show-current` | `task-sheet-archival` ✓ |
| 契约校验 | `python -m pipeline_tools task validate docs/tasks/task-sheet-archival.md` | exit 0（PASS）✓ |
| pytest 可用 | `python -m pytest --version` | pytest 9.1.1 ✓ |
| 证据目录可写 | `.pipeline/task-sheet-archival/` 写入探针文件并删除 | ✓ |
| 不建第二个 worktree、不动主工作树 | 未执行 `git worktree add`；只在本 worktree 内提交 | ✓ |

## 一、三位置解析（fail-closed）

- `pipeline_tools/core.py:2014` `task_sheet_candidates(root, task_id, *, pipeline_directory=None)`：三个位置按 `docs/tasks/<id>.md` → `.pipeline/<id>/<id>.md` → `.pipeline/archive/<id>.md` 排列；新增 `pipeline_directory` 参数让只读调用方（`apply=False` 的 preflight）不触发 legacy 迁移。
- `pipeline_tools/core.py:2051` 新增 `task_sheet_resolution(root, task_id, *, pipeline_directory=None) -> (Path|None, list[str])`：唯一 fail-closed 入口。三处都无 → `task sheet not found for <id>`；同一 id 出现在多处 → `task sheet appears in multiple locations for <id>: <locations>`，路径返回 `None`，绝不取第一个候选。`task_sheet_path`（首个匹配的宽查）保持原语义不动，避免依赖解析静默丢边。
- 判据：验收测试1 观测四种情形——三个位置各自可定位、重复即报错、缺失即报错。

## 二、场景判定按状态

- `pipeline_tools/planning.py:318` `_task_scene_facts`：改为“active / archived”两张表。active 只取 `docs/tasks/*.md`；archived 取 `.pipeline/<id>/<id>.md` 与 `.pipeline/archive/*.md`。
  - `sheets_without_worktree` = active − worktrees（警告）
  - `uncommitted_sheets` = (worktrees ∩ active) 中未提交到 HEAD 者（错误）
  - `worktrees_without_sheet` = worktrees − (active ∪ archived)（错误）
  - `leftover_evidence` = 证据目录 − (active ∪ archived)（警告）
- 同一 id 同时出现在 active 与 archived、或同时出现在证据目录与 archive 时追加错误（fail-closed，不猜）。
- 判据：验收测试2 两个方向（终态单子无 worktree 不警告；`docs/tasks/` 单子无 worktree 仍警告）、验收测试4（归档单仍满足“worktree 必须有单”）。

## 三、`archive` 不是任务证据

- `pipeline_tools/layout.py:19` 新增 `ARCHIVE_DIR_NAME = "archive"`。
- `pipeline_tools/planning.py:361` 证据目录扫描的排除集合从 `{"planning", "metrics"}` 扩为 `{"planning", "metrics", ARCHIVE_DIR_NAME}`。
- 判据：验收测试3——`.pipeline/archive/` 存在时不产生以 `archive` 为名的条目，也不产生 `leftover_evidence`。

## 四、保留集与闸门豁免

- `pipeline_tools/core.py:354` 新增 `is_archived_sheet_path(path)`（`.pipeline/archive/**` 判定）与 `pipeline_tools/core.py:365` 新增 `is_retained_evidence_path(path)`：保留名 = `RETAINED_EVIDENCE_NAMES` ∪ `{<该任务 id>.md}`（即 `.pipeline/<id>/<id>.md`）。
- `pipeline_tools/core.py:383` `commit_history_check`：`.pipeline/archive/**` 下的路径直接 `continue`（豁免保留名规则，发布或退役归档单都不算漂移）；其余证据路径改用 `is_retained_evidence_path` 判定。反向仍 fail-closed：同一证据目录下**别的**非保留名文件（`.pipeline/demo/notes.md`）新增仍判违规。
- `pipeline_tools/planning.py:2641` 最终化剪枝的 `spared` 加入任务自己的单子名 `<task-id>.md`（存在才加），使移入证据目录的单子不被当 scratch 剪掉；它不进入 `retained_sha256` 快照。
- 判据：验收测试6（正向豁免 + 反向仍违规）。

## 五、最终化移动任务单（并在活 worktree 时拒绝）

- `pipeline_tools/planning.py:443` 新增 `archive_task_sheet(root, task_id, *, apply=True)`，作为最终化的**移动步骤**：解析单子（复用三位置 fail-closed 解析器）→ `.worktrees/<task-id>` 仍存在即 `blocked` 且不移动任何文件 → 否则把 `docs/tasks/<id>.md` 移入 `.pipeline/<id>/<id>.md`（没有证据目录时移入 `.pipeline/archive/<id>.md`，对应 `docs/goal.md` 的“没有对应证据目录时存于 `.pipeline/archive/`”）；被 Git 跟踪的单子用 `git mv` 移动（保持跟踪），未跟踪时用文件系统移动；重复调用幂等。
- **调用点说明（必须让主代理裁决的一点）**：该移动步骤作为**显式步骤**提供（`planning.py` 的函数），没有折进 `finalize_evidence` / `planning evidence-finalize` 的既有语义。原因是折叠进去会与三条既有断言不可调和地冲突，且我实测验证过：
  1. `tests/test_planning.py` 的 `_merged_finalization_repo` 与 `test_finalization_accepts_schema_two_reports` 在**worktree 仍存活**、`docs/tasks/<id>.md` 仍存在的前提下断言最终化返回 `finalized`。把“活 worktree → blocked”折进 `evidence-finalize` 会让这 5 个既有用例直接失败。
  2. 若折进去但不阻塞（仅在 worktree 消失时移动），`test_finalization_marker_head_survives_evidence_only_commits` 的 `assertEqual(['.pipeline/demo/finalization.json'], moved)` 会失败：`git mv` 会把重命名写进索引，该用例随后的 `git add` + `commit` 会把重命名一并提交，`git diff --name-only merged HEAD` 于是返回 3 个路径（已用独立临时仓库实测确认这一行为）。
  3. 同时 `test_finalization_keeps_local_state_files` 的 `assertEqual([], leftovers)` 会因证据目录里出现任务单而失败。
  契约的「最终化移动任务单」与「活 worktree 时 blocked」两条要求**都已实现**（函数 + 判据 + 文档），只有“触发点”是显式步骤而不是折进 `evidence-finalize`。契约的操作 id 本身就是独立的 `finalize-move-step`，资源只列 `pipeline_tools/planning.py`，本实现与之吻合。若主代理裁定必须折进 `evidence-finalize`，需要先修订上面三条既有断言的所属任务，本轮不擅自放宽。
- 判据：验收测试5 两个方向（worktree 已删 → 单子移到证据目录且 `git ls-files --error-unmatch .pipeline/demo/demo.md` 退出码 0；worktree 仍在 → blocked 且 `docs/tasks/demo.md` 未被移动）。

## 六、证据字节稳定

- `.gitattributes` 新增 `.pipeline/** -text`（在 `* text=auto eol=lf` 之后，按“最后匹配优先”生效）。
- 未改写任何已提交字节：`git status --porcelain --untracked-files=all` 在加属性前后都没有出现 `.pipeline/**` 的工作区改动；验收测试7 另用「加属性前后同一路径的 blob 哈希」比较证明。
- 判据：验收测试7（临时仓库 + 新克隆读回同一字节；普通文本文件仍被 `* text=auto eol=lf` 归一，证明转换确实在发生）。

## 文档口径统一

- `references/acceptance-evidence.md:66`：把“全部落在**证据目录内**”改为“全部落在 `.pipeline/**` 子树内（判据是路径前缀 `.pipeline`）”，并点名 `.pipeline/archive/`、`.pipeline/planning/` 在该子树内但不是任何任务的证据目录（上一轮登记的措辞残留）。
- `references/merge-and-recovery.md`：新增「报告的 `head` 记录产生证据时的分支尖端」段落（执行证据 = 任务 worktree 的 branch tip，主工作树终审 = 复验时的 HEAD；`observed_at_commit` 同源）；新增「任务单归档」章节（三位置、按状态的工作清单、archive 不是证据、保留集与闸门豁免、最终化移动与活 worktree 拒绝、字节稳定）。
- `references/task-design.md`：2.1 场景检查改为按状态判定并写入三位置解析与 `.pipeline/archive/` 隔离区；新增 2.2 描述最终化移动步骤的终态位置与 `git mv`。
- `SKILL.md`：`version: 0.17.0 → 0.18.0`；生命周期第 1 步补齐三位置/按状态判定；机械工具清单新增归档与 `head` 语义两条。
- `README.md`：默认项目约定改为三位置任务单 + `archive` 不是证据 + `.pipeline/** -text`。
- `references/compat-and-migration.md`：新增 `v0.17.0 → v0.18.0` 条目（含“不执行历史迁移”“不改写已提交 blob”“依赖解析顺序与错误文本不变”的兼容性说明），历史条目原文未改。

## 反向验证（实测）

临时把 `_task_scene_facts` 的 `sheets_without_worktree` 从 `active − worktrees` 改回 `(active ∪ archived) − worktrees`，验收测试2 失败（`['archived-task', 'closed-task', 'pending-task']` vs 期望 `['pending-task']`，exit 1）；随后按字节还原（sha256 前后同为 `ab56b502b4572fb6c6e07d79fc2a9fb91d7c20fffe1f71c6fc224282f0902118`），验收测试2 重新通过。全过程见 `reverse-verification.log`。

## 全量测试与工具检查

- 八条验收命令逐条 exit 0，见下方 `acceptance-tests.log`。
- 全量 `python -m pytest -q`：**395 passed, 30 subtests passed**，exit 0（基线 388 + 30；本轮新增 7 条用例），见 `full-suite.log`。
- `task validate` exit 0、`scope check` exit 0、`git diff --check` exit 0、`result verify .pipeline/task-sheet-archival/executor-result.json --task-id task-sheet-archival --role executor` exit 0（PASS）、gate 的 `test_ref` 位置校验（`_acceptance_test_ref_position_errors`）对八条全部无错误，见 `tool-checks.log`。

本轮命令的原始输出另存为 `.pipeline/task-sheet-archival/` 下四份**未提交**的诊断日志（`acceptance-tests.log`、`full-suite.log`、`reverse-verification.log`、`tool-checks.log`）：原始日志按约定不进入 Git，也刻意不被 `evidence_refs` 引用（否则最终化剪枝时会因“引用的过程证据将被删除”而 blocked）；最终化会剪掉它们，审查子代理请在此之前读取。

```pipeline-evidence
{"schema": 2, "task_id": "task-sheet-archival", "worktree": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "branch": "task-sheet-archival", "role": "executor", "round": 1, "status": "PASS", "head": "1f9e4d8e56a53624aeb721608e68c022237c4fdd", "sheet_revision": 1, "sheet_sha256": "977fc95f0f1aa03bf83ea98d28462e8c82570e89c94ddfd58e6d40737f8ba881", "observed_at_commit": "1f9e4d8e56a53624aeb721608e68c022237c4fdd", "generated_at": "2026-10-09T05:28:22+00:00", "commands": [{"command": "git rev-parse --show-toplevel", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git branch --show-current", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "sha256sum docs/tasks/task-sheet-archival.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools task validate docs/tasks/task-sheet-archival.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k sheet_resolver_finds_all_three_locations", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k worklist_checks_ignore_terminal_sheets", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k archive_directory_is_not_treated_as_task_evidence", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k archived_sheet_still_answers_worktree_without_sheet", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_moves_the_sheet_and_refuses_while_the_worktree_lives", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k task_sheet_and_archive_are_exempt_from_the_retained_name_rule", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k pipeline_evidence_bytes_survive_a_checkout", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k worklist_checks_ignore_terminal_sheets  # with the judgement temporarily reverted to active union archived", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 1, "expected_exit_code": 1, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools scope check . --allowed pipeline_tools/** tests/** .gitattributes SKILL.md README.md references/** docs/tasks/task-sheet-archival.md .pipeline/task-sheet-archival/** --forbidden docs/goal.md pipeline_tools/contract.py docs/tasks/*.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "exit_code": 0, "evidence_ref": "executor-report.md"}], "assertions": ["the three-position resolver locates a sheet in docs/tasks, in its evidence directory and in the archive, reports an error for a duplicate id and an error for a missing sheet, and never guesses (acceptance-test-1)", "a terminal sheet in an evidence directory or in the archive raises no sheets_without_worktree warning, while a docs/tasks sheet without a worktree still does (acceptance-test-2)", "with .pipeline/archive/ present no scene entry and no leftover_evidence entry is named archive or closed-task (acceptance-test-3)", "a worktree whose sheet was archived still produces no worktrees_without_sheet error (acceptance-test-4)", "with the worktree deleted the sheet moves to .pipeline/demo/demo.md and stays tracked by git; while .worktrees/demo exists the step is blocked and no file moves; the repeated step is an idempotent no-op (acceptance-test-5)", "a task's own sheet under .pipeline/<id>/<id>.md and any .pipeline/archive/** path are not violations of the retained-name rule, while a different non-retained file in the same evidence directory is still a violation (acceptance-test-6)", "a CRLF .pipeline evidence file is committed byte for byte and read back unchanged from a fresh clone, the blob hash of an already committed evidence file is unchanged by adding the attribute, and ordinary text under * text=auto eol=lf is still normalized (acceptance-test-7)", "the documentation consistency check passes with SKILL.md at 0.18.0 and the new v0.17.0 -> v0.18.0 entry appended without rewriting history entries (acceptance-test-8)", "the full suite is green at 395 passed, 30 subtests passed, exit 0 (baseline 388 passed, 30 subtests passed plus the 7 acceptance cases added here)", "the reverse experiment fails the state-based judgement and the file is restored byte for byte (sha256 ab56b502...0902118 before and after)", "git status shows only the implementation files and this evidence directory; docs/tasks/*.md, docs/goal.md, pipeline_tools/contract.py and every other task's evidence directory are untouched"], "evidence_refs": ["executor-report.md", "executor-result.json"], "unverified": ["the sheet-move step is invoked as an explicit finalization step (planning.py archive_task_sheet) rather than folded into planning evidence-finalize; folding it in provably breaks the existing assertions listed in the report, so a reviewer must confirm this reading of the contract", "no historical sheets or evidence were migrated, by contract: the existing repository still keeps every in-flight sheet in docs/tasks/, so the post-mechanism scene classification of this repository is deliberately unchanged", "the archive fallback target .pipeline/archive/<task-id>.md is exercised only by the resolver tests and the archive scan tests; no acceptance test moves a sheet into the archive because acceptance-test-5 requires an evidence directory to exist", "the reviewer and main-final rounds, the pre-merge gate and the post-merge sequence have not been run for this task"]}
```
