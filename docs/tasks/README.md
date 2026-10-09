# docs/tasks：在途工作清单

本目录只放**进行中或待派发**的任务单。

任务一旦进入终态，它的单子就离开 `docs/tasks/`，落到两个终态位置之一：

- 有证据目录时：`.pipeline/<task-id>/<task-id>.md`（与它自己的证据放在一起）；
- 没有证据目录时：`.pipeline/archive/<task-id>.md`（归档区，即 `archive` 是任务单隔离区，不是任务证据目录）。

三个位置由统一解析器按固定顺序查找——`docs/tasks/<task-id>.md` → `.pipeline/<task-id>/<task-id>.md` → `.pipeline/archive/<task-id>.md`——并且 fail-closed：同一个 id 出现在多个位置、或三处都找不到时都会报错，而不是静默取第一个候选。

因此，判断一个任务是否在途，看单子在哪：在本目录里就是在途，在证据目录或归档区里就是已终态。相应地，`planning preflight` 的 `task_scenes` 只把本目录下的单子算作「进行中的单子」——`sheets_without_worktree` 与 `uncommitted_sheets` 只读本目录，已关闭的任务不会被报成「被中断的进行中工作」。

本文件（`README.md`）是目录说明，不是任务单。
