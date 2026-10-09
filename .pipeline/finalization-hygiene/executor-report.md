# executor-report：finalization-hygiene（round 2，纯文档同步）

## 任务身份

- task-id：`finalization-hygiene`
- task-type：`repair`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene`
- branch：`finalization-hygiene`
- 分支尖端（本轮开始）：`d002c23f765bfae675e613ed7939e6eac24bb64e`
- 实现提交（本轮文档提交）：`21e81682cd0a46288da2263f9e92ab2183015f28`
- role：executor，round **2**
- sheet_revision：**2**
- sheet_sha256：`65f6e2069ad08e3edad532a1c728191b81a96020d6781d427a8b2da0494a552e`

## 背景与范围

round 1 按契约 `allowed_paths`（revision 1）的边界停下：实现已完成并交付，但 `references/acceptance-evidence.md` 与 `references/execution-and-review.md` 不在当时的 `allowed_paths` 内，因此这两份文件里**已收窄前**的旧口径被记入 `unverified` 而未改。主代理随后用 `task amend` 登记 revision 2，把这两份文件加入 `allowed_paths`（`allowed_paths.added: ['references/acceptance-evidence.md', 'references/execution-and-review.md']`）。本轮在 revision 2 下只做这两处文档同步，**实现代码一字未动**（`pipeline_tools/core.py`、`pipeline_tools/planning.py`、`tests/**`、`references/merge-and-recovery.md`、`SKILL.md` 均无改动，实现提交 `f21189248027ed7b37ce7e7e2c847fb659aa7c19` 保持不变）。

## 改动一：`references/acceptance-evidence.md`（第 68 段）

改动前（原文）：

> 同一套基准（`pipeline_tools/core.py` 的 `evidence_only_paths`）也决定 schema-2 报告的 `head` 是否仍然有效：报告写的是它评判的实现提交，而提交这份报告本身就会移动 `HEAD`，因此 `head != HEAD` 时只要 `head` 是 `HEAD` 的祖先、且 `head..HEAD` 只动**本任务证据目录**（含 `.pipeline/metrics/`）就仍然通过（`head_advanced_by_evidence_only`）。`head` 不是 `HEAD` 的祖先（例如未知提交），或区间内改动了产品/测试路径时，`evidence verify` 仍报 `<report> head does not match current Git identity`。这条规则不是“任何 head 都接受”：它**只豁免任务自身证据**的提交。

改动后（原文）：

> 同一套基准（`pipeline_tools/core.py` 的 `evidence_only_paths`）也决定 schema-2 报告的 `head` 是否仍然有效：报告写的是它评判的实现提交，而提交这份报告本身就会移动 `HEAD`，因此 `head != HEAD` 时只要 `head` 是 `HEAD` 的祖先、且 `head..HEAD` 的改动全部落在 `.pipeline/` 子树内就仍然通过（`head_advanced_by_evidence_only`）。证据路径按路径判定：`.pipeline/**` 下**任意**任务的证据目录、`.pipeline/metrics/` 与 `.pipeline/planning/` 都算证据路径，`.pipeline` 之外的任何改动都不算——因此别的任务提交自己的证据不会让这份报告失效。`head` 不是 `HEAD` 的祖先（例如未知提交），或区间内改动了产品/测试路径时，`evidence verify` 仍报 `<report> head does not match current Git identity`。这条规则不是“任何 head 都接受”：同一提交同时改动证据路径与产品路径的**混合提交**，以及路径无法解析的区间，一律判为**非**仅证据提交，仍然报错。

改对的判据：证据路径按路径判定（`.pipeline/**` 任意任务、`.pipeline/metrics/`、`.pipeline/planning/` 都算，`.pipeline` 之外不算）；混合提交与无法解析的区间 fail-closed；保留反向边界（`head` 非 `HEAD` 祖先时仍报 `head does not match current Git identity`）。

## 改动二：`references/execution-and-review.md`（第 32 条）

改动前（原文片段）：

> ……而是接受“**只有本任务证据**的推进”：`head` 是 `HEAD` 的祖先且 `head..HEAD` 的改动**全部落在 `.pipeline/<task-id>/**`**（含 `.pipeline/metrics/`）内时报告仍然有效（`core.py` 的 `head_advanced_by_evidence_only`）；`head` 不是祖先、或区间内动了产品/测试路径时仍报 `head does not match current Git identity`。

改动后（原文片段）：

> ……而是接受“只有证据提交的推进”：`head` 是 `HEAD` 的祖先且 `head..HEAD` 的改动全部落在 `.pipeline/` 子树内时报告仍然有效（`core.py` 的 `head_advanced_by_evidence_only`）——证据路径按路径判定，`.pipeline/**` 下**任意**任务的证据目录（含 `.pipeline/metrics/` 与 `.pipeline/planning/`）都算证据路径，`.pipeline` 之外的任何改动都不算，因此别的任务提交自己的证据不使本报告失效；同一提交同时改动证据路径与产品路径的**混合提交**，以及路径无法解析的区间，一律判为**非**仅证据提交（fail-closed）；`head` 不是祖先、或区间内动了产品/测试路径时仍报 `head does not match current Git identity`。

该条尾部原有的一句「刻意非零的命令必须在报告里用 `expected_exit_code` 声明，否则 gate 报 `contains a non-zero command exit_code`」逐字保留，未改动。

## 改动最小性

- `git diff` 只含每个文件的一处段落替换：`references/acceptance-evidence.md` 1 行、`references/execution-and-review.md` 1 行。
- 未改其它段落、未重写整节、未改实现代码、未改 `references/merge-and-recovery.md` 与 `SKILL.md`（round 1 已写对）、未改版本号与 `references/compat-and-migration.md`、未回退任何提交、未动主工作树与其它任务证据目录。

## grep 逐句核对（三项被推翻的表述）

命令（cwd = worktree 根）：

`grep -rn "只动本任务证据目录\|只豁免任务自身证据\|全部落在 \`.pipeline/<task-id>/\*\*\`\|只有本任务证据" references/ SKILL.md`

结果：**无输出，退出码 1**（grep 无匹配即退出码 1，属期望结果）。三类旧表述已从 `references/` 与 `SKILL.md` 全部消失：

| 旧表述 | 查询结果 |
|---|---|
| 「只动本任务证据目录」 | 无匹配（退出码 1） |
| 「只豁免任务自身证据」 | 无匹配（退出码 1） |
| 「全部落在 `.pipeline/<task-id>/**`」 | 无匹配（退出码 1） |

补充扫描：`grep -rn "只动本任务\|只豁免任务自身\|只有本任务证据\|本任务证据的提交\|本任务证据提交推进" references/ SKILL.md` → 无匹配（退出码 1）。

已落地的放宽口径：`grep -c "任意\*\*任务" references/acceptance-evidence.md references/execution-and-review.md` → 两文件各 1 处命中。

## 验收测试（逐条）

| ID | 命令（cwd = worktree 根） | 退出码 |
|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files` | 0（1 passed, 55 deselected） |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit` | 0（1 passed, 55 deselected） |
| acceptance-test-3 | `python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits` | 0（1 passed, 51 deselected） |
| acceptance-test-4 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0（1 passed, 27 deselected） |

全量测试：`python -m pytest -q`（cwd = worktree 根，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）→ 退出码 0，**401 passed, 28 subtests passed**（与 round 1 交付后的 401/28 一致：本轮只改文档，未增删用例与断言）。

## 其它检查（cwd = worktree 根）

- `python -m pipeline_tools task validate docs/tasks/finalization-hygiene.md` → 退出码 0（PASS）。
- `python -m pipeline_tools result verify .pipeline/finalization-hygiene/executor-result.json --task-id finalization-hygiene --role executor` → 退出码 0（PASS）。
- `python -m pipeline_tools scope check . --task-id finalization-hygiene --allowed <revision 2 的 allowed_paths，含新增的两份 references> --forbidden <revision 2 的 forbidden_paths>` → 退出码 0（PASS）。
- `git diff --check` → 退出码 0。
- 身份核对：`git rev-parse HEAD` 本轮起点 = `d002c23f765bfae675e613ed7939e6eac24bb64e`；`git branch --show-current` = `finalization-hygiene`。

## 契约一致性核对

- revision 2 的 `allowed_paths` 已含 `references/acceptance-evidence.md` 与 `references/execution-and-review.md`；`scope check` PASS 即证明本轮改动全部落在允许范围内。
- `docs/tasks/finalization-hygiene.md` 未被本轮改动；`sha256sum docs/tasks/finalization-hygiene.md` = `65f6e2069ad08e3edad532a1c728191b81a96020d6781d427a8b2da0494a552e`，与主工作树 `.pipeline/finalization-hygiene/amendments.json` 里 revision 2 记录的 `sheet_sha256` 逐字一致（只读核对，未写入主工作树）。
- 非目标逐项未触碰：未把放宽范围扩到 `.pipeline` 之外的任意路径；未保留保留集之外的一般过程产物；未放宽 retention 快照判据与产品路径失效判据；未改历史任务单/历史证据/五个已完成任务的证据目录；未删除或放宽任何既有断言（全量 401 passed 未变）。

## 决策点核查

1. 混合提交无法机械判定性质 —— 未触发（本轮不改实现）。
2. 既有断言必须被实质性削弱才能通过 —— 未触发（断言一字未改）。
3. 保留本地状态文件破坏 retention 快照或既有校验 —— 未触发。
4. 实现必须修改契约未列出的文件 —— 未触发（revision 2 已把两份文件纳入 `allowed_paths`，`scope check` PASS）。

```pipeline-evidence
{"schema": 2, "task_id": "finalization-hygiene", "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "branch": "finalization-hygiene", "role": "executor", "round": 2, "status": "PASS", "head": "21e81682cd0a46288da2263f9e92ab2183015f28", "sheet_revision": 2, "sheet_sha256": "65f6e2069ad08e3edad532a1c728191b81a96020d6781d427a8b2da0494a552e", "observed_at_commit": "21e81682cd0a46288da2263f9e92ab2183015f28", "generated_at": "2026-10-09T11:20:00+00:00", "commands": [{"command": "git rev-parse HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git branch --show-current", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools task validate docs/tasks/finalization-hygiene.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "grep -rn \"只动本任务证据目录\\|只豁免任务自身证据\\|全部落在 `.pipeline/<task-id>/**`\\|只有本任务证据\" references/ SKILL.md  # no matches is the expected result", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 1, "expected_exit_code": 1, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools result verify .pipeline/finalization-hygiene/executor-result.json --task-id finalization-hygiene --role executor", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools scope check . --task-id finalization-hygiene --allowed pipeline_tools/core.py pipeline_tools/planning.py tests/test_planning.py tests/test_evidence.py references/merge-and-recovery.md references/acceptance-evidence.md references/execution-and-review.md SKILL.md docs/tasks/finalization-hygiene.md .pipeline/finalization-hygiene/** --forbidden docs/goal.md .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/finalization-report-reader/** .pipeline/security-scan-repair-20261001/** .pipeline/security-scan-repair-20261001-continuation-1/** .env credentials/**", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene", "exit_code": 0, "evidence_ref": "executor-report.md"}], "assertions": ["references/acceptance-evidence.md and references/execution-and-review.md now describe the widened, path-based evidence-only basis instead of this task's own evidence directory", "the three overturned phrasings no longer appear anywhere under references/ or in SKILL.md (grep exits 1, no matches)", "mixed evidence-plus-product commits and unresolvable ranges are documented as fail-closed, and the reverse boundary (a non-ancestor head still reports head does not match current Git identity) is preserved", "the change is one paragraph per file: no other paragraph, no implementation code, no other document was touched", "the implementation commit f211892 is unchanged and all four acceptance tests plus the full suite still pass at 401 passed, 28 subtests passed", "the task sheet is unmodified and its sha256 matches the revision 2 record in the main worktree amendment chain"], "evidence_refs": ["executor-report.md", "executor-result.json"], "unverified": ["round 1 stopped at the contract boundary (revision 1 allowed_paths excluded these two reference files) and recorded the stale wording in unverified; round 2, under revision 2, syncs those two documents to the widened evidence-only basis", "references/acceptance-evidence.md line 66 (the evidence_freshness product_head paragraph) still says changes must fall inside the evidence directory without naming .pipeline explicitly; it names neither a task-specific directory nor the .pipeline/<task-id>/** form, and the instruction scoped this round to the two named passages, so it was deliberately left untouched for the reviewer to decide", "the document-only round changes no behaviour, so no new runtime observation beyond the unchanged acceptance tests and full suite was collected"]}
```
