# 任务单归档机制

<!-- Task ID: task-sheet-archival -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "task-sheet-archival",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "pipeline_tools/core.py",
    "pipeline_tools/planning.py",
    "pipeline_tools/layout.py",
    "tests/test_planning.py",
    "tests/test_evidence.py",
    "tests/test_task_evidence_reconcile.py",
    ".gitattributes",
    "SKILL.md",
    "README.md",
    "references/task-design.md",
    "references/merge-and-recovery.md",
    "references/acceptance-evidence.md",
    "references/compat-and-migration.md",
    "docs/tasks/task-sheet-archival.md",
    ".pipeline/task-sheet-archival/**"
  ],
  "forbidden_paths": [
    "docs/goal.md",
    "pipeline_tools/contract.py",
    ".pipeline/task-sheet-revision-and-evidence-binding/**",
    ".pipeline/post-merge-evidence-identity/**",
    ".pipeline/finalization-and-reconcile-phase/**",
    ".pipeline/finalization-marker-head-tolerance/**",
    ".pipeline/finalization-report-reader/**",
    ".pipeline/finalization-hygiene/**",
    ".pipeline/derived-creation-removal/**",
    ".pipeline/security-scan-repair-20261001/**",
    ".pipeline/security-scan-repair-20261001-continuation-1/**",
    "docs/tasks/*.md",
    ".env",
    "credentials/**"
  ],
  "non_goals": [
    "不执行历史迁移：本任务只建立机制，不搬动任何既有任务单",
    "不删除、移动或改写任何现有任务的证据目录与已最终化标记",
    "不放宽 retention 快照判据与产品路径失效判据",
    "不发散到全部文档：只处理契约列出的文件与已登记的措辞残留",
    "不为让测试变绿而删除或放宽任何既有断言"
  ],
  "operations": [
    {
      "id": "three-position-sheet-resolution",
      "kind": "repair",
      "scope": "one resolver for the three task sheet locations",
      "resources": ["pipeline_tools/planning.py", "pipeline_tools/core.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-5"]
    },
    {
      "id": "scene-facts-by-state",
      "kind": "repair",
      "scope": "worklist checks use active sheets only; archive is excluded from the evidence scan",
      "resources": ["pipeline_tools/planning.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-2", "acceptance-test-3", "acceptance-test-4"]
    },
    {
      "id": "retention-and-forward-gate",
      "kind": "repair",
      "scope": "a task's own sheet is retained; archive paths are exempt from the retained-name rule",
      "resources": ["pipeline_tools/core.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-6"]
    },
    {
      "id": "line-ending-stability",
      "kind": "repair",
      "scope": "pipeline evidence bytes survive a checkout unchanged",
      "resources": [".gitattributes"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-7"]
    },
    {
      "id": "finalize-move-step",
      "kind": "repair",
      "scope": "finalization moves the task sheet into its evidence directory, refusing while the worktree exists",
      "resources": ["pipeline_tools/planning.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-5"]
    },
    {
      "id": "documentation",
      "kind": "repair",
      "scope": "record the three-location rule, the worklist semantics and the registered wording residue",
      "resources": ["SKILL.md", "README.md", "references/task-design.md", "references/merge-and-recovery.md", "references/acceptance-evidence.md", "references/compat-and-migration.md"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-8"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: planning evidence-finalize and planning preflight CLI"],
    "interaction": ["pipeline_tools/planning.py: sheet resolver and task scene facts"],
    "application": ["pipeline_tools/core.py: retained set and forward baseline gate"],
    "domain": ["active versus terminal sheets; archive quarantine; byte stability of evidence"],
    "persistence": [".pipeline/task-sheet-archival/finalization.json and the task sheet after the move"],
    "readback": ["tests/test_planning.py", "tests/test_evidence.py"],
    "recovery": ["a missing sheet still fails closed; a live worktree blocks the move"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_sheet_resolver_finds_all_three_locations",
      "command_ref": "python -m pytest -q tests/test_planning.py -k sheet_resolver_finds_all_three_locations"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_worklist_checks_ignore_terminal_sheets",
      "command_ref": "python -m pytest -q tests/test_planning.py -k worklist_checks_ignore_terminal_sheets"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_archive_directory_is_not_treated_as_task_evidence",
      "command_ref": "python -m pytest -q tests/test_planning.py -k archive_directory_is_not_treated_as_task_evidence"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_archived_sheet_still_answers_worktree_without_sheet",
      "command_ref": "python -m pytest -q tests/test_planning.py -k archived_sheet_still_answers_worktree_without_sheet"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_finalization_moves_the_sheet_and_refuses_while_the_worktree_lives",
      "command_ref": "python -m pytest -q tests/test_planning.py -k finalization_moves_the_sheet_and_refuses_while_the_worktree_lives"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_task_sheet_and_archive_are_exempt_from_the_retained_name_rule",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k task_sheet_and_archive_are_exempt_from_the_retained_name_rule"
    },
    {
      "id": "acceptance-test-7",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_pipeline_evidence_bytes_survive_a_checkout",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k pipeline_evidence_bytes_survive_a_checkout"
    },
    {
      "id": "acceptance-test-8",
      "evidence_level": 3,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract",
      "command_ref": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract"
    }
  ],
  "dependencies": ["derived-creation-removal"],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "A sheet's location encodes its state: docs/tasks for in-flight work, the task's evidence directory for terminal work, and a flat archive for sheets with no evidence directory to move into."},
    {"id": "assumption-2", "statement": "Because the task sheet is not in the retained set, finalization would prune the moved sheet; the retained set must therefore accept the task's own sheet name, and the forward baseline gate must exempt the archive directory."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "How many existing sheets and evidence directories would change their scene classification once the resolver lands has not been enumerated; the migration itself is out of scope, so the resolver must not move anything."},
    {"id": "unknown-2", "statement": "Whether declaring .pipeline evidence as non-text changes any already committed byte has not been verified; if adding the attribute would rewrite existing blobs, stop and report rather than silently altering closed evidence."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：任务单归档机制
- 任务类型：`repair`
- 用户结果或系统能力：任务单可以存在于三个位置且被统一解析；工作清单只看进行中的单子；最终化把任务单移入其证据目录且在有活 worktree 时拒绝移动；证据字节经 checkout 不变
- 执行 worktree 约定：`<仓库根目录>/.worktrees/task-sheet-archival`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/task-sheet-archival/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- `docs/goal.md` 已规定：进行中的任务单存于 `docs/tasks/<task-id>.md`，已终态的任务单存于其证据目录 `.pipeline/<task-id>/`，没有对应证据目录时存于 `.pipeline/archive/`；`docs/tasks/` 只保留进行中或待派发的任务单。
- 之前的任务已建立：证据绑定修订版本、阶段分工、最终化与读取器、最终化保留本地状态文件、移除派生创建路径。
- 实测事实：`planning` 的方案核对按 `docs/tasks/*.md` 建表、`.pipeline` 子目录一律视为任务证据（仅排除 `planning`、`metrics`）；最终化只保留 `RETAINED_EVIDENCE_NAMES`；前向基线闸门按保留集判定新增/删除。

### 允许修改

- `pipeline_tools/planning.py`：任务单解析、场景检查、最终化移动步骤
- `pipeline_tools/core.py`：保留集判定与闸门豁免
- `pipeline_tools/layout.py`：`archive` 目录的布局常量（如需要）
- `tests/test_planning.py`、`tests/test_evidence.py`、`tests/test_task_evidence_reconcile.py`
- `.gitattributes`
- `SKILL.md`、`README.md`、`references/` 下契约列出的六份文档
- 本任务单与 `.pipeline/task-sheet-archival/**`

### 明确不改

- `docs/goal.md`、`pipeline_tools/contract.py`、任何既有任务单（`docs/tasks/*.md` 在 `forbidden_paths` 中）、任何既有任务的证据目录与已最终化标记
- retention 快照判据与产品路径失效判据

### 非目标

- **不执行历史迁移**：本任务只建立机制，不搬动任何既有单子或证据；历史迁移是后续任务。
- 不顺手改其它文档口径（除契约列出的六份）。
- 不实现 worktree 清理。

## 事实、假设与待决

### 已确认事实

- `planning` 的场景检查用三张表：`docs/tasks/*.md` 建的单子表、`.worktrees/` 建的工作树表、`.pipeline/` 下子目录（排除 `planning`、`metrics`）建的证据表；`sheets_without_worktree` 与 `leftover_evidence` 是警告，`worktrees_without_sheet` 与 `uncommitted_sheets` 是错误。
- `RETAINED_EVIDENCE_NAMES` 是三份报告 + 三份机器结果 + `finalization.json`，不含任务单；最终化会剪掉不在该集合里的文件。
- 前向基线闸门：`.pipeline` 证据根下新增非保留名文件即违规，删除保留名文件即违规。
- `.gitattributes` 现有 `* text=auto eol=lf` 与 `docs/tasks/*.md -text`。
- 实测：主工作树里若干证据文件在工作区是 CRLF，提交时 git 提示"CRLF 将被替换为 LF"，即工作区字节与提交内容可能不一致。

### 未验证事实

- 尚未枚举机制落地后有多少既有单子与证据目录会改变场景分类。
- 尚未确认给 `.pipeline` 声明非文本会不会改写已提交的字节。
- 尚未在实现 worktree 中运行任何新增测试。

### 禁止猜测

- 不得自行决定 archive 目录的**名字**：契约按 `docs/goal.md` 采用 `.pipeline/archive/`。
- 不得自行决定是否顺带迁移历史单子；一律不做。
- 不得自行决定"活 worktree 存在时是拒绝移动还是先删 worktree"；按契约拒绝并报 blocked。

## 设计与行为契约

[触发] 规划前置检查或最终化处理某任务时
→ [处理] 通过统一解析器定位该任务单，并按位置判定其状态
→ [状态] 工作清单与证据归属按状态区分；最终化把终态单子移入证据目录
→ [可见结果] `docs/tasks/` 只反映进行中的工作；归档单仍可被解析引用；证据字节稳定

- **三个位置**（按序解析）：`docs/tasks/<task-id>.md` → `.pipeline/<task-id>/<task-id>.md` → `.pipeline/archive/<task-id>.md`。
- **场景判定按状态**：`active` 只取 `docs/tasks/*.md`；`archived` 取 `.pipeline/<task-id>/<task-id>.md` 与 `.pipeline/archive/*.md`。`sheets_without_worktree` 与 `uncommitted_sheets` 只用 `active`；`worktrees_without_sheet` 用 `active ∪ archived`；`leftover_evidence` = 证据目录减去两者。
- **archive 不是任务证据**：`.pipeline/archive` 必须加入证据目录扫描的排除集合（与 `planning`、`metrics` 同级），不得被当成一个叫 archive 的任务。
- **保留集**：某任务的保留名 = `RETAINED_EVIDENCE_NAMES` ∪ {`<该任务 id>.md`}；前向基线闸门对 `.pipeline/archive/**` 下的路径豁免保留名规则。
- **最终化移动**：最终化把任务单从 `docs/tasks/<task-id>.md` 移到 `.pipeline/<task-id>/<task-id>.md`（用 `git mv` 保持跟踪）；若 `.worktrees/<task-id>` 仍然存在，则 **blocked**，不移动任何文件。
- **字节稳定**：`.pipeline/**` 下的证据文件必须声明为不做换行转换，使其经 checkout 后字节不变；新增该属性**不得改写已提交的既有字节**。
- fail-closed：三个位置都找不到任务单、或同一任务单出现在多个位置、或 worktree 与单子状态矛盾——一律报错，不猜。

## 环境前置

1. `python` 与 `git` 可执行，仓库可读写。
2. 在实现 worktree 中运行聚焦与全量测试。

## 验收测试

### 验收测试1：三位置解析

- 触发：分别把同一任务单放在 `docs/tasks/`、`.pipeline/<id>/`、`.pipeline/archive/` 三处之一。
- 断言：解析器都能定位到它；同一 id 出现在多个位置时报错；三处都不存在时报错。
- 测试：`tests/test_planning.py: PlanningTests.test_sheet_resolver_finds_all_three_locations`
- 命令：`python -m pytest -q tests/test_planning.py -k sheet_resolver_finds_all_three_locations`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；四种情形都必须被观测到。

### 验收测试2：工作清单只看进行中的单子

- 触发：造一个终态单子（位于证据目录或 archive）而没有 worktree。
- 断言：不产生 `sheets_without_worktree` 警告；而 `docs/tasks/` 下的单子没有 worktree 时仍产生该警告。
- 测试：`tests/test_planning.py: PlanningTests.test_worklist_checks_ignore_terminal_sheets`
- 命令：`python -m pytest -q tests/test_planning.py -k worklist_checks_ignore_terminal_sheets`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；两个方向都要观测到。

### 验收测试3：archive 不被当作任务证据

- 触发：仓库里存在 `.pipeline/archive/`。
- 断言：它不出现在证据表里，不产生 `leftover_evidence` 或任何以 `archive` 为任务名的条目。
- 测试：`tests/test_planning.py: PlanningTests.test_archive_directory_is_not_treated_as_task_evidence`
- 命令：`python -m pytest -q tests/test_planning.py -k archive_directory_is_not_treated_as_task_evidence`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0。

### 验收测试4：归档单仍能满足"worktree 必须有单"

- 触发：worktree 存在，而该任务的单子位于 `.pipeline/archive/` 或证据目录。
- 断言：不产生 `worktrees_without_sheet` 错误。
- 测试：`tests/test_planning.py: PlanningTests.test_archived_sheet_still_answers_worktree_without_sheet`
- 命令：`python -m pytest -q tests/test_planning.py -k archived_sheet_still_answers_worktree_without_sheet`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0。

### 验收测试5：最终化移动任务单，并在 worktree 存活时拒绝

- 触发：对一份齐全证据的任务运行最终化，分别在"worktree 已删除"与"worktree 仍存在"两种状态下。
- 断言：worktree 已删 → 任务单被移动到证据目录、仍被 Git 跟踪、最终化成功；worktree 仍在 → blocked 且任务单未移动。
- 测试：`tests/test_planning.py: PlanningTests.test_finalization_moves_the_sheet_and_refuses_while_the_worktree_lives`
- 命令：`python -m pytest -q tests/test_planning.py -k finalization_moves_the_sheet_and_refuses_while_the_worktree_lives`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；两个方向都要观测到。

### 验收测试6：保留集与闸门豁免

- 触发：证据目录里有该任务自己的任务单；以及 `.pipeline/archive/` 下有一个单子。
- 断言：二者都不被判为违规（保留集接纳自有单子；archive 路径豁免保留名规则）；而同类目录下一个**别的**非保留名文件仍被判违规。
- 测试：`tests/test_evidence.py: EvidenceTests.test_task_sheet_and_archive_are_exempt_from_the_retained_name_rule`
- 命令：`python -m pytest -q tests/test_evidence.py -k task_sheet_and_archive_are_exempt_from_the_retained_name_rule`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；反向情形必须仍被判违规。

### 验收测试7：证据字节经 checkout 不变

- 触发：在临时仓库里以 CRLF 写入一份 `.pipeline` 下的证据文件并提交，然后在新克隆/检出的目录里读取同一文件。
- 断言：字节与提交时一致（不发生换行转换）；且新增该属性未改写任何既有已提交字节。
- 测试：`tests/test_evidence.py: EvidenceTests.test_pipeline_evidence_bytes_survive_a_checkout`
- 命令：`python -m pytest -q tests/test_evidence.py -k pipeline_evidence_bytes_survive_a_checkout`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；第二个断言必须用「加属性前后的既有 blob 哈希」比较来证明。

### 验收测试8：文档记录规则

- 触发：运行文档与模板一致性检查。
- 断言：一致性检查通过；契约列出的文档写明三位置规则、工作清单语义、最终化移动与活 worktree 拒绝、以及 `acceptance-evidence.md` 中"落在证据目录内"的措辞已改为按 `.pipeline` 判定的口径。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`
- 命令：`python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；该段由审查子代理逐句核对。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 给 `.pipeline` 声明非文本会改写既有已提交字节。
2. 让归档单满足"worktree 必须有单"必须放宽既有的错误判据。
3. 最终化移动任务单会破坏 retention 快照判据或既有最终化校验。
4. 实现必须修改契约未列出的文件。
