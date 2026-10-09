# 独立审查报告：finalization-report-reader

- 任务单：`docs/tasks/finalization-report-reader.md`，revision 1
- worktree：`D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader`
- branch：`finalization-report-reader`
- 待审实现提交：`f138659f61e7d5e47e84138b3ee4d69b064d9a87`
- 审查运行时分支尖端：`a8f963f5e4210db9e98cf837d22cf7a756676359`（相对 f138659 仅新增本任务证据文件）
- 契约基线：`238f36773941e4200f0c782d8ba28ca2431251ca`
- 全部复验均在实现 worktree 内亲自执行；主工作树只读访问，未做任何写操作。

## 1. 环境检查（逐项）

| # | 检查 | 命令 | 结果 |
|---|------|------|------|
| 1 | toplevel == worktree | `git rev-parse --show-toplevel` | PASS → `D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader` |
| 2 | branch | `git branch --show-current` | PASS → `finalization-report-reader` |
| 3 | HEAD | `git rev-parse HEAD` | PASS → `a8f963f5e4210db9e98cf837d22cf7a756676359` |
| 4 | 实现提交为祖先 | `git merge-base --is-ancestor f138659 HEAD` | PASS → 退出码 0 |
| 5 | 任务单校验 | `python -m pipeline_tools task validate docs/tasks/finalization-report-reader.md` | PASS → 退出码 0，输出 `PASS` |
| 6 | 只读产品代码 / 不动主工作树 | 见第 5 节 | PASS → 主工作树 `git status` 无因本次审查产生的改动 |

`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` 已导出。

## 2. 修复内容复核（读代码）

`pipeline_tools/planning.py:2395` 的 `_read_evidence_block` 现在：

1. 起始围栏（```` ```pipeline-evidence ````）必须恰好一行，否则 `None`；
2. 块边界为起始围栏之后**第一条** ```` ``` ```` 行（`next(...)`，找不到则 `None`）；
3. 块内 JSON 解析失败或非对象 → `None`。

闸门侧 `pipeline_tools/core.py:468` 的 `_read_machine_evidence` 本来就用 `next(...)` 取第一条收尾围栏。两处实现现在在围栏选取与 JSON 判据上语义一致，且各自保留实现（符合契约 unknown-2 的约束）。

diff（`238f367..f138659`）只触及三个文件：`pipeline_tools/planning.py`、`references/merge-and-recovery.md`、`tests/test_planning.py`；`core.py` 与 `tests/test_evidence.py` 未改动（允许但不是必需）。

## 3. 高风险点独立复验（自建夹具）

复验脚本 `/tmp/frr-review/independent_check.py`（临时目录，非仓库文件）自建报告与临时 git 仓库，共 37 条断言，全部通过，退出码 0。

### 点 1 — 正文含后续代码块的报告可解析 + 端到端最终化

- 自建三分报告：机器块在文件前部，之后是普通正文 + `bash` 代码块 + 第二个 `json` 代码块（每份报告共 3 个收尾围栏）。
- 读取器返回 dict；并在临时 git 仓库里「建任务分支写证据 → 提交 → 产品改动提交 → `git merge --no-ff` → `gate post-merge --task-id demo --branch main`（退出码 0）→ `planning evidence-finalize --task-id demo --success`」。
- 观察：`gate post-merge` rc=0，`evidence-finalize` rc=0，输出 `{"status": "finalized", "missing": []}`，`finalization.json` 已生成。
- 报告字节：最终化前后 `executor-report.md` / `review-report.md` / `final-check.md` 三份字节完全相同。

### 点 2 — fail-closed 未放宽（四种情形全部观测到）

| 情形 | `_read_evidence_block` | 闸门读取器 | `finalize_evidence` |
|------|------------------------|-----------|---------------------|
| 缺起始围栏 | `None` | 拒绝（missing or duplicate block） | `blocked`，含 `invalid executor-report.md` |
| 起始围栏重复 | `None` | 拒绝 | `blocked` |
| 缺收尾围栏 | `None` | 拒绝（JSON invalid） | `blocked` |
| 机器块 JSON 非法 | `None` | 拒绝（JSON invalid） | `blocked` |

四种情形均未生成 `finalization.json`。

### 点 3 — 块边界正确

自建报告：机器块之后**紧接**一行普通正文，再紧跟一个 fenced 代码块。读出的 JSON 键集合与机器块完全一致（无正文混入）。

### 点 4 — 两个读取器一致

对自建的三份"机器块之后还有代码块"的报告，`planning._read_evidence_block` 与 `core._read_machine_evidence` 返回值逐字段相等；闸门 rc=0 时最终化输出 `finalized` 且 `missing` 不含 `invalid <report>`。

### 点 5 — 真实文件只读复验（主工作树，未写入）

用 `git archive 238f367 pipeline_tools` 抽出基线读取器到临时目录，在同一进程外分别加载基线/新代码，只读比较主工作树下四份真实报告：

| 报告 | 收尾围栏数 | 旧读取器 | 新读取器 | 闸门读取器 | 结论 |
|------|-----------|---------|---------|-----------|------|
| `task-sheet-revision-and-evidence-binding/executor-report.md` | 5 | `None` | dict(role=executor) | dict，无错误 | 旧不可读→新可读，与闸门一致 |
| `task-sheet-revision-and-evidence-binding/review-report.md` | 9 | `None` | dict(role=reviewer) | dict，无错误 | 同上 |
| `post-merge-evidence-identity/executor-report.md` | 7 | `None` | dict(role=executor) | dict，无错误 | 同上 |
| `post-merge-evidence-identity/review-report.md` | 11 | `None` | dict(role=reviewer) | dict，无错误 | 同上 |

四份文件字节在读取前后均未变化；主工作树未执行任何写型命令（未运行 `evidence-finalize`）。

### 点 6 — 未改写任何既有报告

`git diff --name-only 238f367 f138659` 输出为 `pipeline_tools/planning.py`、`references/merge-and-recovery.md`、`tests/test_planning.py`，无任何 `.pipeline/**` 既有报告被改写（本任务证据目录出现在 `a8f963f`，属本任务自身）。

### 点 7 — 既有断言完整性

`git diff 238f367 f138659 -- tests/` 的删除行逐行核对：全部是 `_write_schema_two_evidence` 内部构造逻辑重构与 `_merged_finalization_repo` 签名加默认参数，**无任何 `assert`/`assertEqual` 等断言被删除或放宽**。

### 点 8 — 无越界

改动路径全部落在 revision 1 的 `allowed_paths` 内；`forbidden_paths`（四个已完成任务证据目录、`docs/goal.md`、`.env`、`credentials/**`）零改动。`scope check`（含全部 allowed/forbidden 模式）退出码 0。

## 4. 亲自运行的命令

| 命令 | cwd | 退出码 |
|------|-----|--------|
| `python -m pytest -q tests/test_planning.py -k evidence_block_reader_accepts_fences_after_the_machine_block` | worktree | 0（1 passed, 53 deselected） |
| `python -m pytest -q tests/test_planning.py -k evidence_block_reader_still_rejects_malformed_blocks` | worktree | 0（1 passed） |
| `python -m pytest -q tests/test_planning.py -k finalization_and_gate_readers_agree_on_the_same_report` | worktree | 0（1 passed） |
| `python -m pytest -q` | worktree | 0（**398 passed, 28 subtests passed**） |
| `python -m pipeline_tools task validate docs/tasks/finalization-report-reader.md` | worktree | 0 |
| `python -m pipeline_tools result verify .pipeline/finalization-report-reader/executor-result.json --task-id finalization-report-reader --role executor` | worktree | 0（PASS） |
| `python -m pipeline_tools scope check . --task-id … --allowed … --forbidden …` | worktree | 0（PASS） |
| `git diff --check` | worktree | 0 |
| `python /tmp/frr-review/independent_check.py`（自建夹具） | worktree | 0（37/37 断言通过） |
| 旧/新读取器对四份真实报告的只读比较 | 临时目录 | 0 |

全量结果与执行者声明的 **398 passed, 28 subtests passed** 完全一致。

## 5. 结论

**PASS**

- 缺陷确实被修复：正文在机器块之后还有 fenced 代码块的历史报告现在可被最终化读取器读出，端到端最终化成功且报告字节不变。
- fail-closed 未被放宽：四种结构非法情形全部被拒绝并 blocked。
- 两个读取器对同一报告结论一致，且由 `tests/test_planning.py` 的一致性用例钉住。
- 无越界，无历史报告改写，无既有断言被削弱。

## 6. findings（契约层面，非缺陷）

- 契约 operation `reader-agreement` 把 `pipeline_tools/core.py`、`tests/test_evidence.py` 列为资源，但实际无需改动（一致性用例落在 `tests/test_planning.py`，即 acceptance-test-3 的 `test_ref`）。资源列表是允许集合的超集，不构成违规；无需改契约。
- `unknown-1`（有多少既有报告在机器块之后还有代码块）本任务未枚举，但已用四份真实报告抽样确证旧读取器不可读、新读取器可读。

## 7. 未验证项

- 未在真实合并流程中对 `task-sheet-revision-and-evidence-binding` / `post-merge-evidence-identity` 跑完整 `evidence-finalize`（主工作树只读，禁止写型命令）；仅以只读比较证明其报告现在可被两个读取器一致读出。

```pipeline-evidence
{
  "schema": 2,
  "task_id": "finalization-report-reader",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
  "branch": "finalization-report-reader",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "head": "f138659f61e7d5e47e84138b3ee4d69b064d9a87",
  "sheet_revision": 1,
  "sheet_sha256": "7e8c6a5fb3ce0add707100e484c9dc6b022c58c50dc7a67852a5f41bdeceb4f1",
  "observed_at_commit": "a8f963f5e4210db9e98cf837d22cf7a756676359",
  "generated_at": "2026-10-09T02:08:03+00:00",
  "commands": [
    {
      "command": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_accepts_fences_after_the_machine_block",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_still_rejects_malformed_blocks",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m pytest -q tests/test_planning.py -k finalization_and_gate_readers_agree_on_the_same_report",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m pytest -q",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m pipeline_tools task validate docs/tasks/finalization-report-reader.md",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m pipeline_tools result verify .pipeline/finalization-report-reader/executor-result.json --task-id finalization-report-reader --role executor",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m pipeline_tools scope check . --task-id finalization-report-reader --allowed pipeline_tools/planning.py pipeline_tools/core.py tests/test_planning.py tests/test_evidence.py references/merge-and-recovery.md docs/tasks/finalization-report-reader.md .pipeline/finalization-report-reader/** --forbidden docs/goal.md .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/security-scan-repair-20261001/** .pipeline/security-scan-repair-20261001-continuation-1/** .env credentials/**",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "git diff --check",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python /tmp/frr-review/independent_check.py",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python /tmp/frr-review/real_files_check.py /tmp/frr-review/baseline old",
      "exit_code": 0,
      "cwd": "/tmp/frr-review",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python /tmp/frr-review/real_files_check.py D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader new",
      "exit_code": 0,
      "cwd": "/tmp/frr-review",
      "evidence_ref": "review-report.md"
    }
  ],
  "assertions": [
    "environment: toplevel/branch/HEAD/ancestor/task validate all pass",
    "the fix reads the machine block up to its first closing fence (planned boundary) and later fenced prose is not part of the block",
    "a self-built report whose machine block is followed by two fenced code blocks is read as a dict and finalized end to end (gate post-merge rc=0, evidence-finalize status=finalized, finalization.json written)",
    "reports are byte-identical before and after finalization",
    "all four malformed shapes (missing opening fence, duplicate opening fence, missing closing fence, invalid JSON) are rejected by both readers and leave finalization blocked with no finalization.json",
    "the finalization reader and the gate reader return equal values for the same report; gate PASS never yields invalid <report>",
    "the four real reports in the main worktree are None under the baseline reader and dict under the fixed reader, matching the gate reader, with bytes unchanged",
    "no existing report file under .pipeline/** was rewritten and no existing test assertion was deleted or weakened",
    "the full suite reports 398 passed, 28 subtests passed"
  ],
  "evidence_refs": [
    "review-report.md",
    "reviewer-result.json"
  ],
  "unverified": [
    "no full evidence-finalize was run for task-sheet-revision-and-evidence-binding or post-merge-evidence-identity in the main worktree (write operations prohibited there); their acceptance is shown by read-only reader comparison only"
  ],
  "blockers": [],
  "recommendation": "ready_for_finalization"
}
```
