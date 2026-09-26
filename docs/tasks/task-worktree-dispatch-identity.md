# task-worktree-dispatch-identity：任务工作树与派发身份

<!-- Task ID: task-worktree-dispatch-identity -->

## 任务目标

在任务单冻结后建立唯一 worktree 和 dispatch identity 校验，绑定 task-id、branch、baseline HEAD、绝对路径与契约提交，阻止路径漂移、分支复用、孤立工作树和错误代理继续执行。本任务是 prerequisite，不代表用户功能完成。

## 任务类型

`prerequisite`

## 需求引用

- `implement-plan.md`：普通任务从主工作树创建、身份稳定和派发规则。
- `references/task-design.md`：标准 `.worktrees/<task-id>` 创建与核对。
- `SKILL.md`：executor/reviewer 使用主代理传入路径，不自行建第二 worktree。

## 允许修改

- `pipeline_tools/core.py`
- `pipeline_tools/planning.py`
- `pipeline_tools/__main__.py`
- `tests/test_worktree_dispatch_identity.py`
- `tests/test_git_checks.py`
- `references/**`
- `SKILL.md`
- `docs/tasks/task-worktree-dispatch-identity.md`

## 明确不改

- `implement-plan.md`、`IDEA.md`
- 既有任务单和 `.pipeline/**` 历史/metrics
- 产品业务代码、Git 历史、外部仓库
- 不自动修复冲突、不创建第二 worktree、不自动提交/合并

## 前置依赖

- `planning-run-lifecycle` 已合并。
- `task-plan-contract-consistency` 已合并。
- `.gitignore` 已包含 `/.worktrees/`。

## 设计与行为契约

[触发] 冻结任务单后请求创建或派发
→ [处理] 从主工作树创建标准 worktree，读取 Git list、root、branch、HEAD 和契约提交并比较
→ [状态] 写入 dispatch identity 与核对结果
→ [可见结果] 只有身份完全一致才可派发；冲突保留现场并 BLOCKED

- 创建前后必须核对 `git worktree list --porcelain`；目标必须是仓库根目录 `.worktrees/<task-id>`。
- 同 task-id 第二 worktree、已占用 branch、baseline 漂移、任务单/dispatch 路径不一致都拒绝。
- reviewer 使用同一 worktree，只读产品文件；不得自行创建 worktree。

## 七段链路

entry：`pipeline_tools/__main__.py`；interaction：dispatch JSON 与 Git 命令事实；application：`pipeline_tools/core.py`/`planning.py`；domain：task identity、branch、HEAD、path、role；persistence：`.worktrees/<task-id>` 与 `.pipeline/<task-id>/` dispatch 结果；readback：dispatch/result verify JSON；recovery：保留冲突现场并要求 reconcile。

## 外部操作绑定

- `worktree-create-identity`：创建并绑定唯一 worktree。
- `dispatch-identity-verify`：核对任务、分支、HEAD、路径和角色。
- `dispatch-path-scope-check`：阻止越界路径和第二 worktree。

## 环境前置

1. 主工作树根目录执行 `git rev-parse --show-toplevel`、`git status --short --branch`、`git worktree list --porcelain`。
2. 测试使用临时 Git 仓库和临时任务单；不得污染真实 `.worktrees`。

## 验收测试

### 验收测试1：标准创建与身份核对

- 触发：对已冻结任务单请求创建 dispatch。
- 断言：只创建 `.worktrees/<task-id>`，branch、HEAD、root 与 dispatch identity 完全匹配。
- 测试：`tests/test_worktree_dispatch_identity.py: WorktreeDispatchIdentityTests.test_create_and_verify_standard_worktree_identity`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_worktree_dispatch_identity.WorktreeDispatchIdentityTests.test_create_and_verify_standard_worktree_identity -v`
- 验收模式：Git 集成；证据等级：3；结果要求：退出码 0，list 前后证据可读。


- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试2：路径、分支和基线漂移拒绝

- 触发：传入仓库外路径、已占用分支、错误 HEAD 或复制 dispatch identity。
- 断言：拒绝派发，返回明确漂移类别，不创建第二 worktree。
- 测试：`tests/test_worktree_dispatch_identity.py: WorktreeDispatchIdentityTests.test_identity_drift_and_duplicate_worktree_are_blocked`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_worktree_dispatch_identity.WorktreeDispatchIdentityTests.test_identity_drift_and_duplicate_worktree_are_blocked -v`
- 验收模式：Git 安全边界；证据等级：3；结果要求：每个变体非零且既有注册项不变。


- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试3：角色路径与 scope 校验

- 触发：executor/reviewer 使用错误 worktree、写入禁止路径或试图创建第二 worktree。
- 断言：scope check 和 dispatch verify 阻止操作，报告包含 task-id、role、path。
- 测试：`tests/test_git_checks.py: GitChecksTests.test_dispatch_scope_requires_registered_task_worktree_and_role_identity`
- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecksTests.test_dispatch_scope_requires_registered_task_worktree_and_role_identity -v`
- 验收模式：机械检查；证据等级：2；结果要求：退出码 0 表示非法输入被正确拒绝。


- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。
### 验收测试4：回归

- 触发：全量测试、契约和 diff check。
- 断言：既有 Git 检查无回归。
- 测试：`tests/: complete regression suite`；命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`
- 验收模式：回归；证据等级：1；结果要求：退出码 0。

## 决策点

1. Git worktree 已存在但身份不明时停下，不猜测归属。
2. 需要使用仓库外路径、改写历史或强制删除 worktree 时停下。
3. 无法验证角色权限时保留现场并 BLOCKED。

---

## 任务级进度（主代理维护）

- 基线 HEAD：待提交契约前确认；契约提交：待完成
- 执行分支：`task-worktree-dispatch-identity`
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/task-worktree-dispatch-identity`

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-1 | 未开始 | - | - | - |
| acceptance-test-2 | 未开始 | - | - | - |
| acceptance-test-3 | 未开始 | - | - | - |
| acceptance-test-4 | 未开始 | - | - | - |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 1 | 任务单创建 | 未开始 | - | 契约提交后派发 executor |

### 设计变更与延续任务索引

- 无。

### 最终结果

- 状态：未开始；执行子代理：未开始；独立审查子代理：未开始；主代理最终检查：未开始；合并提交：-；合并后复验：未开始；遗留项：-

```pipeline-contract
{"schema":2,"task_id":"task-worktree-dispatch-identity","task_type":"prerequisite","implement_plan":{"path":"implement-plan.md"},"allowed_paths":["pipeline_tools/core.py","pipeline_tools/planning.py","pipeline_tools/__main__.py","tests/test_worktree_dispatch_identity.py","tests/test_git_checks.py","references/**","SKILL.md","docs/tasks/task-worktree-dispatch-identity.md"],"forbidden_paths":["implement-plan.md","IDEA.md","docs/tasks/** existing tasks",".pipeline/** existing history",".pipeline/metrics/**","**/*secret*","**/*token*"],"operations":[{"id":"worktree-create-identity","kind":"create","scope":"worktree","acceptance_tests":["acceptance-test-1"]},{"id":"dispatch-identity-verify","kind":"validate","scope":"dispatch","acceptance_tests":["acceptance-test-1","acceptance-test-2"]},{"id":"dispatch-path-scope-check","kind":"gate","scope":"dispatch","acceptance_tests":["acceptance-test-2","acceptance-test-3"]}],"chain":{"entry":["pipeline_tools/__main__.py"],"interaction":["pipeline_tools/__main__.py"],"application":["pipeline_tools/core.py","pipeline_tools/planning.py"],"domain":["pipeline_tools/core.py"],"persistence":[".worktrees/task-worktree-dispatch-identity/",".pipeline/task-worktree-dispatch-identity/"],"readback":["pipeline_tools/__main__.py"],"recovery":["pipeline_tools/core.py"]},"acceptance_tests":[{"id":"acceptance-test-1","evidence_level":3,"test_ref":"tests/test_worktree_dispatch_identity.py: WorktreeDispatchIdentityTests.test_create_and_verify_standard_worktree_identity","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_worktree_dispatch_identity.WorktreeDispatchIdentityTests.test_create_and_verify_standard_worktree_identity -v"},{"id":"acceptance-test-2","evidence_level":3,"test_ref":"tests/test_worktree_dispatch_identity.py: WorktreeDispatchIdentityTests.test_identity_drift_and_duplicate_worktree_are_blocked","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_worktree_dispatch_identity.WorktreeDispatchIdentityTests.test_identity_drift_and_duplicate_worktree_are_blocked -v"},{"id":"acceptance-test-3","evidence_level":2,"test_ref":"tests/test_git_checks.py: GitChecksTests.test_dispatch_scope_requires_registered_task_worktree_and_role_identity","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecksTests.test_dispatch_scope_requires_registered_task_worktree_and_role_identity -v"},{"id":"acceptance-test-4","evidence_level":1,"test_ref":"tests/: complete regression suite","command_ref":"PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v"}],"dependencies":["planning-run-lifecycle","task-plan-contract-consistency"],"required_evidence_levels":[1,2,3]}
```

## 生命周期记录

过程事件写入 `.pipeline/task-worktree-dispatch-identity/`，不改冻结契约。

- 命令：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v`（历史命令未重新核验）
- 证据等级：1
- 结果要求：重新执行后确认退出码与证据；本轮保持 UNVERIFIED。


## 任务身份

- 项目：pipeline
- 领域或阶段：历史任务结构迁移
- 用户结果或系统能力：保留原任务语义并符合当前结构校验。
- 执行 worktree 约定：UNVERIFIED（历史任务单未在本轮重新核验）
- 状态：UNVERIFIED


## 依赖与范围

### 前置条件

- 原任务单、当前 schema 和校验脚本。

### 允许修改

- 本任务单结构字段。

### 明确不改

- implement-plan.md、IDEA.md、产品代码、metrics 和历史验收结论。


## 事实、假设与待决

### 已确认事实

- 本轮仅依据 task validate 输出修复结构缺口。

### 未验证事实

- 历史验收结果、提交和证据新鲜度保持 UNVERIFIED。

### 禁止猜测

- 不把结构校验通过解释为产品或验收通过。


### 任务锚点

- 基线 HEAD：UNVERIFIED
- 契约提交：UNVERIFIED
- 执行分支：UNVERIFIED
- 执行 worktree：UNVERIFIED


### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| 验收测试1 | UNVERIFIED | - | - | 历史结果未重新核验 |

- 合并提交：UNVERIFIED
