# pipeline

服务于大语言模型与具备子代理机制的 agent 软件的编程工作流，以及配套的 Python 机械闸门工具。

## 工作流边界

- 主代理负责任务拆分、冻结契约、真实设计判断、独立审查调度和最终裁决。
- 执行子代理在隔离 worktree 实现冻结任务。
- 审查子代理从独立上下文复验。
- `pipeline_tools` 只校验机械事实：契约结构、Git 身份、范围、命令退出码、证据身份和本地统计；它不判断产品语义，也不自动合并。

默认项目约定：

- 任务单：`docs/tasks/<task-id>.md`
- 正式任务证据：`.pipeline/<task-id>/`（仅阶段报告、机器结果和 `finalization.json`；成功收敛前的临时文件不属于交付）
- 恢复索引：`.pipeline/recovery-index.json`；规划中间审计和 stage 文件写入系统临时目录 `pipeline-tools/planning/`，项目只保留恢复索引
- 临时目录与原始日志：系统临时目录下的 `pipeline-tools/`；`command run` 未指定 `--log` 时不会写入仓库
- 项目级统计：`.pipeline/metrics/`（由工具自动生成；是否纳入 Git 由项目开发者决定）
- 执行 worktree：`.worktrees/<task-id>`（主代理从主工作树创建唯一目录）
- 任务契约提交后冻结，任务单不可变；需要改变契约时新建 `derived` 任务，不回写原任务单
- 任务级状态只由 lifecycle API/CLI 管理；状态写入（`transition`、`event`）只允许主代理角色接口（`role=main-agent`），其他角色只能读取或报告 findings
- 任务单只承载冻结契约与人类可读的契约说明；过程记录和阶段报告写入 `.pipeline/<task-id>/`，不另行维护项目级状态文档
- 跨会话优先使用 `lifecycle resume/status/list/inspect` 恢复和读取任务状态，不从通知、自然语言报告或项目级状态文件推断
- 合并前需要执行、独立审查和主代理终检；实现提交与 `.pipeline/<task-id>/` 正式 evidence 提交分开；合并后在主工作树复验并单独提交 post-merge evidence
- 审批策略：`.pipeline/config.json` 的 `approval_mode`（`automatic` | `manual`）是项目级默认，解析顺序为显式参数 → 运行记录 → 项目配置 → 默认 `automatic`；该文件需手工创建，没有命令会写入它

## 任务类型与命名

契约里的任务类型 token 只有四个（`pipeline_tools/contract.py` 的 `TASK_TYPES`）：`vertical-feature`、`prerequisite`、`repair`、`derived`。选择依据是任务与用户功能的关系，不是工作量：

- `vertical-feature`：交付一条完整用户链路（入口 → 交互 → 应用处理 → 领域事实 → 持久化 → 回读 → 恢复），有真实外部入口和可观察的用户结果。链路段不允许豁免，证据下限至少 2。
- `repair`：修复已有用户功能链路上的缺陷；按 `vertical-feature` 的标准覆盖完整链路，链路段同样不允许豁免。
- `prerequisite`：只产出被后续任务消费的底座（schema、协议、算法、持久化、构建或环境能力）。契约必须写明 `non_user_completion_reason`；链路段允许结构化豁免。
- `derived`：从一个父任务的明确提交派生出的新任务，重新生成独立任务单，不复用父任务的证据。包含设计变更后按裁决重开的那一类。

**命名统一**：任务类型字段写 `derived`，机器 id 和路径前缀保留 `continuation`——两者指同一件事，必须成对出现。`create_derived_dispatch(..., continuation=True)` 要求子任务 id 含 `continuation`。`derived` 子契约逐字段复制父契约、只覆盖 `task_id`/`task_type`/`dependencies`/`derived_from`，因此它不继承父类型的链路段强制、`vertical-feature` 证据下限加成和 `prerequisite` 的 `non_user_completion_reason` 要求；详见 `references/task-design.md` 的「`derived` 子任务继承什么、不继承什么」。

创建实现 worktree 时，从仓库根目录执行：

```bash
git worktree add -b "<branch>" ".worktrees/<task-id>" "<baseline-head>"
```

`git worktree add` 会创建目标目录及缺失的 `.worktrees` 父目录，不需要预先 `mkdir`。项目根目录的 `.gitignore` 应包含 `/.worktrees/`。执行和审查子代理只使用主代理传入的 worktree，不自行创建第二个目录。

## 机械工具

Python 3.11 标准库即可运行；不联网、不遥测、不上传数据：

```bash
python -m pipeline_tools --help
python -m pipeline_tools task validate docs/tasks/<task-id>.md
python -m pipeline_tools task preflight . --contract <frozen-commit> --task-sheet docs/tasks/<task-id>.md
python -m pipeline_tools scope check . --allowed 'src/**' --forbidden '**/.env'
python -m pipeline_tools command run --cwd . --timeout 180 -- python -m unittest  # 原始日志默认进入系统临时目录
python -m pipeline_tools evidence verify .pipeline/<task-id> --task-id <task-id> --branch <branch>
python -m pipeline_tools gate pre-merge .pipeline/<task-id> --task-id <task-id> --branch <branch>
python -m pipeline_tools gate post-merge .pipeline/<task-id> --task-id <task-id> --branch <branch>
```

退出码：`0` 通过、`1` 被执行命令失败、`2` 参数/配置错误、`3` 证据不足或环境阻塞、`4` 身份/契约/范围漂移。

新任务单使用 `templates/task-sheet.md`，填完后复制其 `pipeline-contract` 区块；用 `templates/pipeline-evidence.json` 为 executor、reviewer 和 main-final 报告生成机器证据。空模板本身故意不能通过校验，填入真实字段后才应通过。

## 项目级反馈

除 `metrics` 子命令外，所有 `pipeline-tools` 阶段命令默认自动记录一个结构化指标事件到
目标项目的 `.pipeline/metrics/`。该目录由工具自动创建和写入；是否把它纳入 Git 由项目开发者
决定，技能既不要求也不禁止（本仓库把 `.pipeline/metrics/` 加入了 `.gitignore`）。自动采集
只使用命令退出码、结构化结果和可定位的证据路径，不会从自然语言报告推断产品结论，也不会
记录 token、凭据、完整命令输出或业务数据。

自动采集可以通过环境变量 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` 暂时关闭（仅用于测试或
明确的诊断场景）；正常任务执行不要关闭。`metrics` 子命令本身不递归生成阶段事件，但
`metrics record` 仍可用于补充经过直接证据确认的事件。

```bash
python -m pipeline_tools metrics record . retry --confidence observed --task-id <task-id> --result unknown --attempt 1
python -m pipeline_tools metrics report .
python -m pipeline_tools metrics report . --task-id <task-id> --terminal-only
python -m pipeline_tools metrics export . .pipeline/metrics-summary.json
python -m pipeline_tools metrics purge .
python -m pipeline_tools metrics import-opencode-session . <session-export.json> --task-id <task-id>
python -m pipeline_tools runtime preflight . --node 22.23.2 --pnpm 10.27.0
python -m pipeline_tools runtime handshake . .pipeline/<task-id> --role reviewer --node 22.23.2 --pnpm 10.27.0
python -m pipeline_tools runtime role-scope . --role main-agent --product-pattern 'packages/**'
python -m pipeline_tools --format json --output .pipeline/<task-id>/task-validate.json task validate docs/tasks/<task-id>.md
python -m pipeline_tools --format json lifecycle resume . --task-id <task-id>
python -m pipeline_tools --format json lifecycle status . --task-id <task-id>
python -m pipeline_tools --format json lifecycle list .
python -m pipeline_tools --format json lifecycle inspect . --task-id <task-id>
# 兼容旧版证据查询：仍支持 --evidence
python -m pipeline_tools --format json lifecycle status . --task-id <task-id> --evidence .pipeline/<task-id>
python -m pipeline_tools dispatch write dispatch.json .pipeline/<task-id>/dispatch.json
python -m pipeline_tools result verify .pipeline/<task-id>/reviewer-result.json --task-id <task-id> --role reviewer
python -m pipeline_tools --format json freshness . .pipeline/<task-id> --result .pipeline/<task-id>/reviewer-result.json
python -m pipeline_tools --format json evidence readiness .pipeline/<task-id> --task-id <task-id>
```

自动事件和 `metrics record` 事件都逐文件原子写入 `.pipeline/metrics/`。只有 `observed` 和 `derived` 进入核心聚合；`reported` 只留作追溯。新版本工具第一次访问已有 `.workflow/` 项目时会自动把整个目录原样迁移到 `.pipeline/`，核对文件哈希并将后续工具写入路径统一切换到 `.pipeline/`；不会改写 evidence 文件内部的历史文本引用。若 `.pipeline/` 已存在则停止并报告冲突，不会覆盖或双写。详见 `references/metrics-contract.md`。

`metrics import-opencode-session` 只从 OpenCode Desktop 的结构化导出中提取可验证的工具错误、子代理错误和用户流程纠正信号；不会把自然语言 PASS 当作验收事实。`runtime preflight` 应在派发 executor/reviewer 前执行，`runtime role-scope` 用于阻止未授权的主代理产品代码修改。

`runtime handshake` 是可选的能力检查，写入 `<workflow>/capability-handshake.json`，记录仓库可读、workflow 可写、产品代码写权限与 runtime 状态；它不是被移除的那个强制握手机制，新任务不依赖该命令也能完成闭环。版本差异见 `references/compat-and-migration.md`。

角色进度日志 `.pipeline/<task-id>/<role>-progress.jsonl` 是过程记录，由 `.gitignore` 规则 `.pipeline/*/*-progress.jsonl` 排除，不进入 Git；规划 stage、规划中间审计和原始日志优先写入系统临时目录 `pipeline-tools/`，项目侧仅保留 `.pipeline/recovery-index.json` 用于恢复索引，不把临时产物当正式 evidence。正式任务 evidence 仍在 `.pipeline/<task-id>/`；pre-merge 必须先提交包含 `final-check.md`/`final-result.json` 在内的完整报告和机器结果集合以满足 gate，merge 后主工作树更新这些同名文件并提交 `final-check.md`、`final-result.json`、`finalization.json` 作为独立 post-merge evidence；`.pipeline/metrics/` 的指标事件不受这条规则约束，是否纳入 Git 由项目开发者决定（本仓库把 `.pipeline/metrics/` 加入了 `.gitignore`）。正式 `evidence verify` 前先执行 `evidence readiness`，避免把尚未生成 final-check 的正常阶段顺序误报为最终证据缺陷。

结构化命令使用统一响应外壳：`schema`、`command`、`status`、`exit_code`、`observed`、`errors`、`blockers`、`artifacts`、`next_actions` 和 `unverified`。JSON 文件是流程编排输入，终端摘要只用于人类查看。

结构化闭环顺序为：`dispatch write` → agent 写入 `executor-result.json`/`reviewer-result.json` → `final-check` → `evidence readiness` → `result verify` → `freshness` → `lifecycle status` → merge gate。跨会话恢复时先用 `lifecycle resume/status/list/inspect`，再读取 `.pipeline/recovery-index.json` 和正式 evidence；Markdown 报告用于人类阅读，JSON 结果用于机械编排。

## 测试

```bash
python -m unittest discover -s tests -v
```

Windows 入口：`bin\pipeline-tools.cmd`；POSIX 入口：`bin/pipeline-tools`。两者会把工具根目录加入 Python 模块搜索路径，因此可以从其他工作目录调用。

## 许可证

MIT，见 `LICENSE`。
