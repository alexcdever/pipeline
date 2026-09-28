# 验收矩阵与证据完整性

## 验收测试必须可执行

每条验收测试绑定：精确测试文件和用例名；触发动作和输入；具体断言（成功、失败、持久化、恢复边界）；完整命令、工作目录、环境前置和超时；当前轮次的实际输出、退出码和产物路径。

机器编排的权威输入输出应使用当前任务目录中的 `dispatch.json`、`executor-result.json`、`reviewer-result.json` 和 `final-result.json`。Markdown 报告保留给人类阅读；`result verify` 与 `freshness` 必须先通过，语义代理的 recommendation 才能进入下一阶段。

这三份机器结果 JSON 不只是补充记录，而是 **pre-merge gate 的必需项**：`gate` 要求 `executor-result.json`、`reviewer-result.json`、`final-result.json` 三者存在且各为 JSON 对象。只有 Markdown 报告、缺任何一份机器结果，pre-merge gate 直接 FAIL。

报告里的 `commands[]` 条目每条可带可选字段 `cwd`（该命令实际运行的工作树的绝对路径）。post-merge gate 要求 `final-check.md` 里至少有一条 `exit_code == 0` 且 `cwd` 解析到主工作树根的命令，否则判定「合并后复验缺失」（`cwd` 缺省时回退到报告级 `worktree`）。

`commands[]` 条目还可带可选字段 `expected_exit_code`（整数），用于记录**故意的非零结果**。语义：未声明 `expected_exit_code` 时，`exit_code` 必须为 `0`；声明了它时，`exit_code` 必须等于它（允许非零，但必须显式声明），二者不符即判失败。`expected_exit_code` 本身必须是整数，否则报错。这样把一个真实的非零结果从「只能删除」变成「必须显式声明」——机器仍能核验，且声明本身可审查。

“跑全量测试”、“功能正常”或“所有验收测试通过”都不是验收证据。

## 事实与结论边界

报告按“观察、结论、未验证项”区分：只有本轮直接运行或读取的结果才能作为事实；无法读取原始输出、产物或当前代码时，结论必须是 `BLOCKED` 或“未验证”，不能根据代理自述、通知或相似历史任务补全。

## 验收台账

每条验收测试一行。契约中的稳定 ID 使用 `acceptance-test-*` 完整形式；新 schema 2/3 任务单、台账、模板和 evidence 示例不得使用诸如 `AT1`、`AT2B` 的缩写。旧 schema 1 契约仅保留历史读取兼容，新任务不得以该兼容规则生成缩写 ID。台账是过程记录，写在 `.pipeline/<task-id>/` 的进度日志和阶段报告中，不写入任务单。

| 字段 | 要求 |
|---|---|
| 验收测试 | 与当前任务单完全一致 |
| 测试 | 当前文件和精确用例名 |
| 行为 | 证明的产品不变量 |
| 命令 | 实际运行的完整命令 |
| 结果 | 当前输出、退出码和超时边界 |
| 复验 | 审查子代理直接运行或检查的结果 |

验收测试的 `test_ref` 必须指名真实存在的位置：文件必须存在，且当 `test_ref` 写出 `文件: 类名.方法名` 时，该符号必须在文件里真实声明。规划期另有一层位置校验：`test_ref` 指名的文件必须落在任务资源的 `allowed_paths` 之内（当任务声明了与测试同目录树的资源时）。两层规则分别由 `pipeline_tools/planning.py` 与 `pipeline_tools/core.py` 的 `gate` 机械核验，语义判断仍归大语言模型。
| 证据 | 当前任务的报告或原始输出路径 |

缺任何一项不得标记 PASS。

## 矩阵而不是测试数量

测试数量增长、全量命令为绿色或报告声称"完整矩阵"都不能证明覆盖。审查时直接读高风险测试正文，确认：表格参数真正影响 fixture/输入/故障点；每变体有不同断言；期望值不是从被测路径重算的；无 `undefined === undefined`、空数组往返、自比较或恒真断言；多进程、重启、回滚、互斥和隔离用真实边界，而非同进程 Promise 并发或手写终态。

## 证据身份和新鲜度

每份报告必须标明：task-id、worktree、branch、角色、轮次、生成时间、当前测试数量和关键命令；报告目录与任务单必须完全同名。

失效情形：引用其他任务/worktree/旧 branch；worktree 在报告后继续变化而未重生成；reviewer 只复制执行报告；报告只有结论没有命令和断言；任务单验收测试或范围已变而无对应 `derived` 任务（任务类型写 `derived`，机器 ID/path 保留 `continuation`）。

### 证据引用解析基准

`commands[].evidence_ref` 与 `acceptance[].evidence_refs` 使用**同一解析基准**：两者都以**证据目录**（`.pipeline/<task-id>/`）为相对根。裸文件名（如 `test.log`、`executor-report.md`）解析到证据目录；显式以 `.pipeline/` 开头的引用仍从项目根解析。绝对路径和包含 `..` 的穿越引用一律判为非法，`freshness` 报 `evidence artifact missing`。

`acceptance[].evidence_refs` 的解析必须复用 `pipeline_tools/core.py` 的 `_evidence_file_exists`，不得另写一套基准，否则同一份 `executor-result.json` 里 `commands[]` 能过而 `acceptance[]` 报缺失。

### evidence_only 与 `.pipeline/metrics/`

`evidence_freshness` 用 `evidence_only` 判断 `product_head..HEAD` 的改动是否全部落在证据目录内。`.pipeline/metrics/` 是工作流元数据（见 `references/metrics-contract.md`），始终豁免：`is_metrics_path` 命中的路径不破坏 `evidence_only`，与 `scope_check` 口径一致。否则任何跑过 pipeline-tools 的任务都会因 metrics 事件翻转为 `evidence_only: false` 并误报 `product/test HEAD drifted`。产品代码、测试或证据目录之外的其它改动仍照常触发 `product/test HEAD drifted`。

## 证据等级

1. 领域/算法单元测试；
2. 协议、核心服务和持久化集成测试；
3. 组件或前端测试；
4. 真实浏览器/桌面/移动端用户路径；
5. 多进程、真实网络或真实设备 E2E。

任务单必须声明每条验收测试的证据等级；低等级通过不能替代高等级验收。低等级测试全绿、全量命令为绿色或退出码为 0，都不构成高等级验收的证据。

### 证据等级下限

`pipeline_tools/contract.py` 的 `evidence_floor(risk, project_type, task_type)` 是唯一的计算来源，`templates/task-sheet.md` 和 `pipeline-tools task validate` 都按它执行。规则：

1. 起算值取 `risk`：`low` = 1、`medium` = 2、`high` = 3。
2. 当 `risk` 不是 `low` 且 `project_type` 在 `{web, desktop, multi-process}` 内时，取与 `EVIDENCE_FLOOR_BY_PROJECT_TYPE` 的较大值：`web` = 3、`desktop` = 3、`multi-process` = 4。`risk` 为 `low` 时项目类型不下调也不上调下限，仍为 1。
3. 当 `task_type` 是 `vertical-feature` 时，取与 `VERTICAL_FEATURE_EVIDENCE_FLOOR` = 2 的较大值。
4. `project_type` 缺省是 `service`，它不在项目类型表里，因此不改变下限。

按项目类型的样例（`risk` 取 `medium` 起算值 2）：

| project_type | risk | task_type | 下限 | 理由 |
|---|---|---|---|---|
| `library` | `medium` | `repair` | 2 | 项目类型不参与，只剩 risk 的 2 |
| `cli` | `medium` | `repair` | 2 | 同上 |
| `service` | `medium` | `vertical-feature` | 2 | 项目类型不参与；vertical-feature 下限 2 与 risk 持平 |
| `web` | `medium` | `repair` | 3 | 项目类型把下限抬到 3 |
| `desktop` | `high` | `repair` | 3 | risk 3 与项目类型 3 取大 |
| `multi-process` | `medium` | `prerequisite` | 4 | 项目类型 4 是最高的，压过 risk 2 |
| `library` | `low` | `vertical-feature` | 2 | low 不触发项目类型，但 vertical-feature 抬到 2 |
| `multi-process` | `low` | `repair` | 1 | risk 为 low 时项目类型不下调，下限保持 1 |

契约里每条 `acceptance_tests[].evidence_level` 都不得低于该任务的下限；`pipeline-tools task validate` 会报 `evidence_level N is below the required floor M`。

## 时间限制

单条测试或命令默认三分钟硬上限，超时停止诊断；整套测试用更大的明确累计上限，不把单条三分钟机械当全套三分钟。网络、子进程、数据库锁和后台 worker 双方都要有界等待；失败后收集现场退出，不留无限等待进程。后台监督与完成通知不能替代验收。

## 结论分类

状态：`PASS`、`FAIL`、`BLOCKED`、`FLAKY`、`EXPLORATORY_ONLY`。重试后通过是 `FLAKY` 不是干净 `PASS`；缺真实 API 是 `BLOCKED`，不是降级断言后的 `PASS`。

证据最终化必须先将待清理 raw evidence 移入同目录临时暂存区，完成清理并移除暂存区后，才可原子写入 `finalization.json`。任何清理异常都必须回滚暂存移动、删除临时 marker、返回 `blocked`，并保留 raw evidence 的路径与字节；相同故障重试不得留下 marker，故障解除后重试才可完成且重复成功幂等。

## 保留证据集

一个成功完成并已最终化的任务目录，只保留 7 个文件：`executor-report.md`、`review-report.md`、`final-check.md`、`executor-result.json`、`reviewer-result.json`、`final-result.json`、`finalization.json`。其余过程产物（原始命令输出、acceptance 日志、握手 JSON、探针脚本等）在最终化时清理，不留在任务目录里。

这 7 个名字是**唯一的保留集**，由 `pipeline_tools/core.py` 的 `RETAINED_EVIDENCE_NAMES` 单点定义，`commit_history_check` 和 `finalize_evidence` 共用同一常量。新增或删减保留文件必须改这一处，不允许在两个模块里各写一份硬编码清单。

`commit_history_check` 对 `.pipeline/<task-id>/` 下的提交逐条扫描，并按 Git 状态区分方向：新增（`A`）和修改（`M`）的文件名不在保留集内即报违规；删除（`D`）只在被删文件**属于保留集**时报违规——清理非保留证据是契约要求的动作，删除保留文件才是不可接受的漂移。`-progress.jsonl` 进度日志无论方向都额外单独报 `progress log must not enter Git`。`.pipeline/metrics/` 的指标事件始终豁免——它们是可审查的流水线历史，规则见 `references/metrics-contract.md`。

## 前向基线闸门

历史里已存在的漂移证据不重写 Git 历史。`scope history` 子命令默认扫描全部可达历史（等价 `--all`），可选用 `--since <commit>` 把扫描范围收窄到 `<since>..HEAD`：基线之前的违规不再报告，基线之后新引入的违规照常报告。

`--since` 是**前向闸门**，不是豁免：省略时行为与旧版本完全一致，逐条扫描全部历史。`pipeline-tools scope history <root> --evidence-root <path> [--since <commit>]`；存在违规时退出码 4（`DRIFT`），干净时退出码 0（`PASS`）。
