# implement-plan-completeness-repair-continuation-1 evidence revalidation continuation-1

<!-- Task ID: implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 -->
<!-- Contract section is frozen after commit. This continuation re-establishes current-main evidence identity for the parent task without rewriting any merged parent history. -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": [
    "docs/tasks/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md",
    ".pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/**",
    ".gitignore"
  ],
  "forbidden_paths": [
    "docs/tasks/implement-plan-completeness-repair-continuation-1.md",
    ".pipeline/implement-plan-completeness-repair-continuation-1/**",
    ".pipeline/metrics/**",
    "pipeline_tools/**",
    "tests/**",
    "implement-plan.md",
    "IDEA.md"
  ],
  "operations": [
    {
      "id": "revalidate-current-main-evidence-identity",
      "kind": "evidence-revalidation",
      "scope": "re-run current-main identity, contract, regression and evidence lifecycle checks for the parent completeness repair, binding fresh executor/reviewer/final evidence to current main HEAD",
      "acceptance_tests": ["acceptance-test-1", "acceptance-test-2", "acceptance-test-3", "acceptance-test-4", "acceptance-test-5"]
    },
    {
      "id": "repair-stale-full-test-log-hygiene",
      "kind": "repository-hygiene-repair",
      "scope": "keep the untracked stale full_test.log out of git status and scope evaluation without deleting data or touching metrics",
      "acceptance_tests": ["acceptance-test-6"]
    }
  ],
  "chain": {
    "entry": ["docs/tasks/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md"],
    "interaction": ["pipeline-tools task/lifecycle/evidence/gate commands"],
    "application": ["current main HEAD, unique execution worktree and frozen contract identity"],
    "domain": ["current-main evidence identity and immutable historical parent evidence"],
    "persistence": [".pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/**"],
    "readback": ["executor-report.md", "review-report.md", "final-check.md", "final-result.json", "finalization.json"],
    "recovery": ["historical parent branch or product_head drift is recorded as a historical fact and never rewritten as current evidence"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 2,
      "test_ref": "git identity commands: current main HEAD, canonical parent and unique execution worktree",
      "command_ref": "git rev-parse --show-toplevel && git branch --show-current && git rev-parse HEAD && git worktree list --porcelain"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 1,
      "test_ref": "scripts/validate_task_sheet.py: this continuation task sheet and all Markdown task sheets under docs/tasks",
      "command_ref": "python scripts/validate_task_sheet.py docs/tasks/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md && python -m pipeline_tools --format json task validate docs/tasks/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 2,
      "test_ref": "pipeline_tools result/freshness: current evidence roles bound to this task-id, branch and current HEAD",
      "command_ref": "python -m pipeline_tools --format json result verify .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/executor-result.json --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --role executor && python -m pipeline_tools --format json result verify .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/reviewer-result.json --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --role reviewer"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 1,
      "test_ref": "tests/: complete regression suite on the current-main execution worktree",
      "command_ref": "python -m unittest discover -s tests -v"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 2,
      "test_ref": "pipeline_tools evidence lifecycle: readiness, verify and merge gate for this continuation evidence",
      "command_ref": "python -m pipeline_tools --format json evidence readiness .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 && python -m pipeline_tools --format json evidence verify .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --branch implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 && python -m pipeline_tools --format json gate pre-merge .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --branch implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 1,
      "test_ref": "repository hygiene: stale untracked full_test.log is excluded by .gitignore without deletion",
      "command_ref": "git check-ignore -v full_test.log && git status --short"
    }
  ],
  "dependencies": ["implement-plan-completeness-repair-continuation-1 (merged parent; immutable)"],
  "required_evidence_levels": [1, 2]
}
```

`pipeline-contract` is the frozen schema 2 contract for a current-main identity revalidation of the merged parent `implement-plan-completeness-repair-continuation-1`. The parent task sheet, its branch, its reports and its evidence directory are historical and must remain byte-for-byte unchanged.

## 任务身份

- 项目：programing-pipeline / pipeline-tools
- 领域或阶段：merged parent evidence closure revalidation on current `main`
- 用户结果或系统能力：在绑定当前 `main` HEAD 的唯一 worktree 上，为父任务补齐当前身份可追溯的 executor、reviewer、final-check、final-result、finalization 证据闭环；父任务已合并历史的身份漂移、缺失 final-result/finalization 只记录、不改写。
- canonical parent：`implement-plan-completeness-repair-continuation-1`（任务单 `docs/tasks/implement-plan-completeness-repair-continuation-1.md`，证据 `.pipeline/implement-plan-completeness-repair-continuation-1/`）
- 历史证据策略：父任务单、父分支/worktree、父 reports 与父证据全部保留原样，不修改、不搬运、不覆盖、不重新归属。
- 执行 worktree 约定：`<仓库根目录>/.worktrees/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1`，由主代理在契约提交后用 `git worktree add` 创建唯一 worktree
- 状态：已完成并已合并，主工作树复验通过

## 依赖与范围

### 前置条件

- 当前主工作树是 `main`，其 HEAD、branch 与 worktree 由本轮直接命令确认。
- 父任务已合并：父任务单记录 `已完成并已合并`，父证据目录只含 `executor-report.md`、`executor-result.json`、`review-report.md`、`reviewer-result.json`、`final-check.md`；缺少 `final-result.json` 与 `finalization.json`。
- 父证据身份漂移已确认存在：父 `reviewer-result.json` 的 `identity.head` 为 `feb1a3d...`、`identity.product_implementation_head` 为短 SHA `9b170b1`；父 `executor-result.json` 的 `identity.product_head` 为 `54425a2...`；二者均不等于当前 `main` HEAD，且父 branch 与当前 `main` 不一致。该漂移只作历史事实记录。
- Python 运行时与 `pipeline_tools` 可执行；metrics 按用户要求忽略，不纳入本轮证据结论。

### 允许修改

- `docs/tasks/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md` 的生命周期区。
- `.pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/**` 的本轮证据。
- `.gitignore`：仅新增忽略规则，使未跟踪的陈旧 `full_test.log` 不再进入 git status 与 scope 评估。

### 明确不改

- `docs/tasks/implement-plan-completeness-repair-continuation-1.md` 与所有历史任务单、旧 branch/worktree、旧 reports、旧证据、旧 final-check。
- `.pipeline/implement-plan-completeness-repair-continuation-1/**`：不得写入、不得补齐、不得改写其身份或结果。
- `.pipeline/metrics/**`：忽略，不删除、不纳入验收。
- `pipeline_tools/**`、`tests/**`、`implement-plan.md`、`IDEA.md` 与任何产品实现代码。

## 事实、假设与待决

### 已确认事实

- 当前 `main` HEAD 为 `f8aa3795961a28a2fd0ed4c84192e605b19f9f21`，分支 `main...origin/main [ahead 210]`。
- 父任务证据目录缺少 `final-result.json` 与 `finalization.json`；已 finalize 的其他任务证据目录（如 `.pipeline/acceptance-id-and-template-compliance/`）含该两份文件。
- `full_test.log` 未被 git 跟踪，且不在当前 `.gitignore` 中，因此出现在 `git status --short` 的未跟踪列表里。
- `.gitignore` 已包含 `/.worktrees/`，实现 worktree 不会污染主树状态。
- 父任务 worktree `.worktrees/implement-plan-completeness-repair-continuation-1` 仍存在并指向 `0641020...`，与当前 `main` HEAD 不同。

### 未验证事实

- 当前 `main` HEAD 下完整 unittest 回归是否全绿，待本轮 worktree 直接运行确认。
- 本轮 evidence lifecycle（readiness → verify → gate）在当前身份下是否形成闭环，待证据写入后直接确认。
- 父证据身份漂移是否被父任务单已记录，需以只读方式核对父任务单文本确认。

### 禁止猜测

- 不把父任务已合并的 PASS、旧 branch、旧 worktree 或旧 reports 迁移为本轮当前身份证据。
- 不把 metrics 文件或指标结果当作任务验收证据。
- 不因发现身份、范围或环境冲突而静默改写契约或父历史；保留现场并标记 BLOCKED。

## 设计与行为契约

[触发] 从当前 `main` 冻结本 continuation 并创建唯一执行 worktree
→ [处理] 在该 worktree 重新运行身份、任务单、回归与 evidence lifecycle 检查，并生成当前身份的五份证据文件
→ [状态] executor、reviewer、final-check、final-result、finalization 均绑定本 task-id、当前 branch、worktree 与本轮 HEAD；父证据保持原样
→ [可见结果] 证据闭环通过并合并回当前 `main`；陈旧 `full_test.log` 不再进入 git status

- readiness 必须先于 verify，verify 必须先于 gate。
- 当前 task-id、branch、worktree、HEAD 与 evidence references 必须一致。
- reviewer 独立复验，不修改产品代码或父历史证据。
- 任一身份漂移、父证据变化、范围越界、命令失败或证据缺失均为 BLOCKED/FAIL，不得改写为 PASS。

## 环境前置

1. 在仓库根目录运行 `python -m pipeline_tools --format json task validate docs/tasks/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md`，任务单必须先通过。
2. 从主工作树冻结并提交本任务单，然后以契约提交为基线创建唯一 `.worktrees/<task-id>`。
3. 在 execution worktree 核对 `git rev-parse --show-toplevel`、`git branch --show-current`、`git rev-parse HEAD` 和 `git worktree list --porcelain`。
4. 运行任务单校验、完整回归和 evidence readiness → verify → gate；metrics 忽略。

## 验收测试

### 验收测试1：当前 main canonical identity

- 触发：从当前 main 冻结契约并创建 continuation execution worktree。
- 断言：main 基线、契约提交、执行 branch/worktree 和 task evidence 目录均可追溯，且不复用父 branch/worktree。
- 测试：`git identity commands: current main HEAD, canonical parent and unique execution worktree`
- 命令：`git rev-parse --show-toplevel && git branch --show-current && git rev-parse HEAD && git worktree list --porcelain`
- 验收模式：其他（身份核对）
- 证据等级：2
- 结果要求：退出码 0；记录绝对路径、branch、HEAD，并证明父证据目录未被修改。

### 验收测试2：任务单 schema2 结构有效

- 触发：在仓库根目录对本任务单运行静态结构校验与机器合同校验。
- 断言：必需标题、锚点字段、验收台账与合并提交字段齐全；`pipeline-contract` 唯一且为 schema 2。
- 测试：`scripts/validate_task_sheet.py: this continuation task sheet`
- 命令：`python scripts/validate_task_sheet.py docs/tasks/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md && python -m pipeline_tools --format json task validate docs/tasks/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md`
- 验收模式：其他（机械结构校验）
- 证据等级：1
- 结果要求：两条命令退出码均为 0。

### 验收测试3：当前身份 executor/reviewer 结果新鲜度

- 触发：executor 与独立 reviewer 在本 worktree 生成结果文件后运行机械校验。
- 断言：两份结果文件的 task-id、role、worktree、branch 与本轮一致，且可被 freshness 识别为当前证据。
- 测试：`pipeline_tools result/freshness: current evidence roles bound to this task-id and HEAD`
- 命令：`python -m pipeline_tools --format json result verify .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/executor-result.json --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --role executor && python -m pipeline_tools --format json result verify .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/reviewer-result.json --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --role reviewer`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；任何身份不一致必须报 BLOCKED，不得改写为 PASS。

### 验收测试4：当前 main 完整回归

- 触发：在当前 execution worktree 运行项目完整测试套件。
- 断言：所有既有 tests 通过，无失败或错误。
- 测试：`tests/: complete regression suite on the current-main execution worktree`
- 命令：`python -m unittest discover -s tests -v`
- 验收模式：集成
- 证据等级：1
- 结果要求：退出码 0；实际测试数量与完整命令记录在 executor/reviewer 证据中。

### 验收测试5：当前身份 evidence closure

- 触发：本任务 executor、reviewer、final-check、final-result 与 finalization 均已写入当前证据目录。
- 断言：readiness 先于 verify；verify 与 pre-merge gate 确认 task-id、branch、worktree、HEAD、报告状态和引用一致；合并后再运行 post-merge 复验。
- 测试：`pipeline_tools evidence readiness, evidence verify and gate`
- 命令：`python -m pipeline_tools --format json evidence readiness .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 && python -m pipeline_tools --format json evidence verify .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --branch implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 && python -m pipeline_tools --format json gate pre-merge .pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --task-id implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1 --branch implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1`
- 验收模式：集成
- 证据等级：2
- 结果要求：所有当前角色报告 PASS，命令退出码 0，pre-merge gate 通过；父证据不参与当前 gate。

### 验收测试6：full_test.log 陈旧卫生

- 触发：主工作树与 execution worktree 存在未跟踪的陈旧 `full_test.log`。
- 断言：`.gitignore` 新增忽略规则后 `full_test.log` 被识别为忽略文件，不再出现在 `git status --short` 未跟踪列表；文件本身不被删除，metrics 不受影响。
- 测试：`repository hygiene: stale untracked full_test.log is excluded by .gitignore without deletion`
- 命令：`git check-ignore -v full_test.log && git status --short`
- 验收模式：其他（仓库卫生）
- 证据等级：1
- 结果要求：`git check-ignore` 退出码 0 并输出匹配规则；`git status --short` 不再列出 `full_test.log`。

## 决策点

出现以下情况时，保留 worktree 并报告给主代理，不得静默改变契约：

1. 当前 `main`、契约提交、execution worktree 或 task evidence 身份漂移。
2. 任何父任务单、旧 branch/worktree 或旧证据需要修改才能通过。
3. metrics 进入产品证据或 scope 结果，或工具无法按用户要求忽略 metrics。
4. 陈旧 `full_test.log` 需要删除文件本体（而非仅加入忽略规则）才能通过卫生检查。
5. readiness、verify、gate 无法在当前 identity 下形成闭环。

---

## 任务级进度（主代理维护）

> 契约区在提交后冻结；以下仅记录本轮直接证据和生命周期状态。

### 任务锚点

- 基线 HEAD：`f8aa3795961a28a2fd0ed4c84192e605b19f9f21`
- 契约提交：`49ae00cb60b7e96808161cebd88ecd3d93acfb56`
- 产品实现提交：`0e188fedd60c04c1964fcfba68a6c23a1038c156`
- 证据提交：`41ffd69eae9ad0853ceec0906e09ca9989c83d58`
- 合并提交（main）：`cc7f6d47026bcb73c683cf45d6c63586bedb0866`
- 执行分支：`implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1`

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| 验收测试1 | PASS | `git rev-parse --show-toplevel && git branch --show-current && git rev-parse HEAD && git worktree list --porcelain` | `executor-report.md` | 当前 main 基线与唯一 worktree 已核对 |
| 验收测试2 | PASS | `python scripts/validate_task_sheet.py ... && python -m pipeline_tools task validate ...` | `executor-report.md` | schema2 合同与结构有效 |
| 验收测试3 | PASS | `pipeline_tools result verify` executor + reviewer | `final-check.md` | 两角色结果均 pass |
| 验收测试4 | PASS | `python -m unittest discover -s tests -v` | `executor-report.md`; `review-report.md` | 168 tests OK |
| 验收测试5 | PASS | `evidence readiness/verify` + `gate pre-merge/post-merge` | `final-check.md` | 当前身份闭环 PASS |
| 验收测试6 | PASS | `git check-ignore -v full_test.log && git status --short` | `executor-report.md` | 陈旧日志被忽略且未删除 |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 创建轮 | schema 2 current-main revalidation continuation task sheet committed | PASS | commit `49ae00c` | 创建唯一执行 worktree |
| 执行轮1 | executor 身份、任务单、全量回归、full_test.log 卫生 | PASS | `executor-report.md`, `executor-result.json` | 独立审查 |
| 审查轮1 | reviewer 独立重跑校验与全量回归 | PASS | `review-report.md`, `reviewer-result.json` | 主代理终检 |
| 终检轮1 | readiness → verify → result verify → pre-merge gate | PASS | `final-check.md`, `final-result.json`, `finalization.json` | 合并回 main |
| 合并轮 | `git merge --no-ff` 到 main | PASS | merge commit `cc7f6d4` | 主工作树复验 |
| 复验轮 | main 全量回归、task validate、post-merge gate、卫生检查 | PASS | 168 tests OK；post-merge gate PASS；`full_test.log` 被忽略 | 完成 |

### 设计变更与延续任务索引

- canonical parent：`implement-plan-completeness-repair-continuation-1`（历史任务单 `docs/tasks/implement-plan-completeness-repair-continuation-1.md`）
- 历史证据：`.pipeline/implement-plan-completeness-repair-continuation-1/`，保留原样，不作为当前证据；其缺失 `final-result.json`/`finalization.json` 与身份漂移仅作历史事实记录。
- 本任务为 current-main 证据复验 continuation-1；如设计仍需变化，建立新的 continuation，不覆盖本任务或 parent 历史。

### 最终结果

- 状态：MERGED（当前 main 身份证据闭环 PASS）
- 执行子代理：PASS；`.pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/executor-report.md`
- 独立审查子代理：PASS；`.pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/review-report.md`
- 主代理最终检查：PASS；`.pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/final-check.md`
- 合并提交：`cc7f6d47026bcb73c683cf45d6c63586bedb0866`
- 合并后复验：PASS；主树 `python -m unittest discover -s tests -v`（168 tests OK）、task validate、post-merge gate、`full_test.log` 忽略检查均通过
- 遗留项：父任务 `implement-plan-completeness-repair-continuation-1` 的历史身份漂移（reviewer/product head 非当前 main）与缺失 `final-result.json`/`finalization.json` 保留为历史事实，不在本任务改写；metrics 按用户要求忽略