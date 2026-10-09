# 任务设计与拆分

## 设计责任

主代理把用户目标转成可执行、可验收、可恢复的任务契约。执行/审查子代理可提设计问题，但不得在实现阶段自行改契约。

## 规划前置检查

1. 读产品目标、架构决策和与当前工作相关的任务单；任务单承载冻结契约与人类可读的契约说明，过程记录（锚点、验收台账、执行记录、最终结果）在 `.pipeline/<task-id>/` 的角色进度日志和阶段报告中。
2. 查主分支、活动 worktree、未提交修改、最近提交和已有任务证据。
2.1 检查已有任务现场。任务单的位置编码状态：`docs/tasks/<task-id>.md` 是进行中或待派发，`.pipeline/<task-id>/<task-id>.md` 是已终态且有自己的证据目录，`.pipeline/archive/<task-id>.md` 是已终态且没有证据目录；三者按此顺序解析，同一 id 出现在多个位置或三处都没有时 fail-closed 报错（`pipeline_tools/core.py` 的 `task_sheet_resolution`）。`pipeline-tools planning preflight` 的 `task_scenes` 结果据此报告四类事实，判断标准不同：
   - `worktrees_without_sheet`：**阻塞**。存在任务工作树却没有任务单（active 或 archived 都算有单），违反「没有已提交且冻结的任务单不得存在对应任务工作树」。
   - `uncommitted_sheets`：**阻塞**。`docs/tasks/<task-id>.md` 已存在但未提交到 HEAD；只对 active 单子判定。
   - `sheets_without_worktree`：警告。进行中的单子已提交但工作树不在，通常是上一轮被中断，需要先 reconcile；只看 active 单子，已关闭的任务（证据目录内或 archive 里的单子）不产生该警告。
   - `leftover_evidence`：警告。`.pipeline/<task-id>/` 有证据目录但既无 active 单子也无 archived 单子，通常是遗留现场，需要先 reconcile。`.pipeline/archive/` 是任务单隔离区而不是证据目录（与 `planning`、`metrics` 同级排除），不会被当成一个叫 `archive` 的任务。
   只要 `task_scenes` 非空，`next_actions` 就会给出 `reconcile existing task scenes before planning`；先 reconcile，再规划。
2.2 任务关闭后单子进入终态位置：最终化的移动步骤 `pipeline_tools/planning.py` 的 `archive_task_sheet(root, task_id)` 把单子从 `docs/tasks/` 移入 `.pipeline/<task-id>/<task-id>.md`（没有证据目录时移入 `.pipeline/archive/<task-id>.md`），被跟踪的单子用 `git mv` 保持跟踪；`.worktrees/<task-id>` 仍存在时该步骤 blocked，不移动任何文件。`docs/tasks/` 因此只反映进行中的工作。
3. 读将改变的符号、直接调用方、持久化边界和现有测试。
4. 搜索被替换的标签、接口、字段、错误、日志事件和旧测试。
5. 记录现有测试对产品行为的约束，分类为保留/迁移/替换/删除。

不要只看目录名或文件名推断范围；影响面和调用链必须有证据。

## 审批策略配置

项目级默认值存放在 `<仓库根目录>/.pipeline/config.json`：

```json
{"approval_mode": "automatic"}
```

- 取值只能是 `automatic` 或 `manual`；这是该文件当前唯一被读取的键。
- 路径、键名和取值枚举由 `pipeline_tools/planning.py` 的 `_project_approval_mode` 固定。
- 解析顺序是显式参数 → 运行记录（`lifecycle.json` 的 `approval_mode`）→ 项目配置 → 默认 `automatic`。
- **没有任何命令会创建或改写该文件**；需要项目级默认值时必须手工创建。
- 文件缺失、不可读、JSON 非法或取值不在枚举内时都回退到默认 `automatic`。
- 取值为 `manual` 时，主代理在每个任务派发前停下等待人工确认。

## 事实、假设与未知

冻结前把影响契约的事实绑定到文件、符号、命令输出或架构决策；把未验证内容单列为未知，把会改变范围或验收的未知列为决策点。不能因为文件名、旧任务或代理摘要“看起来如此”就写成已确认事实。

`planning_to_dispatch` 生成任务单时会把项目事实里的 `assumptions`/`unknowns` 原样写入每份契约（schema 3 的 `assumptions`、`unknowns` 数组），因此假设与未知随契约一起冻结，而不是只留在规划会话里。

## 需求多义冲突的裁决清单

需求本身含多义、互相矛盾的约束，或同一实体出现冲突取值时，主代理不能挑一个“看起来合理”的解释继续规划——必须先把它变成机械可查的冲突记录，再决定是否停下请求开发者裁决。可执行步骤如下：

1. **何时判定为多义/冲突**：同一 `entity_id` 出现两个无法同时成立的 `value`；一条需求与另一条需求或项目事实直接矛盾；需求文本对同一行为给出互斥的范围（例如同时要求“不得改协议”与“必须扩展协议”）。只是信息缺失、不构成矛盾时，按未知处理，不写成冲突。
2. **如何写记录**：把这些事实写进项目事实模型的 `conflicts` 数组，每条含稳定 `id`、涉及的事实/实体引用、以及为什么不能同时成立。会阻塞规划或派发、需要人裁决的条目同时写进 `decision_blockers`，`status` 用 `blocking`。`conflicts`/`decision_blockers` 会被 `gate_facts_for_planning` 校验，并保留在规划审计链里。
3. **如何触发阻断**：`planning_to_dispatch` 的 `facts-gate` 阶段会调用 `gate_facts_for_planning`。只要存在 `blocking` 的决策阻塞项，gate 返回 `blocked`，编排在 `facts-gate` 阶段即停止，不进入任务生成与派发。
4. **何时停下请求开发者裁决**：出现 `blocking` 决策阻塞项时停下，把冲突条目和候选解释列给开发者，由开发者给出裁决。主代理不得自行 `resolution`/`decision`/`auto_resolve`——`validate_project_facts` 会把这些字段判为未授权并报错。裁决落定后，用解析后的结论重建事实模型（必要时用 `task amend` 修订任务单或重新规划），再重新规划。
5. **不要绕过**：不能通过删掉冲突条目、把 `blocking` 降级为 `non_blocking`、或在没有开发者裁决的情况下改写事实来“让规划通过”。这类改写属于伪造事实，违反「事实与上下文规则」。

## 任务单位

以用户行为或可验证能力为单位，通常贯通：用户操作 → UI/前端状态 → 类型化命令/查询/事件 → 核心服务 → 领域事实或文档 → 持久化与投影 → 订阅回显 → 重启/重连恢复。

纯 schema、协议、算法或持久化底座可作 prerequisite，但任务单必须写明"非用户功能完成"，并保留后续消费该底座的用户行为任务。

### 任务类型与命名

契约里的任务类型 token 只有三个：`vertical-feature`、`prerequisite`、`repair`。选择依据是任务与用户功能的关系，不是工作量：

- `vertical-feature`：交付一条完整用户链路（入口 → 交互 → 应用处理 → 领域事实 → 持久化 → 回读 → 恢复），有真实外部入口和可观察的用户结果。
- `repair`：修复已有用户功能链路上的缺陷，链路本身已存在；必须按 `vertical-feature` 的标准覆盖完整链路，不能只改一个技术层就宣称修好。
- `prerequisite`：只产出被后续任务消费的底座（schema、协议、算法、持久化、构建或环境能力）。任务计划必须为该任务声明 `non_user_completion_reason`，说明为什么它不是用户功能完成；生成器把它原样写入契约，缺失或空白时任务单生成失败（不再填默认英文）。

非目标「不得冒充完整用户功能」（goal.md 第 28 行）直接决定类型选择：只要任务产出不构成用户可观察的完成，就不能标 `vertical-feature` 或 `repair`，必须标 `prerequisite` 并在 `non_user_completion_reason` 里说清它只是底座。反过来说，用 `prerequisite` 逃避真实用户链路的验收也是违规——底座本身仍要有验收测试，只是它不冒充最终用户功能。

**新任务不再派生**：接替关系一律用 `dependencies` 表达。规划期声明 `type: derived`（或带 `parent_task_id`/`derived_from` 的派生形态）会被 `validate_task_plan` **fail-closed 拒绝**并给出可读原因；生成器不再产出 `task_type: derived` 的任务单，也不写 `derived_from`；派发期的派生创建入口（`dispatch derived-create`）已移除。新任务从当前 `HEAD` 建 worktree，把接替关系写进 `dependencies`，由 `depends_on`/`dependencies` 机械校验（任务存在、无环）。需要修正已冻结的任务单时用 `task amend`（见「契约修订」），不再需要开派生任务。

**历史 `derived` 只作读取兼容**：`pipeline_tools/contract.py` 的 `TASK_TYPES` 仍含 `derived`，已冻结的历史派生契约原样继续可读——`task validate` 照旧通过，校验规则一字未变（见下节）。`continuation` 作为历史机器 id/path token 同样保留，只是不再有任何新的创建路径。

### 历史 `derived` 契约的读取规则

对**已有**的派生契约，校验按子契约自己的 `task_type`（`derived`）判定，并读取 `derived_from.parent_task_type` 收紧约束。`derived_from` 含 `task_id`、`commit`、`branch`、`parent_task_type` 四字段，`parent_task_type` **必填**且必须是类型 token 之一；缺失或非法时校验失败（`pipeline_tools/contract.py` 的 `_validate_derived_from`）。

读取规则按父类型分三种情况，与移除创建路径前**完全一致**：

- **链路段强引用**：`_requires_full_chain` 在 `task_type` 为 `vertical-feature` 或 `repair` 时返回 `True`；当 `task_type == "derived"` 时，它读取 `derived_from.parent_task_type`，父类型为 `vertical-feature` 或 `repair` 时同样返回 `True`。也就是说历史 `derived` 契约**不再**无条件获得链路豁免——父类型是 `vertical-feature`/`repair` 时，七个段都必须给出真实引用。父类型为 `prerequisite` 时才允许 `{"not_applicable": true, "reason": "..."}` 结构化豁免。
- **证据下限加成**：`evidence_floor` 在 `task_type == "vertical-feature"` **或** `parent_task_type == "vertical-feature"` 时把下限抬到至少 2（`pipeline_tools/contract.py:131-145`）。`repair` 父类型不触发这项加成——`repair` 本身也只在链路强引用上收紧，不抬高证据下限。其余仍受 `risk` 下限和 `project_type` 加成约束。
- **`prerequisite` 的 `non_user_completion_reason`**：该字段仍只在 `task_type == "prerequisite"` 时被要求（`pipeline_tools/contract.py` 的 `_validate_schema3_contract`）；父类型为 `prerequisite` 的历史 `derived` 契约不校验它。

`derived_from.parent_task_type` 是这条历史判定唯一的开关，漏填或填错会让契约落到错误的约束档位。这些规则只作用于**读取**：没有创建函数、没有规划期派生校验分支、没有生成期派生单分支。

### 链路段与 `not_applicable`

契约的 `chain` 固定七个段（`CHAIN_NAMES`）：`entry`、`interaction`、`application`、`domain`、`persistence`、`readback`、`recovery`。每段的写法按 schema 区分（`pipeline_tools/contract.py`）：

- **schema 1/2**：每段必须是非空数组，元素只能是纯引用字符串；不接受结构化豁免段。写入 `{"not_applicable": true, "reason": "..."}` 会被判为 `chain.<name> must be a non-empty array`。
- **schema 3**：仅当任务不需要完整链路时才允许结构化豁免段，即 `{"not_applicable": true, "reason": "<非空理由>"}`。判定函数是 `_requires_full_chain`（`pipeline_tools/contract.py:166`）：`vertical-feature`、`repair` 为 `True`；历史 `derived` 契约取其 `derived_from.parent_task_type`，父类型为 `vertical-feature`/`repair` 时同样为 `True`；`prerequisite` 为 `False`。返回 `True` 的任务必须在全部七个段给出真实引用，只有 `prerequisite`（以及父类型为 `prerequisite` 的历史 `derived`）可以豁免。
- 任何 schema 都不接受字面量 `"not-applicable"`；schema 3 会明确报错要求改用结构化形式（`NOT_APPLICABLE_LITERAL`，`pipeline_tools/contract.py:34`）。

### `resource_mode` 单/批规则

schema 3 的每个 operation 必须声明 `resource_mode`，取值只能是 `single` 或 `batch`（`OPERATION_RESOURCE_MODES`），并且必须与 `resources` 数量一致：只有 1 个资源时必须是 `single`，2 个及以上时必须是 `batch`；`resources` 本身必须是非空数组（`pipeline_tools/contract.py` 的 `OPERATION_RESOURCE_MODES` 校验）。

### 规划期资源存在性规则

手写的 `.pipeline/<dir>/` 资源在规划期由 `pipeline_tools/planning.py` 的 `validate_task_plan` 机械校验，前提是调用方传入了 `root`（Python API 的 `validate_task_plan(..., root=root)`；CLI 的 `planning task-plan-validate --root <root>`）。规则只有两条：

- **目录必须真实存在**：`task.resources` 或 `operation.resources` 里任何一个以 `.pipeline/` 开头、且不只是 `.pipeline/` 本身的资源路径，必须在 `root` 下解析为一个真实目录；否则报 `names a .pipeline directory that does not exist`。
- **删除类操作必须有可删文件**：kind 含删除语义 token（`delete`、`remove`、`purge` 及其屈折形式）的 operation，其 `.pipeline/<dir>/` 资源目录里必须至少有一个**非保留**文件；只有保留证据（`RETAINED_EVIDENCE_NAMES`）或角色进度日志（`*-progress.jsonl`）时报 `the directory holds no deletable files`。保留集是证据最终化的产物，删除它们才是漂移。

这条校验是**机械的、与具体目录名无关的**：它只检查路径指向的文件系统事实，不硬编码任何目录名白名单。它只作用于规划输入，因此**不会追溯地让已冻结的任务单失效**——冻结任务单由 `task validate` 和 gate 期校验负责，本规则不重跑它们。

### `test_ref` 的位置规则

`test_ref` 的书写格式是 `文件路径: 类名.方法名`，冒号前的文件路径是项目相对路径，冒号后的符号目标是可选位置声明；`test_ref` 与 `command_ref` 都不含尖括号。

位置规则分两层，分别由规划期和 gate 期机械校验：

- 规划期（`pipeline_tools/planning.py`）：`test_ref` 指名的文件必须落在任务的 `allowed_paths` 之内；这条判定是无条件的，不因任务是否声明了与测试同目录树的资源而改变。允许的写法包括精确路径、目录前缀（`tests/` 结尾）和通配（`tests/*`）。落在任务资源范围之外的验收测试会被判 `... test_ref ... is outside the task's allowed paths`。
- gate 期（`pipeline_tools/core.py`）：`test_ref` 指名的文件必须真实存在，且当 `test_ref` 声明了类名或方法名时，该符号必须在文件里真实声明；缺失会被判 `... test_ref method is absent from ...`。gate 只做位置与存在性核验，不解释测试语义。

### 证据等级下限表

schema 3 的 `risk`、`project_type`、`task_type` 共同推导每条验收测试的最低 `evidence_level`（`pipeline_tools/contract.py:35-39`、`:131-140`）：

| 输入 | 取值 → 下限 |
|---|---|
| `risk` | `low` → 1，`medium` → 2，`high` → 3 |
| `project_type` 加成（仅当 `risk` 不是 `low`） | `web` / `desktop` → 3，`multi-process` → 4 |
| `task_type` 加成 | `vertical-feature` → 至少 2 |

最终下限取上述各项的最大值；`risk` 非法时函数返回 `None`，不施加下限。低于下限的验收测试会被判 `evidence_level ... is below the required floor ...`。

### 新任务的提交顺序

每个新任务都从当前 `HEAD` 创建唯一的实现 worktree（`git worktree add -b "<branch>" ".worktrees/<task-id>" "<baseline-head>"`）：

1. 任务单先提交并冻结；需要修订时用 `task amend` 登记（见「契约修订」），不回写历史。
2. 从当前 `HEAD` 创建任务 worktree 与分支（标准路径 `<仓库根目录>/.worktrees/<task-id>`）。
3. 在 worktree 内实现、产出证据。
4. 接替关系不靠父任务现场：写在 `dependencies` 里，由机械校验确认依赖任务单存在且依赖图无环。

不复制任何任务单、证据或历史，也不复用别的任务的工作树；失败、裁决和已验收部分不得被覆盖。

## 代码阅读与委派

- 多文件、跨目录或需汇总对比的地形侦察可委派范围明确的检索；返回须含关键定义、签名、字段和约束的逐字摘录，并注明未读范围。
- 精确修改点的目标符号、调用方、持久化边界和现有测试，主代理必须亲读原文后再冻结任务单。
- 单文件读取、报错定位和短上下文问题由主代理直接处理，不为分工而增加无价值委派。
- 委派简报只包含任务身份、读取范围、输出格式和停止条件；子代理先返回证据，再给结论，不重复粘贴已提供的项目文档。

## 拆分规则

- 有产物依赖顺序执行；仅文件范围、fixture 和运行资源完全不重叠且无隐含依赖才并行。
- 含多个独立领域聚合、多平台或十个以上互不共享 fixture 的验收族时，按可独立审查边界拆分。
- 不按目录、技术层机械切割用户行为；跨介质操作先写阶段顺序、失败点、不变量和恢复路径。

## 规划产物的落盘规则

规划成功与规划失败的处理不同，这是失败恢复的前提：

- **成功时**：`.pipeline/planning/<planning-run-id>/` 下不保留任何东西——没有阶段 JSON、没有 `dispatch.json`、没有 `lifecycle.json`、没有 `result.json`，也不创建该目录。成功后只留下已冻结的任务单（`docs/tasks/<task-id>.md`）。`planning_run_finalize(..., success=True)` 会删除审计目录，`planning_to_dispatch` 成功返回时 `artifacts` 为空；重复 finalize 是幂等的（目录不存在即视为已最终化）。
- **任务单生成失败时**：`generate_task_sheets` 不写任何审计文件，失败结果只通过返回值交给人类开发者裁决，`.pipeline/planning/<planning-run-id>/` 不会因此创建。
- **其他失败 / 中断 / 冲突时**：保留完整审计链，包括 `lifecycle.json`、按序的阶段 JSON 和 `result.json`，供恢复与诊断使用。

因此不要以「`.pipeline/planning/` 里有没有记录」判断规划是否成功；成功本来就不留记录。

## 契约冻结

任务单提交前必须写清：目标、范围、禁止修改、数据链路、依赖、验收测试、环境前置和决策点，并为每条验收测试指定可观察产物和证据等级。提交后执行子代理只在契约内实现、审查子代理只按当前修订版契约判断；实现遇冲突停下报告；设计真变时记录裁决并修订任务单（见「契约修订」），只有在范围或目标已变成另一个任务时才新建任务单——用新的 task ID、从当前 `HEAD` 建 worktree，接替关系写进 `dependencies`。

不能为让测试变绿而删除困难验收测试，也不能把未验证环境降级伪装成已验证。

## 契约修订

契约冻结不等于绝对不可变：冻结后的每次改变都必须留痕，工具只做校验、分类与登记，不生成也不重写任务单内容。

```bash
python -m pipeline_tools task amend <root> --task-id <id> --reason '<为什么需要这次修订>' \
    [--adjudication <裁决引用>] [--requested-by main-agent|executor|reviewer] [--feedback-ref <locator>] [--role main-agent]
```

流程：主代理先手工编辑 `docs/tasks/<task-id>.md`（契约区块与对应散文段落），再调用 `task amend`；工具读完新契约后与上一版契约做结构性比对，追加一条记录到 `.pipeline/<task-id>/amendments.json`，然后主代理提交任务单。

- **身份字段不可修订**：`schema`、`task_id`、`task_type`、`derived_from` 描述"这是哪个任务"，改了就不再是同一份契约。需要换任务身份时新建任务单。
- **判据一：是否改变验证面**。`acceptance_tests`、`allowed_paths`、`forbidden_paths`、`chain`、`required_evidence_levels`、`operations`、`risk` 任一实质变化即 `verification_surface_changed: true`，已有阶段证据作废，必须对最新版本重做独立审查。
- **判据二：是否放松约束**。删除验收测试、降低某条 `evidence_level`、降低任务级 `required_evidence_levels` 的下限（`max(required_evidence_levels)` 下降，或元素移除后下限随之下降）、改写某条的 `test_ref` 或 `command_ref`、扩大 `allowed_paths`、收窄 `forbidden_paths`、删除非目标条目都判 `loosened: true`，必须带 `--adjudication`；只收紧（新增测试、提高证据等级、抬高任务级下限、缩小允许范围）不需要裁决。
- **`dependencies` 的增删**只需 `--reason`，但修订后必须机械校验：每个依赖 id 都能按解析顺序（`docs/tasks/<id>.md` → `.pipeline/<id>/<id>.md` → `.pipeline/archive/<id>.md`）找到对应任务单，且依赖图不成环。
- **记录结构**：`revision` 从 2 起单调递增（revision 1 是冻结版，其哈希即 `.pipeline/<task-id>/goal.json` 里的 `task_sheet_sha256`），每条含 `at`、`by`、`requested_by`、`feedback_ref`、`reason`、`adjudication_ref`、`previous_sheet_sha256`、`sheet_sha256`、两个判据、`changes`（验收测试增删改、依赖增删、路径增删、非目标增删、风险前后值、证据等级增删、链路与 operation 变化）以及该版契约快照。记录是追加式的，旧条目字节不变，哈希链可逐条回溯。
- **原子性**：拒绝或校验失败时不追加任何条目、不改变任何哈希、不移动任何文件。
- **基准连锁**：`freeze_check`、lifecycle 的 `task_sheet_sha256` 漂移检查和 `freshness` 都以最新修订版的哈希为准，所以已登记的修订不再报漂移；未走 `task amend` 的直接改动仍报 `task sheet changed after freeze`。计划与契约一致性检查（`compare_task_plan_contract`）也以最新修订版为基准，依赖在规划后被修订时报告"规划后被修订过"并给出 `sheet_revision`，而不是裸的漂移错误。
- **终止条件**：合并后不再修订；需求变化重新规划或新建任务。执行/审查子代理始终不得改任务单，发现缺陷只提交结构化反馈（`requested_by` + `feedback_ref`）。

## Worktree 创建

任务单契约提交后，主代理从主工作树根目录创建唯一实现 worktree：

```bash
git worktree add -b "<branch>" ".worktrees/<task-id>" "<baseline-head>"
```

标准路径是 `<仓库根目录>/.worktrees/<task-id>`。`git worktree add` 会创建不存在的目标目录及缺失的 `.worktrees` 父目录，不需要先用 `mkdir`；不要因为目录尚未存在而改用仓库同级路径。创建前后都要用 `git worktree list --porcelain` 核对，并把核对后的绝对路径写入 dispatch 记录与任务锚点进度事件，不写入任务单——任务单只承载冻结契约。

项目根目录的 `.gitignore` 必须包含 `/.worktrees/`。如果缺少该规则，只有在任务单允许范围内补齐并记录后才能创建；否则停下报告范围问题。执行/审查子代理不得自行创建第二个 worktree，路径或分支冲突必须先 reconcile。

## 证据目录迁移

新任务使用 `<仓库根目录>/.pipeline/<task-id>/` 和 `.pipeline/metrics/`。任何工具命令发现旧 `.workflow/` 时，必须在继续执行前自动把它原样移动为 `.pipeline/`，核对全部文件哈希不变，再更新任务单/报告/机器 JSON 中的路径引用；若 `.pipeline/` 已存在则停止并报告冲突，不得覆盖或双写。不要删除历史证据，也不要复制文件造成重复统计。

## 产品替换的测试迁移

删除或替换旧行为时，任务单须列出：

| 旧测试或旧契约 | 保留的产品不变量 | 决定 | 新测试或新契约 |
|---|---|---|---|
| `<path>: <test>` | `<what remains true>` | 保留/迁移/替换/删除 | `<exact test>` |

特别检查取消清理、超时、幂等、日志脱敏、竞态、权限和持久化恢复等隐藏不变量。旧用户路径保留 ≠ 旧二进制协议和旧数据格式必须保留；两者分别写明。
