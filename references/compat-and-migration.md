# 版本兼容与迁移

本文件收纳技能版本历史、`.workflow/` 目录迁移规则和一次性优化动作。这些是低频读取的参考信息，不随每次任务加载；运行时指令以 `SKILL.md` 为准。

## 版本升级与兼容性

### 目录结构变化

- **v0.10.0 → v0.11.0**：移除“每个任务必须写握手 JSON 文件”的强制要求，改用模板化环境检查列表；证据文件改为失败时保存，成功时不保存。`pipeline-tools runtime handshake` 命令仍然存在，它是可选的能力检查，写入 `capability-handshake.json`，与已移除的强制握手 JSON 不是同一件事。
- **旧版本迁移**：`.workflow/<task-id>/` 目录在新版本工具首次发现时自动迁移到 `.pipeline/<task-id>/` 并校验；若 `.pipeline/` 已存在则报告冲突并停止，不覆盖、不双写。迁移由 `pipeline_tools/layout.py` 的 `migrate_layout` 执行，事件契约层面的细节见 `references/metrics-contract.md`。

### 向后兼容性

- 已存在的 `.pipeline/` 目录结构完全兼容新版本
- 旧版握手 JSON 文件（如果存在）不影响新版本工作流，主代理使用环境检查列表机制
- 成功任务目录只保留 7 个最终化文件（`RETAINED_EVIDENCE_NAMES`），其余过程产物由 `finalize_evidence` 清理；历史里遗留的漂移证据不重写 Git 历史，改用 `scope history --since <commit>` 前向基线闸门约束新提交，规则见 `references/acceptance-evidence.md`

### 升级建议

- 更新技能版本后，主代理在下次任务启动时自动使用新的环境检查列表机制
- 不需要手动清理旧版握手 JSON 文件或证据文件，但可选择清理成功任务的原始输出以节省空间
- 历史提交里的旧证据保留在原处；新提交按保留集和前向基线闸门审查，不追溯重写
- `.pipeline/metrics/` 是指标历史，必须纳入 Git 追踪，不应加入项目 `.gitignore`
- 角色进度日志 `.pipeline/*/*-progress.jsonl` 是过程记录，由项目根目录 `.gitignore` 规则排除，不得进入 Git

`.pipeline/metrics/` 与进度日志的完整规则见 `references/metrics-contract.md` 的「进度日志不进入 Git」一节。

## 自动优化机制

主代理在任务启动的「恢复核对」阶段执行以下优化操作（除注明外均为主代理职责，不是 `pipeline_tools` 的自动行为）：

- **清理已合并的 worktree**：任务成功合并后由主代理删除该任务的 worktree（包括其中的原始输出）；`pipeline_tools` 只创建和校验 worktree，没有自动清理命令
- **应用新证据策略**：新任务执行时按"失败保存、成功不保存"规则处理证据文件，由 `pipeline-tools planning evidence-finalize` 机械执行；成功任务的保留集见 `references/acceptance-evidence.md`
- **环境检查升级**：主代理在派发子代理前使用模板化环境检查列表，替代旧版握手机制，见 `SKILL.md` 的「机械工具与项目级反馈」一节
- **目录结构校验**：主代理确认 `.pipeline/` 目录结构符合当前版本要求；旧 `.workflow/` 目录由 `pipeline_tools` 首次访问时自动迁移，规则见上文

`.pipeline/` 的内容分工：`.pipeline/metrics/` 纳入 Git 追踪；`.pipeline/<task-id>/` 存放阶段报告与机器结果，成功任务最终化后只保留 7 个保留文件；角色进度日志 `.pipeline/*/*-progress.jsonl` 由项目 `.gitignore` 排除，不得进入 Git。

提交顺序遵循 `SKILL.md`「标准生命周期」的合并复验一步：在 worktree 中提交实现代码和报告文档，再合并到主分支，合并成功后清理 worktree。

以上优化在主代理的「恢复核对」阶段执行，不影响正在进行中的任务。