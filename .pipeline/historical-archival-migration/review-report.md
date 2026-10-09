# 审查报告：historical-archival-migration（revision 2）

- task_id: `historical-archival-migration`
- role: reviewer
- worktree: `D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration`
- branch: `historical-archival-migration`
- 被审 HEAD: `c81330a63f6d26166aaab56e23219063c943329e`
- 基线: `de5c6c87225bcfcd094dbc6b5d452f82feb8625c`
- 任务单: revision 2
- 轮次: 2
- observed_at_commit: `c81330a63f6d26166aaab56e23219063c943329e`（产生本证据时的分支尖端）
- 状态: **PASS**

复验方式：全部命令由审查者本人在 worktree 根目录独立运行；不采信执行报告的结论。审查工作树 `git status --porcelain` 干净。

## 1. 五条验收命令（审查者独立运行，真实退出码）

| 验收 | 命令（cwd = worktree 根） | 真实退出码 | 输出摘要 |
| --- | --- | --- | --- |
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked` | **0** | 1 passed, 61 deselected |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree` | **0** | 1 passed, 61 deselected |
| acceptance-test-3 | `python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover` | **0** | 1 passed, 61 deselected |
| acceptance-test-4 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | **0** | 1 passed, 27 deselected |
| acceptance-test-5 | `python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration` | **0** | 1 passed, 54 deselected |

退出码序列：1→0，2→0，3→0，4→0，5→0。

## 2. 断言是否真的在断言（读源码 + 变异测试）

四张新增/断言用例（1/2/3/5）均基于 `tempfile.TemporaryDirectory()` 构造真实 Git 仓库夹具（`PlanningTests._scene_repo`/`_commit_all`、`EvidenceTests._make_git_repo`/`_git`），不依赖本 worktree 的偶然事实，也没有断言真实仓库里 `sheets_without_worktree` 为空。

为排除“恒真”可能，审查者在 worktree 之外的临时副本上做了定点变异（改后即还原，未触碰被审代码）：

| 变异 | 目标用例 | 结果 |
| --- | --- | --- |
| `sheets_without_worktree` 计算由 `set(active) - set(worktrees)` 改为 `known - set(worktrees)`（把终态/归档单计入） | at2 | **FAILED**（`AssertionError`，tests/test_planning.py:1684） |
| `leftover_evidence` 由 `set(evidence) - known` 改为 `set(evidence) - set(active)` | at3 | **FAILED**（tests/test_planning.py:1731） |
| `archive_task_sheet` 强制 `tracked = False`（走非 `git mv` 分支） | at1 | **FAILED** |
| 移动后追加字节改写目标文件 | at1 | **FAILED** |
| `retained_evidence_snapshot` 额外纳入 `<task-id>.md` | at5 | **FAILED**（tests/test_evidence.py:1307） |

结论：at1/at2/at3/at5 都会因相应行为回归而真实失败，非恒真。at4 为新增的字面断言块（`assertIn("只放"|"进行中或待派发"|".pipeline/<task-id>/<task-id>.md"|".pipeline/archive/<task-id>.md")` 三处文档 + `assertFalse(docs/tasks/README.md 存在)`），缺任一处即失败，属真实断言（tests/test_acceptance_id_and_template_compliance.py:383-393）。

## 3. 字节不变（审查者独立复算 sha256）

对每张抽样单：`git show <基线>:<原路径> | sha256sum` 与迁移后目标文件 `sha256sum` 比对。

| 原路径（基线） | 迁移后路径 | sha256 | 结论 |
| --- | --- | --- | --- |
| `docs/tasks/repository-evidence-hygiene.md` | `.pipeline/repository-evidence-hygiene-continuation-5/repository-evidence-hygiene-continuation-5.md` | `cf458bd9…` | 一致 |
| `docs/tasks/pipeline-tools-v1.md` | `.pipeline/pipeline-tools-v1/pipeline-tools-v1.md` | `308b5743…` | 一致 |
| `docs/tasks/implement-plan-coverage-repair-continuation-1.md` | `.pipeline/archive/implement-plan-coverage-repair-continuation-1.md` | `252a1cdd…` | 一致 |
| `docs/tasks/pipeline-evidence-lifecycle-migration.md` | `.pipeline/archive/pipeline-evidence-lifecycle-migration.md` | `aa9bae30…` | 一致 |
| `docs/tasks/task-sheet-archival.md` | `.pipeline/task-sheet-archival/task-sheet-archival.md` | `5f3c92d8…` | 一致 |
| `docs/tasks/toolchain-freshness-fixes.md` | `.pipeline/toolchain-freshness-fixes/toolchain-freshness-fixes.md` | `8bcc46f1…` | 一致 |
| `docs/tasks/acceptance-id-and-template-compliance.md` | `.pipeline/acceptance-id-and-template-compliance/acceptance-id-and-template-compliance.md` | `2329761b…` | 一致 |

7/7 完全一致，含按声明 id 改名的 `repository-evidence-hygiene.md`。另有全局证据：`git diff --name-status -M <基线> <HEAD>` 中 **46 条全部为 `R100`**（100% 相似度重命名），即全量 46 张单子逐字节未变。

## 4. 最终状态

- `git ls-tree <基线> docs/tasks/` = **48**；`git ls-tree <HEAD> docs/tasks/` = **2**；`R100` 重命名 = **46**。
- `docs/tasks/` 仅剩 `historical-archival-migration.md`、`security-scan-repair-20261001.md`（两张在途单）。
- `.pipeline/archive/` 仅 2 张：`implement-plan-coverage-repair-continuation-1.md`、`pipeline-evidence-lifecycle-migration.md`。
- `.pipeline/repository-evidence-hygiene-continuation-5/repository-evidence-hygiene-continuation-5.md` 存在。
- `docs/tasks/README.md` **不存在**；`docs/tasks/` 下无任何非 `.md` 文件。

## 5. preflight 场景（审查者运行）

`python -m pipeline_tools planning preflight .` → 退出码 0，`status=pass`，`errors=[]`：

- `task_scenes.leftover_evidence` = `[]`（无遗留证据目录）
- `task_scenes.worktrees_without_sheet` = `[]`
- `task_scenes.sheets_without_worktree` = `["historical-archival-migration", "security-scan-repair-20261001"]`（仅两张在途单，无幻影单 `README`）
- `task_scenes.uncommitted_sheets` = `[]`

## 6. `tests/test_cli.py` 的修复

`test_json_output_has_common_envelope_and_can_be_saved`（tests/test_cli.py:294）与 `test_task_validate_real_sheet`（tests/test_cli.py:911）原先硬编码 `ROOT/'docs'/'tasks'/'pipeline-tools-v1.md'`，现改为 `real_sheet('pipeline-tools-v1')`，经 `pipeline_tools.planning.task_sheet_resolution` 三位置定位。断言**行为未被削弱**：仍断言 `returncode == 0`、JSON 封套 `schema==1` 与 `--output` 落盘、以及 `task validate` 对真实单子退出 0 / 对 `nope.md` 退出 2。这两条在全量回归中通过。

## 7. 文档一致性（审查者逐处核对）

`README.md:14`、`SKILL.md:92`、`references/merge-and-recovery.md:65-68` 三处均写明：

- `docs/tasks/` 只放**进行中或待派发**的任务单，不放 README 之类说明文件；
- 终态单子在其证据目录 `.pipeline/<task-id>/<task-id>.md`，没有证据目录时在 `.pipeline/archive/<task-id>.md`；
- 按声明 id 归档，文件名与声明 id 不符时以声明 id 为准。

三处口径一致，且**没有任何文档反过来指示往 `docs/tasks/` 放 README**（全仓 grep `docs/tasks/README` 只命中任务单自身的“不新增”条款、测试断言与注释）。

## 8. 范围检查

`git diff --name-only <基线> <HEAD>` 全部路径经 fnmatch 对照契约 `allowed_paths`/`forbidden_paths`：**无越界**（violations: none）。具体：

- 未改 `pipeline_tools/**`、`docs/goal.md`、`.worktrees/**`、任何 `.env`/`credentials/**`；
- **没有任何 `finalization.json` 出现在 diff 中**（保留集与标记文件逐字未动）；
- 唯有 `docs/tasks/historical-archival-migration.md` 是本任务自身单子的 rev1→rev2 修订（属 `docs/tasks/**`，且是契约修订的一部分）；除它之外的 46 张单子全部为 `R100` 纯重命名。

## 9. 证据卫生

`git ls-files .pipeline/historical-archival-migration/` 仅两项：`executor-report.md`、`executor-result.json`（均为保留名）。无原始日志（`acceptance-*.log`、`preflight.log`、`migration-map.json` 等）被跟踪——这些在 `c81330a` 中已被删除。工作树 `git status --porcelain` 为空。

## 10. 全量回归（审查者独立运行）

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q
399 passed, 30 subtests passed in 416.55s (0:06:56)
退出码 0
```

与基线 395 passed 相比，本任务新增 4 个用例 → 399 passed、**0 failed**。数字与执行报告一致。

## 11. 已关闭标记复核（补充验证）

审查者遍历全部 24 个含 `finalization.json` 的证据目录调用 `verify_finalization_snapshot`：

- **`finalization retained evidence hash mismatch`：0 例**（保留集哈希无失配）。
- 13 个标记报 `retained evidence snapshot is missing` / `identity snapshot is missing`（旧 schema 标记）；11 个标记报 `head/branch/worktree is stale`。这些标记文件均**未出现在本次 diff 中**，属迁移前既存状态，非本任务引入的漂移。

## 12. 发现与观察（均不构成失败）

1. 执行报告机器区块记录的 `head`/`observed_at_commit` = `f552b13`（实现提交），被审分支尖端为 `c81330a`（仅证据提交）。经 `head_advanced_by_evidence_only(root, f552b13, c81330a)` 复算为 **True**，即该推进是纯证据推进，标记不会因此被判 stale，语义自洽。
2. 上述 24 个标记中的既存 stale / missing-snapshot 状态与本任务无关，但如果主代理后续要达成全仓标记健康，需另行处理（超出本任务范围）。

## 13. 未验证项

- 未对全部 46 张单子逐张复算 sha256（抽样 7 张已全部一致，且 `git diff -M` 的 46 条 `R100` 是更强的全量字节不变证据）。
- 全量回归在 shell 后台运行（416s）取得，未走 `command run`；5 条验收命令均直接运行且远低于超时。

```pipeline-evidence
{"schema": 2, "task_id": "historical-archival-migration", "worktree": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "branch": "historical-archival-migration", "role": "reviewer", "round": 1, "status": "PASS", "head": "c81330a63f6d26166aaab56e23219063c943329e", "sheet_revision": 2, "sheet_sha256": "4b43c666817ffeaa4d4518addc65524b448469aba88498c0dc5e5684c06ed497", "observed_at_commit": "c81330a63f6d26166aaab56e23219063c943329e", "generated_at": "2026-10-09T07:38:47Z", "commands": [{"command": "git rev-parse HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pipeline_tools planning preflight .", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "git diff --name-status -M de5c6c87225bcfcd094dbc6b5d452f82feb8625c c81330a63f6d26166aaab56e23219063c943329e", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "git diff --name-only de5c6c87225bcfcd094dbc6b5d452f82feb8625c c81330a63f6d26166aaab56e23219063c943329e | python - (fnmatch against the contract allowed_paths/forbidden_paths)", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "bash: git show <baseline>:<path> | sha256sum vs sha256sum <migrated path> (7 sampled sheets, incl. the renamed repository-evidence-hygiene sheet)", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "git ls-tree --name-only <baseline|HEAD> docs/tasks/ | wc -l (48 -> 2) and git ls-files .pipeline/archive", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "git ls-files .pipeline/historical-archival-migration/", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python - (verify_finalization_snapshot over all 24 .pipeline/*/finalization.json markers)", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python - (head_advanced_by_evidence_only(root, f552b13, c81330a))", "cwd": "D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration", "exit_code": 0, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked  # on a throwaway copy with archive_task_sheet forced to an untracked move", "cwd": "<temp copy of the worktree>", "exit_code": 1, "expected_exit_code": 1, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked  # on a throwaway copy with a byte rewrite after the move", "cwd": "<temp copy of the worktree>", "exit_code": 1, "expected_exit_code": 1, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree  # on a throwaway copy counting archived sheets as in-flight", "cwd": "<temp copy of the worktree>", "exit_code": 1, "expected_exit_code": 1, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover  # on a throwaway copy where leftover_evidence ignores archived sheets", "cwd": "<temp copy of the worktree>", "exit_code": 1, "expected_exit_code": 1, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration  # on a throwaway copy whose retained snapshot includes the task sheet", "cwd": "<temp copy of the worktree>", "exit_code": 1, "expected_exit_code": 1, "evidence_ref": ".pipeline/historical-archival-migration/review-report.md"}], "assertions": ["all five contract acceptance commands exit 0, run directly from the worktree root by the reviewer (at1, at2, at3, at4, at5 each 0)", "the full suite exits 0 at 399 passed, 30 subtests passed, 0 failed, matching the baseline of 395 passed plus this task's 4 new cases", "7 sampled sheets have byte-identical sha256 before and after (git show <baseline>:<path> vs the migrated file), including the renamed docs/tasks/repository-evidence-hygiene.md -> .pipeline/repository-evidence-hygiene-continuation-5/repository-evidence-hygiene-continuation-5.md", "all 46 baseline..HEAD migration entries are R100 (100% similarity renames), the whole-diff proof that no sheet byte changed", "docs/tasks/ holds exactly the two in-flight sheets (48 -> 2), .pipeline/archive/ holds exactly the two terminal sheets with no evidence directory, docs/tasks/README.md does not exist, and planning preflight reports leftover_evidence=[] and worktrees_without_sheet=[] with sheets_without_worktree=[historical-archival-migration, security-scan-repair-20261001] and no phantom README", "every changed path is inside the contract allowed_paths: no pipeline_tools/**, docs/goal.md, .worktrees/**, and no finalization.json appears anywhere in the diff", "mutation tests on a throwaway copy show the new tests are not tautological: counting archived sheets as in-flight fails at2, ignoring archived sheets in leftover_evidence fails at3, an untracked move and a byte rewrite each fail at1, and a retained snapshot that includes the task sheet fails at5", "verify_finalization_snapshot over all 24 finalization.json markers yields 0 'finalization retained evidence hash mismatch' results; the observed stale and missing-snapshot entries are pre-existing because no finalization.json appears in the diff", "tests/test_cli.py now resolves pipeline-tools-v1 through pipeline_tools.planning.task_sheet_resolution while keeping its behavioural assertions (returncode 0, JSON envelope, --output persistence, and exit 2 for nope.md)", "README.md, SKILL.md and references/merge-and-recovery.md all state the worklist convention with one voice and none instructs placing a README under docs/tasks/"], "evidence_refs": ["review-report.md", "reviewer-result.json"], "unverified": ["only 7 of the 46 migrated sheets were re-hashed by hand (including the renamed repository-evidence-hygiene sheet); byte-identity for the rest rests on the stronger whole-diff signal that all 46 baseline..HEAD entries are R100", "mutation testing that proves the new tests fail on regression was run on a throwaway copy of the tree, which has been deleted", "the full regression (399 passed, 30 subtests passed, 0 failed, exit 0) was run directly from the shell rather than through command run, because it takes about 417s and command run's default timeout is 180s", "13 of the 24 finalization markers report a missing retained/identity snapshot and 11 report a stale head/branch/worktree; these are pre-existing and left untouched by this task"], "blockers": [], "recommendation": "ready_for_finalization"}
```
