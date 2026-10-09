# 报告机器块读取器取首个收尾围栏

<!-- Task ID: finalization-report-reader -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "finalization-report-reader",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "pipeline_tools/planning.py",
    "pipeline_tools/core.py",
    "tests/test_planning.py",
    "tests/test_evidence.py",
    "references/merge-and-recovery.md",
    "docs/tasks/finalization-report-reader.md",
    ".pipeline/finalization-report-reader/**"
  ],
  "forbidden_paths": [
    "docs/goal.md",
    ".pipeline/task-sheet-revision-and-evidence-binding/**",
    ".pipeline/post-merge-evidence-identity/**",
    ".pipeline/finalization-and-reconcile-phase/**",
    ".pipeline/finalization-marker-head-tolerance/**",
    ".pipeline/security-scan-repair-20261001/**",
    ".pipeline/security-scan-repair-20261001-continuation-1/**",
    ".env",
    "credentials/**"
  ],
  "non_goals": [
    "不放宽结构校验：缺少起始围栏、重复起始围栏、未闭合、机器块 JSON 非法时仍必须拒绝",
    "不重写任何历史报告——由读取器适配既有形态，而不是改写历史证据",
    "不修改任何历史任务单或历史证据，也不修改四个依赖任务的证据目录",
    "不为让测试变绿而删除或放宽任何既有断言",
    "不实现任务单归档、历史迁移或 worktree 清理"
  ],
  "operations": [
    {
      "id": "single-fence-reader",
      "kind": "repair",
      "scope": "finalization report reader takes the first closing fence after the machine block opening",
      "resources": ["pipeline_tools/planning.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2"]
    },
    {
      "id": "reader-agreement",
      "kind": "validate",
      "scope": "the finalization reader and the gate reader agree on the same report",
      "resources": ["pipeline_tools/core.py", "tests/test_evidence.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-3"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: planning evidence-finalize CLI"],
    "interaction": ["pipeline_tools/planning.py: evidence block reader"],
    "application": ["pipeline_tools/planning.py: finalization report validation"],
    "domain": ["machine block extraction from a report whose prose contains further fenced blocks"],
    "persistence": [".pipeline/finalization-report-reader/ stage reports and machine results"],
    "readback": ["tests/test_planning.py"],
    "recovery": ["malformed blocks still return no block; no partial parse"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_evidence_block_reader_accepts_fences_after_the_machine_block",
      "command_ref": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_accepts_fences_after_the_machine_block"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_evidence_block_reader_still_rejects_malformed_blocks",
      "command_ref": "python -m pytest -q tests/test_planning.py -k evidence_block_reader_still_rejects_malformed_blocks"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_finalization_and_gate_readers_agree_on_the_same_report",
      "command_ref": "python -m pytest -q tests/test_planning.py -k finalization_and_gate_readers_agree_on_the_same_report"
    }
  ],
  "dependencies": ["finalization-marker-head-tolerance"],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "A report's machine block is delimited by its opening fence and the next fence line, so later fenced blocks in the prose are not part of it; requiring a single closing fence in the whole tail is a parser defect, not a contract rule."},
    {"id": "assumption-2", "statement": "The gate already reads such reports successfully, so the finalization reader must be brought into agreement with it rather than the other way round."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "How many existing reports carry a fenced block after their machine block has not been enumerated; the reader fix must accept them without rewriting them."},
    {"id": "unknown-2", "statement": "Whether the two readers can be reduced to a single shared implementation without disturbing gate behaviour is not known; if unification risks gate behaviour, keep two readers and pin their agreement with a test."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：最终化报告解析
- 任务类型：`repair`
- 用户结果或系统能力：正文在机器块之后还有其它 fenced 代码块的报告也能被最终化读取并通过校验；结构非法时仍然 fail-closed；最终化读取器与闸门读取器对同一份报告结论一致
- 执行 worktree 约定：`<仓库根目录>/.worktrees/finalization-report-reader`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/finalization-report-reader/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- 最终化链路已恢复（`finalization-and-reconcile-phase`）、标记 head 判据已可用（`finalization-marker-head-tolerance`），两者均已合并并最终化。
- 实测事实：两条已合并任务的 `evidence-finalize` 返回 `{"status":"blocked","missing":["invalid executor-report.md","invalid review-report.md"]}`，而同一条任务的 `gate post-merge` 返回 PASS。

### 允许修改

- `pipeline_tools/planning.py`：报告机器块读取
- `pipeline_tools/core.py`：仅在需要抽取共享实现或对齐闸门读取时
- `tests/test_planning.py`、`tests/test_evidence.py`：新增回归用例，保持既有断言
- `references/merge-and-recovery.md`：如需记录该解析规则
- 本任务单与 `.pipeline/finalization-report-reader/**`

### 明确不改

- `docs/goal.md`；任何历史任务单与历史证据；四个已完成任务的证据目录
- 既有报告文件本身——本任务修的是读取器，不是报告

### 非目标

- 不把解析放宽成"没有围栏也能读"。
- 不重写 `task-sheet-revision-and-evidence-binding` 与 `post-merge-evidence-identity` 的历史报告；它们会被本修复自然接纳。
- 不顺手实现归档、历史迁移或 worktree 清理。

## 事实、假设与待决

### 已确认事实

- `pipeline_tools/planning.py:2395-2407` 的 `_read_evidence_block` 收集起始围栏之后的**全部** ```` ``` ```` 行，并要求其数量恰好为 1；否则返回 `None`。
- 实测：某任务报告机器块位于第 2–4 行、正文另有 4 段代码块（第 23/34/46/52 行）→ 收尾围栏计数为 5 → 返回 `None` → 最终化报 `invalid executor-report.md`；另一任务报告机器块位于文件末尾（第 123–176 行）→ 计数为 1 → 解析成功。
- 闸门侧读取（`pipeline_tools/core.py` 中的机器块读取）对同一份报告判定成功，因此同一文件出现两个相反结论。
- 工作区字节为 LF，与换行符无关。

### 未验证事实

- 尚未枚举有多少既有报告在机器块之后还有 fenced 代码块。
- 尚未在实现 worktree 中运行任何新增测试。

### 禁止猜测

- 不得自行决定"是否把两个读取器合并为单一实现"——若合并可能改变闸门行为，保留两个读取器并用测试钉住一致性。
- 不得自行决定是否放宽其它结构校验（缺围栏、未闭合、JSON 非法）；这些必须保持拒绝。

## 设计与行为契约

[触发] 对一个报告正文在机器块之后还有其它 fenced 代码块的任务运行 `planning evidence-finalize`
→ [处理] 读取器定位机器块
→ [状态] 取起始围栏之后的**第一个**收尾围栏作为块边界
→ [可见结果] 机器块被正确读出并校验；结构非法的报告仍然被拒绝

- **块边界**：块内容为起始围栏行之后、**其后第一条** ```` ``` ```` 行之前的全部行。正文中更靠后的围栏与本块无关。
- **保持 fail-closed**：没有起始围栏、起始围栏出现多次、找不到收尾围栏、块内容 JSON 非法或非对象——一律视为不可读，最终化 blocked。
- **读取器一致**：同一份报告，闸门判定为通过时，最终化读取器不得判为不可读；两处若保留各自实现，必须有一致性测试钉住。
- 本修复不得改变任何报告文件的字节。

## 环境前置

1. `python` 与 `git` 可执行，仓库可读写。
2. 在实现 worktree 中运行聚焦与全量测试。

## 验收测试

### 验收测试1：机器块之后还有代码块也能被读出并最终化

- 触发：构造一份报告，机器块之后正文再含至少一个 fenced 代码块；在临时仓库中走完整链路（合并 → `gate post-merge` → `evidence-finalize`）。
- 断言：机器块被正确读出；最终化成功产出 `finalization.json`；报告文件字节未变。
- 测试：`tests/test_planning.py: PlanningTests.test_evidence_block_reader_accepts_fences_after_the_machine_block`
- 命令：`python -m pytest -q tests/test_planning.py -k evidence_block_reader_accepts_fences_after_the_machine_block`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；不得通过改写报告来达标。

### 验收测试2：结构非法的块仍被拒绝

- 触发：分别构造缺少起始围栏、起始围栏重复、缺少收尾围栏、机器块 JSON 非法的报告。
- 断言：读取器一律返回不可读，最终化 blocked。
- 测试：`tests/test_planning.py: PlanningTests.test_evidence_block_reader_still_rejects_malformed_blocks`
- 命令：`python -m pytest -q tests/test_planning.py -k evidence_block_reader_still_rejects_malformed_blocks`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；四种情形都必须被观测到。

### 验收测试3：两个读取器对同一报告一致

- 触发：对同一份"机器块之后还有代码块"的报告，分别跑闸门判定与最终化校验。
- 断言：闸门 PASS 时最终化不得报 `invalid <report>`；两者结论一致。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_and_gate_readers_agree_on_the_same_report`
- 命令：`python -m pytest -q tests/test_planning.py -k finalization_and_gate_readers_agree_on_the_same_report`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；该一致性由测试钉住，而不是靠人工核对。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 让两个读取器一致必须改变闸门的既有判定结果。
2. 既有断言必须被实质性削弱才能通过。
3. 修复必须通过改写既有报告文件才能验证。
4. 实现必须修改契约未列出的文件。
