# 任务单与证据的历史归档

<!-- Task ID: historical-archival-migration -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "historical-archival-migration",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "docs/tasks/**",
    ".pipeline/**",
    "docs/tasks/README.md",
    "tests/test_planning.py",
    "tests/test_evidence.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "references/merge-and-recovery.md",
    "SKILL.md",
    "README.md"
  ],
  "forbidden_paths": [
    "docs/goal.md",
    "pipeline_tools/**",
    ".env",
    "credentials/**",
    ".worktrees/**"
  ],
  "non_goals": [
    "不修改任何任务单的内容：只移动文件，字节必须逐字不变",
    "不修改任何已最终化的 finalization.json 或其保留集内容",
    "不重写 Git 历史：迁移是前向提交，不是改写既有提交",
    "不触碰 pipeline_tools 下的任何实现代码",
    "不为让检查变绿而删除任何任务单或证据文件"
  ],
  "operations": [
    {
      "id": "classify-and-move-sheets",
      "kind": "repair",
      "scope": "move every terminal task sheet into its evidence directory, or into the archive when it has none, leaving the two in-flight sheets in place",
      "resources": ["docs/tasks/**", ".pipeline/**"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-5"]
    },
    {
      "id": "orphan-evidence-note",
      "kind": "repair",
      "scope": "give the evidence directory that has no sheet a dated historical note",
      "resources": [".pipeline/repository-evidence-hygiene-continuation-5/**"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-3"]
    },
    {
      "id": "worklist-convention",
      "kind": "repair",
      "scope": "document that docs/tasks holds in-flight work only",
      "resources": ["docs/tasks/README.md", "README.md", "SKILL.md", "references/merge-and-recovery.md"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-4"]
    }
  ],
  "chain": {
    "entry": ["docs/tasks/: the in-flight worklist"],
    "interaction": ["pipeline_tools/planning.py: the three-location resolver delivered by the previous task"],
    "application": ["pipeline_tools/core.py: the retained-name and archive exemptions"],
    "domain": ["terminal sheets move to their evidence directory; terminal sheets with no evidence directory move to the archive; in-flight sheets stay in docs/tasks"],
    "persistence": [".pipeline task evidence directories and .pipeline/archive"],
    "readback": ["planning preflight task_scenes"],
    "recovery": ["a sheet that cannot be classified by the mechanical rule stays in docs/tasks and is reported"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_migrated_sheets_keep_their_bytes_and_are_tracked",
      "command_ref": "python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_migration_leaves_no_active_sheet_without_a_worktree",
      "command_ref": "python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_planning.py: PlanningTests.test_orphan_evidence_directory_is_no_longer_leftover",
      "command_ref": "python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract",
      "command_ref": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 3,
      "test_ref": "tests/test_evidence.py: EvidenceTests.test_closed_task_markers_still_verify_after_the_migration",
      "command_ref": "python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration"
    }
  ],
  "dependencies": ["task-sheet-archival"],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "Among the sheets in docs/tasks only the in-flight work stays: this task's own sheet and the sheet of the still-open security-scan-repair-20261001 task; every other sheet in docs/tasks belongs to a terminal task."},
    {"id": "assumption-2", "statement": "The terminal home is the presence of the task's own evidence directory: it exists means the sheet moves there, it does not means the sheet moves to the archive."},
    {"id": "assumption-3", "statement": "Moving a file with git mv keeps it tracked and changes no byte, so the freeze hashes, retained snapshots and finalization markers stay valid."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "Whether every sheet in docs/tasks belongs to a terminal task has not been re-derived by hand; sheets that the mechanical rule cannot classify must stay in docs/tasks and be listed rather than guessed."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：历史归档迁移（数据迁移，非代码）
- 任务类型：`repair`
- 用户结果或系统能力：`docs/tasks/` 只保留进行中或待派发的任务单；已终态的单子位于其证据目录或无证据目录时的 `.pipeline/archive/`；`planning preflight` 不再报"单子无 worktree"与"遗留证据目录"；已关闭任务的最终化标记仍然有效
- 执行 worktree 约定：`<仓库根目录>/.worktrees/historical-archival-migration`，由主代理用 `git worktree add` 创建；迁移在任务 worktree 内完成并提交，随后合并到主工作树。注意：主工作树里仅有的**未跟踪**本地文件（各任务的 `goal.json`/`amendments.json`，`security-scan-repair-20261001` 的未提交现场）在任务 worktree 中不可见，本任务不处理它们；`.worktrees/**` 在任务 worktree 视角下不存在，因此本任务不得调用会对"存在的工作树"fail-closed 的入口来判定分类，而必须按下方显式的在途排除清单分类
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/historical-archival-migration/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- `task-sheet-archival` 已合并：三位置解析、场景判定按状态、`archive` 隔离、保留集与闸门豁免、显式归档步骤、`.pipeline/** -text` 全部就位。
- **在途排除清单**：`docs/tasks/` 中只有两张单子属于在途工作，必须留在原处：本任务自身的 `historical-archival-migration.md`，以及仍是开放任务的 `security-scan-repair-20261001.md`。除此之外的每一张 `docs/tasks/*.md` 都视为终态并可迁移。执行者必须以迁移时的实际清单为准，逐张记录判定依据。
- 当前实测状态：迁移基线为 `docs/tasks/*.md` 共 **48** 张（含本任务自身的单子）；`.pipeline` 下已跟踪的任务证据目录 **43** 个（排除 `planning`、`metrics`、`archive`）；主工作树另有 1 个**未跟踪**证据目录 `.pipeline/security-scan-repair-20261001/`（在任务 worktree 中不可见）。可迁移的终态单子中，**3** 张没有对应证据目录（`implement-plan-coverage-repair-continuation-1`、`pipeline-evidence-lifecycle-migration`、`repository-evidence-hygiene`），应进入 `.pipeline/archive/`；**1** 个证据目录没有单（`.pipeline/repository-evidence-hygiene-continuation-5/`），需补一份历史说明单。
- `planning preflight` 当前警告：38 条"单子无 worktree"（迁移后应只剩 2 张在途单，且其 worktree 由主代理维护）与 1 条"遗留证据目录"（补说明单后应消失）。

### 允许修改

- `docs/tasks/**`（移出；以及新增 `docs/tasks/README.md`）
- `.pipeline/**`（接收单子；补说明单）
- `tests/test_planning.py`、`tests/test_evidence.py`（新增回归用例）
- `tests/test_acceptance_id_and_template_compliance.py`（扩展现有一致性用例，加工作清单约定断言）
- `references/merge-and-recovery.md`、`SKILL.md`、`README.md`（记录约定）
- 本任务证据目录 `.pipeline/historical-archival-migration/**`

### 明确不改

- 任何任务单的**内容**（只移动，字节逐字不变）
- 任何 `finalization.json` 与其保留集内容
- `pipeline_tools/**`（实现代码一律不动）
- `docs/goal.md`

### 非目标

- 不重写 Git 历史；不做批量删除。
- 不创建、不删除、不修改任何 `.worktrees/**`；不删除分支。
- 不重新验证已关闭任务的产品行为。

## 事实、假设与待决

### 已确认事实

- 三个位置由统一解析器按序查找；同一 id 多处存在或三处皆无时报错。
- 场景检查按状态区分：终态单子不再产生"单子无 worktree"警告；`worktrees_without_sheet` 接受归档位置的单子；`leftover_evidence` 减去 active 与 archived 两者。
- 保留名 = `RETAINED_EVIDENCE_NAMES` ∪ {`<task-id>.md`}；`.pipeline/archive/**` 豁免闸门。
- 24 个任务目录已持有 `finalization.json`；它们的 `retained_sha256` 只覆盖保留集内的文件，不含任务单本身。

### 未验证事实

- 尚未逐张确认除那两个在途单之外的单是否都属于终态任务；本任务要求无法机械分类的一律留在 `docs/tasks/` 并列出。
- 尚未在迁移后运行全量测试与迁移前后的哈希比对。

### 禁止猜测

- 不得自行决定把"无法机械分类"的单子移走或删除；只列出来留给主代理。
- 不得创建、删除或修改任何 `.worktrees/**`；工作树维护不属于本任务。
- 不得把在途排除清单之外的单子留在 `docs/tasks/`，也不得把在途单迁走。

## 设计与行为契约

[触发] 主代理对本仓库执行历史归档迁移
→ [处理] 按下面的机械判据逐张分类，用 `git mv` 移动
→ [状态] 终态单子出现在终态位置；`docs/tasks/` 只剩在途工作
→ [可见结果] `planning preflight` 不再报那两类警告；已关闭任务的标记仍然可校验

- **在途排除**：`historical-archival-migration`（本任务自身）与 `security-scan-repair-20261001`（仍是开放任务）留在 `docs/tasks/`，不迁移。
- **机械判据**：对其余每张单，任务的证据目录 `.pipeline/<task-id>/` 存在 → 单子移到 `.pipeline/<task-id>/<task-id>.md`；不存在 → 移到 `.pipeline/archive/<task-id>.md`。
- **字节不变**：只移动，不编辑；每张单迁移前后的 sha256 必须相同。
- **保持跟踪**：用 `git mv` 或等价做法，单子在迁移后仍被 Git 跟踪。
- **不使用会 fail-closed 的入口判定在途**：任务 worktree 视角下 `.worktrees/**` 不可见，因此不得依赖"worktree 是否存在"来判定分类；分类只依据显式在途排除清单 + 证据目录是否存在。
- **孤儿证据目录**：`.pipeline/repository-evidence-hygiene-continuation-5/` 补一份以该 id 命名的历史说明单，记录它的来历与它为何没有任务单；它**不必**是完整的 schema 4 契约，但必须能被三位置解析器按文件名找到。
- **已关闭标记不受影响**：迁移后对若干已关闭任务运行 `verify_finalization_snapshot`，不得出现保留集哈希失配。
- **验收测试4必须被扩展而不是照旧通过**：`test_lifecycle_and_evidence_documentation_matches_current_contract` 在迁移前已存在且为绿；执行者必须在该用例内新增断言，使其在 `docs/tasks/README.md` 缺失、或未写明"此处只放进行中或待派发的任务单，已终态的单子在其证据目录或 `.pipeline/archive/`"时失败。只更新文档而不扩展断言视为未完成。
- **回归用例以夹具为准**：验收测试1/2/3/5 必须在 `tempfile` 临时仓库上构造夹具并调用解析/场景/标记校验入口断言机制行为，不得依赖本任务 worktree 中 `.worktrees/**` 不可见这一偶然事实，也不得断言真实仓库里 `sheets_without_worktree` 为空（真实仓库仍有 2 张在途单）。
- **worktree 不在本任务范围内**：本任务不创建、不删除、不修改任何 `.worktrees/**`。迁移后仍留在 `docs/tasks/` 的在途单对应的、以及已终态任务遗留的 worktree，由主代理在本任务合并后作为独立维护动作处理。
- **无法分类的**：留在 `docs/tasks/` 并列出来，不猜。
- fail-closed：迁移后若 `docs/tasks/` 下仍有在途清单之外的单子、或有终态单子的证据目录成为遗留证据目录，必须报出具体清单。

## 环境前置

1. `python` 与 `git` 可执行，任务 worktree 可读写。
2. 迁移前先记录每张单的 sha256，迁移后逐一比对。

## 验收测试

### 验收测试1：迁移后单子字节不变且仍被跟踪

- 触发：在 `tempfile` 临时仓库里放置若干张 `docs/tasks/*.md`（部分配有 `.pipeline/<id>/` 目录，部分没有），按机械判据迁移，比较迁移前后的 sha256 与 Git 跟踪状态。
- 断言：sha256 逐张相同；单子仍在 `git ls-files` 中；原路径不再存在；有证据目录的落入 `.pipeline/<id>/<id>.md`，没有的落入 `.pipeline/archive/<id>.md`。
- 测试：`tests/test_planning.py: PlanningTests.test_migrated_sheets_keep_their_bytes_and_are_tracked`
- 命令：`python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；比对必须用真实哈希，不得只看文件存在。

### 验收测试2：迁移后终态单子不再留在工作清单

- 触发：在临时仓库夹具里构造"若干已迁移的终态单 + 若干仍在 `docs/tasks/` 的在途单"，运行场景检查。
- 断言：终态单不再计入在途集合；若迁移后仍有终态单留在 `docs/tasks/`，必须列出具体任务且测试失败。该用例不得断言真实仓库里 `sheets_without_worktree` 为空（真实仓库仍有 2 张在途单）。
- 测试：`tests/test_planning.py: PlanningTests.test_migration_leaves_no_active_sheet_without_a_worktree`
- 命令：`python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0。

### 验收测试3：孤儿证据目录不再是遗留

- 触发：在临时仓库夹具里构造一个只有证据目录、没有任务单的 `.pipeline/<id>/`，补入以该 id 命名的说明单后运行场景检查。
- 断言：该目录能被三位置解析器按文件名找到；`task_scenes.leftover_evidence` 不再包含它。
- 测试：`tests/test_planning.py: PlanningTests.test_orphan_evidence_directory_is_no_longer_leftover`
- 命令：`python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0。

### 验收测试4：文档记录工作清单约定

- 触发：运行文档与模板一致性检查。
- 断言：一致性检查通过；`docs/tasks/README.md` 写明此处只放进行中或待派发的任务单，已终态的单子在其证据目录或 `.pipeline/archive/`；`README.md`、`SKILL.md`、`references/merge-and-recovery.md` 口径一致。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`
- 命令：`python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；该段由审查子代理逐句核对。

### 验收测试5：已关闭标记在迁移后仍可校验

- 触发：在临时仓库夹具里构造若干已最终化的任务（含 `finalization.json` 与保留集文件），用 `git mv` 把它们的单子迁入证据目录，再运行 `verify_finalization_snapshot`。
- 断言：保留集哈希不失配（只可能出现"标记 head 变旧"这类已记录的漂移，不得出现 `finalization retained evidence hash mismatch`）。
- 测试：`tests/test_evidence.py: EvidenceTests.test_closed_task_markers_still_verify_after_the_migration`
- 命令：`python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；必须覆盖至少三个已最终化任务。

## 决策点

出现以下情况时，保留现场并报告给主代理，不得静默改变契约：

1. 某张单无法按机械判据分类（既有证据目录又不该算终态，或反之）。
2. 迁移会改动任何单子的字节或任何已关闭标记的保留集哈希。
3. 需要修改 `pipeline_tools/**` 才能完成迁移。
4. 任何需要创建、删除或修改 `.worktrees/**` 才能继续的诉求。
5. 除已列出的两个在途单之外，还发现某张单其实属于尚未终结的任务。
