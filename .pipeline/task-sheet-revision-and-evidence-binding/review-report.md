# Review report

```pipeline-evidence
{"schema":2,"task_id":"task-sheet-revision-and-evidence-binding","worktree":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","branch":"task-sheet-revision-and-evidence-binding","role":"reviewer","round":1,"status":"FAIL","head":"753f0a6aca79bf1de80a241dc2c5277636a795a3","sheet_revision":1,"sheet_sha256":"a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783","observed_at_commit":"e525d802c83ab277135381b179045bf03886794d","generated_at":"2026-10-08T09:51:44Z","commands":[{"command":"git rev-parse --show-toplevel; git branch --show-current; git rev-parse HEAD","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#环境检查"},{"command":"git merge-base --is-ancestor 02a71a3b735e8a95358a7552a5f077fd3fb5ab22 HEAD","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#环境检查"},{"command":"python -m pipeline_tools task validate docs/tasks/task-sheet-revision-and-evidence-binding.md","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#环境检查"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试1"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试2"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k verification_surface_and_loosening","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试3"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amend_rejects_missing_or_cyclic_dependencies","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试4"},{"command":"python -m pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试5"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k evidence_validity_tracks_sheet_revision","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试6"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_record_is_append_only","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试7"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k plan_contract_consistency_uses_latest_revision","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试8"},{"command":"python -m pytest -q tests/test_task_sheet_amendment.py -k amend_requires_main_agent_role","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试9"},{"command":"python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#验收测试10"},{"command":"python -m pytest -q","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#全量测试"},{"command":"python -m pytest -q tests/test_git_checks.py tests/test_evidence.py tests/test_task_evidence_reconcile.py tests/test_metrics.py tests/test_security_repairs.py tests/test_task_lifecycle.py tests/test_worktree_dispatch_identity.py","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#高风险点7"},{"command":"git diff --name-only 02a71a3 753f0a6","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#范围与历史卫生"},{"command":"git diff --check 02a71a3..753f0a6","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#范围与历史卫生"},{"command":"git diff --name-only 02a71a3 e525d80 -- docs/goal.md docs/tasks/security-scan-repair-20261001.md docs/tasks/security-scan-repair-20261001-continuation-1.md .pipeline/security-scan-repair-20261001 .pipeline/security-scan-repair-20261001-continuation-1 .env credentials","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#范围与历史卫生"},{"command":"git reflog show --date=iso HEAD; git log --oneline -8; git -C D:/Projects/Skills/pipeline log --oneline -3","cwd":"D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding","exit_code":0,"evidence_ref":"review-report.md#范围与历史卫生"},{"command":"IMPL_WORKTREE=<worktree> PYTHONPATH=<worktree> python probe1_amend.py (own harness: loosening gate, silent tamper, identity, lifecycle, dependencies, append-only)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md#高风险点1"},{"command":"IMPL_WORKTREE=<worktree> PYTHONPATH=<worktree> python probe2_evidence.py (own harness: evidence validity on both criteria)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md#高风险点6"},{"command":"PYTHONPATH=<baseline-02a71a3> python legacy_reconcile.py <fixture>; PYTHONPATH=<worktree> python legacy_reconcile.py <fixture>","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md#高风险点7"},{"command":"IMPL_WORKTREE=<worktree> PYTHONPATH=<worktree> python minimal_repro.py (FAIL reproduction)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md#findings"},{"command":"PYTHONPATH=<worktree> python -m pytest -q doccheck/tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract (doc-assertion sensitivity A/B)","cwd":"C:/Users/alexc/AppData/Local/Temp/reviewer-probe","exit_code":0,"evidence_ref":"review-report.md#高风险点8"}],"assertions":["all ten acceptance commands exit 0 on the frozen sheet revision 1 and commit 753f0a6","the full suite is green: 377 passed, 28 subtests passed, exit 0 (matches the executor claim)","the loosening gate rejects a deleted acceptance test without --adjudication (exit 3, no record, no hash change) and accepts it with one","a prose-only amendment needs neither adjudication nor raises either criterion","a direct task sheet edit that never went through task amend still reports task sheet changed after freeze (exit 4) and still blocks the lifecycle reader","identity fields (task_type, task_id) are rejected even when the tamper is committed so that HEAD agrees with it","dependencies: missing id, cycle, and a sheet without a contract are all rejected; a legal dependency is accepted","evidence validity was observed on both criteria separately: HEAD moving over an unrelated path keeps evidence fresh, a change to a verified operation resource invalidates it","reconcile yields exactly the same errors as the 02a71a3 baseline when evidence is revision-bound, and adds staleness errors when it is not (stricter, never looser)","the amendment record is append-only: the first record line stays byte-identical after the second amendment and the hash chain links revision to revision","unverified: lowering the task-level required_evidence_levels passes the loosening gate with loosened=false and no adjudication, although the contract lists lowering the evidence level as loosening"],"evidence_refs":["review-report.md","executor-report.md","executor-result.json"],"unverified":["the 367-passed baseline figure claimed by the executor was not re-run at 02a71a3 (only the delta of 10 new test methods was reasoned about)","whether any downstream consumer other than pipeline_tools reads the rewritten documentation paragraphs (contract unknown-2)","post-merge main-worktree re-verification of this task"],"blockers":[],"recommendation":"FAIL on one uncovering of the loosening gate: lowering the task-level required_evidence_levels is accepted with --reason only, recorded as loosened=false, and drops the lifecycle evidence floor from 3 to 2. Fix _contract_loosened to treat a lowered required_evidence_levels as loosening plus a test, or record an adjudicated narrowing of the criterion. Everything else reviewed clean: ten acceptance tests pass, full suite 377 passed, scope and history intact, no existing defence weakened."}
```

## 审查结论摘要

**FAIL** —— 十条验收测试全部亲自通过，全量测试 377 passed，范围与历史完好，既有防线未被削弱；但**放松约束的闸门存在一条未被任何验收测试覆盖的绕过路径**（`required_evidence_levels` 下调），与契约"判据二"明文冲突。详见 [findings](#findings)。

---

## 环境检查（逐项）

| # | 检查 | 命令 | 结果 |
|---|---|---|---|
| 1 | worktree 根 | `git rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/task-sheet-revision-and-evidence-binding` ✔ |
| 2 | 分支 | `git branch --show-current` | `task-sheet-revision-and-evidence-binding` ✔ |
| 3 | HEAD | `git rev-parse HEAD` | `e525d802c83ab277135381b179045bf03886794d` ✔ |
| 4 | 契约基线是祖先 | `git merge-base --is-ancestor 02a71a3 HEAD` | 退出码 0 ✔ |
| 5 | 契约可读且合法 | `python -m pipeline_tools task validate docs/tasks/...md` | `PASS`，退出码 0 ✔ |
| 6 | 未改产品/测试/文档 | 全程只读产品代码；只在证据目录写入本报告与 `reviewer-result.json` | ✔（见下方"临时文件清理"） |

契约基线到分支尖端的提交流：
`abc6768 冻结任务单` → `13a799a`/`02a71a3`（契约修订）→ `7b647f1`（实现）→ `753f0a6`（文档一行修正）→ `e525d80`（执行证据）。

---

## 十条验收测试（逐条亲自运行）

全部命令 cwd = worktree 根，环境变量 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

| # | 命令 | 退出码 | 关键断言（我读到的断言） | 证据引用 |
|---|---|---|---|---|
| 1 | `pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence` | 0 (1 passed) | 执行证据存在后修订散文被接受（revision 1→2）；worktree 列表与证据目录字节不变；`amendments.json` 是唯一新增文件；随后 `freeze_check` 不再报漂移 | 本报告 #验收测试1；`review-report.md` 风险点 1 |
| 2 | `... -k identity_fields_are_not_amendable` | 0 (1 passed, **4 subtests**) | `task_id`/`task_type`/`schema`/`derived_from` 四个身份字段分别被拒且不留记录、不改哈希；`dependencies` 增删被接受 | #验收测试2；风险点 3、5 |
| 3 | `... -k verification_surface_and_loosening` | 0 (1 passed) | 仅改散文不触发判据；收紧验收测试 → 只改验证面；扩大 `allowed_paths`、删除验收测试 → 缺 `--adjudication` 被拒、补上后接受并记录 `loosened=true` | #验收测试3；风险点 1 |
| 4 | `... -k amend_rejects_missing_or_cyclic_dependencies` | 0 (1 passed, **2 subtests**) | 不存在的依赖、成环依赖被拒且无记录；`docs/tasks/` 与 `.pipeline/archive/` 两种合法依赖被接受 | #验收测试4；风险点 5 |
| 5 | `pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze` | 0 (1 passed) | 冻结后直接改文件仍报 `task sheet changed after freeze`（既有用例未放宽） | #验收测试5；风险点 2 |
| 6 | `... -k evidence_validity_tracks_sheet_revision` | 0 (1 passed) | HEAD 移动（无关路径）→ 不失效；被验证路径变化 → stale；修订版本变化 → stale | #验收测试6；风险点 6 |
| 7 | `... -k amendment_record_is_append_only` | 0 (1 passed) | 两条修订按序追加、旧记录字节不变、含哈希链与两个判据、验收测试增删在差异中可见 | #验收测试7；风险点 10 |
| 8 | `... -k plan_contract_consistency_uses_latest_revision` | 0 (1 passed) | 规划后修订 `dependencies` → 报 `revised_after_planning` 且 `next_actions` 变为重新规划；未修订任务仍按原基准 | #验收测试8 |
| 9 | `... -k amend_requires_main_agent_role` | 0 (1 passed, **2 subtests**) | `executor`/`reviewer` 角色被拒（API 与 CLI 退出码 3 均验），无副作用；放松约束缺裁决被拒、补上后接受 | #验收测试9；风险点 1 |
| 10 | `pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 (1 passed) | 七份文档同时含"冻结/修订/身份字段/lifecycle/.pipeline/<task-id>"；六份不得再声称整份任务单绝对不可变 | #验收测试10；风险点 8 |

十条**全部由我亲自运行**，无一条依赖执行子代理的记录。

---

## 全量测试

- 命令：`python -m pytest -q`（cwd = worktree 根）
- 结果：**`377 passed, 28 subtests passed in 437.43s (0:07:17)`，退出码 0**
- 与执行子代理声明的 `377 passed, 28 subtests passed` **一致**；断言计数与退出码均一致。
- 基线 367 我**未重跑**（需检出 02a71a3，会污染只读 worktree）；但差异可解释：新增测试文件 `tests/test_task_sheet_amendment.py` 恰好 10 个测试方法，367+10=377，无其它测试被删除或跳过（`git diff --stat` 显示旧测试文件只有 `test_acceptance_id_and_template_compliance.py` 的 10 行断言改写）。
- 另跑既有防线模块：`pytest -q tests/test_git_checks.py tests/test_evidence.py tests/test_task_evidence_reconcile.py tests/test_metrics.py tests/test_security_repairs.py tests/test_task_lifecycle.py tests/test_worktree_dispatch_identity.py` → **117 passed，退出码 0**。

---

## 范围与历史卫生

| 检查 | 结果 |
|---|---|
| `git diff --name-only 02a71a3 753f0a6` 的 16 个路径 | **全部落在契约 `allowed_paths` 内**（`pipeline_tools/{core,__main__,task_lifecycle,reconcile,planning}.py`、`templates/*`、`tests/test_{task_sheet_amendment,acceptance_id_and_template_compliance,git_checks}.py`、`SKILL.md`、`README.md`、`references/*`）。注意：`tests/test_task_lifecycle.py` 在允许清单内但**未被改动**（新增 lifecycle 覆盖写在 `tests/test_task_sheet_amendment.py` 内） |
| 分支尖端 `02a71a3..e525d80` 全部路径 | 16 个实现文件 + 2 个新证据文件（`.pipeline/<task-id>/executor-report.md`、`executor-result.json`），无其它路径 |
| `forbidden_paths` 零改动 | `git diff --name-only 02a71a3 e525d80 -- docs/goal.md docs/tasks/security-scan-repair-20261001.md docs/tasks/security-scan-repair-20261001-continuation-1.md .pipeline/security-scan-repair-20261001 .pipeline/security-scan-repair-20261001-continuation-1 .env credentials` → **空输出**（零改动） |
| 历史任务单/证据是否被改写 | 除本任务的两个新证据文件外，`docs/tasks/**` 与 `.pipeline/**` 无任何历史文件出现在 diff 中；`references/compat-and-migration.md` 只新增 v0.15.0→v0.16.0 条目（`git diff` 只有 `+2` 行，无删除行） |
| `git diff --check 02a71a3..753f0a6` | 退出码 0（无空白错误） |
| 空白/行尾 | `core.py` 全文件 diff 只有 **2 行删除**（一条 import 行、`freeze_check` 里一行赋值），其余为纯新增 |
| 工作区状态 | `git status --porcelain` 干净（我清理了自己产生的临时文件，见文末） |

---

## 高风险点 1–10（全部由我独立构造验证）

我的独立验证工具（自建夹具，未复用执行子代理的测试辅助函数）位于 `C:/Users/alexc/AppData/Local/Temp/reviewer-probe/`：`probe1_amend.py`（风险点 1/2/3/4/5/10，最终整轮退出码 0）、`probe2_evidence.py`、`probe3_freshness.py`、`probe5_loosening_holes.py`、`probe7_post_amend.py`、`minimal_repro.py`，均以 `PYTHONPATH=<worktree>` 调用产品代码，root 为临时 Git 仓库。

### 1. 放松约束闸门真的生效 ✅（但有一条旁路，见 findings）
自建任务单，删除 `acceptance-test-2`（同时删除其 owner operation）：
- 不带裁决：CLI `task amend` 退出码 **3**，`BLOCKED ... FAIL: loosening the contract requires --adjudication`，`amendments.json` **未创建**，任务单字节哈希不变（`True`），修订版本仍为 1。
- 补 `--adjudication docs/decisions/drop-at2.md`：退出码 **0**，`loosened=true`、`verification_surface_changed=true`，记录中 `adjudication_ref` 与 `changes.acceptance_tests.removed=["acceptance-test-2"]` 均可见。
- 仅改散文：退出码 0，`loosened=false`、`verification_surface_changed=false`、`adjudication_ref=null`（不触发任何判据，无需裁决）。
- 仅增删 `dependencies`：退出码 0，`loosened=false`、`surface=false`（只需理由）。
- 另验：`test_ref`/`command_ref` 改写、收窄 `forbidden_paths` 都被判为放松并拒绝（退出码 3）。

### 2. 静默篡改仍被抓 ✅
先用带裁决的修订把基准推到 revision 2，然后**绕过 `task amend`** 直接改任务单文件（把验收测试删掉）：
`python -m pipeline_tools task freeze-check <root> --contract <冻结提交> --task-sheet docs/tasks/probe.md` → 退出码 **4**，输出 `FAIL: task sheet changed after freeze`。
反向对照（同一夹具）：走 amend 登记后 `freeze-check` 退出码 0 `PASS`，且重复运行仍为 0（幂等）。

### 3. 身份字段保护无法绕过 ✅（四种构造全部被拒）
- 3a 首次修订（基准来自冻结时写入 `goal.json` 的 `task_sheet_contract` 快照）：改 `task_type` → 退出码 3，`FAIL: contract field task_type is not amendable (identity field)`，无 `amendments.json`，修订仍为 1。
- 3b **把篡改提交**（使 HEAD blob 与篡改后的单子一致）后再 amend → 仍退出码 3，同样报身份字段，无记录。说明比对基准是"上一次记录的契约快照"，不是调用瞬间的 HEAD。
- 3c 已有一条修订记录（revision 2）后再偷换 `task_id` → 退出码 3，`FAIL: contract field task_id is not amendable`，修订仍为 2。**确认比对基准是上次记录的 `sheet_contract`，而非当前文件前后状态**。
- 3d 人为移除 `goal.json` 的 `task_sheet_contract` 快照（迫使回退到 `HEAD:` blob 路径）后改 `task_type` → 仍退出码 3。回退路径同样成立。

### 4. `task_lifecycle.init_task` 改动的安全性 ✅
- 初始 `init_task` → `pending`；未登记改动后 `inspect_task` → `blocked ['task sheet hash drift']`，`init_task` → `blocked ['task sheet hash drift']`（fail-closed）。
- 登记过一条修订后 `inspect_task` → `pass`，`init_task` 返回既有状态（不再报身份漂移），即"修订链中的哈希被接受"这条必要改动只对**链上记录过的哈希**生效。
- 再对同一任务做第二次未登记改动 → 仍 `blocked ['task sheet hash drift']`（revision 2 的基准没有被放宽）。
- 伪造 `lifecycle.json` 的 identity（改 `user`）→ `blocked`（未开通道）。
- 代码层面核对：`_identity_matches` 只在 `recorded_hash in recorded_task_sheet_hashes(root, task_id)` 且其余身份字段全等时返回 True；`recorded_task_sheet_hashes` 只收集链上真实观测过的 `previous_sheet_sha256`/`sheet_sha256`。**没有"随便改单子都能通过"的通道。**

### 5. 依赖校验 ✅
同一夹具四个用例：不存在 id → `dependency task sheet not found: no-such-task`（退出码 3，无记录）；成环 → `dependency cycle: probe -> probe-cycle -> probe`；依赖单子存在但无契约块 → `dependency task sheet is not a valid contract: probe-broken`；合法依赖（含 `.pipeline/archive/<id>.md` 形态）→ 退出码 0 接受，`changes.dependencies.added` 正确。全部拒绝场景都不留记录。

### 6. 证据有效性判据：两种情形分别真实观测 ✅
- A 基准（HEAD == `observed_at_commit`）：`stale=false`。
- B 只提交无关路径 `docs/notes.md`，HEAD 从 `bbcb2401` 移到 `78d34275`：`head_changed=true` 但 `stale=false`，`reasons=[]`。
- C 再提交被验证资源 `pipeline_tools/alpha.py`（`78d34275`→`4f19bb33`）：`stale=true`，`reasons=['executor-report.md was produced before changes to paths it verifies: pipeline_tools/alpha.py']`。
- D 既有 `evidence_freshness` 同样两种情形分别可观测：仅无关路径变化时 `pass`（`verified_paths_changed=[]`，`observed_at_commit` 记录在案）；被验证路径变化时 `blocked ['paths under verification changed after this evidence was produced']`。同时旧口径未被删：带 `identity.head` 而无 `observed_at_commit` 的旧格式结果在 HEAD 前移后仍 `blocked ['result HEAD is stale']`。
- E 消费者层（`reconcile`）：revision 绑定正确时 `sheet_revision=1`、6 条记录 `stale=false`、**不产生任何 revision 相关错误**（错误列表与 02a71a3 基线完全相同）；记录不声明修订时 6 条全 stale 并追加 "does not record the task sheet revision / the commit it was observed at"。
- F 新修订使旧证据失效：`produced against task sheet revision 1 but the current revision is 2`。
- G 不声明 `sheet_revision` 的记录 → stale（fail-closed，不静默通过）。

### 7. 没有削弱既有防线 ✅
- `git diff 02a71a3 753f0a6 -- pipeline_tools/reconcile.py`：唯一实质改动是 PASS 判定**增加一个合取项** `not revision_errors`，BLOCKED 判定增加 `revision_errors`，并多输出三个字段。**判定只会更严，不会更松。**
- 手工构造同一份证据目录，分别用 `git archive 02a71a3 pipeline_tools` 抽出的基线代码与新代码跑 `reconcile_task`：
  - 证据带 `sheet_revision`/`observed_at_commit`：基线错误 `['missing or invalid finalization.json','main worktree post-merge re-verification is missing']`，新代码错误**完全相同**（新机制不会误伤合法证据）。
  - 证据不带这些字段（历史形态）：基线错误同上，新代码在此基础上**追加** 6 条记录级 staleness 错误。→ 严格性单调不减。
- `core.py` 的 `evidence_verify`/`gate_check`/`scope_check`/`evidence_readiness`/`verify_structured_result` 函数体**未被改动**（全文件 diff 只有 2 行删除，且都不在这些函数内）。
- 既有防线模块 117 passed（见上文）。
- 附带发现（更严带来的兼容影响）：真实历史证据目录确实没有新字段——我检查了主工作树 `.pipeline/security-scan-repair-20261001-continuation-1/` 的三份报告与三份结果（报告只记 `head`，结果无任何新字段），因此用新代码对该任务跑 `evidence reconcile` 会因"未记录修订版本"而判 BLOCKED。这属于**收紧**而非削弱，但 `references/compat-and-migration.md` 只说明了"历史证据不被改写"，未提示"历史任务在新代码下 reconcile 会被判 stale/blocked"。

### 8. 文档断言的改写没有丢掉约束意图 ✅（但版本号断言被明显弱化，见 findings）
把 worktree 的相关文件复制到独立目录 `doccheck/`（`tests/` 也在其中，`ROOT` 因此指向副本），只跑这一条文档断言做 A/B：
| 变体 | 结果 |
|---|---|
| 原样 | **1 passed** |
| 从 `references/acceptance-evidence.md` 删除全部"修订"字样 | **FAILED**（仍能挡住"文档不再描述当前修订模型"） |
| 在 `README.md` 里加入"任务单不可变" | **FAILED**（"不得再声称整份任务单绝对不可变"的否定断言有效） |
| 把 `SKILL.md` 的 `version: 0.16.0` 改回 `0.15.0` | **1 passed** ← 新断言 `assertRegex(r"version: 0\.\d+\.\d+")` 无法发现"版本号没升"（旧的 `assertIn("version: 0.15.0")` 或者任何形式的明确钉死才行） |

版本号本身我直接读文件核对：`SKILL.md` 由 `0.15.0`（主工作树）升到 `0.16.0`（worktree），契约"技能版本号已升"**事实成立**；但**机械断言已不能守住它**。schema 1-3 历史读取兼容的断言在测试文件其余部分未改动，仍然保留。

### 9. `git reset --soft` 只影响其自身未合并的证据提交 ✅
`git reflog show --date=iso HEAD`：
```
e525d80 commit: executor evidence ...                (17:25)
753f0a6 commit: docs: record the freeze snapshot ... (17:17)
7b647f1 reset: moving to HEAD~1                      (17:17:08)
76dc911 commit: executor evidence ...                (17:08)  <- 被丢弃的第一次证据提交
7b647f1 commit: record task sheet revisions ...      (16:56)
02a71a3 merge main: Fast-forward
```
- 被丢弃的 `76dc911`（父提交 `7b647f1`）只含本任务的 `executor-report.md` 与 `executor-result.json`（42 行新增），**不含任何产品文件**。
- `02a71a3` 及其之前的历史未被改写：主工作树 HEAD 仍是 `02a71a3b735e8a95358a7552a5f077fd3fb5ab22`，`git log --oneline` 链为 `02a71a3 ← 13a799a ← abc6768`，与分支上一致；主工作树工作区干净、未被修改。
- 侧证 `02a71a3` 未受影响：契约校验 `task validate` PASS（其内容哈希与该提交一致），且分支分叉点正是 `02a71a3`。
- 补充说明：`753f0a6` 的实际内容是 `references/execution-and-review.md` 的一行文档修正（提交信息提到 goal.json），`git diff --name-only 02a71a3 e525d80` 里也**没有** `.pipeline/<task-id>/goal.json`——该状态文件未被纳入 Git（与契约 unknown-1 一致）。

### 10. 修订记录的追加性 ✅
连续两次修订（第一次把某条 `evidence_level` 2→3，第二次新增 `acceptance-test-3`）：
- 第一次后的首条记录行（原始字节）在第二次写入后**逐字节相同**（`True`），且 `json.loads` 出的对象相等（`True`）。
- 前缀保护成立（新文件以旧文件的 `\n]}\n` 之前内容开头）；`revisions=[2,3]`，`rev3.previous_sheet_sha256 == rev2.sheet_sha256`（`5e41936f`）。
- 反向对照：把已记录的 `evidence_level` 从 3 改回 2（相对记录版本是降低）**被判为放松**并拒绝（退出码 3）——追加记录不会掩盖"相对上一版"的降低。
- 被拒绝的修订不产生任何记录（多次验证）。

### 额外核对：真实任务的证据绑定自洽 ✅
- 任务单实际 sha256 = `a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783`，与 `executor-report.md` / `executor-result.json` 声明的 `sheet_sha256` **完全一致**（证据确实绑定在它声称的修订版本上）。
- 对该任务直接运行 `task freeze-check` → `PASS`（退出码 0），因为它从未被 amend，基准来自冻结记录。
- 契约决策点 2（裁决引用载体）不构成阻塞：实现把 `adjudication_ref` 存为调用方给出的自由字符串，未自创格式，符合"不得自行决定载体格式"。

---

## findings

### F1（导致 FAIL）放松约束的闸门可被 `required_evidence_levels` 绕过
契约"判据二"：*"是否放松约束（删除或放宽验收测试、**降低证据等级**、扩大允许范围、收窄禁止范围、删除非目标）。放松必须带 `--adjudication`。"*
实现 `_contract_loosened`（`pipeline_tools/core.py:2374-2394`）只检查**单条** `acceptance_tests[].evidence_level` 的下降，**不检查任务级 `required_evidence_levels` 的下调**；执行子代理在自己的报告里也把该条口径收窄成了"降低某条 `evidence_level`"，未按契约决策点停下报告。

最小复现（脚本全文见下，退出码 0）：
```python
# 任务单冻结时 acceptance-test-1 为 evidence_level 3、required_evidence_levels=[3]
# 只把 required_evidence_levels 改为 [2]，acceptance test 保持 level 3
value = amend_task_sheet(root, "demo", reason="lower the evidence level")   # 无 --adjudication
print(value["status"], value["loosened"], value["changes"]["required_evidence_levels"])
```
观察到的输出：
```
{"status": "pass", "loosened": false, "verification_surface_changed": true, "errors": []}
recorded required_evidence_levels delta: {'added': [2], 'removed': [3]}
revision after the amendment: 2
floor after the un-adjudicated amendment: 2 ready: True
```
影响是真实的、不只是分类好看：`task_lifecycle._evidence`（`pipeline_tools/task_lifecycle.py:241-247`）用 `max(required_evidence_levels)` 作为证据下限计算 `ready`，该下限被从 3 降到 2 后，只提供 2 级证据也可 `ready=True`。整条路径只用了 `--reason`，没有任何裁决引用，记录里 `loosened=false`。
复现脚本：`C:/Users/alexc/AppData/Local/Temp/reviewer-probe/minimal_repro.py`（可整体 `python minimal_repro.py` 运行；本报告 `commands` 中已列出该命令，退出码 0）。

建议（任一即可，均属主代理决策）：
1. 把"下调 `required_evidence_levels`"纳入 `_contract_loosened`，并补一条验收测试（例如扩展验收测试 3 的触发集）；或
2. 明确裁决并记录"判据二中的'降低证据等级'仅指单条 `acceptance_tests[].evidence_level`"这一收窄口径，同时说明任务级下限变更为何不算放松。

### F2（finding，不单独构成 FAIL）文档断言的技能版本号检查被弱化
`tests/test_acceptance_id_and_template_compliance.py` 把 `assertIn("version: 0.15.0", skill)` 改成 `assertRegex(skill, r"version: 0\.\d+\.\d+")`。A/B 实测（见高风险点 8）：把版本改回 `0.15.0` 该用例仍然通过，即"技能版本号已升"不再有任何机械保证。事实层面 `SKILL.md` 已升到 `0.16.0`（我直接读文件核对），契约该条**事实成立**；建议改成"版本号不等于基线版本"或与 `references/compat-and-migration.md` 的版本条目交叉校验，以恢复约束力。

### F3（observation）另外两类变更未被归为"放松"
我把它们与契约比对后认为**不违反契约明文**（契约判据二未列），但值得主代理知晓，避免后续误用：
- 删除整个 operation 而保留全部验收测试 → `loosened=false`，只在 `verification_surface_changed=true` 上留痕（会被要求重做证据）。
- 收窄 operation 的 `resources`（减少被验证路径）→ 同上。
两者都会使既有证据 stale（必须对最新修订重做），影响面因此有界。

### F4（compat 提示，非实现缺陷）
新 `evidence reconcile` 对历史证据是**更严**的：真实历史证据（我核对了主工作树 `security-scan-repair-20261001-continuation-1` 的 6 份文件）都不含 `sheet_revision`/`sheet_sha256`/`observed_at_commit`，因此在新代码下会被判 stale/BLOCKED。`references/compat-and-migration.md` 目前只说明"历史任务单与历史证据不被批量改写"，未提示这一后果。建议在兼容文档里补一句（不属本任务的验收标准，故不据此判 FAIL）。

---

## unverified / blockers

**unverified**
- 基线 367 passed 未重跑（只做了 367+10=377 的差异推理，未见删除或跳过的测试）。
- 契约 unknown-2：是否有 pipeline_tools 之外的下游消费者依赖被改写段落的旧措辞，未确认。
- 合并后主工作树复验（post-merge re-verification）未进行——按流程属主代理动作。

**blockers**：无（环境、权限、证据均齐备，契约本身未发现自相矛盾；契约虽然在"降低证据等级"的口径上可作两解，但那由主代理裁决即可，不阻塞本次判定）。

**我未复验的内容**：无（十条验收、全量测试、范围与历史卫生、高风险点 1–10 均已亲自运行；仅上述 unverified 三项超出本次审查范围）。

---

## 临时文件清理（保持 worktree 与主工作树原状）

- 我在审查中运行了 `python -m pipeline_tools task freeze-check .`（真实任务单）以验证"修订后不再报漂移"，该命令按产品设计写入了 `.pipeline/task-sheet-revision-and-evidence-binding/goal.json`。该文件在我运行前**不存在**（证据目录当时只有提交里的两份文件），我已**删除**它，使证据目录恢复为提交状态。
- 我为全量测试日志临时写的 `.pipeline/reviewer-fulltest.log` 也已删除。`git status --porcelain` 现在是干净的。
- 除本目录的 `review-report.md` 与 `reviewer-result.json` 外，我没有写任何文件；未修改任何产品/测试/文档/任务单；未新建 worktree；未在主工作树中改任何文件（对主工作树只有 `git log/show/status` 与 `Read` 等只读访问）。
