# derived-task-dispatch-recovery 状态记录

- 状态：暂停，保留现场；未提交产品代码。
- worktree：`D:/Projects/Skills/pipeline/.worktrees/derived-task-dispatch-recovery`
- branch：`derived-task-dispatch-recovery`
- HEAD：`244f453db77ec9990f763208d29feecd9e5db2cf`
- 自动 metrics：已使用 `DISABLE_AUTO_METRICS=1` / `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`。

## 当前未提交实现

- `pipeline_tools/core.py`：新增 `create_derived_dispatch`，涉及派生任务父提交校验、子 worktree/task sheet/evidence identity 创建。
- `pipeline_tools/__main__.py`：新增 `dispatch derived-create` CLI。
- `tests/test_derived_task_dispatch_recovery.py`：新增 3 个派生任务/恢复/continuation 测试。
- 本状态记录：`.pipeline/derived-task-dispatch-recovery/status-record.md`。

## 已运行测试

- 聚焦：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_derived_task_dispatch_recovery -v` — 3 tests，OK。
- 既有 CLI/worktree：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_cli tests.test_worktree_dispatch_identity -v` — 42 tests，OK。
- 全量：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests -v` — 119 tests，OK。
- 语法检查：`python -m py_compile pipeline_tools/core.py pipeline_tools/__main__.py` — OK。
- `git diff --check` — OK。

## 安全并行边界

当前实现不能与另一个同时修改共享核心模块的任务安全并行。共享文件/符号包括：

- `pipeline_tools/core.py`：`git`、证据/身份校验基础设施及新增 `create_derived_dispatch` 所在核心 dispatch 区域。
- `pipeline_tools/__main__.py`：统一 CLI parser、dispatch 路由、自动 metrics/命令生命周期入口。
- `tests/test_cli.py` 与 dispatch/worktree 测试链路：共享 CLI dispatch 行为与临时 Git worktree 断言。

因此停止扩大实现范围，不创建第二 worktree，不提交当前产品代码。

## 需要主代理裁决/后续拆分

1. 重新拆分共享核心模块，避免两个任务同时修改 `core.py` / `__main__.py`；可将派生任务 API、CLI 接线和测试按不重叠切片串行派发。
2. 若设计需要改变父子任务契约、恢复分类或证据 identity，建立新的 `continuation` 任务单，不修改本冻结任务单或父任务历史。
3. 恢复执行前重新核对本 worktree、branch、HEAD、未提交 diff 与 evidence identity；失败现场和当前未提交实现均保留。
