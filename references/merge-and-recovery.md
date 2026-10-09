# 恢复、合并与主工作树复验

## Worktree 路径与恢复

实现 worktree 的规范路径是 `<仓库根目录>/.worktrees/<task-id>`，由主代理在契约提交后用 `git worktree add` 创建；Git 会创建缺失的目标目录和父目录，不需要预先 `mkdir`。新任务证据的规范路径是 `<仓库根目录>/.pipeline/<task-id>`；工具首次访问旧 `.workflow/<task-id>` 时自动迁移到 `.pipeline/<task-id>`，并核对文件哈希、引用和工具测试。若 `.pipeline/` 已存在则报告冲突并停止，不覆盖、不双写。合并或恢复前必须以当前 `git worktree list --porcelain` 为准，核对任务单、dispatch、报告和实际路径一致。迁移完成后不能继续写入旧目录。路径冲突时先保留现场并 reconcile。

发现仓库同级 worktree、项目内第二个 worktree、路径漂移或同一 branch 被多个 worktree 占用时，先保留所有现场并 reconcile；不得删除、移动或重新创建来掩盖身份问题。失败恢复继续使用已核对的 worktree；如果必须更换路径，记录裁决并按 `derived` 任务处理（机器 ID/path 保留 `continuation`）。

## 后台运行与通知边界

长任务可后台运行，配合冻结检测、完成通知或自动恢复；这些机制不是工作流角色，不参与验收：

- 完成通知和退出码只证明生命周期变化，不作验收证据；
- 冻结或中断时保留 worktree、分支、日志和证据；
- 恢复以 `lifecycle resume/status/list/inspect` 的结构化状态为首要入口，再核对当前任务单、Git、`.pipeline/recovery-index.json` 和正式 evidence；活动进程和最新日志用于诊断，过程记录以 `.pipeline/<task-id>/` 的角色进度日志和阶段报告为准，不重猜用户目标；任务单冻结后只按记录的修订版本演进（`.pipeline/<task-id>/amendments.json`，身份字段不可修订），任务状态不从项目级状态文件、通知或自然语言报告恢复。
- 无这些机制时主代理仍可前台执行同一生命周期。

## 冻结或失败恢复

1. 通过 lifecycle API/CLI 读取任务状态；需要写状态时仅由主代理使用 `role=main-agent` 接口。
2. 将原始日志、规划中间审计和 stage 文件优先保存在系统临时目录；项目仅保留 `.pipeline/recovery-index.json`，正式 evidence 仍写入 `.pipeline/<task-id>/`。
3. 保存 Git 状态、测试产物和报告。
4. 读最新业务活动和当前子进程，区分真冻结、等待测试、权限阻塞和正常退出。
5. 保留 worktree、branch、未提交实现和任务级证据。
6. 必要时建 checkpoint，不为"干净"删现场。
5. 契约需改变时先分类：仍在交付本任务时由主代理用 `pipeline-tools task amend` 记录一条修订版本（放松约束必须带裁决引用，身份字段不可修订），在同一 worktree 继续；只有范围或目标已变成另一个任务时，才记录裁决并开 `derived` 任务单和新证据目录——任务类型写 `derived`，机器 ID/path 保留 `continuation`。合并之后不再修订，需求变化重新规划。
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

worktree 通过而主工作树失败 → 仍 FAIL/BLOCKED，不因合并已发生就改完成。post-merge 的 `final-check.md`、`final-result.json` 与 `finalization.json` 应作为独立的 post-merge evidence 提交，不能用 pre-merge 报告替代。`finalization.json` 必须可解析且绑定当前 task；缺失、旧 marker 或身份不一致时 reconcile 不能 PASS。

**最终化标记的 head 判据**：提交 `finalization.json` 这个动作本身就会推动 `HEAD`，若要求标记记录的 `head` 严格等于 `HEAD`，标记会在提交后自我失效。因此 `verify_finalization_snapshot` 对 `head` 施加与阶段报告相同的容忍：标记的 `head` 等于当前 `HEAD`，**或**它是当前 `HEAD` 的祖先且两者之间只有该任务的证据提交（复用 `head_advanced_by_evidence_only`，证据目录取该任务的证据目录）。产品路径改动仍失败 closed：标记 head 之后只要出现改动产品路径（或任何非证据路径）的提交，仍报 `finalization head is stale`；`head` 不是合法提交、不是 `HEAD` 祖先、证据目录无法解析时同样报 stale。`branch` 与 `worktree` 不适用该容忍，仍按严格相等判定；`retained_sha256` 快照失配仍报 `finalization retained evidence hash mismatch`。`planning evidence-finalize` 对已存在标记的幂等复核走同一判据，因此提交标记后重复调用仍返回 `finalized`。schema 1 报告仅用于 legacy/unverified 查询；schema 2 报告的身份判据按阶段分工，见下文。events.jsonl 还必须从 `created` 开始、transition 可重放且终态与 lifecycle.json 一致。

**证据身份的阶段分工**：`active`（pre-merge）阶段把报告绑定到它观察的提交——`head` 等于 `HEAD` 或仅被本任务证据提交推进，`branch`/`worktree` 等于当前 Git 身份；`finalized`（post-merge）阶段**只用任务单 id 与 `sheet_revision` 识别证据**，`head`、`branch`、`worktree` 降为记录事实（仍必须存在且格式合法），`observed_at_commit` 为可选记录事实，该阶段不再作任何相等性或路径相交判定——合并必然在当前 `HEAD` 上引入产品路径提交，所以该阶段这些判据都不可能成立，闸门因此不再要求刷新 head 或改写报告身份。fail-closed：`sheet_revision` 缺失或与当前修订版本不符、`task_id` 与受验任务不符、证据目录名与任务 id 不符、阶段取值无法确定，一律报错。`reconcile` 的报告身份一致与完整判据同样只看 `task_id` 与 `sheet_revision`（`branch`、`worktree`、`head` 不再参与一致性比较），任务分支报告与主工作树终审报告并存不再判为 `report identity conflict`。`reconcile` 对已合并交付（存在 `finalized` 标记，或报告记录的分支尖端已是当前 `HEAD` 的祖先——判断分支时排除 `HEAD` 当前所在分支，主工作树终审报告记的正是它，其尖端永远是 `HEAD` 的祖先）走 post-merge 判据，对未合并任务仍施加完整提交绑定。`active` 阶段的判定与错误文本与改动前逐字一致；`gate post-merge` 与 `evidence verify --phase finalized` 走 post-merge 判据，`gate pre-merge` 与默认（`--phase active`）走 active 判据。

**报告机器块的边界**：阶段报告的 `pipeline-evidence` 机器块从起始围栏行开始，到其后**第一条**收尾围栏行（只由三个反引号组成的那一行）结束。机器块之后的正文可以再有自己的 fenced 代码块，它们不属于机器块。最终化读取器（`planning._read_evidence_block`）与闸门读取器（`core._read_machine_evidence`）用同一判据定位边界，因此对同一份报告结论一致，该一致性由 `tests/test_planning.py` 的一致性用例钉住。仍 fail-closed：没有起始围栏、起始围栏出现多次、找不到收尾围栏、块内 JSON 非法或不是对象——一律判为不可读、最终化 blocked。该边界判据只影响读取，从不改写报告字节，因此机器块之后带代码块的历史报告被自然接纳。

合并后不再修订任务单：`amendments.json` 是追加式哈希链（旧条目字节不变），合并不会改写它；此后的需求变化重新规划或开新任务。post-merge 复验证据同样写明它评判的 `sheet_revision` 与 `sheet_sha256`，有效性只按修订版本判定：合并在当前 `HEAD` 上引入了产品路径提交，"改动路径"判据在该阶段必然成立，因此不再施加。`observed_at_commit` 是可选记录事实，写明即有格式要求，缺失不算错误；不含 `sheet_revision` 的历史形态证据不因此新增错误，只报为 `unverified`。

## 状态恢复与并发护栏

每次后台间隙、会话切换或重启后，在写报告、提交、合并或派发前重新核对：当前任务单；主分支 HEAD；`git worktree list`；活动进程和最新日志；是否已有另一个主代理接管并完成任务。

任务已完成或 worktree 已被重新绑定时，旧上下文必须停止，不覆盖新证据。
