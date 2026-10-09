# executor-report：finalization-report-reader

## 任务身份

- task-id：`finalization-report-reader`
- task-type：`repair`
- worktree：`D:\Projects\Skills\pipeline\.worktrees\finalization-report-reader`
- branch：`finalization-report-reader`
- baseline HEAD：`238f36773941e4200f0c782d8ba28ca2431251ca`
- 实现提交：`f138659f61e7d5e47e84138b3ee4d69b064d9a87`
- role：executor，round 1
- sheet_revision：1

## 缺陷与修复

`pipeline_tools/planning.py` 的 `_read_evidence_block` 原本收集起始围栏之后的**全部** ```` ``` ```` 行并要求其数量恰好为 1；当报告正文在机器块之后还有别的 fenced 代码块时，收尾围栏计数大于 1，读取器返回 `None`，最终化报 `invalid <report>`。闸门侧读取器（`pipeline_tools/core.py` 的 `_read_machine_evidence`）取的是**其后第一条**围栏，所以同一份报告出现两个相反结论。

修复（`pipeline_tools/planning.py:2395-2413` 的 `_read_evidence_block`）：不再枚举全部收尾围栏，改为

- 定位**唯一**一条起始围栏行（缺失或出现多次 → 不可读）；
- 取起始围栏之后**第一条**围栏行作为块边界（找不到 → 不可读）；
- 块内容为起始围栏与收尾围栏之间的全部行，正文中更靠后的围栏与本块无关；
- 块内容按 JSON 解析，非法或不是对象 → 不可读。

fail-closed 语义不变：没有起始围栏、起始围栏重复、缺少收尾围栏、JSON 非法/非对象，四种情形一律返回 `None`，最终化 blocked。修复只改读取边界，不改写任何报告字节。

两个读取器保留各自实现（`core.py` 用 `errors="replace"` 的宽容解码、`planning.py` 保留 `UnicodeError` 处理），一致性由新增测试 `PlanningTests.test_finalization_and_gate_readers_agree_on_the_same_report` 钉住；未改动 `core.py` 的读取行为。

## 改动文件

- `pipeline_tools/planning.py`：`_read_evidence_block` 取首个收尾围栏（约 2395–2413 行）。
- `tests/test_planning.py`：新增 `PlanningTests` 下三条验收用例；`_write_schema_two_evidence` 与 `_merged_finalization_repo` 增加默认 `trailing_prose=False` 参数（默认值保持既有调用行为不变），新增 `TRAILING_FENCED_PROSE` 常量。
- `references/merge-and-recovery.md`：在“合并后”新增一段记录机器块边界判据与 fail-closed 集合。

未改动：`docs/goal.md`、任何历史任务单与历史证据、四个已完成任务的证据目录（`task-sheet-revision-and-evidence-binding`、`post-merge-evidence-identity`、`finalization-and-reconcile-phase`、`finalization-marker-head-tolerance`），未改写任何报告文件。

## 验收测试

| ID | 测试 | 命令 | 退出码 |
|---|---|---|---|
| acceptance-test-1 | `test_evidence_block_reader_accepts_fences_after_the_machine_block` | `python -m pytest -q tests/test_planning.py -k evidence_block_reader_accepts_fences_after_the_machine_block` | 0 |
| acceptance-test-2 | `test_evidence_block_reader_still_rejects_malformed_blocks` | `python -m pytest -q tests/test_planning.py -k evidence_block_reader_still_rejects_malformed_blocks` | 0 |
| acceptance-test-3 | `test_finalization_and_gate_readers_agree_on_the_same_report` | `python -m pytest -q tests/test_planning.py -k finalization_and_gate_readers_agree_on_the_same_report` | 0 |

- 验收测试1：临时仓库构造三份报告（机器块之后各含 3 段 fenced 代码块）→ 任务分支提交 → `git merge --no-ff` → `gate post-merge` PASS → `evidence-finalize` 产出 `finalization.json`；并断言三份报告字节在最终化前后逐字节相等（`before[name] == (evidence/name).read_bytes()`）。
- 验收测试2：四种结构非法情形（缺起始围栏、起始围栏重复、缺收尾围栏、JSON 非法）逐一断言 `_read_evidence_block` 返回 `None`、`finalize_evidence` 为 `blocked` 且 `missing` 含 `invalid executor-report.md`、且未产出 `finalization.json`。
- 验收测试3：对同一份报告分别调用闸门读取器 `core._read_machine_evidence` 与最终化读取器 `planning._read_evidence_block`，断言错误列表为空、两者解析出的对象相等；再端到端断言闸门 PASS 时最终化成功且 `missing` 不含 `invalid executor-report.md` / `invalid review-report.md`。

全量测试：`python -m pytest -q` → 退出码 0，`398 passed, 28 subtests passed`（基线 395 passed，新增 3 条）。

## 真实仓库只读复验（基线 vs 修复后）

主工作树 `D:\Projects\Skills\pipeline` 只读，未修改其中任何文件，未运行会删除其证据文件的写命令。基线复现（读取主工作树里仍为旧代码的 `pipeline_tools`）：

- `python -m pipeline_tools planning evidence-finalize .pipeline/task-sheet-revision-and-evidence-binding --task-id task-sheet-revision-and-evidence-binding --success` → 退出码 3，`{"status":"blocked","missing":["invalid executor-report.md","invalid review-report.md"],"finalization":null}`
- `python -m pipeline_tools gate post-merge .pipeline/task-sheet-revision-and-evidence-binding --task-id task-sheet-revision-and-evidence-binding --branch main` → 退出码 0，`PASS`
- `post-merge-evidence-identity` 的 `evidence-finalize` 同样返回 `blocked`、`missing` 含两条 `invalid ...`。

修复后，用 worktree 里的读取器对**同一批真实文件字节**做只读比较（不写主工作树）：

| 真实报告 | 旧读取器（本任务基线逻辑） | 新读取器 | 闸门读取器 | 新读取器与闸门一致 |
|---|---|---|---|---|
| task-sheet-revision-and-evidence-binding/executor-report.md | None | dict | dict | 是 |
| task-sheet-revision-and-evidence-binding/review-report.md | None | dict | dict | 是 |
| task-sheet-revision-and-evidence-binding/final-check.md | dict | dict | dict | 是 |
| post-merge-evidence-identity/executor-report.md | None | dict | dict | 是 |
| post-merge-evidence-identity/review-report.md | None | dict | dict | 是 |
| post-merge-evidence-identity/final-check.md | dict | dict | dict | 是 |

对应围栏行号实测：`task-sheet-revision-and-evidence-binding/executor-report.md` 起始围栏在第 2 行、围栏行共 5 条（第 4/23/34/46/52 行）→ 旧读取器计数 5 → `None`；`review-report.md` 起始围栏在第 2 行、围栏行共 9 条 → `None`。

把这两个证据目录**复制**到临时仓库（`<tmp>/.pipeline/<task-id>/`）后用新读取器跑完整最终化（`require_canonical=False`，不复现 post-merge 身份判据，只验证读取路径）：

- `task-sheet-revision-and-evidence-binding` → `{"status":"finalized","missing":[],...}`，`finalization.json` 已产出；
- `post-merge-evidence-identity` → `{"status":"finalized","missing":[],...}`，`finalization.json` 已产出。

即修复后读取器不再对这些真实报告报 `invalid`；四个证据目录本身未被改动。

## 未运行 / 未验证

- 未在主工作树**就地**运行写型的 `planning evidence-finalize`：该命令会删除证据目录里的非保留文件（实测复制目录上删除了 `goal.json`、`amendments.json`）并写出 `finalization.json`，且这两个文件在主工作树里是未跟踪文件，删除不可恢复。硬性约束禁止修改主工作树证据目录，因此改用“真实文件只读读取比较 + 目录副本完整最终化”的等价复验。主工作树最终的证据最终化由主代理负责。
- 主工作树的 post-merge 全链路最终化（gate → finalize → finalized verify）未在主工作树执行，只验证到读取器与其结论一致为止。

```pipeline-evidence
{"schema": 2, "task_id": "finalization-report-reader", "worktree": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "branch": "finalization-report-reader", "role": "executor", "round": 1, "status": "PASS", "head": "f138659f61e7d5e47e84138b3ee4d69b064d9a87", "sheet_revision": 1, "sheet_sha256": "7e8c6a5fb3ce0add707100e484c9dc6b022c58c50dc7a67852a5f41bdeceb4f1", "observed_at_commit": "f138659f61e7d5e47e84138b3ee4d69b064d9a87", "generated_at": "2026-10-09T01:56:03+00:00", "commands": [{"command": "python -m pipeline_tools task validate docs/tasks/finalization-report-reader.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_accepts_fences_after_the_machine_block", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_still_rejects_malformed_blocks", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k finalization_and_gate_readers_agree_on_the_same_report", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools scope check . --task-id finalization-report-reader --allowed pipeline_tools/planning.py pipeline_tools/core.py tests/test_planning.py tests/test_evidence.py references/merge-and-recovery.md docs/tasks/finalization-report-reader.md .pipeline/finalization-report-reader/** --forbidden docs/goal.md .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/security-scan-repair-20261001/** .pipeline/security-scan-repair-20261001-continuation-1/**", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline/.worktrees/finalization-report-reader", "exit_code": 0, "evidence_ref": "executor-report.md"}], "assertions": ["the reader takes the first closing fence after the opening fence, so a report whose prose carries further fenced blocks is read", "malformed blocks (no opening fence, duplicate opening fence, no closing fence, invalid JSON) all return unreadable and finalization stays blocked", "the finalization reader and the gate reader parse the same report bytes into equal objects", "no report file was rewritten: the acceptance test asserts byte equality before and after finalization", "the real reports under .pipeline/task-sheet-revision-and-evidence-binding and .pipeline/post-merge-evidence-identity are no longer read as invalid, verified read-only on their real bytes"], "evidence_refs": ["executor-report.md", "executor-result.json"], "unverified": ["the in-place post-merge finalization of the two blocked evidence directories in the main worktree, which was deliberately not run because that command deletes unrecoverable untracked files (goal.json, amendments.json) from those directories; the equivalent read-only reader comparison plus a full finalization on copies was run instead"]}
```
