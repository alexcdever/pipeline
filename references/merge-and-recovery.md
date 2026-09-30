# 恢复、合并与主工作树复验

## Worktree 路径与恢复

实现 worktree 的规范路径是 `<仓库根目录>/.worktrees/<task-id>`，由主代理在契约提交后用 `git worktree add` 创建；Git 会创建缺失的目标目录和父目录，不需要预先 `mkdir`。新任务证据的规范路径是 `<仓库根目录>/.pipeline/<task-id>`；工具首次访问旧 `.workflow/<task-id>` 时自动迁移到 `.pipeline/<task-id>`，并核对文件哈希、引用和工具测试。若 `.pipeline/` 已存在则报告冲突并停止，不覆盖、不双写。合并或恢复前必须以当前 `git worktree list --porcelain` 为准，核对任务单、dispatch、报告和实际路径一致。迁移完成后不能继续写入旧目录。路径冲突时先保留现场并 reconcile。

发现仓库同级 worktree、项目内第二个 worktree、路径漂移或同一 branch 被多个 worktree 占用时，先保留所有现场并 reconcile；不得删除、移动或重新创建来掩盖身份问题。失败恢复继续使用已核对的 worktree；如果必须更换路径，记录裁决并按 `derived` 任务处理（机器 ID/path 保留 `continuation`）。

## 后台运行与通知边界

长任务可后台运行，配合冻结检测、完成通知或自动恢复；这些机制不是工作流角色，不参与验收：

- 完成通知和退出码只证明生命周期变化，不作验收证据；
- 冻结或中断时保留 worktree、分支、日志和证据；
- 恢复以 `lifecycle resume/status/list/inspect` 的结构化状态为首要入口，再核对当前任务单、Git、`.pipeline/recovery-index.json` 和正式 evidence；活动进程和最新日志用于诊断，过程记录以 `.pipeline/<task-id>/` 的角色进度日志和阶段报告为准，不重猜用户目标；任务单冻结且不可变，任务状态不从项目级状态文件、通知或自然语言报告恢复。
- 无这些机制时主代理仍可前台执行同一生命周期。

## 冻结或失败恢复

1. 通过 lifecycle API/CLI 读取任务状态；需要写状态时仅由主代理使用 `role=main-agent` 接口。
2. 将原始日志、规划中间审计和 stage 文件优先保存在系统临时目录；项目仅保留 `.pipeline/recovery-index.json`，正式 evidence 仍写入 `.pipeline/<task-id>/`。
3. 保存 Git 状态、测试产物和报告。
4. 读最新业务活动和当前子进程，区分真冻结、等待测试、权限阻塞和正常退出。
5. 保留 worktree、branch、未提交实现和任务级证据。
6. 必要时建 checkpoint，不为"干净"删现场。
5. 契约需改变时先记录裁决，再开 `derived` 任务单和新证据目录——任务类型写 `derived`，机器 ID/path 保留 `continuation`。
6. 重新派发前用新运行日志，并把后台监督（若有）重新绑定当前任务；先读上一轮报告的失败分类，同类失败重派不超过一次，仍失败先缩小任务范围或升级为决策点，不无效重派。

退出码为零、通知到达或测试数量增加都不能绕过这一步。

## 合并前

正式 evidence 位于 `.pipeline/<task-id>/`，其提交生命周期与产品代码分开管理：pre-merge 先提交实现，再单独提交三份报告和三份机器结果 JSON（其中包含 pre-merge 版 `final-check.md` 与 `final-result.json`，以满足 gate）；merge 只合并已核对的产品提交与正式 evidence，不混入原始日志或 progress log。

合并输入必须是 `git worktree list` 确认过的 branch ref，不凭旧路径。检查：worktree 状态和冲突索引；`git diff --check`；三份报告和每条验收测试证据；验收台账与执行记录；改动路径和范围；分支含任务单冻结提交；无其他运行操作同一 worktree 或主分支。

先提交实现，再单独提交证据和状态文件；不用会吸收无关产物的全量暂存命令。

## 合并后

严格顺序是：`post-merge gate` → `finalization` → `finalized verify`。任何一步失败都必须保留现场，不得提前标记完成。

主工作树可能缺 worktree 中的依赖、原生模块或构建产物。按项目真实命令：检查依赖和生成物可加载；manifest/lockfile 改动时先用项目批准的冻结安装重新水合；重跑聚焦验收、全量测试、构建、post-build 测试、lint 和差异检查；检查合并提交文件路径无监督标记/临时文件/其他任务内容；验证主分支和远程状态再标已合并。

**合并后复验是硬要求，不是建议**：post-merge gate 需要 `final-check.md` 里至少一条 `exit_code == 0` 的命令证据，且该命令的 `cwd` 解析到主工作树根（`gate_check` 的 `_post_merge_reverified_in_main_worktree`）。只在任务 worktree 里跑过、或只在报告里写“主工作树已验证”而没有可解析的命令条目，都不算复验通过。

worktree 通过而主工作树失败 → 仍 FAIL/BLOCKED，不因合并已发生就改完成。post-merge 的 `final-check.md`、`final-result.json` 与 `finalization.json` 应作为独立的 post-merge evidence 提交，不能用 pre-merge 报告替代。`finalization.json` 必须可解析且绑定当前 task；缺失、旧 marker 或身份不一致时 reconcile 不能 PASS。schema 1 报告仅用于 legacy/unverified 查询，ready/merged/reconcile 最终 PASS 需要 schema 2 的 branch、worktree、HEAD 身份一致。events.jsonl 还必须从 `created` 开始、transition 可重放且终态与 lifecycle.json 一致。

## 状态恢复与并发护栏

每次后台间隙、会话切换或重启后，在写报告、提交、合并或派发前重新核对：当前任务单；主分支 HEAD；`git worktree list`；活动进程和最新日志；是否已有另一个主代理接管并完成任务。

任务已完成或 worktree 已被重新绑定时，旧上下文必须停止，不覆盖新证据。
