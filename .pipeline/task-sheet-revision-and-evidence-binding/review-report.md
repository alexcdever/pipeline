# Review report (round 2)

```pipeline-evidence
{"schema":2,"task_id":"task-sheet-revision-and-evidence-binding","worktree":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","branch":"task-sheet-revision-and-evidence-binding","role":"reviewer","round":2,"status":"PASS","head":"45be2dbac64d1af49bcbdb8e385e72ac87c17a11","sheet_revision":1,"sheet_sha256":"a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783","observed_at_commit":"5de6c48b87574a31fa7203f7f923b86b3a3671df","generated_at":"2026-10-08T10:28:55Z","commands":[{"command":"git rev-parse --show-toplevel; git branch --show-current; git rev-parse HEAD","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git merge-base --is-ancestor 02a71a3b735e8a95358a7552a5f077fd3fb5ab22 HEAD","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pipeline_tools task validate docs/tasks/task-sheet-revision-and-evidence-binding.md","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k verification_surface_and_loosening","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amend_rejects_missing_or_cyclic_dependencies","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k evidence_validity_tracks_sheet_revision","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_record_is_append_only","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k plan_contract_consistency_uses_latest_revision","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amend_requires_main_agent_role","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python -m pytest -q","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"F2 negative experiment: SKILL.md version temporarily set to 0.15.0, then python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":1,"evidence_ref":"review-report.md"},{"command":"F2 restore: SKILL.md restored byte-identically (sha256 f2f8132...), then the same pytest selection","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python probe_f1.py (own harness: task-level evidence floor boundaries, lifecycle required_level)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python probe_f1_edges.py (own harness: non-integer/dict level shapes, raising the floor)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python probe1_amend.py (round-1 harness re-run against round-2 code)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python probe2_evidence.py (both evidence criteria, HEAD move vs verified path change)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python probe3_freshness.py (evidence_freshness both criteria + legacy identity.head rule)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md"},{"command":"python probe7_post_amend.py (freeze-check after a recorded amendment)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PYTHONPATH=<baseline 02a71a3 pipeline_tools> python legacy_reconcile.py <legacy fixture>; PYTHONPATH=<worktree> python legacy_reconcile.py <legacy fixture> (F4 A/B)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md"},{"command":"PYTHONPATH=<baseline> / <worktree> python legacy_reconcile.py <mismatched-revision fixture> (new criterion still active)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md"},{"command":"evidence_revision_status on the real task evidence (executor round 2 fresh, reviewer round 1 stale)","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git diff --name-only 02a71a3 45be2db","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git diff --check 02a71a3..45be2db","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git diff --name-only 02a71a3 5de6c48 -- docs/goal.md docs/tasks/security-scan-repair-20261001.md docs/tasks/security-scan-repair-20261001-continuation-1.md .pipeline/security-scan-repair-20261001 .pipeline/security-scan-repair-20261001-continuation-1 .env credentials","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"},{"command":"git reflog show --date=iso HEAD; git show --stat --oneline 45be2db 5de6c48; git status --porcelain","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md"}],"assertions":["round 1 finding F1 is fixed: lowering the task-level required_evidence_levels floor is now rejected without --adjudication (exit 3, no record) and accepted with it, recorded loosened=true with the adjudication reference","F1 boundaries behave: floor unchanged ([3]->[3,2], [2,3]->[3]) and floor raised ([2]->[3], [2]->[2,3]) are not loosening; dropping the highest element ([3,2]->[2]) and emptying the list are loosening; a lowered single acceptance-test evidence_level is still caught","the real consequence is closed: an un-adjudicated lowering leaves the lifecycle required_level at 3, and only the adjudicated revision moves it to 2","round 1 finding F2 is fixed: with SKILL.md reverted to 0.15.0 the documentation consistency case fails (exit 1, assertion names 0.16.0), and it passes again after the byte-identical restore","round 1 finding F4 is fixed: on legacy-shaped evidence (no sheet_revision/observed_at_commit) the round-2 code produces exactly the same status and error list as the 02a71a3 baseline, and the records are reported as unverified instead of stale","the new revision criterion is still active: evidence declaring a wrong sheet_revision still yields stale records and blocking revision errors, and bound evidence whose verified resource changed is still stale","all ten acceptance commands exit 0, and the full suite is 379 passed / 28 subtests passed (exit 0), matching the executor claim","every changed path between 02a71a3 and 45be2db is inside allowed_paths, forbidden_paths are untouched across 02a71a3..5de6c48, git diff --check is clean, and no historical task sheet or evidence was modified","the executor round-2 evidence command with exit_code 1 is the deliberate F2 negative experiment (SKILL.md temporarily reverted to 0.15.0), not a real failure; I reproduced it independently","the round-2 evidence is honestly bound: the sheet hash still matches a12f29a7..., executor round-2 evidence is fresh, and the round-1 reviewer evidence is correctly stale because the fix changed the paths it verifies"],"evidence_refs":["review-report.md","executor-report.md","executor-result.json"],"unverified":["the 367-passed baseline figure of round 1 was not re-run at 02a71a3 (only the +2 test-method delta is accounted for)","whether any consumer other than pipeline_tools reads the rewritten documentation paragraphs (contract unknown-2)","post-merge main-worktree re-verification of this task","residual risk noted in O1: a revision-bound record that omits observed_at_commit skips the changed-path criterion and is surfaced only in reconcile's unverified list, which no gate currently reads"],"blockers":[],"recommendation":"PASS. F1, F2 and F4 are all fixed and independently reproduced, the ten acceptance tests and the full suite (379 passed / 28 subtests) are green, scope and history are intact, and the fix introduced no new weakening. Two non-blocking observations for the main agent: (O1) reconcile can report PASS with the changed-path criterion unevaluated (unverified) when a revision-bound record omits observed_at_commit, and (O2) the F1 fix is a behaviour change to the loosening criterion, so the amended criterion wording in README/SKILL/references/templates should be reviewed once by the main agent."}
```

## 结论摘要

**PASS**。上一轮的三条 findings（F1 阻塞项、F2、F4）全部修复并经我自建夹具独立复现；十条验收测试全绿；全量测试 **379 passed, 28 subtests passed**（退出码 0），与执行子代理声明一致；范围与历史零越界；修复没有引入新的削弱，只留下两条不阻塞的观察（O1/O2，见文末）。

---

## 环境检查（逐项）

| # | 检查 | 结果 |
|---|---|---|
| 1 | `git rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding` ✔ |
| 2 | `git branch --show-current` | `task-sheet-revision-and-evidence-binding` ✔ |
| 3 | `git rev-parse HEAD` | `5de6c48b87574a31fa7203f7f923b86b3a3671df` ✔ |
| 4 | `git merge-base --is-ancestor 02a71a3 HEAD` | 退出码 0 ✔ |
| 5 | `python -m pipeline_tools task validate docs/tasks/task-sheet-revision-and-evidence-binding.md` | `PASS`，退出码 0 ✔ |
| 6 | 只读产品代码；临时改动全部还原 | ✔（F2 的临时改版本号已按字节还原，`git status --porcelain` 空） |

审查对象链：`02a71a3` → `7b647f1` → `753f0a6` → `e525d80`（round 1 执行证据）→ `ec560ba`（round 1 审查证据）→ **`45be2db`（本轮实现 head）** → `5de6c48`（round 2 执行证据）。
修复范围 `git diff --stat 753f0a6..45be2db`：`core.py` +88/-…、`reconcile.py`、5 份文档 + 模板、`test_acceptance_id_and_template_compliance.py`、`test_task_sheet_amendment.py`（新增 2 个测试方法）。

---

## F1（上一轮阻塞项）：任务级证据下限已纳入放松判据 ✅ 修复

`_contract_loosened(previous, current, changes)` 现在比较 `required_evidence_floor = max(required_evidence_levels)`，下降即 `loosened`。我用自己的夹具（自建仓库，未复用执行子代理的测试辅助函数）逐项复验：

| 场景（单条 `acceptance_tests[].evidence_level` 均保持 3 不变） | 结果 |
|---|---|
| `[3]→[2]`，**不带** `--adjudication` | **blocked**，退出码 3，`loosening the contract requires --adjudication`，`amendments.json` **未创建** |
| `[3]→[2]`，带 `--adjudication docs/decisions/evidence-floor.md` | **pass**，`loosened=true`、`verification_surface_changed=true`、`changes.required_evidence_levels={added:[2],removed:[3]}`、`adjudication_ref` 记录在案 |
| `[3]→[3,2]`（下限不变、元素增加） | pass，`loosened=false` |
| `[2,3]→[3]`（下限不变、元素减少） | pass，`loosened=false` |
| `[2]→[3]`（下限上升） | pass，`loosened=false`，`surface=true` |
| `[2]→[2,3]`（新增更严测试抬高下限） | pass，`loosened=false` |
| `[3,2]→[2]`（删除最高元素导致下限下降） | **blocked**（放松） |
| `[3]→[]`（下限整体移除） | **blocked**（放松） |
| 单条 `evidence_level` 3→2（上一轮场景） | **blocked**（仍被抓住） |
| `required_evidence_levels: ["3"]` / `{"levels":[2]}`（非整数/错形状） | `config`，契约校验拒绝（`required_evidence_levels must contain integers 1-5`），无法把下限"投毒"成 None |

**真实后果已消除**（我用 `task_lifecycle` 直接观测，不只是看分类字段）：
- 冻结时 `required_evidence_levels=[3]`，`init_task` 后 `lifecycle_status(...)["evidence"]["required_level"] == 3`，状态 `pass`。
- 未带裁决的下调被拒后（把任务单还原为冻结版本），`required_level` 仍为 **3**。
- 补裁决后同一修订被接受，`lifecycle_status` 的 `required_level` 才降到 **2** —— 分类与真实后果一致。

补充说明：被拒绝时工具**不会回写调用方改过的任务单**（这是契约规定的"不移动任何文件"），所以我先还原文件再读 lifecycle；这不是缺陷。

## F2：版本号断言已恢复约束力 ✅ 修复

断言从 `assertRegex(r"version: 0\.\d+\.\d+")` 改为解析 `^version: (\d+)\.(\d+)\.(\d+)$` 并要求 `>= (0,16,0)`。我按指示在 worktree 内做了一次临时回退实验（先备份字节，事后还原）：

| 步骤 | 命令 | 退出码 |
|---|---|---|
| `SKILL.md` 临时改为 `version: 0.15.0` | `pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | **1**，`AssertionError: (0, 15, 0) not greater than or equal to (0, 16, 0) : SKILL.md version must be at least 0.16.0 (found version: 0.15.0)` |
| 还原为 `0.16.0` | 同一命令 | **0** |

还原是字节级的：改动前后 `sha256(SKILL.md)` 都是 `f2f81325079dc496e0fb8ef2ed9db4232b112e377b5fb9f99127f00a063ae15d`，`git status --porcelain` 为空。

## F4：历史形态证据不再新增错误 ✅ 修复

`evidence_revision_status` 改为只对**声明了 `sheet_revision`** 的记录应用修订判据；未声明的记录进 `unverified` 而不是 `errors`。用上一轮的 A/B 手法（`git archive 02a71a3 pipeline_tools` 抽基线代码 vs 本轮代码，对同一夹具跑 `reconcile_task`）：

| 夹具 | 02a71a3 基线 | round 2 代码 |
|---|---|---|
| 历史形态（无 `sheet_revision`/`observed_at_commit`） | `BLOCKED`，errors `['missing or invalid finalization.json','main worktree post-merge re-verification is missing']` | **完全相同的 status 与 errors**；6 条记录 `stale=false`，另在 `unverified` 注明"未被修订判据覆盖" |
| 携带正确修订绑定 | 同上 | **identical**（无误伤） |
| 携带**错误**修订号（`revision+1`） | 同上（基线根本不读该字段） | 追加 6 条 `produced against task sheet revision 2 but the current revision is 1`，记录 `stale=true` |

→ 新判据没有被整体关掉，只是不再因"缺字段"本身报错。

**同时复核了上一轮的新判据仍然生效**（我自己的夹具重跑）：
- 只提交无关路径、HEAD 前移 → 证据 `stale=false`；提交被验证资源 `pipeline_tools/alpha.py` → `stale=true` 且原因指名该路径。
- 新增任务单修订后，旧证据 `produced against task sheet revision 1 but the current revision is 2`。
- `evidence_freshness` 两条判据分别可观测，旧 `identity.head` 口径仍报 `result HEAD is stale`。

**真实产物上的端到端验证**（值得单独记录）：对本任务真实证据直接跑 `evidence_revision_status`（只读）——
- 任务单哈希仍为 `a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783`，与两份执行/审查证据声明的 `sheet_sha256` 一致，`sheet_revision=1`。
- round 2 执行证据（`observed_at_commit=45be2db`）→ **fresh**（其后的 `5de6c48` 只改了 `.pipeline/<task-id>/**`，不与任何 operation 的 `resources` 相交）。
- round 1 审查证据（我的 `review-report.md`/`reviewer-result.json`，`observed_at_commit=e525d80`）→ **stale**，原因是 round 2 的实现提交修改了它验证的路径（`pipeline_tools/core.py`、`pipeline_tools/reconcile.py`、`tests/…` 等）。这正是"修复让上一轮审查失效、必须重审"的机械体现，说明判据在真实证据上工作正常。

## 复跑上一轮的全部行为（回归）

round 2 代码上重跑我上一轮的 4 个自建探针，**除 F4 意图内的差异外全部一致**：
- `probe1_amend.py`（退出码 0）：放松闸门 1a/1b/1c/1d、静默篡改报漂移（退出码 4）、身份字段四种构造全拒、lifecycle 漂移、依赖四条、追加式字节与哈希链 —— 与 round 1 相同。
- `probe2_evidence.py`（退出码 0）：A/B/C 两条判据、F 修订使证据失效 —— 相同；仅 G（无 `sheet_revision`）从 `stale=true` 变为 `stale=false`，即 F4 的预期修复。
- `probe3_freshness.py`（退出码 0）：freshness 两条判据 + 旧 `identity.head` 规则 —— 相同。
- `probe7_post_amend.py`（退出码 0）：登记修订后 `freeze-check` 退出码 0（幂等）—— 相同。

---

## 十条验收测试（逐条亲自运行）

cwd = worktree 根；`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

| # | 命令（`python -m pytest -q …`） | 退出码 | 结果 |
|---|---|---|---|
| 1 | `tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence` | 0 | 1 passed（11 deselected） |
| 2 | `… -k identity_fields_are_not_amendable` | 0 | 1 passed, 4 subtests passed |
| 3 | `… -k verification_surface_and_loosening` | 0 | 1 passed |
| 4 | `… -k amend_rejects_missing_or_cyclic_dependencies` | 0 | 1 passed, 2 subtests passed |
| 5 | `tests/test_git_checks.py -k task_sheet_change_after_freeze` | 0 | 1 passed |
| 6 | `… -k evidence_validity_tracks_sheet_revision` | 0 | 1 passed |
| 7 | `… -k amendment_record_is_append_only` | 0 | 1 passed |
| 8 | `… -k plan_contract_consistency_uses_latest_revision` | 0 | 1 passed |
| 9 | `… -k amend_requires_main_agent_role` | 0 | 1 passed, 2 subtests passed |
| 10 | `tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | 1 passed |

（`tests/test_task_sheet_amendment.py` 现有 12 个用例，故 `-k` 显示 11 deselected，比 round 1 多 2 个。）

## 全量测试

- 命令：`python -m pytest -q`（cwd = worktree 根）
- 结果：**`379 passed, 28 subtests passed in 462.19s (0:07:42)`，退出码 0**
- 与执行子代理声明的 **379 passed, 28 subtests passed 一致**。相对 round 1 的 377 增加 2，正好对应新增的 `test_loosening_covers_the_task_level_evidence_floor` 与 `test_legacy_evidence_without_revision_fields_keeps_its_verdict`，没有测试被删除或跳过。

## 范围与历史卫生

| 检查 | 结果 |
|---|---|
| `git diff --name-only 02a71a3 45be2db`（20 个路径） | **全部在 `allowed_paths` 内**：`.pipeline/task-sheet-revision-and-evidence-binding/**`（含我 round 1 的两份审查证据）、`README.md`、`SKILL.md`、`pipeline_tools/{__main__,core,planning,reconcile,task_lifecycle}.py`、`references/{acceptance-evidence,compat-and-migration,execution-and-review,merge-and-recovery,task-design}.md`、`templates/{pipeline-evidence.json,task-sheet.md}`、`tests/test_{acceptance_id_and_template_compliance,task_sheet_amendment}.py` |
| `git diff --check 02a71a3..45be2db` | 退出码 0（无空白错误） |
| `forbidden_paths` 在 `02a71a3..5de6c48` | **零改动**（`docs/goal.md`、两张 security-scan 任务单、两个 security-scan 证据目录、`.env`、`credentials` 全部无输出） |
| 历史任务单/证据 | 分支尖端 diff 只含上述实现文件 + 本任务证据目录；`docs/tasks/**` 无历史任务单被改（本任务单本身在两轮中都未被修订，revision 仍为 1） |
| 历史改写 | `git reflog` 显示 `45be2db`、`5de6c48` 都是 `ec560ba` 的线性后继；round 1 的 `ec560ba` 仍在链上且哈希未变；`45be2db` 只改实现/文档/测试，`5de6c48` 只改两份证据文件（+66/−16 行） |
| 临时文件 | 无残留；`git status --porcelain` 空（本轮测试日志写在 `C:/Users/alexc/AppData/Local/Temp/reviewer-probe/fullsuite2.log`） |

## 4.4 那条 `exit_code: 1` 的命令：查明结论

它是**执行子代理 round 2 证据里刻意构造的反向实验**，不是真实失败。证据块中原样写着：

```
"command": "SKILL.md version temporarily set to 0.15.0, then: python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_cur…", "exit_code": 1
"command": "SKILL.md restored to 0.16.0, then: python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "exit_code": 0
```

即"先把版本号退回旧值证明断言会失败，再还原证明会通过"，紧跟着的还原命令退出码 0。我**独立复现**了同一实验（见 F2 小节）：回退版本号 → 退出码 1 且断言信息点名 `>= (0, 16, 0)`；字节级还原后 → 退出码 0。结论：该 `exit_code: 1` 是证明断言有力的反向证据，不是回归失败，也不影响任何验收结论。

---

## 上一轮 findings 状态与新观察

| 编号 | 内容 | 本轮状态 |
|---|---|---|
| F1 | 任务级 `required_evidence_levels` 下调绕过放松闸门 | **已修复**，含边界与真实后果复验（见上） |
| F2 | 文档断言的版本号检查无保证 | **已修复**，回退版本号会失败，还原后通过 |
| F3 | 删除整个 operation / 收窄 `resources` 只算验证面变更（不违反契约明文） | 未改动；执行子代理在证据里明确说明"契约判据二是穷举清单，扩大需主代理裁决"——我认可以为依据契约的正确处置，不算缺陷 |
| F4 | 历史形态证据在新代码下新增错误 | **已修复**，与 02a71a3 基线判定完全一致，同时新判据仍生效 |

### O1（观察，非缺陷）修订绑定证据缺 `observed_at_commit` 时路径判据不执行
复验（我的夹具，全套证据声明 `sheet_revision`/`sheet_sha256` 但都不声明 `observed_at_commit`）：
`errors` 只剩与本次改动无关的两条（`missing or invalid finalization.json`、`main worktree post-merge re-verification is missing`），6 条记录 `revision_bound=true`、`changed_paths_judged=false`、`stale=false`、`reasons=[]`，而 `unverified` 列出 6 条 `"… does not record the commit it was observed at; the changed-path criterion was not evaluated"`。
即：这类证据的"被验证路径是否变化"判据**不执行也不阻塞**，只在 `unverified` 里注明。契约明文是"证据与报告的有效性判据是 `sheet_revision` 加 `sheet_sha256`；`observed_at_commit` 只作事实记录"，而 `direct_pass` 只要求 `not revision_errors`，所以这与契约一致、且是 round 2 有意的兼容设计（`references/compat-and-migration.md` 已写明）。残留风险仅在于：若某个消费者只读 `status`/`errors` 而不读 `unverified`，可能在路径判据未执行的情况下看到 PASS。建议主代理知悉；是否收紧（例如让 revision 绑定证据缺 commit 时进入 blocking）属契约层决策。

### O2（观察，非缺陷）F1 是判据行为变更，文档口径需主代理确认
本轮把"降低任务级证据下限"新增为放松情形，并同步改了 `README.md`、`SKILL.md`、`references/{task-design,execution-and-review,compat-and-migration}.md`、`templates/task-sheet.md`（措辞一致，均写"含任务级 `required_evidence_levels` 的下限""下限上升不算放松"）。这些改动都在 `allowed_paths` 内、且文档一致性用例通过；我逐句核对未发现与实现不符之处。因为属于判据语义的正式变更，建议主代理按 final-check 再确认一次口径即可。

### O3（提示）本任务自身没有修订记录
`task_sheet_revision(root, task-id)` = `(1, None)`：本任务从未 `task amend`，且当前 worktree 下没有 `.pipeline/<task-id>/goal.json`（round 1 我运行 `freeze-check` 时它被生成、我在收尾时删除，round 2 未再生成）。因此工具此刻无法比对证据声明的 `sheet_sha256`（基线为 None），只能比对修订号；`freeze_check` 一旦运行会重新落盘基线（round 1 实测退出码 0、`PASS`，其临时状态文件已清理，`git status --porcelain` 为空）。不影响结论，仅提示证据哈希比对的基线依赖该状态文件存在。

---

## unverified / blockers

**unverified**
- round 1 声明的基线 367 passed 未重跑（仅核对了 +2 用例的差异来源）。
- 契约 unknown-2：是否有 pipeline_tools 之外的消费者依赖被改写段落的旧措辞。
- 合并后主工作树复验（post-merge re-verification）——按流程属主代理动作。
- O1 的残留风险（路径判据未执行时只有 `unverified` 提示）。

**blockers**：无。

**findings**：无阻塞级缺陷。F1/F2/F4 已修复；F3 为契约穷举清单范围内的既定处置；O1/O2/O3 仅为观察与提示。

## 只读与清理声明

全程未修改产品/测试/文档/任务单文件（唯一例外是 F2 要求的 `SKILL.md` 临时改版本号，已按字节还原并验证 `sha256` 一致、`git status` 干净）；未新建 worktree；主工作树只有 `git log/show/status` 与读取，零改动；除本目录的两份交付文件外没有写入任何文件。
