# 历史说明单：repository evidence hygiene continuation-5

<!-- Task ID: repository-evidence-hygiene-continuation-5 -->

这是一份**历史说明单**，不是一份完整的 schema 4 任务契约。它存在的原因只有一个：让本证据目录在任务单的三位置解析（`docs/tasks/<task-id>.md` → `.pipeline/<task-id>/<task-id>.md` → `.pipeline/archive/<task-id>.md`）下，能按文件名 `<task-id>.md` 被找到，从而不再被判为「遗留证据目录」（`task_scenes.leftover_evidence`）。

## 来历

- 该任务是一次修复任务的延续（continuation），承接 `repository-evidence-hygiene` 与 `task-evidence-reconcile` 的历史，工作在 `.pipeline/repository-evidence-hygiene-continuation-5/` 下交付。
- 它的任务单当年被**错名存放**为 `docs/tasks/repository-evidence-hygiene.md`：文件名对应的是父任务的 id，而文件内的契约 `task_id` 实际是 `repository-evidence-hygiene-continuation-5`。
- 因此按文件名机械判据，`repository-evidence-hygiene` 没有自己的证据目录；而真正属于本目录的单子从未以 `repository-evidence-hygiene-continuation-5.md` 的名字出现在 `docs/tasks/`。

## 现状

- 本目录保留集（`executor-report.md`、`review-report.md`、`final-check.md`、`executor-result.json`、`reviewer-result.json`、`final-result.json`、`finalization.json`）原样不动；本说明单不进入 `retained_sha256` 快照，也不改变任何已关闭标记。
- 错名的那份单子按机械判据被移入归档：`.pipeline/archive/repository-evidence-hygiene.md`，内容逐字不变。
- 历史归档迁移任务 `historical-archival-migration` 未更改本目录内任何既有文件的内容，也未改动任何 `finalization.json` 或保留集文件。
