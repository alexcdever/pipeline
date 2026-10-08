# 任务单修订与证据版本绑定

<!-- Task ID: task-sheet-revision-and-evidence-binding -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "task-sheet-revision-and-evidence-binding",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "pipeline_tools/core.py",
    "pipeline_tools/__main__.py",
    "pipeline_tools/task_lifecycle.py",
    "pipeline_tools/reconcile.py",
    "pipeline_tools/planning.py",
    "templates/pipeline-evidence.json",
    "tests/test_task_sheet_amendment.py",
    "tests/test_acceptance_id_and_template_compliance.py",
    "tests/test_git_checks.py",
    "tests/test_task_lifecycle.py",
    "SKILL.md",
    "README.md",
    "references/task-design.md",
    "references/acceptance-evidence.md",
    "references/execution-and-review.md",
    "references/merge-and-recovery.md",
    "references/compat-and-migration.md",
    "docs/tasks/task-sheet-revision-and-evidence-binding.md",
    ".pipeline/task-sheet-revision-and-evidence-binding/**"
  ],
  "forbidden_paths": [
    "docs/goal.md",
    "docs/tasks/security-scan-repair-20261001.md",
    "docs/tasks/security-scan-repair-20261001-continuation-1.md",
    ".pipeline/security-scan-repair-20261001/**",
    ".pipeline/security-scan-repair-20261001-continuation-1/**",
    ".env",
    "credentials/**"
  ],
  "non_goals": [
    "不修改 docs/goal.md，不修改任何历史任务单或历史证据",
    "不实现任务完成后的任务单归档与历史迁移",
    "不移除派生任务的创建路径",
    "不放松静默篡改检测，不降低任何既有验收标准"
  ],
  "operations": [
    {
      "id": "amend-command-and-record",
      "kind": "repair",
      "scope": "task amend CLI, two-axis classification and append-only revision record",
      "resources": ["pipeline_tools/__main__.py", "pipeline_tools/core.py", "pipeline_tools/task_lifecycle.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-3", "acceptance-test-4", "acceptance-test-7", "acceptance-test-9"]
    },
    {
      "id": "evidence-revision-binding",
      "kind": "repair",
      "scope": "evidence validity bound to the sheet revision instead of HEAD",
      "resources": ["pipeline_tools/reconcile.py", "templates/pipeline-evidence.json"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-6"]
    },
    {
      "id": "plan-contract-consistency-baseline",
      "kind": "repair",
      "scope": "compare the task plan against the latest sheet revision",
      "resources": ["pipeline_tools/planning.py"],
      "resource_mode": "single",
      "acceptance_tests": ["acceptance-test-8"]
    },
    {
      "id": "silent-tamper-detection",
      "kind": "validate",
      "scope": "freeze_check stays fail-closed for unrecorded edits",
      "resources": ["pipeline_tools/core.py", "tests/test_git_checks.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-5"]
    },
    {
      "id": "documentation-alignment",
      "kind": "repair",
      "scope": "align skill rules, templates and documentation pins with the revision model",
      "resources": ["SKILL.md", "README.md", "references/task-design.md", "references/acceptance-evidence.md", "references/execution-and-review.md", "references/merge-and-recovery.md", "references/compat-and-migration.md", "tests/test_acceptance_id_and_template_compliance.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-10"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: task amend CLI entry"],
    "interaction": ["pipeline_tools/core.py: amend_task_sheet classification and validation"],
    "application": ["pipeline_tools/core.py: freeze_check and evidence validity resolution"],
    "domain": ["revision chain, verification surface, loosening threshold, identity-field invariants"],
    "persistence": [".pipeline/task-sheet-revision-and-evidence-binding/amendments.json", ".pipeline/task-sheet-revision-and-evidence-binding/goal.json"],
    "readback": ["tests/test_task_sheet_amendment.py"],
    "recovery": ["rejected amendment leaves no partial record, no hash change and no moved file"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_amendment_is_allowed_after_executor_evidence",
      "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_identity_fields_are_not_amendable_and_dependencies_are",
      "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_verification_surface_and_loosening_are_classified_independently",
      "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k verification_surface_and_loosening"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_amend_rejects_missing_or_cyclic_dependencies",
      "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k amend_rejects_missing_or_cyclic_dependencies"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 3,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_freeze_check_detects_task_sheet_change_after_freeze",
      "command_ref": "python -m pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 3,
      "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_evidence_validity_tracks_sheet_revision",
      "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k evidence_validity_tracks_sheet_revision"
    },
    {
      "id": "acceptance-test-7",
      "evidence_level": 3,
      "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_amendment_record_is_append_only_and_structured",
      "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_record_is_append_only"
    },
    {
      "id": "acceptance-test-8",
      "evidence_level": 3,
      "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_plan_contract_consistency_uses_latest_revision",
      "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k plan_contract_consistency_uses_latest_revision"
    },
    {
      "id": "acceptance-test-9",
      "evidence_level": 3,
      "test_ref": "tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_amend_requires_main_agent_role_and_adjudication_for_loosening",
      "command_ref": "python -m pytest -q tests/test_task_sheet_amendment.py -k amend_requires_main_agent_role"
    },
    {
      "id": "acceptance-test-10",
      "evidence_level": 3,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract",
      "command_ref": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract"
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [3],
  "assumptions": [
    {"id": "assumption-1", "statement": "The authoritative copy of a task sheet lives under docs/tasks/ in the main worktree HEAD; an amendment is committed there and the task worktree then synchronises to it."},
    {"id": "assumption-2", "statement": "Whether files under .pipeline/ are tracked by Git is the project developer's decision; the skill must work both when amendments.json is tracked and when it is not."}
  ],
  "unknowns": [
    {"id": "unknown-1", "statement": "This repository currently does not track the per-task goal.json evidence file; the amendment record inherits that choice unless the project decides otherwise."},
    {"id": "unknown-2", "statement": "Whether any downstream consumer depends on the exact previous wording of the rewritten documentation paragraphs must be confirmed by review."}
  ]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：任务单生命周期规则修复
- 任务类型：`repair`
- 用户结果或系统能力：主代理能在任意阶段（含执行证据已产生之后）按记录修订任务单并在同一实现 worktree 继续交付；每份阶段证据写明它评判的任务单修订版本；未经记录的改动仍被机械拦截
- 执行 worktree 约定：`<仓库根目录>/.worktrees/task-sheet-revision-and-evidence-binding`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态与过程记录：由 lifecycle API/CLI 和 `.pipeline/task-sheet-revision-and-evidence-binding/` 正式 evidence 管理；此处不手工改写

## 依赖与范围

### 前置条件

- `docs/goal.md` 已按新的任务单生命周期需求更新并提交；本次改动以该版本为需求基线。
- 既有的冻结检测（`freeze_check` 的整份任务单哈希比对）必须保持有效，不得削弱。
- 执行环境具备 Python 与 pytest，且可以创建 Git worktree。

### 允许修改

- `pipeline_tools/core.py`、`pipeline_tools/__main__.py`、`pipeline_tools/task_lifecycle.py`、`pipeline_tools/reconcile.py`、`pipeline_tools/planning.py`
- `templates/pipeline-evidence.json`
- `tests/test_task_sheet_amendment.py`（新增）、`tests/test_git_checks.py`、`tests/test_acceptance_id_and_template_compliance.py`、`tests/test_task_lifecycle.py`
- `SKILL.md`、`README.md`、`references/` 下本任务列出的六份文档
- 本任务单与 `.pipeline/task-sheet-revision-and-evidence-binding/**`

### 明确不改

- `docs/goal.md` 与全部历史任务单、历史证据
- 派生任务的创建路径（`dispatch derived-create`）——移除属于后续任务
- 任务完成后的任务单归档与历史迁移——属于后续任务

### 非目标

- 不追求把任务单变成"随时可随意改写"：可修订，但每次修订必须留痕，放松约束必须带裁决引用。
- 不重构与修订无关的 CLI 结构。
- 不为迁就实现结果而调整任何验收测试。

## 事实、假设与待决

### 已确认事实

- `freeze_check`（`pipeline_tools/core.py`）比对整份任务单 sha256 与 `.pipeline/<task-id>/goal.json`（schema 1-3 为 `implement-plan.json`）中记录的 `task_sheet_sha256`；首次运行会落盘记录，之后运行才检出改动。
- `pipeline_tools/task_lifecycle.py` 的 `_read_state` 另行比对 `lifecycle.json` 中的 `task_sheet_sha256`，漂移即 blocked。
- `create_worktree_dispatch` 要求任务单已提交且工作区干净（`pipeline_tools/core.py`）。
- 派发之后没有任何机械程序读取 `dependencies`；`pipeline_tools/reconcile.py` 完全不涉及该字段。
- 计划的依赖校验（id 已知、不重复、无环）只发生在生成期，契约层只校验"是数组、元素为字符串或字典"。
- `tests/test_git_checks.py` 与 `tests/test_acceptance_id_and_template_compliance.py` 已存在并覆盖冻结检测与文档措辞断言。

### 未验证事实

- 尚未确认改写文档措辞后除本任务列出的两处断言外是否还有其它测试依赖旧措辞。
- 尚未确认在本仓库不追踪 `goal.json` 的前提下，`amendments.json` 采用何种跟踪策略更合适。
- 尚未在实现 worktree 中运行任何新增测试。

### 禁止猜测

- 不得自行决定放松约束时"裁决引用"的具体载体格式；若既有裁决记录方式无法承载，停下报告。
- 不得自行扩大允许修改范围以绕过文档措辞断言。

## 设计与行为契约

[触发] 主代理执行 `pipeline-tools task amend <root> --task-id <id> --reason <text> [--adjudication <ref>] [--requested-by <role>] [--feedback-ref <locator>]`
→ [处理] 工具校验调用角色与任务单合法性，把新旧契约做结构性比对，得出两个正交判据
→ [状态] 追加一条修订记录，并原子更新当前版本哈希
→ [可见结果] 同一 worktree 按最新修订版继续实现；再次 `freeze_check` 不再报漂移；未走 amend 的直接文件改动仍报漂移

- 修订对象是任务单文件本身：工具只做结构校验、分类与记录，不生成、不重写任务单内容。
- 身份字段 `task_id`、`task_type`、`schema`、`derived_from` 与已存在的 `dependencies` 条目不可修订；其余契约字段可修订。
- 判据一：是否改变验证面（`acceptance_tests`、`allowed_paths`、`forbidden_paths`、`chain`、`required_evidence_levels`、`operations`、`risk`）。改变即让已有阶段证据标为 stale。
- 判据二：是否放松约束（删除或放宽验收测试、降低证据等级、扩大允许范围、收窄禁止范围、删除非目标）。放松必须带 `--adjudication`。
- `dependencies` 的增删只需 `--reason`，但修订后必须校验依赖 id 有对应任务单存在且不构成环。
- 修订记录为追加式，含前版与新版哈希、理由、发起角色、裁决引用与结构性差异；旧记录不得改写。
- 证据与报告的有效性判据是 `sheet_revision` 加 `sheet_sha256`；`observed_at_commit` 只作事实记录，HEAD 移动本身不得让证据失效。
- 失败、被拒绝或校验不通过的修订必须原子回滚：不留下部分记录、不改变任何哈希、不移动任何文件。

## 环境前置

1. `python` 与 `git` 可执行，仓库可读写。
2. 在实现 worktree 中运行聚焦与全量测试；不得只运行新增测试就宣称完成。

## 验收测试

### 验收测试1：执行证据已存在后仍可修订并在同一 worktree 继续

- 触发：某任务已产生执行阶段证据（含 `executor-result.json`），主代理以 `--reason` 修订任务单并继续派发。
- 断言：修订被接受；同一实现 worktree 与同一证据目录被继续使用；不新建 worktree 或证据目录；后续阶段推进成功。
- 测试：`tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_amendment_is_allowed_after_executor_evidence`
- 命令：`python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_is_allowed_after_executor_evidence`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；断言失败即 FAIL；不得以新建 worktree 的方式绕过。

### 验收测试2：身份字段不可修订，依赖可修订

- 触发：分别尝试修订 `task_id`、`task_type`、`schema`、`derived_from`、已有 `dependencies` 条目与 `dependencies` 新增项。
- 断言：身份字段的修订被拒绝且文件未被改动；`dependencies` 的增删被接受并写入修订记录。
- 测试：`tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_identity_fields_are_not_amendable_and_dependencies_are`
- 命令：`python -m pytest -q tests/test_task_sheet_amendment.py -k identity_fields_are_not_amendable`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；被拒绝的修订不得留下任何记录或哈希变化。

### 验收测试3：验证面变更与放松约束是两个独立判据

- 触发：构造四类修订——仅改散文、改 `acceptance_tests`（收紧）、改 `allowed_paths`、删除一条验收测试。
- 断言：仅改散文不触发任何判据；改变验证面使已有阶段证据标为 stale；放松约束在缺少 `--adjudication` 时被拒绝，提供后被接受并记录为放松。
- 测试：`tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_verification_surface_and_loosening_are_classified_independently`
- 命令：`python -m pytest -q tests/test_task_sheet_amendment.py -k verification_surface_and_loosening`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；两个判据的取值必须在修订记录中分别可见。

### 验收测试4：依赖修订必须校验存在性与无环

- 触发：修订引入一个没有对应任务单的依赖 id，以及一个形成依赖环的依赖 id。
- 断言：两种修订都被拒绝，报出具体原因；合法依赖被接受。
- 测试：`tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_amend_rejects_missing_or_cyclic_dependencies`
- 命令：`python -m pytest -q tests/test_task_sheet_amendment.py -k amend_rejects_missing_or_cyclic_dependencies`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；拒绝时任务单与修订记录均保持不变。

### 验收测试5：未经记录的改动仍被判为漂移

- 触发：在任务单冻结之后直接编辑任务单文件，不走 `task amend`。
- 断言：`freeze_check` 报出任务单在冻结后被改动，退出码为漂移类。
- 测试：`tests/test_git_checks.py: GitChecks.test_freeze_check_detects_task_sheet_change_after_freeze`
- 命令：`python -m pytest -q tests/test_git_checks.py -k task_sheet_change_after_freeze`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；该既有用例必须保持通过，不得为适配新机制而放松断言。

### 验收测试6：证据有效性绑定修订版本而不是 HEAD

- 触发：产出证据后再产生若干提交（HEAD 移动），随后修改被验证路径。
- 断言：HEAD 移动本身不让证据失效；被验证路径发生变化时证据标为 stale；报告携带 `sheet_revision` 与 `sheet_sha256`。
- 测试：`tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_evidence_validity_tracks_sheet_revision`
- 命令：`python -m pytest -q tests/test_task_sheet_amendment.py -k evidence_validity_tracks_sheet_revision`
- 验收模式：集成
- 证据等级：3
- 结果要求：退出码 0；两种情形必须分别可观察，不得只用一种情形代表两种。

### 验收测试7：修订记录为追加式且结构完整

- 触发：连续执行两次修订。
- 断言：记录为两个版本、按序追加、旧记录字节不变；每条含前版与新版哈希、理由、发起角色、裁决引用与结构性差异；验收测试集合的增删改在差异中可见。
- 测试：`tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_amendment_record_is_append_only_and_structured`
- 命令：`python -m pytest -q tests/test_task_sheet_amendment.py -k amendment_record_is_append_only`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；哈希链必须可逐条回溯。

### 验收测试8：计划与契约的一致性检查以最新修订版为基准

- 触发：先修订 `dependencies`，再运行计划与契约一致性检查。
- 断言：检查以最新修订版为基准，报出"规划后被修订过"而不是裸漂移；未修订的任务仍按原基准比对。
- 测试：`tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_plan_contract_consistency_uses_latest_revision`
- 命令：`python -m pytest -q tests/test_task_sheet_amendment.py -k plan_contract_consistency_uses_latest_revision`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；不得通过跳过一致性检查来达标。

### 验收测试9：角色与裁决门槛

- 触发：以非主代理角色调用 `task amend`；以及在不提供 `--adjudication` 的情况下执行一次放松约束的修订。
- 断言：前者被拒绝；后者被拒绝；补齐裁决引用后被接受。
- 测试：`tests/test_task_sheet_amendment.py: TaskSheetAmendmentTests.test_amend_requires_main_agent_role_and_adjudication_for_loosening`
- 命令：`python -m pytest -q tests/test_task_sheet_amendment.py -k amend_requires_main_agent_role`
- 验收模式：单元
- 证据等级：3
- 结果要求：退出码 0；被拒绝的调用不得产生任何副作用。

### 验收测试10：文档与不变量一致

- 触发：运行文档与模板一致性检查。
- 断言：本任务列出的文档与模板描述版本化修订而不是绝对不可变；技能版本号已升；措辞断言与当前规则一致；schema 1-3 的历史读取兼容保持不变。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_lifecycle_and_evidence_documentation_matches_current_contract`
- 命令：`python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract`
- 验收模式：组件
- 证据等级：3
- 结果要求：退出码 0；改写断言时不得删除其对"文档必须描述当前状态模型"的约束意图。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 既有验收测试的断言需要实质性削弱才能通过——这属于设计冲突，不是实现细节。
2. 放松约束所需的裁决引用在既有记录方式中没有承载位置。
3. 证据有效性判据的改动需要同时重写历史证据才能通过。
