---
name: pipeline
description: "Use when an agent plans, builds, reviews, or merges code."
version: 0.11.0
author: Alex Chen (alexcdever)
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [coding, workflow, planning, testing, review, worktree, agents]
  related_skills: []
---

# 编程工作流

与具体产品和工具无关的多代理编程工作流：定义主代理、执行子代理、审查子代理之间的协作契约，以及任务单、验收测试、证据、恢复与合并规则。不规定具体子代理调用方式或通知方式；实现 worktree 的路径、创建和核对规则除外。

## 适用场景

AI agent 修改、重构、修复、扩展或验证 Git 项目时使用，尤其需要隔离 worktree、独立审查和真实测试的任务。

执行 agent 须能读写项目文件、运行构建/测试命令、创建 Git worktree 并创建子代理；能力不足时在结果中标注证据边界，单代理自检 ≠ 独立审查。主代理成功返回、测试数量增加、退出码为 0 或报告文件存在，都不能单独代表产品完成。

## 角色契约

- **用户**：提供目标、优先级；裁决真实设计决策、外部授权、不可逆风险。
- **主代理**：读状态 → 拆任务 → 写任务单+逐条验收测试 → 提交冻结后派发 → 调度执行/审查子代理 → 核全部证据并重跑关键验收 → 把任务级过程记录写入 `.pipeline/<task-id>/` 的角色进度日志和阶段报告 → 全闸门通过后合并并在主工作树复验。不默认替执行子代理写业务代码；遇真实决策点保留现场停下，不猜测。
- **执行子代理**：在指定 worktree 按红→绿→蓝实现冻结任务单；跑验收命令与必要回归；只在自己任务证据目录写执行报告。不改冻结目标/范围/验收测试，不自行扩大产品设计。
- **审查子代理**：独立上下文读任务单、代码、执行报告；亲自重跑验收测试；查正确性、边界、范围、覆盖率与证据新鲜度；发现问题报 BLOCKED/FAIL。默认只读，不改产品代码。

## 实现 worktree 约定

- 任务单契约提交后，由主代理从主工作树创建该任务唯一的实现 worktree。标准路径是 `<仓库根目录>/.worktrees/<task-id>`；不得使用仓库同级目录、项目内的 `worktrees/`，也不得为同一个任务创建第二个实现 worktree。
- 必须从主工作树根目录执行：

  ```bash
  git worktree add -b "<branch>" ".worktrees/<task-id>" "<baseline-head>"
  ```

  `git worktree add` 会创建不存在的目标目录及缺失的 `.worktrees` 父目录；不需要先执行 `mkdir`。该命令同时把目录登记为 Git worktree。目标路径已存在、分支已被其他 worktree 使用或身份不明确时，先停止并 reconcile，不得换到仓库外另建目录绕过冲突。
- 创建前确认 `git rev-parse --show-toplevel`、`git status --short --branch` 和 `git worktree list --porcelain`；创建后再次运行 `git worktree list --porcelain`，并用目标 worktree 的 `git rev-parse --show-toplevel`、`git branch --show-current` 和 `git rev-parse HEAD` 核对路径、分支和基线。
- 核对后的绝对路径写入 executor/reviewer dispatch 记录（以及任务锚点进度事件），不写入任务单——任务单只承载冻结契约。执行子代理和审查子代理使用主代理传入的路径，不得自行选择或创建另一个 worktree；独立审查上下文不等于再创建一个 Git worktree。
- 项目根目录的 `.gitignore` 必须忽略 `/.worktrees/`，避免实现 worktree 的文件污染主工作树状态。缺少该规则时，须在允许修改范围内先补齐并记录；不能在契约冻结后静默扩大范围。
- 发现任务单、dispatch、报告或 `git worktree list` 中的路径不一致，必须标记身份漂移并保留现场；不得把仓库同级目录或第二个路径改写成规范路径后继续执行。

## 主代理阶段推进不变量

主代理把执行/审查子代理视为阶段性工具调用。子代理返回只证明该阶段返回，不证明任务完成；主代理不得因为收到子代理结果、看到测试摘要或已经写出阶段总结，就结束当前任务。

- 每个子代理返回后，主代理必须重新读取当前任务单、Git/worktree 身份和本轮 `.pipeline/<task-id>/` 证据，核对 task-id、branch、HEAD、角色和报告新鲜度。
- 任务单规定还有后续阶段时，主代理必须继续推进下一个阶段，而不是先向用户发送总结；阶段性报告不是终止条件。
- 标准闭环是：执行子代理 → 独立审查子代理 → 主代理最终检查 → 合并后主工作树复验。审查通过不等于主代理最终检查通过。
- 子代理返回 FAIL、BLOCKED、超时或证据缺失时，主代理必须分类并按恢复规则保留现场、建立 `derived` 任务（机器 ID/path 保留 `continuation`）或上报阻塞；不得把阶段结果改写为 PASS，也不得跳过后续核验。
- 只有当前任务的最终证据全部齐全，或遇到必须由用户裁决、外部授权或无法自愈的阻塞，主代理才能结束本轮。
- 默认推进策略是自动推进后续任务：完成并合并当前任务后，主代理继续队列中的下一个任务，不需要用户逐条确认。这是默认行为，不是例外。
- 该策略按两级切换：运行级存于该次运行的 `lifecycle.json` 的 `approval_mode`，项目级存于 `.pipeline/config.json` 的 `approval_mode`；解析顺序是显式参数 → 运行记录 → 项目配置 → 默认 `automatic`。切换为 `manual` 时，主代理在每个任务派发前停下等待人工确认。
- 项目级配置的形态是 `<仓库根目录>/.pipeline/config.json` 里的 `{"approval_mode": "automatic" | "manual"}`，这是它当前唯一被读取的键；路径、键名和取值枚举都由 `pipeline_tools/planning.py` 的 `_project_approval_mode` 固定。**没有任何命令会创建或改写该文件**——需要项目级默认值时必须手工创建。文件缺失、不可读、JSON 非法或 `approval_mode` 不在枚举内时都回退到默认 `automatic`，即默认自动推进后续任务。

## 事实与上下文规则

- 事实只能来自本轮直接读取的文件、命令输出或测试产物；推断必须标为推断，未执行或未读取必须标为未验证，不能补造结果。
- PASS 必须能回溯到当前 task-id、HEAD、worktree、branch、完整命令、退出码、关键断言和产物；通知、代理自述和旧报告不能代替当前证据。
- 任务单只承载冻结契约与人类可读的契约说明：任务身份、依赖与范围、事实与假设、设计与行为契约、环境前置、验收测试和决策点。
- 过程记录不在任务单内。细粒度事件写入 `.pipeline/<task-id>/<role>-progress.jsonl`（角色进度日志）；阶段结论写入三份阶段报告（`executor-report.md`、`review-report.md`、`final-check.md`）、机器结果 JSON 和 `finalization.json`；任务锚点与合并提交保存在进度事件和 dispatch 记录中。
- 主代理按需读取本文件和相关 reference，不默认加载全部资料；委派简报只传任务身份、冻结契约路径、允许范围、验收 ID/命令、决策点和报告格式，证据不足再扩展阅读。

## 机械工具与项目级反馈

机械检查和统计由本技能内置的 `pipeline_tools` 命令程序执行；不要再依赖已废弃的独立工具 worktree。技能只规定调用时机和判断边界。新任务单必须包含 `pipeline-contract` 机器区块，由 `pipeline-tools task validate` 校验；任务执行前运行 `task preflight`，执行中用 `command run` 统一超时和日志，范围用 `scope check`，正式证据校验前运行 `evidence readiness`，合并前后用 `evidence verify` 与 `gate`。

- 工具输出的退出码和原始日志是机械事实；终端摘要不替代日志。
- 在派发 executor/reviewer 前先运行 runtime preflight，确认 Node/pnpm/Git、native ABI 和项目所需测试能力；环境不匹配不得伪装成产品失败或继续正式验收。
- 子代理启动前，主代理生成环境检查列表，包含：可读任务与worktree、可执行验收命令、可写 `.pipeline/**`、reviewer不可写产品代码等。子代理按检查列表逐项验证，通过后开始工作，任何检查失败立即向主代理报告BLOCKED。
- 主代理未经用户明确授权不得修改产品代码；executor/reviewer 失败后应重派、建立 `derived` 任务（机器 ID/path 保留 `continuation`）或保留决策点，不得接管实现。
- OpenCode Desktop 会话可用 `metrics import-opencode-session` 导入结构化流程信号；导入器不得从自然语言推断产品 PASS。
- 程序化命令应优先使用 `--format json --output <path>`；JSON 结果是后续阶段的权威输入，终端短摘要不作为流程状态来源。
- 使用 `lifecycle status` 获取当前阶段和允许/禁止动作；语义代理只能提交 recommendation/findings，不能直接把自然语言结论当作 gate 状态。`lifecycle status` 在 merge 阶段返回的动作标识 `merge_branch_in_main_worktree` 表示由主代理手工合并，`pipeline-tools` 没有对应的合并命令，不要去找它。
- 结构化执行闭环使用 `dispatch write`、`result verify` 和 `freshness`；只有当前 task-id、角色、HEAD、验收结果和证据引用均通过机械校验，才能把语义代理的 recommendation 交给下一阶段。
- 工具不可用、命令超时、证据缺失或身份/范围漂移时标为 `BLOCKED`/漂移，不绕过工具改写成 PASS。
- 报告必须包含机器可读的 `pipeline-evidence` 区块；自然语言报告不能单独产生验收结论。
- 每个非 `metrics` 的 `pipeline-tools` 阶段命令默认自动写入一个 `observed` 结果事件到项目 `.pipeline/metrics/`；超时、环境阻塞、证据缺口、范围漂移等只根据机械退出码和结构化结果追加 `derived` 反馈事件。新版本工具首次发现 `.workflow/` 时会先自动迁移并校验；若 `.pipeline/` 已存在则报告冲突并停止，不覆盖、不双写。`reported` 只能保留追溯，统计不参与验收，不自动改写技能或契约。
- 自动采集不得从自然语言报告推断产品 PASS；不得记录 prompt、完整命令输出、凭据、token 或业务数据。仅在测试/明确诊断时使用 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` 关闭。
- `gate` 的 pre-merge 要求 `executor-result.json`、`reviewer-result.json`、`final-result.json` 存在且各为 JSON 对象；post-merge 要求 `final-check.md` 中至少有一条 `exit_code == 0` 且 `cwd` 为主工作树根的命令（合并后复验），二者缺一即 FAIL。
- 任务单在 freeze 时记录 sha256（写入 `.pipeline/<task-id>/implement-plan.json` 的 `task_sheet_sha256`）；`freeze_check` 据此检测任务单在冻结后被改动。
- `planning_to_dispatch` 支持 `expected_requirements_sha256` 绑定规划期需求基线；传入后 preflight 用它在派发前核对 `implement-plan.md` 哈希是否漂移。
- `prerequisite` 任务必须在任务计划里声明 `non_user_completion_reason`；生成器不再替它编造理由，缺失即生成失败。
- 生成的 schema-3 契约携带 `assumptions`/`unknowns`（来自项目事实），随任务单一并冻结。
- 正式 `evidence verify` 前先运行 `evidence readiness`；缺 final-check 或必要报告时记录“未准备好”，不要把阶段顺序问题误作产品验收失败。指标报告优先按 task/run/terminal 维度解释，不用全项目累计 `success_rate` 代替终态结论。
- 正常只把短摘要放入上下文；完整输出、报告和统计事件留在项目文件中，需要诊断时再读取。

## 不可违反的规则

1. 任务单先于实现：契约必须提交后才能创建唯一 `.worktrees/<task-id>` 实现 worktree 或派发；执行/审查子代理不得另建 worktree。
2. 契约冻结：不得为迁就实现改验收测试；设计变更记裁决并开 `derived` 任务——任务类型字段写 `derived`，机器 task-id/path 保留 `continuation`——保留原历史。
3. 验收测试即用例：每条必须指向当前测试文件、用例、断言、命令、结果边界。
4. 独立审查：独立上下文直接复验；转述他人结果不算。
5. 证据属当前任务：task-id、worktree、branch、测试输出、报告路径必须一致且本轮生成。
6. 真实链路不可替代：单元/组件/协议/持久化/真实浏览器/设备各自证明各自边界。
7. 合并后复验：worktree 通过 ≠ 主工作树通过（依赖、构建产物、原生模块可能不同）。
8. 超时有界：单条测试默认 3 分钟硬上限，超时必须停止诊断；整套用更大的明确累计上限。
9. 决策点停下：缺产品决策、协议兼容、权限、外部服务或验收环境时保留现场上报，不替用户定案。
10. 数量≠覆盖率：绿色数、退出码、完成通知、报告存在、代码行数增加都不能单独 PASS。

## 标准生命周期

1. 恢复核对：读与当前任务相关的产品/架构文档、任务单、Git 状态和已有证据；通过任务单、worktree、分支和证据目录核对活动任务身份，过程记录以 `.pipeline/<task-id>/` 的进度日志和阶段报告为准；发现多个活动任务或状态不一致时先 reconcile；禁止盲目重派或重建现场。规划前置检查还要核验已有任务现场：`worktrees_without_sheet` 是阻塞项（没有已提交任务单就存在任务工作树），`uncommitted_sheets` 与它同级也是阻塞项（`docs/tasks/<task-id>.md` 已存在但未提交到 HEAD），`sheets_without_worktree` 和 `leftover_evidence` 是警告项。
2. 规划拆分：以用户行为或可验证能力为单位；定依赖、范围、契约、风险、决策点、验收矩阵；未写成具体用例即设计未完成。有产物依赖顺序执行；仅文件范围与 fixture 完全不重叠且无隐含依赖才并行。
3. 冻结任务单：默认 `docs/tasks/<task-id>.md`，证据 `.pipeline/<task-id>/`；提交任务单后把契约提交记录进 dispatch 记录与角色进度日志，主代理从主工作树用 `git worktree add` 创建 `<仓库根目录>/.worktrees/<task-id>`，确认主分支 HEAD、新 worktree、branch 与契约提交的关系；之后契约冻结。
4. 执行：子代理只在任务 worktree 实现；用户功能贯通 UI→前端/协议→核心→领域事实→持久化/投影→回显→重启恢复；纯基建任务标 prerequisite，不得冒充产品闭环。
5. 独立审查：新上下文核身份和报告新鲜度，逐条复验；通过 ≠ 已合并。
6. 最终检查：读任务单/执行/审查/最终检查报告，抽查高风险测试，重跑关键验收、全量测试、构建、lint、范围、冲突检查；全部有证据才 ready-to-merge。
7. 合并复验：提交实现+证据，用 branch ref 合并；主工作树重装依赖，重跑聚焦验收、全量测试、构建、lint、差异检查；通过才标已合并。
8. 持久化：把验收台账、执行记录、`derived`/`continuation` 任务索引和最终结果写入 `.pipeline/<task-id>/` 的角色进度日志、阶段报告和机器结果；成功最终化后只保留阶段报告、机器结果和 `finalization.json`，失败时保留完整现场。不另行维护项目级状态文档。完成通知含项目、task-id、阶段、分支、合并提交、验收状态、遗留项。

## 证据目录最小要求

`.pipeline/<task-id>/` 至少含 `executor-report.md`、`review-report.md`、`final-check.md`；每份写明 task-id、worktree、branch、轮次、命令、退出码、关键断言。验收失败时保存完整日志等证据文件用于诊断；成功时无需保存原始输出。旧 `.workflow/<task-id>/` 必须迁移到这里，不能继续作为运行目录。

## 版本升级与兼容性

### 目录结构变化
- **v0.10.0 → v0.11.0**：移除“每个任务必须写握手 JSON 文件”的强制要求，改用模板化环境检查列表；证据文件改为失败时保存，成功时不保存。`pipeline-tools runtime handshake` 命令仍然存在，它是可选的能力检查，写入 `capability-handshake.json`，与已移除的强制握手 JSON 不是同一件事。
- **旧版本迁移**：`.workflow/<task-id>/` 目录在新版本工具首次发现时自动迁移到 `.pipeline/<task-id>/` 并校验；若 `.pipeline/` 已存在则报告冲突并停止，不覆盖、不双写

### 向后兼容性
- 已存在的 `.pipeline/` 目录结构完全兼容新版本
- 旧版握手JSON文件（如果存在）不影响新版本工作流，主代理会使用新的检查列表机制
- 已保存的证据文件（包括成功时的原始输出）可保留作为历史记录，新任务按新规则执行

### 升级建议
- 更新技能版本后，主代理在下次任务启动时自动使用新的环境检查列表机制
- 不需要手动清理旧版握手JSON文件或证据文件，但可选择清理成功任务的原始输出以节省空间
- `.pipeline/metrics/` 是指标历史，必须纳入 Git 追踪，不应加入项目 `.gitignore`，详见 `references/metrics-contract.md`
- 角色进度日志 `.pipeline/*/*-progress.jsonl` 是过程记录，由项目根目录 `.gitignore` 规则排除，不得进入 Git；`commit_history_check` 会按名拒绝它们，`scope_check` 对其豁免

### 自动优化机制
主代理在任务启动的「恢复核对」阶段执行以下优化操作（下列各项除注明外均为主代理职责，不是 `pipeline_tools` 的自动行为）：
- **清理已合并的worktree**：任务成功合并后由主代理删除该任务的 worktree（包括其中的原始输出）；`pipeline_tools` 只创建和校验 worktree，没有自动清理命令
- **主工作树 `.pipeline/` 内容约定**：`.pipeline/metrics/` 是纳入 Git 追踪的指标历史；`.pipeline/<task-id>/` 存放阶段报告与机器结果；角色进度日志 `.pipeline/*/*-progress.jsonl` 由项目 `.gitignore` 排除，不得进入 Git
- **应用新证据策略**：新任务执行时按"失败保存、成功不保存"规则处理证据文件，由 `pipeline-tools planning evidence-finalize` 机械执行
- **环境检查升级**：主代理在派发子代理前使用模板化环境检查列表，替代旧版握手机制，见「机械工具与项目级反馈」一节
- **目录结构校验**：主代理确认 `.pipeline/` 目录结构符合当前版本要求；旧 `.workflow/` 目录由 `pipeline_tools` 首次访问时自动迁移（`layout.migrate_layout`），若 `.pipeline/` 已存在则报告冲突并停止

正确流程：主代理在worktree中commit实现代码，再在worktree中commit报告文档，然后合并worktree分支到主分支（代码+报告一起合并），合并成功后清理worktree。

以上优化在主代理的「恢复核对」阶段执行，不影响正在进行中的任务。

## 任务规模与 `derived` 任务

- 含多个独立领域聚合、十个以上互不共享 fixture 的验收族或多平台任务，先拆成可独立审查的切片。
- 实现失败/证据缺失/环境阻塞/设计改变分开记录；设计或契约改变时创建 `derived` 任务——任务类型字段写 `derived`，机器 ID/path 保留 `continuation`——使用新 ID、新任务单、新证据目录，从父任务的明确提交创建，父任务失败、裁决、已验收部分不得覆盖。
- 保留实现和证据现场，不无理由删 worktree、分支或报告。
- `derived` 任务的 `derived_from.parent_task_type` **必填**，取父契约的 `task_type`（`pipeline_tools/contract.py` 的 `_validate_derived_from`）。缺失或不是四个类型 token 之一时任务单校验失败。父类型为 `vertical-feature`/`repair` 时，子任务同样被强制完整链路（`_requires_full_chain`）；父类型为 `vertical-feature` 时证据下限被抬到至少 2（`evidence_floor` 的 `parent_task_type` 分支），`repair` 父类型不额外抬高证据下限。

## 参考文件（按需读取）

| 关注点 | 文件 |
|---|---|
| 任务单模板 | `templates/task-sheet.md` |
| 规划、拆分、契约冻结 | `references/task-design.md` |
| 验收矩阵、证据完整性、结论分类 | `references/acceptance-evidence.md` |
| 执行/审查子代理规则、主代理最终检查 | `references/execution-and-review.md` |
| 恢复、合并、主工作树复验 | `references/merge-and-recovery.md` |
| 真实浏览器、设备、多层证据 | `references/live-and-browser.md` |
| 跨介质操作故障矩阵 | `references/multi-medium.md` |
| 项目级反馈事件与 Git 追踪 | `references/metrics-contract.md` |
| 任务单 Markdown 结构检查（旧版辅助；真正的闸门是 `pipeline-tools task validate`） | `scripts/validate_task_sheet.py` |
