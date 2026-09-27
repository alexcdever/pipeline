# 执行子代理与审查子代理

## Worktree 身份

主代理在契约提交后创建唯一的 `<仓库根目录>/.worktrees/<task-id>`，并在 dispatch 中传入绝对路径。执行子代理和审查子代理必须先核对该路径、branch、task-id 与 `git worktree list --porcelain` 一致，再在指定 worktree 工作；不得自行运行 `git worktree add`，不得改用仓库同级目录或为同一任务创建第二个 worktree。独立审查上下文不要求新建 Git worktree。工具首次访问任务证据时会自动把 `.workflow/<task-id>/` 迁移为 `.pipeline/<task-id>/`，并核对文件哈希、路径引用和工具测试；若 `.pipeline/` 已存在则报告冲突并停止。迁移完成后不能继续写入旧目录。

## 执行期 implement-plan 哈希稳定性

`implement-plan.md` 的 sha256 在规划、任务生成和执行期间必须稳定（implement-plan.md 第 39 行）。`pipeline_tools/core.py` 为此提供两个函数：

- `implement_plan_status(root, contract, task_id=None)`：比较契约记录的哈希与实时文件的哈希，返回**四元组** `(errors, recorded, observed, unverified)`（`pipeline_tools/core.py:912-951`）。调用方必须按四元组解包；只解三元的代码会抛 `ValueError`。`recorded` 的完整回退顺序是：契约的 `implement_plan.sha256` → `.pipeline/planning/*/dispatch.json|lifecycle.json|result.json` 里的 `requirements_sha256`（或 `identity.requirements_sha256`，见 `_planning_requirements_sha256`，`pipeline_tools/core.py:875-894`）→ `.pipeline/<task-id>/implement-plan.json` 里的 `sha256`（见 `_recorded_implement_plan_sha256`，`pipeline_tools/core.py:897-909`）。
- 第四个返回值 `unverified` 是未验证项列表，不是可以忽略的附加信息：任务没有记录哈希时，即使文件可读、`errors` 为空，也会返回 `implement-plan hash unrecorded: <path>`；既无记录又读不到文件时返回 `implement-plan hash unrecorded and plan unreadable: <path>`（`pipeline_tools/core.py:943`、`:950`）。这表示哈希未被强制，必须按未验证处理，不能当作通过。
- `_record_implement_plan_hash(root, task_id, observed)`：把观察到的哈希写入 `.pipeline/<task-id>/implement-plan.json`（内容为 `{"schema": 1, "task_id": ..., "sha256": observed}`，`pipeline_tools/core.py:963`），让后续阶段能继续强制它。创建 worktree 后调用一次；冻结检查也会调用它（见下）。

执行时的检查点：

- 派发（`create_worktree_dispatch`）时会调用 `implement_plan_status`；任何漂移都返回 `blocked`，并给出 `re-plan before continuing`，不会创建 worktree。
- 冻结检查（`freeze_check`，即 `task preflight` / `task freeze-check`）在传入 `--task-sheet` 时会再查一次，并且**有写副作用**：它调用 `_record_implement_plan_hash` 把本次观察到的哈希持久化到 `.pipeline/<task-id>/implement-plan.json`。因此这两个命令不是纯只读的身份检查——它们会创建或更新该证据文件。哈希漂移仍然会让 `errors` 非空，不会因为写入而被掩盖。`unverified` 只在调用方传入列表时回传；两个命令在文本输出里打印 `UNVERIFIED: ...`，在 `--format json` 下把同一列表放进结果的 `unverified` 字段。未记录哈希不是失败，但也不是通过。
- 新鲜度检查（`evidence_freshness`）会记录 `implement_plan_recorded` 与 `implement_plan_observed` 两个观察项，漂移计入 `errors`。

结论：哈希漂移等于需求在执行期被改动，正确反应是**停下重新规划**，不是放宽断言、改契约或继续合并。审查子代理和主代理终检都不得把漂移解释成可接受的差异。

## 执行子代理

收到的是已提交且冻结的任务单，不是可自由重写的目标。标准循环：

1. 读任务单和项目规则，确认 task-id、branch、worktree 与允许范围。
2. 每个行为先写失败测试，真实运行确认按预期失败；失败原因不符合预期时先诊断，不进入实现。
3. 最小实现使测试通过。
4. 重构、补边界和回归，保持全绿。
5. 跑任务单指定的验收命令、构建、lint 和范围检查；失败先分类为产品、测试、环境或契约问题，不静默重试、放宽断言或改超时。
6. 写当前任务 `executor-report.md`：改动、命令、结果、未完成项和环境限制。

不得：改契约/删困难验收测试/扩范围；用 mock 代替任务要求的真实核心、数据库、浏览器或设备链路；把环境缺失写成产品通过；用其他任务报告证明当前任务；在主工作树直接改产品代码。

## 审查子代理

从独立上下文开始，先核对：任务单已提交；worktree 和 branch 匹配；当前报告属当前 task-id 且本轮生成；每条验收测试有对应测试和证据。然后独立执行：

1. 读生产代码、测试正文和差异，不只看执行报告。
2. 逐条复跑当前验收测试（含失败路径、边界、持久化、恢复）。
3. 查实现是否超范围、是否改变未声明的协议/数据格式/用户行为。
4. 查真实链路是否被单元/mock 测试替代。
5. 查日志脱敏、有界等待、清理幂等、并发和隔离。
6. 写 `review-report.md`，给出每条验收测试的独立结论。

默认只读；无法直接写报告时留下可归属的审查输出，由主代理按真实来源补齐，不冒充审查子代理写入。缺少当前原始证据时必须标 `BLOCKED`，不能按执行子代理自述判 PASS。

## 主代理最终检查

不能只接收 "review PASS" 就合并，必须：

- 重读任务身份、Git 状态、worktree 列表和 branch ancestry；
- 查三份当前任务报告存在、非空、身份正确且新鲜；
- 抽查代表性高风险断言；
- 后台监督结果（若有）只是生命周期证据，不作验收结论；
- 独立运行关键验收测试、全量测试、构建、lint、差异和冲突检查；
- 结论写入 `final-check.md`；过程记录（任务锚点、验收台账、执行记录）写入 `.pipeline/<task-id>/` 的角色进度日志和阶段报告，不写入任务单；每条验收测试有当前证据；
- 全部 PASS 且无未裁决阻塞才进入合并；最终报告同时列出已观察事实和未验证项。

主代理最终检查是第三层验证，不应变成"抄 reviewer 的摘要"。
