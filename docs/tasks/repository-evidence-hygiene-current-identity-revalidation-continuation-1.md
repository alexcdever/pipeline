# 任务：repository evidence hygiene current identity revalidation continuation-1

<!-- Task ID: repository-evidence-hygiene-current-identity-revalidation-continuation-1 -->
<!-- Contract section is frozen after commit. This continuation establishes current-main identity without rewriting historical evidence. -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "repository-evidence-hygiene-current-identity-revalidation-continuation-1",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": [
    "docs/tasks/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md",
    ".pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1/**"
  ],
  "forbidden_paths": [
    "docs/tasks/repository-evidence-hygiene.md",
    "docs/tasks/task-evidence-reconcile.md",
    ".pipeline/repository-evidence-hygiene-continuation-5/**",
    ".pipeline/metrics/**",
    "IDEA.md",
    "implement-plan.md"
  ],
  "operations": [
    {
      "id": "revalidate-current-main-evidence-identity",
      "kind": "repository-evidence-revalidation",
      "scope": "re-run repository hygiene and full validation from current main identity while preserving historical task evidence",
      "acceptance_tests": [
        "acceptance-test-current-identity",
        "acceptance-test-task-sheet-validation",
        "acceptance-test-repository-hygiene",
        "acceptance-test-full-regression",
        "acceptance-test-evidence-closure"
      ]
    }
  ],
  "chain": {
    "entry": ["current main HEAD, branch, worktree and canonical parent identity"],
    "interaction": ["task validation, repository hygiene checks and evidence lifecycle commands"],
    "application": ["current task-scoped executor/reviewer/final evidence"],
    "domain": ["canonical current-main identity and historical evidence preservation"],
    "persistence": [".pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1/**"],
    "readback": ["identity, validation, hygiene, regression, readiness, verify and gate results"],
    "recovery": ["retain repository-evidence-hygiene-continuation-5 evidence unchanged; classify drift or missing evidence as BLOCKED"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-current-identity",
      "evidence_level": 2,
      "test_ref": "git identity commands: current main branch, canonical parent and unique execution worktree",
      "command_ref": "git rev-parse --show-toplevel && git branch --show-current && git rev-parse HEAD && git worktree list --porcelain"
    },
    {
      "id": "acceptance-test-task-sheet-validation",
      "evidence_level": 1,
      "test_ref": "scripts/validate_task_sheet.py: every Markdown task sheet under docs/tasks",
      "command_ref": "for task in docs/tasks/*.md; do python scripts/validate_task_sheet.py \"$task\" || exit $?; done"
    },
    {
      "id": "acceptance-test-repository-hygiene",
      "evidence_level": 2,
      "test_ref": "pipeline_tools scope and task validation: current evidence is isolated and historical evidence remains untouched",
      "command_ref": "python -m pipeline_tools task validate docs/tasks/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md && python -m pipeline_tools scope check . --allowed 'docs/tasks/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md' --allowed '.pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1/**' --forbidden '.pipeline/metrics/**' --forbidden '.pipeline/repository-evidence-hygiene-continuation-5/**'"
    },
    {
      "id": "acceptance-test-full-regression",
      "evidence_level": 1,
      "test_ref": "tests/: complete regression suite",
      "command_ref": "python -m unittest discover -s tests -v"
    },
    {
      "id": "acceptance-test-evidence-closure",
      "evidence_level": 2,
      "test_ref": "pipeline_tools evidence lifecycle: readiness, verify and pre-merge gate for current task evidence",
      "command_ref": "python -m pipeline_tools --format json evidence readiness .pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1 --task-id repository-evidence-hygiene-current-identity-revalidation-continuation-1 && python -m pipeline_tools --format json evidence verify .pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1 --task-id repository-evidence-hygiene-current-identity-revalidation-continuation-1 --branch repository-evidence-hygiene-current-identity-revalidation-continuation-1 && python -m pipeline_tools --format json gate pre-merge .pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1 --task-id repository-evidence-hygiene-current-identity-revalidation-continuation-1 --branch repository-evidence-hygiene-current-identity-revalidation-continuation-1"
    }
  ],
  "dependencies": ["repository-evidence-hygiene-continuation-5"],
  "required_evidence_levels": [1, 2]
}
```

`pipeline-contract` is the frozen schema 2 contract for a current-main identity revalidation. The canonical parent is `repository-evidence-hygiene-continuation-5`; its task sheet and evidence are historical inputs and must remain unchanged.

## 任务身份

- 项目：pipeline
- 领域或阶段：repository evidence hygiene / current-main identity revalidation
- 用户结果或系统能力：在当前 `main` 身份重新运行卫生检查与完整 evidence 闭环，生成只属于本 continuation 的 executor、reviewer、final evidence，同时保留旧 task 的证据不变。
- canonical parent：`repository-evidence-hygiene-continuation-5`，任务单 `docs/tasks/repository-evidence-hygiene.md`，历史证据 `.pipeline/repository-evidence-hygiene-continuation-5/`
- 历史证据策略：旧 task sheet、旧 branch/worktree 绑定和旧 evidence 全部保留，不修改、不搬运、不覆盖、不重新归属。
- 执行 worktree 约定：`<仓库根目录>/.worktrees/repository-evidence-hygiene-current-identity-revalidation-continuation-1`；由主代理在契约提交后创建唯一 worktree
- 状态：未开始

## 依赖与范围

### 前置条件

- 当前主工作树是 canonical `main`，其 HEAD、branch、worktree 由本轮直接命令确认。
- `repository-evidence-hygiene-continuation-5` 是历史 canonical parent；其证据只作保留和对照，不作本轮 PASS 证据。
- Python 运行时和 `pipeline_tools` 可执行；metrics 按用户要求忽略，不纳入本轮证据结论。

### 允许修改

- `docs/tasks/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md` 的生命周期区。
- `.pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1/**` 的本轮 evidence。

### 明确不改

- `docs/tasks/repository-evidence-hygiene.md` 和所有历史任务单、旧 branch/worktree、旧证据。
- `.pipeline/repository-evidence-hygiene-continuation-5/**`，不得改写其身份、报告或结果。
- `.pipeline/metrics/**`；metrics 忽略，不删除、不纳入验收。
- `IDEA.md`、`implement-plan.md` 和任何产品代码。

## 事实、假设与待决

### 已确认事实

- 用户指定当前实际 task 为 `repository-evidence-hygiene-continuation-5`，但其历史 evidence 绑定旧 branch/worktree；本 continuation 重新建立当前 main 身份闭环。
- 当前 task 必须使用新 task-id、新 evidence 目录和当前 main 创建的唯一 execution worktree。

### 未验证事实

- 当前 main HEAD、契约提交、执行 branch/worktree、测试和 evidence lifecycle 结果，均待本轮直接命令确认。
- 历史 evidence 未被本轮改动，待对照哈希或 Git diff 确认。

### 禁止猜测

- 不把旧 evidence 的 PASS、旧 branch 或旧 worktree 迁移成当前身份。
- 不把 metrics 文件或指标结果当作任务验收证据。
- 不因发现身份、范围或环境冲突而静默改写契约；保留现场并标记 BLOCKED。

## 设计与行为契约

[触发] 从当前主工作树冻结本 continuation 并创建唯一执行 worktree
→ [处理] 在该 worktree 重新运行身份、任务单、卫生、全量回归和 evidence lifecycle 检查
→ [状态] executor、reviewer、final evidence 均绑定本 task-id、当前 branch、worktree 和本轮 HEAD
→ [可见结果] 证据闭环通过并合并回当前 main；历史 parent evidence 保持原样

- readiness 必须先于 verify，verify 必须先于 gate。
- 当前 task-id、branch、worktree、HEAD 和 evidence references 必须一致。
- reviewer 独立复验，不修改产品代码或历史 evidence。
- 任一身份漂移、历史 evidence 变化、范围越界、命令失败或证据缺失均为 BLOCKED/FAIL，不得改写为 PASS。

## 环境前置

1. 从主工作树冻结并提交本任务单，然后以契约提交为基线创建唯一 `.worktrees/<task-id>`。
2. 在 execution worktree 核对 `git rev-parse --show-toplevel`、`git branch --show-current`、`git rev-parse HEAD` 和 `git worktree list --porcelain`。
3. 运行任务单校验、卫生检查、完整回归和 evidence readiness → verify → gate；metrics 忽略。

## 验收测试

### 验收测试1：当前 main canonical identity

- 触发：从当前 main 冻结契约并创建 continuation execution worktree。
- 断言：main 基线、契约提交、执行 branch/worktree 和 task evidence 目录均可追溯，且不复用旧 branch/worktree。
- 测试：`git identity commands: current main branch, canonical parent and unique execution worktree`
- 命令：`git rev-parse --show-toplevel && git branch --show-current && git rev-parse HEAD && git worktree list --porcelain`
- 验收模式：其他（身份核对）
- 证据等级：2
- 结果要求：退出码 0；记录绝对路径、branch、HEAD，并证明旧 evidence 未被修改。

### 验收测试2：所有任务单 validate

- 触发：从 execution worktree 遍历 `docs/tasks/*.md`。
- 断言：所有 task sheets 结构有效，当前 continuation schema 为 2，canonical parent 和历史保留约束明确。
- 测试：`scripts/validate_task_sheet.py: validate every Markdown task sheet under docs/tasks`
- 命令：`for task in docs/tasks/*.md; do python scripts/validate_task_sheet.py "$task" || exit $?; done`
- 验收模式：其他（机械结构校验）
- 证据等级：1
- 结果要求：每个任务单退出码 0；不修改历史任务单。

### 验收测试3：当前任务 repository hygiene

- 触发：对当前 continuation 的 task sheet 和 evidence scope 运行工具检查。
- 断言：当前 evidence 只在当前目录；旧 continuation-5 evidence、IDEA、implement-plan 和 metrics 均保持禁止/忽略边界。
- 测试：`pipeline_tools task validate and scope check: current task evidence isolation`
- 命令：`python -m pipeline_tools task validate docs/tasks/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md && python -m pipeline_tools scope check . --allowed 'docs/tasks/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md' --allowed '.pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1/**' --forbidden '.pipeline/metrics/**' --forbidden '.pipeline/repository-evidence-hygiene-continuation-5/**'`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；范围无漂移，历史 evidence 快照不变。

### 验收测试4：完整回归

- 触发：在当前 execution worktree 运行项目测试。
- 断言：所有既有 tests 通过，无失败或错误。
- 测试：`tests/: complete regression suite`
- 命令：`python -m unittest discover -s tests -v`
- 验收模式：集成
- 证据等级：1
- 结果要求：退出码 0；完整输出和测试计数记录在 executor/reviewer evidence。

### 验收测试5：当前身份 evidence closure

- 触发：当前 task 的 executor、reviewer 和 final evidence 已写入当前 evidence 目录。
- 断言：readiness 先于 verify；verify 和 pre-merge gate 均确认 task-id、branch、worktree、HEAD、报告状态和引用一致；合并后再运行 post-merge gate/复验。
- 测试：`pipeline_tools evidence readiness, evidence verify and gate pre/post-merge`
- 命令：`python -m pipeline_tools --format json evidence readiness .pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1 --task-id repository-evidence-hygiene-current-identity-revalidation-continuation-1 && python -m pipeline_tools --format json evidence verify .pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1 --task-id repository-evidence-hygiene-current-identity-revalidation-continuation-1 --branch repository-evidence-hygiene-current-identity-revalidation-continuation-1 && python -m pipeline_tools --format json gate pre-merge .pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1 --task-id repository-evidence-hygiene-current-identity-revalidation-continuation-1 --branch repository-evidence-hygiene-current-identity-revalidation-continuation-1`
- 验收模式：集成
- 证据等级：2
- 结果要求：所有当前角色报告 PASS，命令退出码 0，pre/post-merge gate 通过；历史 evidence 不参与当前 gate。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 当前 main、契约提交、execution worktree 或 task evidence 身份漂移。
2. 任何历史任务单、旧 branch/worktree 或旧 evidence 需要修改才能通过。
3. metrics 进入产品证据或 scope 结果，或工具无法按用户要求忽略 metrics。
4. readiness、verify、gate 无法在当前 identity 下形成闭环。

---

## 任务级进度（主代理维护）

> 契约区在提交后冻结；以下仅记录本轮直接证据和生命周期状态。

### 任务锚点

- 基线 HEAD：UNVERIFIED
- 契约提交：UNVERIFIED
- 执行分支：repository-evidence-hygiene-current-identity-revalidation-continuation-1
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/repository-evidence-hygiene-current-identity-revalidation-continuation-1`

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-current-identity | UNVERIFIED | - | - | 待契约提交和 worktree 核对 |
| acceptance-test-task-sheet-validation | UNVERIFIED | - | - | 待执行 |
| acceptance-test-repository-hygiene | UNVERIFIED | - | - | metrics 忽略 |
| acceptance-test-full-regression | UNVERIFIED | - | - | 待执行 |
| acceptance-test-evidence-closure | UNVERIFIED | - | - | readiness → verify → gate 待执行 |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 创建轮 | 新增当前-main identity continuation task sheet | UNVERIFIED | 本文件 | 提交契约后创建唯一 worktree |

### 设计变更与延续任务索引

- canonical parent：`repository-evidence-hygiene-continuation-5`（历史任务单 `docs/tasks/repository-evidence-hygiene.md`）
- 历史 evidence：`.pipeline/repository-evidence-hygiene-continuation-5/`，保留原样，不作为当前证据
- 本任务为当前身份复验 continuation-1；如设计仍需变化，建立新的 continuation，不覆盖本任务或 parent 历史。

### 最终结果

- 状态：未开始
- 执行子代理：未开始
- 独立审查子代理：未开始
- 主代理最终检查：未开始
- 合并提交：-
- 合并后复验：未开始
- 遗留项：-

## 外部操作

- 按用户要求执行本地 commit、创建 worktree、生成 evidence、合并回 main；不推送、不修改外部服务。
- 不修改、移动、删除或重归属 canonical parent 的历史 task sheet、branch/worktree 或 evidence。
- metrics 忽略，不纳入本任务验收。
