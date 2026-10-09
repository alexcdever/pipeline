# 独立审查报告（round 1）：task-sheet-archival

- 任务单：`docs/tasks/task-sheet-archival.md`，revision **2**
- worktree：`D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival`
- branch：`task-sheet-archival`
- 待审实现提交：`1f9e4d8e56a53624aeb721608e68c022237c4fdd`
- 分支尖端（产生本证据时）：`929ba6e64d212b2f4bd043b28262fd4a249febc8`
- 契约基线：`124cef5e8b29fb02a099a28b7a8448747f781063`
- 全部复验亲自执行；主工作树只读（仅 `git` 只读命令与读文件），未新建 worktree，未写任何产品/测试/文档文件，未动其它任务证据目录。

## 1. 环境检查（逐项）

| # | 检查 | 结果 |
|---|------|------|
| 1 | `git rev-parse --show-toplevel` | PASS → `D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival` |
| 2 | `git branch --show-current` | PASS → `task-sheet-archival` |
| 3 | `git rev-parse HEAD` | PASS → `929ba6e64d212b2f4bd043b28262fd4a249febc8` |
| 4 | `git merge-base --is-ancestor 1f9e4d8 HEAD` | PASS → 退出码 0 |
| 5 | `python -m pipeline_tools task validate docs/tasks/task-sheet-archival.md` | PASS → 退出码 0（PASS） |
| 6 | 只读 / 不动主工作树 / 不新建 worktree / 不改其它证据目录 | PASS → 主工作树仅被执行只读 `git ls-files`/`cat-file`/`status`；本次审查只新增本目录两份报告 |

## 2. 第 4 节各点独立观察

### 点 1 — 三位置解析（自建夹具，四个方向）

自建临时目录（未复用实现测试），`task_sheet_resolution` 逐方向观测：

| 情形 | 结果 |
|------|------|
| 仅 `docs/tasks/x-task.md` | 解析成功，`errors=[]`，返回 active 路径 |
| 仅 `.pipeline/x-task/x-task.md` | 解析成功，返回证据目录路径 |
| 仅 `.pipeline/archive/x-task.md` | 解析成功，返回 archive 路径 |
| active + archive 同时存在 | `resolved=None`，`errors=['task sheet appears in multiple locations for x-task: .pipeline/archive/x-task.md, docs/tasks/x-task.md']` |
| active + 证据目录同时存在 | `resolved=None`，报多处（`ignore` 不生效） |
| 三处皆无 | `resolved=None`，`errors=['task sheet not found for x-task']` |

多处或皆无一律报错、不取第一个候选 → 与契约一致。

### 点 2 — 场景判定两方向（自建 git 夹具）

- 终态单在**证据目录内、无 worktree**：`sheets_without_worktree=[]`、`leftover_evidence=[]`。✓
- 终态单在 **archive、无 worktree**：`sheets_without_worktree=[]`。✓
- `docs/tasks/pending.md` **无 worktree**：`sheets_without_worktree=['pending']`，警告文本含 `pending`。✓

两方向均观测到。

### 点 3 — archive 隔离（自建夹具）

`.pipeline/archive/`（含 `closed.md` 与一个非单子 `notes.md`）下：`archive` 不出现在四类 scene 桶任一；`leftover_evidence=[]`；`warnings+errors` 拼接中无 `archive` 字样。✓

### 点 4 — 归档单满足「worktree 必须有单」

- worktree `closed` + 单在 `.pipeline/archive/closed.md`：`worktrees_without_sheet=[]`，无 `task worktree has no committed task sheet` 错误。✓
- worktree + 单在其证据目录：同样通过。✓
- 反向：worktree `orphan` 而三处皆无单：`worktrees_without_sheet=['orphan']` 且报错。✓

### 点 5 — 归档步骤两方向（自建夹具，直接调用 `archive_task_sheet`）

- `.worktrees/demo` 仍存在：`status='blocked'`，`errors=['task worktree still exists: .worktrees/demo']`，`docs/tasks/demo.md` 仍在、`.pipeline/demo/demo.md` 未生成（**未移动**）。✓
- worktree 已删：`status='archived'`，`from='docs/tasks/demo.md'`、`to='.pipeline/demo/demo.md'`、`tracked=True`；`git ls-files --error-unmatch .pipeline/demo/demo.md` 退出码 0（**仍被跟踪**）；再调用一次仍 `archived`、文件位置不变（**幂等**）；`task_sheet_resolution` 现从其终态位置解析成功。✓
- 无证据目录的任务：移到 `.pipeline/archive/lone.md`。✓

### 点 6 — 保留集与闸门豁免（含反向，自建夹具）

- `is_retained_evidence_path('.pipeline/demo/demo.md')=True`（自有单子）、`('.pipeline/demo/finalization.json')=True`（原保留集）、`('.pipeline/demo/notes.md')=False`（别的非保留名）。✓
- `is_archived_sheet_path('.pipeline/archive/closed.md')=True`。✓
- 自建 git 仓库提交「自有单子 + archive 单子」：`commit_history_check(root,'.pipeline/demo')` 返回 `[]`（不判违规）。✓
- **反向**：同目录下新增 `notes.md` 提交后返回恰好 1 条违规，含 `notes.md`。✓
- 追加反向：删除 archive 下已提交单子不判违规（豁免对删除同样成立）。✓

### 点 7 — 字节稳定（用哈希证明）

**(a) 新检出字节一致**（自建临时仓库，CRLF 写入 `.pipeline` 下文件并提交）：加属性后新写入的 `.pipeline/demo/review-report.md` 以 CRLF 原样入库，`git clone` 后该文件字节 `b'alpha\r\nbeta\r\n'` 与提交一致；对照 `src/control2.txt` 在 `* text=auto eol=lf` 下被规范化为 LF（证明该属性确实在起作用）。✓

**(b) 新增属性未改写既有已提交字节**：自建仓库先以 `* text=auto eol=lf` 提交 CRLF 工作区文件，记录 blob 哈希；随后**只** `git add .gitattributes` 提交新属性，blob 哈希 `fbbee861…` 前后完全相同。✓ 这与实现测试 `test_pipeline_evidence_bytes_survive_a_checkout` 的方法一致。

**(c) 执行者「266 个文件全部一致」的独立复算**：
- 实现 worktree（HEAD `929ba6e`，属性已生效）：`git ls-files .pipeline` = **266** 个已跟踪文件，工作区字节 vs `HEAD` blob 字节**全量 0 处不一致**。→ 执行者的 266/0 与本 worktree 吻合。
- **主工作树**（HEAD `1bd5522`，属性尚未合入）：已跟踪 **264** 个文件，其中 **7 个**工作区字节 ≠ `HEAD` blob 字节，全部是已关闭任务的 `finalization.json`（blob 为 LF、工作区为 CRLF）：
  `.pipeline/derived-creation-removal/`、`.pipeline/finalization-and-reconcile-phase/`、`.pipeline/finalization-hygiene/`、`.pipeline/finalization-marker-head-tolerance/`、`.pipeline/finalization-report-reader/`、`.pipeline/post-merge-evidence-identity/`、`.pipeline/task-sheet-revision-and-evidence-binding/` 各自的 `finalization.json`。
- 因此「266 个文件一致」的结论**只对实现 worktree 成立**，对主工作树不成立（数量也不是 266 而是 264）。见 findings 1。

**(d) 与上述 7 个文件的交互（用真实字节复现）**：把主工作树 `finalization-hygiene/finalization.json` 的真实工作区字节（CRLF）与真实 blob 字节（LF）搬进临时仓库，在 `* text=auto eol=lf` 下 `git status` 为空；提交 `.pipeline/** -text` 后 `git status --porcelain` 变为 ` M .pipeline/finalization-hygiene/finalization.json`。即：属性合入后，这 7 个已提交的最终化标记会显示为已修改；若随后执行 `git add`，其 blob 会被由 LF 改写为 CRLF（自建仓库实测 `add -A` 令该 blob 哈希由 `fbbee861…` 变为 `17f2fc0a…`）。缓解：合入后在主工作树 `git checkout -- .pipeline` 即可令工作区回到 LF（=blob），状态转干净、字节不变。

### 点 8 — 未执行历史迁移

`git diff --name-only 124cef5..HEAD -- docs/tasks/ .pipeline/` 去掉本任务自己的证据目录后，只剩 `docs/tasks/task-sheet-archival.md`（本任务单自身的 revision 2 修订）。既有任务单、既有证据目录、既有最终化标记在区间内**零改动**；实现提交 `1f9e4d8` 范围内 `docs/tasks/` 与 `.pipeline/` 除本任务证据外无任何改动。✓

### 点 9 — 文档

- `references/acceptance-evidence.md:66`：旧措辞「全部落在证据目录内」已消失（grep 退出码 1），改为「全部落在 `.pipeline/**` 子树内（判据是路径前缀 `.pipeline`…）」。✓
- `references/merge-and-recovery.md:61`：新增「报告的 `head` 记录"产生证据时的分支尖端"」段落。✓
- `references/compat-and-migration.md:13`：新增 `v0.17.0 → v0.18.0` 条目；该文件在 `124cef5..1f9e4d8` 为 **1 insertion, 0 deletions**，历史条目未被改写。✓
- `SKILL.md` 版本由 `0.17.0` 递进到 `0.18.0`。✓
- `README.md`、`references/task-design.md` 同步三位置规则、工作清单语义、归档步骤与字节稳定口径。✓

### 点 10 — 既有断言完整性

`git diff --numstat 124cef5 1f9e4d8 -- tests/` = `tests/test_evidence.py` **107 +0 −0**、`tests/test_planning.py` **212 +0 −0**；整个 `124cef5..1f9e4d8` diff 中 `tests/` 无任何以 `-` 开头的行。既有断言零删除、零修改。✓

### 点 11 — 无越界

`git diff --name-only 124cef5 1f9e4d8` = `.gitattributes`、`README.md`、`SKILL.md`、`pipeline_tools/core.py`、`pipeline_tools/layout.py`、`pipeline_tools/planning.py`、`references/{acceptance-evidence,compat-and-migration,merge-and-recovery,task-design}.md`、`tests/{test_evidence,test_planning}.py`，全部落在 revision 2 的 `allowed_paths` 内。对 `docs/goal.md`、`pipeline_tools/contract.py`、`docs/tasks/*.md`（实现提交范围内）与七个已完成任务证据目录的改动 grep 计数为 0。`scope check` 退出码 0。见 findings 2（本任务单自身在修订提交中被改，属 allowed 的 `docs/tasks/task-sheet-archival.md`）。

## 3. 亲自运行的命令

| # | 命令 | cwd | 退出码 |
|---|------|-----|--------|
| 1 | `python -m pytest -q tests/test_planning.py -k sheet_resolver_finds_all_three_locations` | worktree | 0（1 passed, 58 deselected） |
| 2 | `python -m pytest -q tests/test_planning.py -k worklist_checks_ignore_terminal_sheets` | worktree | 0（1 passed） |
| 3 | `python -m pytest -q tests/test_planning.py -k archive_directory_is_not_treated_as_task_evidence` | worktree | 0（1 passed） |
| 4 | `python -m pytest -q tests/test_planning.py -k archived_sheet_still_answers_worktree_without_sheet` | worktree | 0（1 passed） |
| 5 | `python -m pytest -q tests/test_planning.py -k finalization_moves_the_sheet_and_refuses_while_the_worktree_lives` | worktree | 0（1 passed） |
| 6 | `python -m pytest -q tests/test_evidence.py -k task_sheet_and_archive_are_exempt_from_the_retained_name_rule` | worktree | 0（1 passed） |
| 7 | `python -m pytest -q tests/test_evidence.py -k pipeline_evidence_bytes_survive_a_checkout` | worktree | 0（1 passed） |
| 8 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | worktree | 0（1 passed） |
| 9 | `python -m pytest -q` | worktree | 0（**395 passed, 30 subtests passed**，与执行者声明一致） |
| 10 | `python -m pipeline_tools task validate docs/tasks/task-sheet-archival.md` | worktree | 0（PASS） |
| 11 | `python -m pipeline_tools result verify .pipeline/task-sheet-archival/executor-result.json --task-id task-sheet-archival --role executor` | worktree | 0（PASS） |
| 12 | `python -m pipeline_tools scope check . --allowed pipeline_tools/** tests/** .gitattributes SKILL.md README.md references/** docs/tasks/task-sheet-archival.md .pipeline/task-sheet-archival/** --forbidden docs/goal.md pipeline_tools/contract.py docs/tasks/*.md` | worktree | 0（PASS） |
| 13 | `git diff --check` | worktree | 0 |
| 14 | `python /tmp/verify_review.py`（自建夹具 40 条断言） | worktree | 0（40/40 passed） |
| 15 | `python -c '... tracked .pipeline/** workspace vs HEAD blob ...'`（主工作树，只读） | worktree | 0（264 tracked / 7 mismatch） |
| 16 | `python -c '... tracked .pipeline/** workspace vs HEAD blob ...'`（实现 worktree） | worktree | 0（266 tracked / 0 mismatch） |
| 17 | `grep -n "落在证据目录内" references/acceptance-evidence.md` | worktree | 1（刻意非零：旧措辞已消失） |

## 4. 结论

**PASS**

- 六项机制（三位置解析、按状态场景判定、archive 隔离、保留集与闸门豁免、显式归档步骤、字节稳定）在自建夹具下逐条观测通过；两个方向（含反向）均成立，fail-closed 未放宽。
- 八条契约验收命令全部退出码 0；全量 `python -m pytest -q` 为 **395 passed, 30 subtests passed**，与执行者声明完全一致。
- `task validate`、`scope check`、`result verify`（executor）、`git diff --check` 全部退出码 0。
- 无越界；`tests/` 既有断言零删除；`docs/tasks/*.md`、既有证据目录与最终化标记在实现与合并范围内零改动。
- 唯一实质发现（findings 1）是关于**主工作树**既有 7 个 `finalization.json`（CRLF 工作区 / LF blob）与新属性的交互，属契约决策点 1 的边界情形，需主代理裁决；不影响本 worktree 的实现正确性与验收结论，故不改变 PASS。

## 5. findings

1. **（需主代理裁决，合入前处理）** 执行者「已跟踪 `.pipeline/**` 工作区字节 vs blob 字节全部一致」的结论**只对实现 worktree 成立（266/0）**；**主工作树**实为 264 个已跟踪文件、其中 7 个不一致（均为已关闭任务的 `finalization.json`：工作区 CRLF、blob LF）。用真实字节复现表明：`.pipeline/** -text` 合入主工作树后，这 7 个**已最终化标记**会转为 ` M `，若随后 `git add` 则其 blob 由 LF 改写为 CRLF——触及非目标「不改写任何现有任务的证据目录与已最终化标记」与决策点 1 的语义。属性提交本身（只 `git add .gitattributes`）经哈希证明**不**改写任何 blob，故不构成实现缺陷。**建议**：合入后在主工作树执行 `git checkout -- .pipeline`，使这 7 个文件回到 LF（=blob），状态转干净且字节不变；或由主代理裁定接受该 7 个标记的 blob 改写。
2. **（契约观察，非缺陷）** `docs/tasks/task-sheet-archival.md` 字面上匹配 `forbidden_paths` 的 `docs/tasks/*.md`，但它是本任务单自身、同时被 `allowed_paths` 显式列出，其内容变更来自主代理的 revision 2 修订提交 `1bd5522`（`task amend` 是受认可的机制）；**待审实现提交 `1f9e4d8` 自身未触及任何 forbidden 路径**。记录以免被误判为越界。
3. **（环境事实，与执行者 unverified 一致）** 修订链 `.pipeline/task-sheet-archival/amendments.json` 未纳入 Git、仅存在于主工作树，故本 worktree 内 `task_sheet_revision(root,'task-sheet-archival')` 解析为 `(1, None)`；本报告按任务要求标注 `sheet_revision=2`（与执行者声明及主工作树修订链一致）。
4. **（次要，实现细节）** `is_archived_sheet_path` 的豁免在 `commit_history_check` 中不随 `evidence_root` 收窄，即对任意扫描根都豁免 `.pipeline/archive/**`。当前无调用方会把 archive 当作其它证据根，无实际影响；仅作记录。

## 6. unverified

- 主工作树 7 个 `finalization.json` 的 CRLF 工作区状态**何时**形成（是否由历史上某次工具写入/检出造成）未追溯；这不影响本次判定（只与「属性合入后的交互」有关）。
- 属性合入主工作树后，主代理实际是否会执行 `git add`/`git checkout -- .pipeline`（即 7 个标记最终是否被改写）取决于后续合并流程，本审查无法观测。

```pipeline-evidence
{
  "schema": 2,
  "task_id": "task-sheet-archival",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival",
  "branch": "task-sheet-archival",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "head": "929ba6e64d212b2f4bd043b28262fd4a249febc8",
  "sheet_revision": 2,
  "sheet_sha256": "5f3c92d875e6b03d8fd6a4f314b5c3e6f2e5d7f80786493f15b52370a0040d54",
  "observed_at_commit": "929ba6e64d212b2f4bd043b28262fd4a249febc8",
  "generated_at": "2026-10-09T06:00:00Z",
  "commands": [
    {"command": "python -m pytest -q tests/test_planning.py -k sheet_resolver_finds_all_three_locations", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pytest -q tests/test_planning.py -k worklist_checks_ignore_terminal_sheets", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pytest -q tests/test_planning.py -k archive_directory_is_not_treated_as_task_evidence", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pytest -q tests/test_planning.py -k archived_sheet_still_answers_worktree_without_sheet", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pytest -q tests/test_planning.py -k finalization_moves_the_sheet_and_refuses_while_the_worktree_lives", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pytest -q tests/test_evidence.py -k task_sheet_and_archive_are_exempt_from_the_retained_name_rule", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pytest -q tests/test_evidence.py -k pipeline_evidence_bytes_survive_a_checkout", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pytest -q", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pipeline_tools task validate docs/tasks/task-sheet-archival.md", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pipeline_tools result verify .pipeline/task-sheet-archival/executor-result.json --task-id task-sheet-archival --role executor", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -m pipeline_tools scope check . --allowed pipeline_tools/** tests/** .gitattributes SKILL.md README.md references/** docs/tasks/task-sheet-archival.md .pipeline/task-sheet-archival/** --forbidden docs/goal.md pipeline_tools/contract.py docs/tasks/*.md", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "git diff --check", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python /tmp/verify_review.py", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -c 'git ls-files .pipeline + workspace vs HEAD blob (main worktree, read-only)'", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "python -c 'git ls-files .pipeline + workspace vs HEAD blob (implementation worktree)'", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"},
    {"command": "grep -n \"落在证据目录内\" references/acceptance-evidence.md", "exit_code": 1, "expected_exit_code": 1, "cwd": "D:/Projects/Skills/pipeline/.worktrees/task-sheet-archival", "evidence_ref": ".pipeline/task-sheet-archival/review-report.md"}
  ],
  "assertions": [
    "environment: toplevel/branch/HEAD/ancestor/task validate all pass (exit 0)",
    "the resolver finds each of the three locations alone and returns None with an error for a sheet in multiple locations or in none",
    "scene facts judge by state: terminal sheets (evidence dir or archive) do not raise sheets_without_worktree, while an active docs/tasks sheet without a worktree still does",
    ".pipeline/archive is excluded from the evidence scan: it is never a task named archive and never raises leftover_evidence",
    "an archived or evidence-dir sheet answers worktrees_without_sheet, while a worktree with no sheet in any location still errors",
    "archive_task_sheet is blocked with the sheet unmoved while .worktrees/<id> exists, and moves the sheet with git mv (still tracked, idempotent) once it is gone",
    "a task's own sheet is retained and .pipeline/archive/** is exempt from the retained-name rule, while another non-retained file in the same evidence dir is still a violation",
    "adding .pipeline/** -text does not rewrite an already committed blob, and a fresh .pipeline file survives a clone byte for byte while ordinary text is normalized",
    "the implementation worktree has 266 tracked .pipeline files with 0 workspace-vs-blob mismatches; the main worktree has 264 with 7 mismatches (all closed-task finalization.json)",
    "no historical migration: docs/tasks/*.md, existing evidence directories and finalization markers are unchanged apart from this task's own revision-2 sheet",
    "documentation records the three locations, the state-based worklist, the archival move and the byte-stability rule; acceptance-evidence.md no longer says 'falls inside the evidence directory'",
    "tests diff since 124cef5 is purely additive in tests/ (0 deletions); all changed paths are inside revision 2 allowed_paths; forbidden paths untouched",
    "the full suite reports 395 passed, 30 subtests passed"
  ],
  "evidence_refs": [
    ".pipeline/task-sheet-archival/review-report.md",
    ".pipeline/task-sheet-archival/reviewer-result.json"
  ],
  "unverified": [
    "when the CRLF working-tree state of the main worktree's 7 finalization.json files was created is not traced; it matters only for the attribute interaction, not for this verdict",
    "whether the main agent will rewrite those 7 finalization markers (via git add) or normalize them via git checkout after merging is decided by the later merge sequence and cannot be observed here"
  ],
  "blockers": [],
  "recommendation": "ready_for_finalization"
}
```
