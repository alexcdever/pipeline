# 独立审查报告（round 2）：finalization-hygiene

- 任务单：`docs/tasks/finalization-hygiene.md`，revision **2**
- worktree：`D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene`
- branch：`finalization-hygiene`
- 本轮待审（纯文档）：`21e81682cd0a46288da2263f9e92ab2183015f28`
- round 1 实现（代码）：`f211892`
- 审查运行时分支尖端：`07679fcb4f3e4e69de0f8aeab9a8a229b68f6952`
- 全部复验亲自执行；主工作树只读，未做任何写操作。

## 1. 环境检查（逐项）

| # | 检查 | 结果 |
|---|------|------|
| 1 | `git rev-parse --show-toplevel` | PASS → `D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene` |
| 2 | `git branch --show-current` | PASS → `finalization-hygiene` |
| 3 | `git rev-parse HEAD` | PASS → `07679fcb4f3e4e69de0f8aeab9a8a229b68f6952` |
| 4 | `git merge-base --is-ancestor 21e8168 HEAD` | PASS → 退出码 0 |
| 5 | `python -m pipeline_tools task validate docs/tasks/finalization-hygiene.md` | PASS → 退出码 0 |
| 6 | 只读 / 不动主工作树 | PASS → 主工作树 `git status` 无本次审查产生的改动；未新建 worktree |

## 2. 第 4 节各点独立观察

### 点 1 — 口径与实现一致（逐句对照 `pipeline_tools/core.py`）

实现（`core.py:2701 evidence_only_paths`）：空/绝对/盘符/含 `..` 的路径 → `False`；`.pipeline` 或 `.pipeline/` 前缀 → 证据路径；否则 `False`。`core.py:2735 head_advanced_by_evidence_only`：非字符串/非 40 位十六进制/非祖先/区间不可解析 → `False`；区间改动全为证据路径 → `True`。`core.py:1830` 显示 `evidence_freshness` 也调用同一函数。

我用实现本身打了 15 组路径探针，结果与两处新文档逐条吻合：

| 路径 | 结果 | 文档主张 |
|------|------|---------|
| `.pipeline/other-task/executor-report.md` | True | 任意任务证据目录算证据 |
| `.pipeline/metrics/events.jsonl` | True | metrics 算证据 |
| `.pipeline/planning/x/dispatch.json` | True | planning 算证据 |
| `.pipeline/foo/bar/baz.txt` | True | `.pipeline/**` |
| `pipeline_tools/core.py` / `tests/x.py` / `SKILL.md` | False | `.pipeline` 之外不算 |
| `.workflow/task/x.md` | False | `.pipeline` 之外不算 |
| `.pipeline/a/x.md` + `pipeline_tools/core.py` | False | 混合提交 fail-closed |
| `/etc/passwd`、`C:/x/y`、`.pipeline/../../etc/x`、`""` | False | 路径不可解析 fail-closed |

补充：`PIPELINE_DIR_NAMES = (".pipeline",)`，故 `.workflow/metrics/x` 不被 `is_metrics_path` 命中（实测 `False`），文档"`.pipeline` 之外的任何改动都不算"无例外缺口。**未发现文档说 A、实现做 B。**

### 点 2 — 旧表述已消失

在 `references/` 与 `SKILL.md` 全量 grep：`只动本任务证据目录`、`只豁免任务自身证据`、`只有本任务证据`、`` 全部落在 `.pipeline/<task-id>/**` `` —— 四类模式均**无匹配**（各 `exit=1`）。`本任务证据` 在四份在范围内文档中也无匹配。

**残留**：`references/compat-and-migration.md:13`（v0.15.0→v0.16.0 历史条目）仍写"区间内只改本任务证据（含 `.pipeline/metrics/`）时报告保持有效"。该文件不在 revision 2 的 `allowed_paths`、也不在 operation `documentation` 的 resources 内，本轮按要求不得改动——见 findings。

### 点 3 — 反向边界仍在

两处新段落都保留"`head` 不是 `HEAD` 的祖先（例如未知提交）… 仍报 `<report> head does not match current Git identity`"，并明确"这不是『任何 head 都接受』：混合提交与不可解析区间一律判为非仅证据提交"。实测 `head_advanced_by_evidence_only`：相等 → True；非祖先（`9`*40）→ False；非 40 位（`zzz`）→ False；跨产品提交的祖先 → False；跨证据提交的祖先 → True。规则未被写成"任何 head 都接受"。

### 点 4 — 改动最小

`git show --stat 21e8168` = `references/acceptance-evidence.md | 2 +-`、`references/execution-and-review.md | 2 +-`（2 files changed, 2 insertions, 2 deletions）。即两份文件各替换**一整行段落**，无整节重写；未触及 `merge-and-recovery.md`、`SKILL.md`、`compat-and-migration.md`、版本号，也未改任何实现代码。

### 点 5 — 候选残留 `acceptance-evidence.md:66` 的判断

**会误导，报为 finding（未修改文件）。**

`evidence_freshness` 在 `product_head` 分支确实调用放宽后的 `evidence_only_paths`（`core.py:1830`），所以第 66 行"判断 `product_head..HEAD` 的改动是否**全部落在证据目录内**"沿用了收窄前的措辞：读者会理解为"本任务证据目录"，从而以为别的任务的证据提交会触发 `product/test HEAD drifted`。同文件紧邻的第 68 行（本轮刚改）已写明"同一套基准…`.pipeline/**` 下**任意**任务的证据目录…都算证据路径"，两行自相矛盾。该行同属 `acceptance-evidence.md`（在 revision 2 scope 内），本轮只改了第 68 行而未同步第 66 行，属本轮口径同步的漏项。判断：措辞陈旧、与实现和同文件下文不一致，会误导，但实现行为正确、不影响 gate 结果。

### 点 6 — round 1 的 A/B 未被回退（自建夹具抽查）

自建临时 git 仓库（不复用实现测试）共 16 条断言，全部通过、退出码 0：

- **A 剪枝**：最终化 rc=0、`status=finalized`；`goal.json`、`amendments.json` 保留；无关过程文件 `scratch.log` 被剪掉；七件保留集（三报告 + 三结果 + `finalization.json`）齐全。
- **B 别的任务证据不失效**：任务 A 关闭后提交 `.pipeline/other-task/**`，`evidence verify --phase finalized` rc=0 PASS。
- **C 产品提交仍失效**：追加产品路径提交后同一校验 rc=3 `FAIL: finalization head is stale`。
- **D 混合提交仍失效**：`extra-evidence.txt` + `src/app.py` 同一提交后 rc=3 `FAIL: finalization head is stale`（fail-closed）。
- **E head 边界**：见点 3。

### 点 7 — 既有断言完整性

`git diff e75c787 21e8168 -- tests/` 为 **152 insertions, 0 deletions**（`tests/test_evidence.py +55`、`tests/test_planning.py +97`）。删除行为 0，不存在断言被删或弱化。

### 点 8 — 无越界

`git diff --name-only e75c787 21e8168` = `pipeline_tools/core.py`、`pipeline_tools/planning.py`、`tests/test_planning.py`、`tests/test_evidence.py`、`references/merge-and-recovery.md`、`references/acceptance-evidence.md`、`references/execution-and-review.md`、`SKILL.md`、`docs/tasks/finalization-hygiene.md`、`.pipeline/finalization-hygiene/executor-report.md`、`.pipeline/finalization-hygiene/executor-result.json` —— 全部落在 revision 2 `allowed_paths` 内。对五个已完成任务证据目录、`docs/goal.md`、`.env`、`credentials/**` 的改动 grep 计数为 0。`scope check`（全量 allowed/forbidden）退出码 0。

## 3. 亲自运行的命令

| 命令 | cwd | 退出码 |
|------|-----|--------|
| `python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files` | worktree | 0（1 passed, 55 deselected） |
| `python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit` | worktree | 0（1 passed） |
| `python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits` | worktree | 0（1 passed） |
| `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | worktree | 0（1 passed） |
| `python -m pytest -q` | worktree | 0（**401 passed, 28 subtests passed**） |
| `python -m pipeline_tools task validate docs/tasks/finalization-hygiene.md` | worktree | 0 |
| `python -m pipeline_tools result verify .pipeline/finalization-hygiene/executor-result.json --task-id finalization-hygiene --role executor` | worktree | 0（PASS） |
| `python -m pipeline_tools scope check . --task-id finalization-hygiene --allowed … --forbidden …` | worktree | 0（PASS） |
| `git diff --check` | worktree | 0 |
| `grep -rn "只动本任务证据目录" references/ SKILL.md` | worktree | 1（刻意非零：无匹配即正确） |
| `python /tmp/frr-review/hygiene_probe.py`（15 组路径探针） | worktree | 0 |
| `python /tmp/frr-review/hygiene_behaviour.py`（16 条自建行为断言） | worktree | 0 |

全量与执行者声明的 **401 passed, 28 subtests passed** 完全一致。

## 4. 结论

**PASS**

- 两处文档口径与 `evidence_only_paths` / `head_advanced_by_evidence_only` 实现逐条一致，无"文档说 A、实现做 B"。
- 旧表述在 `references/`、`SKILL.md` 中已消失；反向边界（非祖先仍报错）、混合提交 fail-closed、不可解析 fail-closed 均保留。
- 改动最小（两行段落替换，2 files / 2+ / 2−），未波及实现、未波及其它文档或版本号。
- round 1 的剪枝豁免与"仅证据提交"放宽经自建夹具复验未被回退，产品提交与混合提交仍失效。
- 无越界，既有断言零删除。

## 5. findings

1. **（本轮口径同步漏项，会误导）** `references/acceptance-evidence.md:66` 仍写 `evidence_freshness` 判断改动"是否全部落在证据目录内"，未点名 `.pipeline/**`；而实现（`core.py:1830`）与同文件第 68 行（本轮已改）都用放宽后的按路径判据，读者会误以为别的任务的证据提交会触发 `product/test HEAD drifted`。建议后续轮次把该句改为"全部落在 `.pipeline/` 子树内"。实现行为本身正确，不影响 gate 结论，故不改变 PASS 判定。
2. **（范围外残留，未要求本轮处理）** `references/compat-and-migration.md:13` 的 v0.15.0→v0.16.0 历史条目仍写"区间内只改本任务证据（含 `.pipeline/metrics/`）时报告保持有效"。该文件不在 revision 2 的 `allowed_paths`，本轮明确不得改动，仅作记录。
3. **（契约观察）** `acceptance-evidence.md` 与 `execution-and-review.md` 同属 operation `documentation` 的 resources，但本任务单"允许修改"散文段落只列了 `merge-and-recovery.md`、`SKILL.md`；两处文档最终由 revision 2 补入 `allowed_paths`（commit `06ff204`）后才可改，流程上依赖了一次修订，非缺陷。

```pipeline-evidence
{
  "schema": 2,
  "task_id": "finalization-hygiene",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
  "branch": "finalization-hygiene",
  "role": "reviewer",
  "round": 2,
  "status": "PASS",
  "head": "21e81682cd0a46288da2263f9e92ab2183015f28",
  "sheet_revision": 2,
  "sheet_sha256": "65f6e2069ad08e3edad532a1c728191b81a96020d6781d427a8b2da0494a552e",
  "observed_at_commit": "07679fcb4f3e4e69de0f8aeab9a8a229b68f6952",
  "generated_at": "2026-10-09T03:03:05+00:00",
  "commands": [
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalization_keeps_local_state_files",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalized_verification_survives_another_tasks_evidence_commit",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_evidence.py -k finalized_verification_still_fails_after_product_commits",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "python -m pytest -q",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "python -m pipeline_tools task validate docs/tasks/finalization-hygiene.md",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "python -m pipeline_tools result verify .pipeline/finalization-hygiene/executor-result.json --task-id finalization-hygiene --role executor",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "python -m pipeline_tools scope check . --task-id finalization-hygiene --allowed pipeline_tools/core.py pipeline_tools/planning.py tests/test_planning.py tests/test_evidence.py references/merge-and-recovery.md references/acceptance-evidence.md references/execution-and-review.md SKILL.md docs/tasks/finalization-hygiene.md .pipeline/finalization-hygiene/** --forbidden docs/goal.md .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/finalization-report-reader/** .pipeline/security-scan-repair-20261001/** .pipeline/security-scan-repair-20261001-continuation-1/** .env credentials/**",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "git diff --check",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "grep -rn \"只动本任务证据目录\" references/ SKILL.md",
      "exit_code": 1,
      "expected_exit_code": 1,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "python /tmp/frr-review/hygiene_probe.py",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    },
    {
      "command": "python /tmp/frr-review/hygiene_behaviour.py",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-hygiene",
      "evidence_ref": ".pipeline/finalization-hygiene/review-report.md"
    }
  ],
  "assertions": [
    "environment: toplevel/branch/HEAD/ancestor/task validate all pass",
    "the two edited paragraphs match evidence_only_paths and head_advanced_by_evidence_only sentence by sentence",
    "any .pipeline/** path (other tasks, metrics, planning) counts as evidence; anything outside .pipeline does not",
    "mixed evidence+product commits and unresolvable paths stay fail-closed; a non-ancestor head is still rejected",
    "the four old scope phrasings no longer appear in references/ or SKILL.md",
    "commit 21e8168 replaces one paragraph in each of two files only; no code, no other document, no version number changed",
    "finalization spares goal.json and amendments.json, prunes unrelated process files, and keeps the seven retained files",
    "another task's evidence commit keeps a finalized task PASS while product and mixed commits still fail with finalization head is stale",
    "the tests diff since e75c787 is purely additive (152 insertions, 0 deletions)",
    "all changed paths are inside revision 2 allowed_paths; forbidden paths untouched; scope check passes",
    "the full suite reports 401 passed, 28 subtests passed"
  ],
  "evidence_refs": [
    ".pipeline/finalization-hygiene/review-report.md",
    ".pipeline/finalization-hygiene/reviewer-result.json"
  ],
  "unverified": [
    "whether to sync references/acceptance-evidence.md line 66 and references/compat-and-migration.md line 13 is out of this round's scope; both are reported as findings and left untouched"
  ],
  "blockers": [],
  "recommendation": "ready_for_finalization"
}
```
