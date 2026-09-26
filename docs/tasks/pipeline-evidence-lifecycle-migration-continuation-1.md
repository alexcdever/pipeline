# 证据生命周期迁移延续：schema 2 契约与工具面修复

<!-- Task ID: pipeline-evidence-lifecycle-migration-continuation-1 -->
<!-- Contract section is frozen after commit. Lifecycle sections are maintained by the main agent. Parent task remains BLOCKED and is never rewritten by this continuation. -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "pipeline-evidence-lifecycle-migration-continuation-1",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": [
    "pipeline_tools/**",
    "tests/**",
    "docs/tasks/pipeline-evidence-lifecycle-migration-continuation-1.md",
    "references/**"
  ],
  "forbidden_paths": [
    "implement-plan.md",
    "IDEA.md",
    ".pipeline/**",
    ".workflow/**",
    "**/*evidence*",
    "**/.env",
    "**/*secret*",
    "**/*token*"
  ],
  "operations": [
    {
      "id": "repair-schema2-contract-and-fixtures",
      "kind": "repair",
      "scope": "migrate lifecycle contract fixtures and tests to the current schema-2 tool surface without changing the parent task history",
      "acceptance_tests": [
        "acceptance-test-schema2-dispatch",
        "acceptance-test-commit-history-guard",
        "acceptance-test-finalization-current-command",
        "acceptance-test-evidence-verify-current-command",
        "acceptance-test-no-historical-rewrite"
      ]
    }
  ],
  "chain": {
    "entry": ["docs/tasks/pipeline-evidence-lifecycle-migration.md"],
    "interaction": ["pipeline_tools/__main__.py", "tests/test_cli.py"],
    "application": ["pipeline_tools/core.py", "pipeline_tools/planning.py"],
    "domain": ["pipeline_tools/contract.py", "pipeline_tools/layout.py"],
    "persistence": ["tests/fixtures and temporary Git repositories only"],
    "readback": ["pipeline_tools/__main__.py", "tests/test_contract.py", "tests/test_evidence.py"],
    "recovery": ["tests/test_derived_task_dispatch_recovery.py", "docs/tasks/pipeline-evidence-lifecycle-migration.md"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-schema2-dispatch",
      "evidence_level": 2,
      "test_ref": "tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch",
      "command_ref": "python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch -v"
    },
    {
      "id": "acceptance-test-commit-history-guard",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: GitChecks.test_commit_history_evidence_path_guard",
      "command_ref": "python -m unittest tests.test_git_checks.GitChecks.test_commit_history_evidence_path_guard -v"
    },
    {
      "id": "acceptance-test-finalization-current-command",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_evidence_finalize_current_command_preserves_raw_on_block_and_is_idempotent",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_evidence_finalize_current_command_preserves_raw_on_block_and_is_idempotent -v"
    },
    {
      "id": "acceptance-test-evidence-verify-current-command",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: CLITests.test_evidence_verify_current_command_reports_machine_identity_and_finalization_state",
      "command_ref": "python -m unittest tests.test_cli.CLITests.test_evidence_verify_current_command_reports_machine_identity_and_finalization_state -v"
    },
    {
      "id": "acceptance-test-no-historical-rewrite",
      "evidence_level": 2,
      "test_ref": "tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history",
      "command_ref": "python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history -v"
    }
  ],
  "dependencies": [
    "pipeline-evidence-lifecycle-migration remains frozen and BLOCKED",
    "current schema-2 validation and dispatch behavior in pipeline_tools",
    "Python 3.11 standard library and local Git executable"
  ],
  "required_evidence_levels": [2]
}
```

## 任务身份

- 项目：programing-pipeline
- 领域或阶段：证据生命周期迁移兼容性修复（schema 2 prerequisite/repair）
- 用户结果或系统能力：当前 schema 2 工具可以验证、派发并验收生命周期迁移契约；commit history guard、finalization 和 evidence verify 使用当前命令面；父任务的 BLOCKED 事实和历史保持不变。
- 执行 worktree 约定：`D:/Projects/Skills/pipeline/.worktrees/pipeline-evidence-lifecycle-migration-continuation-1`，由主代理用 `git worktree add` 创建；不预先 `mkdir`，不创建仓库同级或第二个 worktree
- 状态：未开始
- 父任务：`docs/tasks/pipeline-evidence-lifecycle-migration.md`（保持 BLOCKED，不改写）

## 依赖与范围

### 前置条件

- 父任务 `pipeline-evidence-lifecycle-migration` 已冻结为 schema 1，且当前主工作树记录其 BLOCKED 状态；该事实只读保留。
- 当前 `pipeline_tools` contract validator 要求 schema 2 的 `task_type`、`implement_plan`、`operations`、完整 acceptance IDs、chain、dependencies 和 evidence levels。
- 当前 dispatch、planning finalization、evidence verify 的实现和测试是迁移目标的事实基线；执行前必须读取并以实际命令验证，不以旧报告推断 PASS。
- Python 3.11 标准库和临时 Git 仓库可用；不联网、不新增第三方依赖。

### 允许修改

- `pipeline_tools/**`：仅为使当前 schema 2 契约、commit history guard、finalization 和 evidence verify 命令可验证而作的工具修复。
- `tests/**`：把本任务涉及的 lifecycle fixtures、契约和测试迁移为 schema 2，并补齐本任务列明的精确验收用例。
- `docs/tasks/pipeline-evidence-lifecycle-migration-continuation-1.md`：本任务级进度和证据索引。
- `references/**`：仅同步当前 schema 2 命令、兼容边界和不可重写历史的说明。

### 明确不改

- 不修改 `docs/tasks/pipeline-evidence-lifecycle-migration.md`；父任务继续记录为 BLOCKED。
- 不修改 `implement-plan.md`、`IDEA.md`，不接触或迁移任何旧 `.pipeline`/`.workflow` evidence 目录和原始 evidence 文件。
- 不把 schema 1 历史任务单、旧 fixtures、旧报告或历史提交静默重写为 schema 2；历史兼容只通过只读解析/明确迁移 fixture 证明。
- 不自动提交、合并、改写或删除 Git 历史，不修改外部消费项目、产品代码或用户数据。
- 不扩大到未列出的 CLI 命令、浏览器、设备或外部服务。

## 事实、假设与待决

### 已确认事实

- 父任务契约区块是 schema 1，而当前 contract validator 对新任务支持并要求 schema 2；父任务已有执行、审查和主终检均记录为 BLOCKED。
- 当前 schema 2 contract 需要完整的 acceptance-test-* IDs，并要求 operation 引用完整 acceptance ID。
- 当前命令入口已有 `dispatch worktree-create`、`planning evidence-finalize`、`evidence verify` 和 `gate` 命令；这些命令的实际行为必须由本任务验收测试确认。
- 现有 continuation dispatch 测试明确要求唯一、幂等且不重写 parent history；该不变量在本任务中保留。

### 未验证事实

- 当前分支是否已经具备本任务所需 commit history guard 的完整实现，须由 `acceptance-test-commit-history-guard` 直接命令验证。
- 当前 finalization 和 evidence verify 的所有 JSON 字段、退出码和 raw-evidence 保留边界，须由对应 CLI 验收直接验证。
- 未执行的命令、未读取的报告和旧 schema 1 报告均不构成本任务 PASS 证据。

### 禁止猜测

- 不把父任务的 BLOCKED 转成 PASS、FAILED 或已合并；本任务只能解除 schema/tool prerequisite，不代表父任务产品验收完成。
- 不把 schema 1 历史契约自动升级、文件存在、报告散文或零退出码推断为语义兼容。
- 不用最终净差异替代逐提交 history guard；不因迁移 fixture 方便而改写历史 task sheet、旧 evidence 或提交历史。

## 设计与行为契约

[读取冻结的 schema 1 父任务（只读）和当前 schema 2 工具契约]
→ [迁移本任务范围内的 contract fixtures/tests，不改父任务或历史 evidence]
→ [当前 schema 2 dispatch 生成身份可验证的 dispatch/worktree 结果]
→ [commit history guard 检查每个提交曾修改的路径并隔离 metrics 豁免]
→ [当前 finalization 命令在阻塞时保留 raw evidence，在成功时按既定规则幂等收口]
→ [当前 evidence verify 命令返回稳定的机器身份、引用闭包和 finalized 状态]
→ [主代理可重新验收父任务；父任务原有 BLOCKED 记录仍保持不变]

- schema 1 历史输入只读兼容；schema 2 新输入必须通过结构校验，不隐式补字段。
- 所有失败、身份漂移、命令不存在、证据不足和范围漂移均保持 BLOCKED/FAIL，不降级为 PASS。
- continuation 任务创建和重复执行必须幂等，且不得重写 parent task sheet 的字节内容或历史进度。
- 迁移只作用于本任务允许的 fixtures/tests；没有全局历史改写、旧 evidence 清理或 `.pipeline`/`.workflow` 目录迁移。

## 环境前置

1. 在主工作树确认父任务文件和 `IDEA.md` 的现有修改不属于本任务；不得覆盖这些修改。
2. 契约提交后，从主工作树创建唯一 `.worktrees/pipeline-evidence-lifecycle-migration-continuation-1`，并核对绝对路径、分支和基线 HEAD。
3. 执行前运行 schema 2 task validate、runtime preflight 和范围检查；每条验收命令三分钟硬超时。
4. 验收使用临时 Git/文件系统 fixture；不得读取或修改既有 evidence 目录。

## 验收测试

### 验收测试1：schema 2 dispatch 身份闭环

- 触发：对 schema 2 repair/prerequisite 契约执行当前 planning-to-dispatch 或 worktree dispatch 流程。
- 断言：dispatch 通过 schema 2 contract、返回稳定 task/branch/head/worktree identity；重复 dispatch 在冲突时 fail closed，不替换已有 worktree 或契约。
- 测试：`tests/test_planning_dispatch_integration.py: PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch`
- 命令：`python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch -v`
- 验收模式：临时真实 Git 仓库集成测试
- 证据等级：2
- 结果要求：退出码 0；测试必须证明 dispatch identity 和 dispatch artifact，不能仅证明 import 或 contract parse。

### 验收测试2：commit history guard 当前命令

- 触发：在临时 Git 仓库中分别提交产品文件、活动任务证据文件、删除/重命名证据文件、metrics 文件以及先添加后删除的证据文件，并执行当前 commit check/history guard 命令。
- 断言：产品提交和明确豁免的 metrics 提交通过；任何曾修改活动任务 evidence 的提交均被阻止并指出提交与路径；逐提交历史检查不被最终净差异绕过。
- 测试：`tests/test_git_checks.py: GitChecks.test_commit_history_evidence_path_guard`
- 命令：`python -m unittest tests.test_git_checks.GitChecks.test_commit_history_evidence_path_guard -v`
- 验收模式：临时真实 Git 仓库集成测试
- 证据等级：2
- 结果要求：退出码 0；测试不得修改本仓库提交，不得把 metrics 豁免扩大到任务 evidence。

### 验收测试3：finalization 当前命令

- 触发：使用当前 `planning evidence-finalize` 命令对未获主代理批准、引用不完整和可最终化的临时 evidence fixture 执行 finalization，并重复执行成功路径。
- 断言：阻塞时 raw evidence 和 marker 均保持；成功时只按既定保留规则收口并可幂等重复；命令退出码、JSON status 和 marker/hash 一致。
- 测试：`tests/test_cli.py: CLITests.test_evidence_finalize_current_command_preserves_raw_on_block_and_is_idempotent`
- 命令：`python -m unittest tests.test_cli.CLITests.test_evidence_finalize_current_command_preserves_raw_on_block_and_is_idempotent -v`
- 验收模式：CLI 真实启动与临时文件系统集成测试
- 证据等级：2
- 结果要求：退出码 0；产品未被 finalization 命令静默改写，失败不得留下半完成 marker。

### 验收测试4：evidence verify 当前命令

- 触发：对 schema 2 任务身份下的 executor/reviewer/final-check 机器证据执行当前 `evidence verify` 命令，覆盖缺失报告、身份漂移、非 PASS 和 finalized/readiness 边界。
- 断言：命令返回当前统一 JSON envelope、准确 task/branch/role/引用闭包和 finalized 状态；缺证据或身份不匹配为 BLOCKED/FAIL，不从散文报告推断 PASS。
- 测试：`tests/test_cli.py: CLITests.test_evidence_verify_current_command_reports_machine_identity_and_finalization_state`
- 命令：`python -m unittest tests.test_cli.CLITests.test_evidence_verify_current_command_reports_machine_identity_and_finalization_state -v`
- 验收模式：CLI 真实启动与临时文件系统集成测试
- 证据等级：2
- 结果要求：退出码 0；测试必须覆盖当前命令输出而非仅调用内部函数。

### 验收测试5：无静默历史重写与 continuation 恢复

- 触发：重复创建相同 continuation dispatch，并在 parent evidence/parent task sheet 存在时执行恢复/冲突路径。
- 断言：相同 child task 只创建一次；重复请求 fail closed 或返回既有身份；parent task sheet 和 parent evidence 字节内容保持不变，parent BLOCKED 状态不被改写。
- 测试：`tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history`
- 命令：`python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history -v`
- 验收模式：临时真实 Git/文件系统集成测试
- 证据等级：2
- 结果要求：退出码 0；必须有 parent bytes-before/after 断言，不得执行历史文件批量重写。

## 决策点

1. 若当前工具没有可验证的 commit history guard 或命令名与契约不一致，保留现场并报告 BLOCKED；不得把已有 scope check 冒充 commit history 验收。
2. 若 finalization/evidence verify 的当前 JSON contract 与本任务断言不一致，记录实际输出并暂停，不能通过修改验收文字静默降级。
3. 若需要修改父任务、`implement-plan.md`、`IDEA.md` 或旧 evidence 才能通过，停止并请求新的明确 continuation 决策；本任务范围不扩张。
4. 本任务完成只表示 prerequisite/repair 可供父任务重新派发；父任务必须继续保持 BLOCKED，直到另行执行其冻结验收。

---

## 任务级进度（主代理维护）

> 以下内容不是新的设计权威。契约区在提交后冻结；此处记录进度、裁决和最终结果。父任务历史不在此处重写。

### 任务锚点

- 基线 HEAD：`e26b5b8d1ced009d16aefc922504f173d2ffbc91`
- 契约提交：`ddfa8aa880d422be8c8b9e4518a2281e07fca910`
- 执行分支：`pipeline-evidence-lifecycle-migration-continuation-1`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/pipeline-evidence-lifecycle-migration-continuation-1`

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-schema2-dispatch | PASS | `python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch -v` | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/executor-report.md` | Current schema 2 dispatch identity test passed. |
| acceptance-test-commit-history-guard | BLOCKED | `python -m unittest tests.test_git_checks.GitChecks.test_commit_history_evidence_path_guard -v` | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/blocker-facts.json` | Named history-guard test is absent; current tool only exposes working-tree scope check. |
| acceptance-test-finalization-current-command | BLOCKED | `python -m unittest tests.test_cli.CLITests.test_evidence_finalize_current_command_preserves_raw_on_block_and_is_idempotent -v` | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/blocker-facts.json` | Named current-command test is absent. |
| acceptance-test-evidence-verify-current-command | BLOCKED | `python -m unittest tests.test_cli.CLITests.test_evidence_verify_current_command_reports_machine_identity_and_finalization_state -v` | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/blocker-facts.json` | Named current-command test is absent; current evidence verify has no finalized phase option. |
| acceptance-test-no-historical-rewrite | PASS | `python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history -v` | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/executor-report.md` | Parent history preservation test passed. |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 2026-09-26 / 1 | Continuation task sheet committed and unique worktree verified | PASS | commit `ddfa8aa880d422be8c8b9e4518a2281e07fca910`; worktree identity at `ddfa8aa880d422be8c8b9e4518a2281e07fca910` | Executor validation |
| 2026-09-26 / 1 | Runtime preflight and schema 2 validation | PASS | runtime preflight JSON output; `task validate` exit 0 | Run frozen continuation tests |
| 2026-09-26 / 1 | Executor acceptance run | BLOCKED | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/executor-report.md`, `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/blocker-facts.json` | Current missing history/finalization command tests require implementation decision |
| 2026-09-26 / 1 | Independent review | BLOCKED | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/review-report.md` | Do not merge |
| 2026-09-26 / 1 | Main final check | BLOCKED | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/final-check.md` | Preserve worktree and report design decision |

### 设计变更与延续任务索引

- 父任务：`docs/tasks/pipeline-evidence-lifecycle-migration.md`（冻结 schema 1，状态 BLOCKED；不得改写）。
- 本任务是唯一 continuation-1；不得创建第二个同 ID 任务单或覆盖父任务历史。
- 无静默历史迁移；任何扩大范围的设计变化必须新建 continuation 并保留本任务现场。

### 最终结果

- 状态：BLOCKED
- 执行子代理：BLOCKED（schema 2 dispatch 与 continuation recovery 通过；冻结的 history/finalization/evidence-verify 精确验收用例不存在）
- 独立审查子代理：BLOCKED（复验发现当前工具面缺少三项冻结用例/命令能力）
- 主代理最终检查：BLOCKED
- 合并提交：-
- 合并后复验：未执行
- 遗留项：需要真实设计决策：是否在新的 continuation 中实现 commit history guard、finalized evidence CLI phase 与对应测试；本任务不伪造 PASS，父任务继续 BLOCKED。
