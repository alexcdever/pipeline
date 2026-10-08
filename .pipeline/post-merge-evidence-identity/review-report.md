# 独立审查报告：post-merge-evidence-identity（revision 4，round 1）

结论：**PASS**。以下全部观察均由审查者本人在实现 worktree 内亲自复验，未转述执行子代理的任何结论。

```pipeline-evidence
{"schema":2,"task_id":"post-merge-evidence-identity","worktree":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","branch":"post-merge-evidence-identity","role":"reviewer","round":1,"status":"PASS","head":"270ebc0192bbd7273b1c207eec26872bc744bbc8","observed_at_commit":"b89f7647f3d5602dae36cf02c69e270e78adf650","generated_at":"2026-10-08T18:57:55Z","sheet_revision":4,"sheet_sha256":"c32e3c23c23cb830ff867374e1be927880700fc8cd21a88c0654eff1a7dc91a9","commands":[{"command":"git rev-parse --show-toplevel","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"git branch --show-current","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"git rev-parse HEAD","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"git merge-base --is-ancestor 270ebc0192bbd7273b1c207eec26872bc744bbc8 HEAD","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools task validate docs/tasks/post-merge-evidence-identity.md","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q tests/test_evidence.py -k post_merge_identity_uses_task_id_and_revision_only","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q tests/test_evidence.py -k post_merge_rejects_revision_mismatch","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q tests/test_evidence.py -k post_merge_rejects_task_id_mismatch","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q tests/test_evidence.py -k post_merge_requires_main_worktree_reverification","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q tests/test_evidence.py -k pre_merge_commit_identity_is_not_weakened","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_identity_agrees_on_task_and_revision","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope check . --task-id post-merge-evidence-identity --allowed pipeline_tools/core.py pipeline_tools/__main__.py pipeline_tools/reconcile.py tests/test_evidence.py tests/test_task_evidence_reconcile.py SKILL.md references/merge-and-recovery.md docs/tasks/post-merge-evidence-identity.md .pipeline/post-merge-evidence-identity/** --forbidden docs/goal.md .pipeline/task-sheet-revision-and-evidence-binding/** docs/tasks/task-sheet-revision-and-evidence-binding.md .pipeline/security-scan-repair-20261001/** .pipeline/security-scan-repair-20261001-continuation-1/** .env credentials/**","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools result verify .pipeline/post-merge-evidence-identity/executor-result.json --task-id post-merge-evidence-identity --role executor","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"git diff --check","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"git status --porcelain","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python /tmp/pmei/fixture_full.py current .","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python /tmp/pmei/fixture_full.py pretask /tmp/pmei/pretask","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"diff /tmp/pmei/active_sets_pretask.json /tmp/pmei/active_sets_current.json","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python /tmp/pmei/historical.py","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"python -m pipeline_tools gate post-merge <merged fixture repo>/.pipeline/demo --task-id demo --branch main  # CLI, merged --no-ff with product-path change","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"python -m pipeline_tools gate pre-merge <same merged fixture repo>/.pipeline/demo --task-id demo --branch main","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":3,"expected_exit_code":3,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"python -m pipeline_tools evidence verify <same merged fixture repo>/.pipeline/demo --task-id demo --branch main --phase active","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":3,"expected_exit_code":3,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"python -m pipeline_tools evidence verify <same merged fixture repo>/.pipeline/demo --task-id demo --branch main --phase finalized","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":3,"expected_exit_code":3,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"git log --oneline -S merged_task_branch_identity -- pipeline_tools/","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"},{"command":"git diff --name-only fe999dcd1519edca410853ff31fa00b3489b35f7 270ebc0192bbd7273b1c207eec26872bc744bbc8","cwd":"D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity","exit_code":0,"evidence_ref":".pipeline/post-merge-evidence-identity/review-report.md"}],"assertions":["environment: toplevel = D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity, branch = post-merge-evidence-identity, HEAD = b89f7647f3d5602dae36cf02c69e270e78adf650, 270ebc0192bbd7273b1c207eec26872bc744bbc8 is an ancestor of HEAD (exit 0), task validate = PASS/exit 0","acceptance-test-1..7: all seven contract command_ref -k invocations exit 0 with exactly 1 passed","full suite: 387 passed, 28 subtests passed, exit 0 (matches the executor's declared 387)","independent fixture (own repository, own reports, own merge): reports recording the task branch + task worktree + implementation head pass gate post-merge (exit 0) after a --no-ff merge that changes src/app.py, the three report files keep identical bytes and the fixture repository stays clean, and the same evidence still fails the active criterion set","independent fixture: a differing sheet_revision, a report naming another task, an evidence directory that does not name the verified task, and a final-check without a main-worktree command each fail closed in the post-merge criterion set","independent fixture: the active criterion set is unchanged -- the error list for unmerged branch / non-ancestor head / non-canonical worktree / missing branch ref is byte-identical between the pre-task code at ace0560 and the delivery (9, 12, 9, 9 errors)","independent fixture: evidence verify --phase active and --phase finalized on one merged evidence directory produce different verdicts driven only by the phase; gate post-merge passes that directory while gate pre-merge rejects it","independent fixture: reconcile no longer reports report identity conflict or report identity is incomplete for task-branch reports plus a main-worktree final check, and still reports report identity conflict when sheet_revision or task_id diverges","independent fixture: historical-shape evidence (no sheet_revision) gains no error from the revision criteria in reconcile -- it is reported as unverified only; a real historical evidence directory yields identical active-phase errors before and after the change","dead code: merged_task_branch_identity has no reference anywhere in the delivered product code (only the task sheet mentions it)","scope: git diff --name-only fe999dc 270ebc0 lists exactly 9 paths, all inside revision 4 allowed_paths; no forbidden path changed; git diff --check exit 0; working tree clean"],"evidence_refs":[".pipeline/post-merge-evidence-identity/review-report.md",".pipeline/post-merge-evidence-identity/reviewer-result.json"],"unverified":["the independent fixture lived in the OS temp directory and is gone; its full source is transcribed in the appendix of this report and the observed outputs are quoted verbatim there","post-merge re-verification of a merged head in the main worktree, final-check.md and finalization.json are the main agent's steps and are not produced by this review round","this worktree holds no .pipeline/post-merge-evidence-identity/amendments.json (it is local main-worktree state, untracked: I read revisions [2, 3, 4] there), so task_sheet_revision reads 1 here while the contract revision is 4; evidence verify --phase finalized run inside this worktree therefore also reports 'was produced against task sheet revision 4 but the current revision is 1' for these two files, which is a limitation of the amendment record's location, not of the reports"],"blockers":[],"recommendation":"accept"}
```

## 1. 审查对象

- 契约：`docs/tasks/post-merge-evidence-identity.md` revision 4（`sha256 = c32e3c23c23cb830ff867374e1be927880700fc8cd21a88c0654eff1a7dc91a9`，本次现算）
- 待审实现提交：`270ebc0192bbd7273b1c207eec26872bc744bbc8`
- 分支尖端（执行者 round-3 证据）：`b89f7647f3d5602dae36cf02c69e270e78adf650`
- 基线：`fe999dcd1519edca410853ff31fa00b3489b35f7`（= `git merge-base HEAD main`，即声明 CLI 入口进入范围的 revision-4 修订提交）
- 所有命令 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`，cwd 一律为实现 worktree 根；未修改任何产品/测试/文档文件，未新建 worktree，未动主工作树（`git status --porcelain` 始终为空）。

## 2. 环境检查（逐项）

| # | 检查 | 结果 |
|---|---|---|
| 1 | `git rev-parse --show-toplevel` == worktree 绝对路径 | 通过：`D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity` |
| 2 | `git branch --show-current` == `post-merge-evidence-identity` | 通过 |
| 3 | `git rev-parse HEAD` == `b89f7647f3d5602dae36cf02c69e270e78adf650` | 通过 |
| 4 | `git merge-base --is-ancestor 270ebc0 HEAD` | 通过：exit 0 |
| 5 | `python -m pipeline_tools task validate docs/tasks/post-merge-evidence-identity.md` | 通过：`PASS`，exit 0 |
| 6 | 只读产品代码、不改历史、不新建 worktree | 通过：全程只读；`git status --porcelain` 空；`git diff --check` exit 0 |

## 3. 高风险点独立复验（1–10）

复验方式：我用自己写的夹具脚本（见附录 A）在临时仓库里独立重建"任务分支 + 任务 worktree + 实现提交 head"的三份 schema-2 报告，并把**改动前的产品代码**从 `ace0560` 用 `git archive` 解到临时目录，用同一份夹具跑两遍、逐条 diff 错误集合。

1. **post-merge 通过性**。临时仓库中三份报告记录 `branch=demo-task`、`worktree=<任务 worktree>`、`head=<实现提交>`；`--no-ff` 合入 main 且合并带来了 `src/app.py` 的产品路径改动（`git diff --name-only <head> HEAD` 含 `src/app.py`）。`gate post-merge`（API 与 CLI 各一次）→ **exit 0 / PASS**；三份报告前后字节逐一相等（CLI 版本另做了 sha256 比对，并为 `True`），夹具仓库 `git status --porcelain` 前后都为空（闸门未改写任何文件）。同一份证据在 `--phase active` 下报 12 条提交身份错误 —— 通过性确实来自阶段判据，而不是身份被改写。
2. **修订版本不符**。把三份报告的 `sheet_revision` 改成 7（当前修订为 1）：`gate post-merge` 的错误列表**恰好**是三条 `… was produced against task sheet revision 7 but the current revision is 1` → 失败（非零）。
3. **`task_id` 不符**。三份报告改成 `other-task` → 三条 `… task identity mismatch`，闸门失败；把受验 task id 换成 `other-task`（报告与目录内的报告一致指向别的任务、证据目录名仍是 `demo`）时，`evidence verify --phase finalized` 的错误**恰好**只有一条 `evidence directory does not match the verified task id`。
4. **缺主工作树复验**。把 `final-check.md`（及另两份）的命令 `cwd` 改成任务 worktree：身份部分完全干净（`--phase finalized` 返回 `[]`），而 `gate post-merge` 报 `post-merge re-verification in the main worktree is missing` → 失败。放宽身份没有一并放宽复验要求。
5. **active 阶段未被削弱（最关键的反方向）**。同一夹具、同一个待审证据目录，分别构造四种情形——(a) 未合并分支、(b) 非祖先的 40 位 `head`、(c) 非规范 `worktree`、(d) 不存在的分支 ref——用**改动前** `ace0560` 的代码与交付代码各跑一遍 `evidence_verify(..., 'main')`，把错误列表排序后 `diff`：**四个情形全部逐字相同**（9 / 12 / 9 / 9 条，`diff` exit 0，输出 `IDENTICAL`）。既没有变多也没有变少。
6. **CLI 阶段接线**。`pipeline_tools/__main__.py:1176` 把 `args.phase` 传给了 `evidence_verify`（`--phase` 的 argparse 定义在 `:279`，取值 `active|finalized`，默认 `active`）。同一份已合并证据目录上：`evidence verify … --phase active` → exit 3，12 条 head/branch/worktree/`branch mismatch` 错误；`--phase finalized` → exit 3，只有 `FAIL: finalization.json is missing`（CLI 既有的 marker 校验）。差异完全由阶段驱动。`gate post-merge` 映射到 finalized：同一目录 `gate post-merge` → exit 0/PASS，而 `gate pre-merge` → exit 3 且报的就是那 12 条提交身份错误；`core.py:2009` 的映射与实测一致。
7. **`reconcile` 混合身份**。构造"任务分支身份的执行/审查报告 + 主工作树身份的终审报告"（`branch`、`worktree`、`head` 全不同，`task_id` 与 `sheet_revision` 一致）：`reconcile_task` 的 `report identity conflict` / `report identity is incomplete` **都不出现**，`identity.task_id == demo`、`identity.sheet_revision == 1`、`identity.branch is None`。把 review 报告的 `sheet_revision` 改成 2 → 重新出现 `report identity conflict`；把它的 `task_id` 改成 `other` → 同样重新报冲突。
8. **历史证据不新增错误**。不含 `sheet_revision`、不含 `observed_at_commit` 的历史形态证据：`evidence_revision_status` 的错误为空，只产出 `… does not record the task sheet revision …` 的 unverified 条目；`reconcile` 不再报 `report identity conflict`（改动前对同一夹具报 1 条，改动后 0 条，即只减不增；`diff` 显示唯一差异就是这个被设计移除的冲突，另有一处只是临时仓库 commit 哈希）。真实历史目录 `.pipeline/task-evidence-reconcile` 在 active 阶段下改动前后的错误列表 **逐字相同**（`diff` exit 0，10 条）。
   - 需要主代理知悉的后果（契约要求、非本任务缺陷）：post-merge 阶段对**历史形态**证据现在会新增两类错误，每条报告各两条——`… sheet_revision must be a positive integer` 与 `… observed_at_commit must be a non-empty string`（实测输出见附录 B）。这正是契约判据表"`head`、`branch`、`worktree`、`observed_at_commit` 字段存在且格式合法 → finalized 必需（记录事实）"与 fail-closed 清单（`sheet_revision` 缺失即报错）的直接结果，而不是实现的额外收紧。
9. **死代码清理**。`merged_task_branch_identity` 在交付的产品代码中**零引用**（全仓库 `grep` 只命中任务单 `docs/tasks/post-merge-evidence-identity.md:153,183` 这两处契约说明）；`git show fe999dc:pipeline_tools/core.py | grep -c merged_task_branch_identity` = 0，`git log -S` 只显示 `8b1ba98`（加入）与 `f39d1f9`（移除）两次提交，HEAD 无残留。
10. **被删用例的合法性**。逐条核对（`git diff ace0560 270ebc0` 与逐 commit 的用例名集合比对）：
    - 本任务之前就存在的用例（`ace0560` 的 `tests/test_evidence.py` 49 个、`tests/test_task_evidence_reconcile.py` 14 个）**全部仍存在**；`tests/test_evidence.py` 在整个交付区间内**没有被删除任何一行**（`diff` 的 `-` 行为空）。
    - `tests/test_task_evidence_reconcile.py` 只删掉 4 行，全部是共享辅助函数的签名/调用：`_report` 增加 `revision=None` 形参、`_evidence` 增加 `override=None` 形参、以及这些调用点。**没有任何断言行被删或改弱**。
    - 唯一被实质改动的既有用例是 `test_identity_conflict_is_blocked_and_does_not_claim_pass`：把"借 `branch` 分歧触发冲突"改成"借 `sheet_revision` 分歧触发冲突"，其 BLOCKED、`report identity conflict`、`identity.branch is None` 三条断言原样保留。这条改动正是 revision 3→4 契约明确要求的（"`reconcile` 不再因混合身份判冲突"），属于**按契约重新指向触发条件**，不是弱化。
    - 执行者在前几轮自行新增、随后删除的 5 个用例（`merged_task_branch_reports_pass_the_post_merge_gate`、`product_change_after_reported_head_is_still_stale`、`unmerged_branch_report_identity_is_still_rejected`、`foreign_worktree_report_identity_is_still_rejected`、`schema_two_report_identity_stays_strict_for_bogus_values`）经核**全部由本任务 revision-2 提交 `8b1ba98` 引入**（`ace0560` 中不含），且确实被 revision 3/4 推翻：它们断言的是"post-merge 仍用提交判据（放宽后的 merged-branch 规则）"，而 revision 4 的 post-merge 完全不做提交判定。其属性已被新的 active 用例 `test_pre_merge_commit_identity_is_not_weakened`（覆盖未合并分支、非祖先 head、非规范 worktree，并断言错误集合精确相等）取代。**没有既有断言被削弱。**

## 4. 七条契约验收（逐条命令、cwd、退出码）

cwd 均为 `D:/Projects/Skills/pipeline/.worktrees/post-merge-evidence-identity`，均带 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

| ID | 命令 | 退出码 | 结果 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_evidence.py -k post_merge_identity_uses_task_id_and_revision_only` | 0 | 1 passed, 49 deselected |
| acceptance-test-2 | `python -m pytest -q tests/test_evidence.py -k post_merge_rejects_revision_mismatch` | 0 | 1 passed, 49 deselected |
| acceptance-test-3 | `python -m pytest -q tests/test_evidence.py -k post_merge_rejects_task_id_mismatch` | 0 | 1 passed, 49 deselected |
| acceptance-test-4 | `python -m pytest -q tests/test_evidence.py -k post_merge_requires_main_worktree_reverification` | 0 | 1 passed, 49 deselected |
| acceptance-test-5 | `python -m pytest -q tests/test_evidence.py -k pre_merge_commit_identity_is_not_weakened` | 0 | 1 passed, 49 deselected |
| acceptance-test-6 | `python -m pytest -q tests/test_task_evidence_reconcile.py -k reconcile_identity_agrees_on_task_and_revision` | 0 | 1 passed, 13 deselected |
| acceptance-test-7 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | 1 passed, 27 deselected |

用例名、类名（`EvidenceTests`、`TaskEvidenceReconcileTests`、`AcceptanceIdAndTemplateComplianceTests`）与契约 `test_ref` 逐字一致；我也用完整 node id 各跑了一遍，同样全绿。

**全量测试**：`python -m pytest -q` → exit 0，**387 passed, 28 subtests passed**（545.87s）。与执行者声明的 387 一致，无差异。

## 5. 范围与历史卫生

- `git diff --name-only fe999dcd… 270ebc01…`（基线 = `merge-base HEAD main` 的 revision-4 修订提交）恰好 9 个路径：`.pipeline/post-merge-evidence-identity/executor-report.md`、`…/executor-result.json`、`SKILL.md`、`pipeline_tools/__main__.py`、`pipeline_tools/core.py`、`pipeline_tools/reconcile.py`、`references/merge-and-recovery.md`、`tests/test_evidence.py`、`tests/test_task_evidence_reconcile.py` —— **全部落在 revision 4 的 `allowed_paths` 内**。（分支尖端 `b89f764` 与基线的差集相同，只多了 round-3 的证据改写。）
- `forbidden_paths`（`docs/goal.md`、依赖任务证据目录、`docs/tasks/task-sheet-revision-and-evidence-binding.md`、两个 `security-scan-repair-*` 证据目录、`.env`、`credentials/**`）在 `fe999dc..270ebc0` 内**零改动**。
- 历史任务单与历史证据零改动：`git diff fe999dc 270ebc0 -- docs/tasks/` 为空；除本任务自己的证据目录外没有任何 `.pipeline/**` 路径出现在差集中。本任务单 `sha256 = c32e3c23…` 与冻结值一致。
- `git diff --check` → exit 0；`git status --porcelain` → 空。
- `python -m pipeline_tools task validate …` → `PASS`/exit 0；`result verify … --role executor` → `PASS`/exit 0；`scope check`（revision 4 的允许/禁止集，含 `pipeline_tools/__main__.py`）→ `PASS`/exit 0。

## 6. findings（不阻断 PASS，供主代理参考）

1. **文档自相矛盾（低）**：`references/merge-and-recovery.md` 新增的"证据身份的阶段分工"段落准确，但同一节"合并后"最后一段仍写着"post-merge 复验证据……按修订版本加被验证路径两条判据判定有效性"，与紧邻的新段落（finalized 不做任何路径相交判定）冲突。建议主代理在后续任务里改掉这句陈旧描述。
2. **reconcile 仍施加 active 提交绑定（中，但符合契约字面）**：`pipeline_tools/reconcile.py:151` 仍以默认 `phase="active"` 调 `evidence_verify`，因此"任务分支报告 + 主工作树终审报告"这种混合身份虽不再报 `report identity conflict`，却仍会累积 `branch/worktree does not match current Git identity`，reconcile 依旧无法 PASS。契约只要求"不再因混合身份判冲突"（acceptance-test-6 亦只断言这一点），而这条绑定正是 non_goal 1 保护、且被既有用例 `test_old_head_and_worktree_are_blocked_against_current_git_identity` 钉住的 pre-merge 严格判定，所以不算违约——但如果任务意图是"混合身份的合并后证据能走到最终化"，这一条会挡住它。执行者已在 `unverified` 中主动声明，我复现确认。
3. **契约内部张力（低，非实现缺陷）**：判据表把 `observed_at_commit` 在 finalized 阶段列为"必需（记录事实）"，于是历史形态证据在 post-merge 会新增 `observed_at_commit must be a non-empty string` 错误，与"历史证据不新增错误"的取向存在张力。我核对了逐字条件：该取向钉住的是 `evidence_revision_status` 的修订/路径判据（reconcile 层面只产出 unverified，实测无新增错误），而 `observed_at_commit` 的格式要求是 revision 3/4 契约显式新增的 post-merge 要求，因此判定为契约要求而非实现额外收紧。主代理在为依赖任务重生成 post-merge 证据时需要补上该字段。

未发现契约本身的缺陷需要单列修订。

## 7. 结论

**PASS**：revision 4 的三项实质要求（post-merge 身份退化为 `task_id` + `sheet_revision`、active 阶段提交绑定逐字不变、CLI `--phase` 接线）均经独立夹具复验成立；7 条验收全绿；全量 387 passed / 28 subtests 与声明一致；范围、禁止路径、历史证据卫生全部干净；既有断言无删除、无弱化。

- `blockers`：无。
- `unverified`：夹具位于系统临时目录、现已销毁（完整源码见附录 A，观察输出见附录 B，可按附录重建复跑）；主工作树合并后复验、`final-check.md` 与 `finalization.json` 属于主代理步骤，不在本轮评审范围。
- 修订版本读数：本 worktree 内没有 `.pipeline/post-merge-evidence-identity/amendments.json`（它是主工作树的本地未跟踪状态；我在主工作树只读读到 `revisions = [2, 3, 4]`），因此 `task_sheet_revision` 在此读作 1、而契约修订为 4。本报告 `sheet_revision` 填 4 与主工作树的读数一致；若在本 worktree 内跑 `evidence verify --phase finalized`，会额外报"revision 4 vs current 1"，这是修订记录位置的限制而非报告本身的问题。

## 附录 A：独立夹具源码

`fixture_full.py`（`fixture.py` 的正文 + 追加的 reconcile / 历史证据段落；`pretask` 模式用 `git archive ace0560` 解出的改动前代码，`current` 模式用交付代码）：

```python
"""Independent reviewer fixture for post-merge-evidence-identity (revision 4)."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

MODE = sys.argv[1] if len(sys.argv) > 1 else "current"
sys.path.insert(0, MODE_PATH := (sys.argv[2] if len(sys.argv) > 2 else "."))
PRE_TASK = MODE != "current"

from pipeline_tools import core  # noqa: E402


def sh(cwd, *args, check=True):
    return subprocess.run(["git", "-C", str(cwd), *args], check=check,
                          capture_output=True, text=True)


def contract_sheet(root, task_id="demo"):
    contract = {
        "schema": 1, "task_id": task_id,
        "allowed_paths": ["src/**", ".pipeline/**"], "forbidden_paths": [],
        "acceptance_tests": [{
            "id": "acceptance-test-1", "evidence_level": 3,
            "test_ref": "tests/test_evidence.py",
            "command_ref": "python -m pytest -q tests/test_evidence.py"}],
    }
    sheet = root / "docs" / "tasks" / f"{task_id}.md"
    sheet.parent.mkdir(parents=True, exist_ok=True)
    sheet.write_text("<!-- Task ID: %s -->\n```pipeline-contract\n%s\n```\n"
                     % (task_id, json.dumps(contract)), encoding="utf-8")
    return sheet


def report(path, task_id, worktree, branch, head, role, main_cwd, **extra):
    value = {
        "schema": 2, "task_id": task_id, "worktree": str(worktree), "branch": branch,
        "role": role, "round": 1, "status": "PASS", "head": head,
        "sheet_revision": 1, "observed_at_commit": head,
        "generated_at": "2026-01-01T00:00:00+00:00",
        "commands": [{
            "command": "python -m pytest -q tests/test_evidence.py", "exit_code": 0,
            "cwd": str(main_cwd) if role == "main-final" else str(worktree),
            "evidence_ref": "test.log"}],
        "assertions": ["phase criteria decide the identity"],
        "evidence_refs": ["test.log"], "unverified": [],
    }
    value.update(extra)
    path.write_text("```pipeline-evidence\n%s\n```\n" % json.dumps(value), encoding="utf-8")


def build(root, task_id="demo", branch="demo-task"):
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text("stable\n", encoding="utf-8")
    (root / ".gitignore").write_text("/.worktrees/\n", encoding="utf-8")
    contract_sheet(root, task_id)
    directory = root / ".pipeline" / task_id
    directory.mkdir(parents=True)
    (directory / "test.log").write_text("observed output\n", encoding="utf-8")
    for name, role in (("executor-result.json", "executor"), ("reviewer-result.json", "reviewer")):
        (directory / name).write_text(json.dumps({
            "schema": 1, "task_id": task_id, "role": role, "status": "pass",
            "acceptance": [], "unverified": []}), encoding="utf-8")
    (directory / "final-result.json").write_text(json.dumps({
        "schema": 1, "task_id": task_id, "role": "final", "status": "pass", "exit_code": 0,
        "acceptance": [{"id": "acceptance-test-1", "status": "pass", "exit_code": 0,
                        "evidence_refs": ["test.log"]}], "unverified": []}), encoding="utf-8")
    sh(root, "init", "-q", "-b", "main")
    sh(root, "config", "user.email", "reviewer@example.invalid")
    sh(root, "config", "user.name", "Reviewer")
    sh(root, "add", ".")
    sh(root, "commit", "-qm", "product baseline")
    reported_head = sh(root, "rev-parse", "HEAD").stdout.strip()
    sh(root, "worktree", "add", "-b", branch, f".worktrees/{task_id}", reported_head)
    worktree = (root / ".worktrees" / task_id).resolve()
    for name, role in (("executor-report.md", "executor"), ("review-report.md", "reviewer"),
                       ("final-check.md", "main-final")):
        report(worktree / ".pipeline" / task_id / name, task_id, worktree, branch,
               reported_head, role, root.resolve())
    sh(worktree, "add", ".pipeline")
    sh(worktree, "commit", "-qm", "task stage reports")
    (worktree / "src" / "app.py").write_text("task product change\n", encoding="utf-8")
    sh(worktree, "add", "src/app.py")
    sh(worktree, "commit", "-qm", "task product change")
    return directory, worktree, reported_head


def verify(directory, task_id, branch, phase=None):
    if phase is None:
        return core.evidence_verify(directory, task_id, branch)
    return core.evidence_verify(directory, task_id, branch, phase)


results = {}


def check(label, value, expected=None, exact=False):
    if expected is None:
        results[label] = value
    else:
        results[label] = {"ok": (value == expected) if exact else bool(value),
                          "observed": value, "expected": expected}


# 1. post-merge passes on merged product-path changes
if not PRE_TASK:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        directory, worktree, head = build(root)
        sh(root, "merge", "--no-ff", "-m", "merge demo-task", "demo-task")
        changed = sh(root, "diff", "--name-only", head, "HEAD").stdout.split()
        before = {n: (directory / n).read_bytes() for n in
                  ("executor-report.md", "review-report.md", "final-check.md")}
        errors = core.gate_check(directory, "demo", "main", "post-merge")
        after = {n: (directory / n).read_bytes() for n in
                 ("executor-report.md", "review-report.md", "final-check.md")}
        check("1a_gate_post_merge_exit_ok", errors, [], exact=True)
        check("1b_product_path_in_merge", "src/app.py" in changed, True, exact=True)
        check("1c_report_bytes_unchanged", before == after, True, exact=True)
        check("1d_active_phase_still_rejects", verify(directory, "demo", "main"), True)
        check("1e_finalized_phase_accepts", verify(directory, "demo", "main", "finalized"), [], exact=True)

# 2. revision mismatch
if not PRE_TASK:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        directory, _worktree, _head = build(root)
        sh(root, "merge", "--no-ff", "-m", "merge demo-task", "demo-task")
        values = {name: json.loads((directory / name).read_text().split("```")[1].split("\n", 1)[1])
                  for name in ("executor-report.md", "review-report.md", "final-check.md")}
        for name, value in values.items():
            value["sheet_revision"] = 7
            (directory / name).write_text("```pipeline-evidence\n%s\n```\n" % json.dumps(value),
                                          encoding="utf-8")
        errors = core.gate_check(directory, "demo", "main", "post-merge")
        check("2a_revision_mismatch_rejected", errors, True)
        check("2b_all_three_named",
              sorted(errors) == sorted(
                  f"{n} was produced against task sheet revision 7 but the current revision is 1"
                  for n in values), True, exact=True)

# 3. task id mismatch
if not PRE_TASK:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        directory, _worktree, _head = build(root)
        sh(root, "merge", "--no-ff", "-m", "merge demo-task", "demo-task")
        for name in ("executor-report.md", "review-report.md", "final-check.md"):
            raw = json.loads((directory / name).read_text().split("```")[1].split("\n", 1)[1])
            raw["task_id"] = "other-task"
            (directory / name).write_text("```pipeline-evidence\n%s\n```\n" % json.dumps(raw),
                                          encoding="utf-8")
        errors = core.gate_check(directory, "demo", "main", "post-merge")
        check("3a_report_names_other_task", errors, True)
        check("3b_task_identity_mismatch_named",
              all(f"{n} task identity mismatch" in errors
                  for n in ("executor-report.md", "review-report.md", "final-check.md")), True, exact=True)
        errors2 = verify(directory, "other-task", "main", "finalized")
        check("3c_directory_name_checked",
              errors2 == ["evidence directory does not match the verified task id"], True, exact=True)

# 4. missing main-worktree re-verification
if not PRE_TASK:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        directory, worktree, _head = build(root)
        sh(root, "merge", "--no-ff", "-m", "merge demo-task", "demo-task")
        for name in ("executor-report.md", "review-report.md", "final-check.md"):
            path = directory / name
            raw = json.loads(path.read_text().split("```")[1].split("\n", 1)[1])
            raw["commands"][0]["cwd"] = str(worktree)
            path.write_text("```pipeline-evidence\n%s\n```\n" % json.dumps(raw), encoding="utf-8")
        errors = core.gate_check(directory, "demo", "main", "post-merge")
        check("4a_missing_reverification_rejected",
              "post-merge re-verification in the main worktree is missing" in errors, True, exact=True)
        check("4b_identity_part_clean", verify(directory, "demo", "main", "finalized"), [], exact=True)

# 5. active phase unchanged (four scenarios, diffed against the pre-task code)
with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    directory, worktree, head = build(root)
    sh(root, "rev-parse", "--verify", "demo-task")
    for name, role in (("executor-report.md", "executor"), ("review-report.md", "reviewer"),
                       ("final-check.md", "main-final")):
        report(directory / name, "demo", worktree, "demo-task", head, role, root.resolve())
    nested = {name: json.loads((directory / name).read_text().split("```")[1].split("\n", 1)[1])
              for name in ("executor-report.md", "review-report.md", "final-check.md")}
    active_unmerged = verify(directory, "demo", "main")
    for name, raw in nested.items():
        (directory / name).write_text(
            "```pipeline-evidence\n%s\n```\n" % json.dumps(dict(raw, head="1" * 40)), encoding="utf-8")
    active_bad_head = verify(directory, "demo", "main")
    for name, raw in nested.items():
        (directory / name).write_text(
            "```pipeline-evidence\n%s\n```\n" % json.dumps(dict(raw, worktree=str(root / "old-worktree"))),
            encoding="utf-8")
    active_bad_worktree = verify(directory, "demo", "main")
    for name, raw in nested.items():
        (directory / name).write_text(
            "```pipeline-evidence\n%s\n```\n" % json.dumps(dict(raw, branch="demo-task-gone")),
            encoding="utf-8")
    active_gone_branch = verify(directory, "demo", "main")
    OUT = Path(__file__).resolve().parent / ("active_sets_%s.json" % MODE)
    OUT.write_text(json.dumps({
        "unmerged_branch": sorted(active_unmerged),
        "non_ancestor_head": sorted(active_bad_head),
        "non_canonical_worktree": sorted(active_bad_worktree),
        "missing_branch_ref": sorted(active_gone_branch)}, indent=1), encoding="utf-8")

# 6. CLI phase wiring (current only)
if not PRE_TASK:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        directory, _worktree, _head = build(root)
        sh(root, "merge", "--no-ff", "-m", "merge demo-task", "demo-task")
        env = {**os.environ, "PIPELINE_TOOLS_DISABLE_AUTO_METRICS": "1",
               "PYTHONPATH": str(Path(MODE_PATH).resolve())}
        base = [sys.executable, "-m", "pipeline_tools", "evidence", "verify", str(directory),
                "--task-id", "demo", "--branch", "main", "--phase"]
        active = subprocess.run([*base, "active"], cwd=root, env=env, capture_output=True, text=True)
        finalized = subprocess.run([*base, "finalized"], cwd=root, env=env, capture_output=True, text=True)
        gate = subprocess.run([sys.executable, "-m", "pipeline_tools", "gate", "post-merge",
                               str(directory), "--task-id", "demo", "--branch", "main"],
                              cwd=root, env=env, capture_output=True, text=True)
        results["6_cli"] = {"active_rc": active.returncode, "active_out": active.stdout.strip(),
                            "finalized_rc": finalized.returncode, "finalized_out": finalized.stdout.strip(),
                            "gate_rc": gate.returncode, "gate_out": gate.stdout.strip()}

# 7. reconcile mixed identity (current only) and 8. historical shape (both modes)
import pipeline_tools.reconcile as reconcile  # noqa: E402


def build_reconcile_repo(root, *, revisions, task_id="demo", final_overrides=None):
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text("stable\n", encoding="utf-8")
    contract_sheet(root, task_id)
    sh(root, "init", "-q", "-b", "main")
    sh(root, "config", "user.email", "reviewer@example.invalid")
    sh(root, "config", "user.name", "Reviewer")
    sh(root, "add", ".")
    sh(root, "commit", "-qm", "baseline")
    head = sh(root, "rev-parse", "HEAD").stdout.strip()
    directory = root / ".pipeline" / task_id
    directory.mkdir(parents=True)
    (directory / "test.log").write_text("observed\n", encoding="utf-8")
    sh(root, "worktree", "add", "-b", "demo-task", ".worktrees/demo", head)
    worktree = (root / ".worktrees" / "demo").resolve()
    for name, role in (("executor-result.json", "executor"), ("reviewer-result.json", "reviewer")):
        (directory / name).write_text(json.dumps({
            "schema": 1, "task_id": task_id, "role": role, "status": "pass",
            "acceptance": [], "unverified": []}), encoding="utf-8")
    (directory / "final-result.json").write_text(json.dumps({
        "schema": 1, "task_id": task_id, "role": "final", "status": "pass", "exit_code": 0,
        "acceptance": [{"id": "acceptance-test-1", "status": "pass", "exit_code": 0,
                        "evidence_refs": ["test.log"]}], "unverified": []}), encoding="utf-8")
    for name, role in (("executor-report.md", "executor"), ("review-report.md", "reviewer")):
        report(directory / name, task_id, worktree, "demo-task", head, role, root.resolve(),
               **({"sheet_revision": revisions} if revisions is not None else {}))
        if revisions is None:
            raw = json.loads((directory / name).read_text().split("```")[1].split("\n", 1)[1])
            raw.pop("sheet_revision", None)
            raw.pop("observed_at_commit", None)
            (directory / name).write_text("```pipeline-evidence\n%s\n```\n" % json.dumps(raw),
                                          encoding="utf-8")
    report(directory / "final-check.md", task_id, root.resolve(), "main", head, "main-final",
           root.resolve(), **({"sheet_revision": revisions} if revisions is not None else {}))
    if revisions is None:
        raw = json.loads((directory / "final-check.md").read_text().split("```")[1].split("\n", 1)[1])
        raw.pop("sheet_revision", None)
        raw.pop("observed_at_commit", None)
        (directory / "final-check.md").write_text("```pipeline-evidence\n%s\n```\n" % json.dumps(raw),
                                                  encoding="utf-8")
    if final_overrides:
        for name, extra in final_overrides.items():
            path = directory / name
            raw = json.loads(path.read_text().split("```")[1].split("\n", 1)[1])
            raw.update(extra)
            path.write_text("```pipeline-evidence\n%s\n```\n" % json.dumps(raw), encoding="utf-8")
    return directory, worktree, head


if not PRE_TASK:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        build_reconcile_repo(root, revisions=1)
        value = reconcile.reconcile_task(root, root / "docs" / "tasks" / "demo.md")
        check("7a_mixed_identity_no_conflict", "report identity conflict" not in value["errors"], True, exact=True)
        check("7b_mixed_identity_not_incomplete", "report identity is incomplete" not in value["errors"], True, exact=True)
        check("7c_identity_task_id", value["identity"]["task_id"], "demo", exact=True)
        check("7d_identity_revision", value["identity"]["sheet_revision"], 1, exact=True)
        check("7e_branch_not_uniform", value["identity"]["branch"], None, exact=True)
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        build_reconcile_repo(root, revisions=1, final_overrides={"review-report.md": {"sheet_revision": 2}})
        value = reconcile.reconcile_task(root, root / "docs" / "tasks" / "demo.md")
        check("7f_diverging_revision_conflict", "report identity conflict" in value["errors"], True, exact=True)
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        build_reconcile_repo(root, revisions=1, final_overrides={"review-report.md": {"task_id": "other"}})
        value = reconcile.reconcile_task(root, root / "docs" / "tasks" / "demo.md")
        check("7g_diverging_task_conflict", "report identity conflict" in value["errors"], True, exact=True)

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    directory, _worktree, _head = build_reconcile_repo(root, revisions=None)
    value = reconcile.reconcile_task(root, root / "docs" / "tasks" / "demo.md")
    from pipeline_tools.core import evidence_revision_status, load_contract  # noqa: E402
    contract = load_contract(root / "docs" / "tasks" / "demo.md")[0]
    records = {name: json.loads((directory / name).read_text().split("```")[1].split("\n", 1)[1])
               for name in ("executor-report.md", "review-report.md", "final-check.md")}
    OUT = Path(__file__).resolve().parent / ("historical_%s.json" % MODE)
    OUT.write_text(json.dumps({
        "reconcile_errors": value["errors"],
        "conflict": "report identity conflict" in value["errors"],
        "incomplete": "report identity is incomplete" in value["errors"],
        "unverified": value["unverified"],
        "revision_status": evidence_revision_status(root, "demo", contract, records)}, indent=1,
        default=str), encoding="utf-8")

# real historical evidence directory: active phase must be identical
REPO = Path.cwd()
historical_dir = REPO / ".pipeline" / "task-evidence-reconcile"
if historical_dir.is_dir():
    OUT = Path(__file__).resolve().parent / ("realhistorical_%s.json" % MODE)
    OUT.write_text(json.dumps(sorted(core.evidence_verify(
        historical_dir, "task-evidence-reconcile", "main")), indent=1), encoding="utf-8")

print(json.dumps(results, indent=1, default=str))
```

`historical.py`（历史形态证据在两相下的判据）：

```python
"""Historical-shaped evidence (no sheet_revision / no observed_at_commit)."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from pipeline_tools import core, reconcile  # noqa: E402


def sh(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True)


def build(root):
    contract = {"schema": 1, "task_id": "demo", "allowed_paths": ["src/**", ".pipeline/**"],
                "forbidden_paths": [],
                "acceptance_tests": [{"id": "acceptance-test-1", "evidence_level": 3,
                                      "test_ref": "tests/test_evidence.py",
                                      "command_ref": "python -m pytest -q tests/test_evidence.py"}]}
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text("stable\n", encoding="utf-8")
    (root / "docs" / "tasks").mkdir(parents=True)
    (root / "docs" / "tasks" / "demo.md").write_text(
        "<!-- Task ID: demo -->\n```pipeline-contract\n%s\n```\n" % json.dumps(contract), encoding="utf-8")
    sh(root, "init", "-q", "-b", "main")
    sh(root, "config", "user.email", "r@example.invalid")
    sh(root, "config", "user.name", "R")
    sh(root, "add", ".")
    sh(root, "commit", "-qm", "baseline")
    head = sh(root, "rev-parse", "HEAD").stdout.strip()
    directory = root / ".pipeline" / "demo"
    directory.mkdir(parents=True)
    (directory / "test.log").write_text("x\n", encoding="utf-8")
    sh(root, "worktree", "add", "-b", "demo-task", ".worktrees/demo", head)
    worktree = (root / ".worktrees" / "demo").resolve()
    for name, role in (("executor-result.json", "executor"), ("reviewer-result.json", "reviewer")):
        (directory / name).write_text(json.dumps({"schema": 1, "task_id": "demo", "role": role,
                                                  "status": "pass", "acceptance": [], "unverified": []}),
                                      encoding="utf-8")
    (directory / "final-result.json").write_text(json.dumps({
        "schema": 1, "task_id": "demo", "role": "final", "status": "pass", "exit_code": 0,
        "acceptance": [{"id": "acceptance-test-1", "status": "pass", "exit_code": 0,
                        "evidence_refs": ["test.log"]}], "unverified": []}), encoding="utf-8")

    def write(name, worktree_value, branch, role):
        target = worktree / ".pipeline" / "demo" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("```pipeline-evidence\n%s\n```\n" % json.dumps({
            "schema": 2, "task_id": "demo", "worktree": str(worktree_value), "branch": branch,
            "role": role, "round": 1, "status": "PASS", "head": head,
            "generated_at": "2026-01-01T00:00:00+00:00",
            "commands": [{"command": "python -m pytest -q tests/test_evidence.py", "exit_code": 0,
                          "cwd": str(root.resolve()), "evidence_ref": "test.log"}],
            "assertions": ["historical shape, no revision fields"],
            "evidence_refs": ["test.log"], "unverified": []}), encoding="utf-8")

    write("executor-report.md", worktree, "demo-task", "executor")
    write("review-report.md", worktree, "demo-task", "reviewer")
    write("final-check.md", worktree, "demo-task", "main-final")
    sh(worktree, "add", ".pipeline")
    sh(worktree, "commit", "-qm", "historical reports")
    (worktree / "src" / "app.py").write_text("changed\n", encoding="utf-8")
    sh(worktree, "add", "src/app.py")
    sh(worktree, "commit", "-qm", "product change")
    return directory, worktree, head


with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    directory, worktree, head = build(root)
    print("== unmerged ==")
    print(" active   :", core.evidence_verify(directory, "demo", "main"))
    print(" finalized:", core.evidence_verify(directory, "demo", "main", "finalized"))
    sh(root, "merge", "--no-ff", "-m", "merge demo-task", "demo-task")
    print("== merged --no-ff with product change ==")
    print(" active   :", core.evidence_verify(directory, "demo", "main"))
    print(" finalized:", core.evidence_verify(directory, "demo", "main", "finalized"))
    value = reconcile.reconcile_task(root, root / "docs" / "tasks" / "demo.md")
    print("reconcile identity errors:", [e for e in value["errors"] if "identity" in e])
    print("reconcile revision unverified:", [u for u in value["unverified"] if "revision" in u])
    print("reconcile revision errors:", [e for e in value["errors"] if "revision" in e])
```

## 附录 B：关键原始输出

**改动前后 active 阶段错误集合逐字相同**（`diff /tmp/pmei/active_sets_pretask.json /tmp/pmei/active_sets_current.json` → 无输出、exit 0）：

```
{"unmerged_branch": 9 条, "non_ancestor_head": 12 条,
 "non_canonical_worktree": 9 条, "missing_branch_ref": 9 条}
```

**同一份已合并证据的两相 CLI**（`6_cli`）：

```
active_rc = 3
active_out = FAIL: executor-report.md head does not match current Git identity; executor-report.md branch does not match current Git identity; executor-report.md worktree does not match current Git identity; executor-report.md branch mismatch; review-report.md head does not match current Git identity; review-report.md branch does not match current Git identity; review-report.md worktree does not match current Git identity; review-report.md branch mismatch; final-check.md head does not match current Git identity; final-check.md branch does not match current Git identity; final-check.md worktree does not match current Git identity; final-check.md branch mismatch
finalized_rc = 3
finalized_out = FAIL: finalization.json is missing
gate_rc = 0
gate_out = PASS
UNVERIFIED: implement-plan hash unrecorded and requirements doc unreadable: implement-plan.md
```

`gate pre-merge`（同一目录）：rc 3，输出即上面那 12 条提交身份错误 —— 证明 `gate post-merge` → finalized、`gate pre-merge`/默认 → active。

**历史形态证据（无 `sheet_revision`、无 `observed_at_commit`），`--no-ff` 合并且改动产品路径后**：

```
active    : 12 条 head/branch/worktree/branch mismatch 错误
finalized : ['executor-report.md sheet_revision must be a positive integer',
             'executor-report.md observed_at_commit must be a non-empty string',
             'review-report.md sheet_revision must be a positive integer',
             'review-report.md observed_at_commit must be a non-empty string',
             'final-check.md sheet_revision must be a positive integer',
             'final-check.md observed_at_commit must be a non-empty string']
reconcile identity errors : 只有 evidence_verify(active) 产生的 6 条 head/worktree 错误
reconcile revision errors : []（revision 判据只产出 unverified，不新增错误）
```

**独立夹具的 post-merge 通过 + 字节不变**（`1a`–`1e` 全 `ok`）：

```
1a_gate_post_merge_exit_ok  = []            # gate_check(...'post-merge') 无错误
1b_product_path_in_merge    = True          # 合并引入 src/app.py
1c_report_bytes_unchanged   = True          # 三份报告字节逐一相等
1d_active_phase_still_rejects = 12 条提交身份错误
1e_finalized_phase_accepts  = []
CLI 版本：gate post-merge rc 0 / PASS；报告 sha256 前后相同；夹具仓库 git status 前后都为空
```
