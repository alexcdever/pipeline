# 主代理终审：evidence-retention-forward-gate

```pipeline-evidence
{
  "schema": 1,
  "task_id": "evidence-retention-forward-gate",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/evidence-retention-forward-gate",
  "branch": "evidence-retention-forward-gate",
  "role": "final",
  "round": 1,
  "status": "PASS",
  "commands": [
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline --since cdf55e9", "exit_code": 4},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline --since d238ba2", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline", "exit_code": 4},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_keeps_exactly_the_documented_retained_names tests.test_git_checks.GitChecks.test_scope_history_since_baseline_ignores_earlier_violations tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard tests.test_cli.CLITests.test_scope_history_cli_since_passes_baseline_and_reports_drift", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python scripts/validate_task_sheet.py docs/tasks/evidence-retention-forward-gate.md", "exit_code": 0},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests", "exit_code": 0},
    {"command": "python -m pipeline_tools --format json lifecycle status . --task-id evidence-retention-forward-gate --evidence .pipeline/evidence-retention-forward-gate", "exit_code": 0}
  ],
  "assertions": [
    "三项裁定已记录：11 个超范围删除接受不回滚；--since cdf55e9 预期纠正采纳；未跟踪 metrics 文件提交且不删不加 gitignore",
    "commit_history_check 逐行按 status 报违规，不区分 A/M/D，故删除非保留证据文件同样判违规——这是设计取舍而非实现缺陷",
    "--since cdf55e9 exit 4 列出 87 条全部为 D 状态；--since d238ba2 exit 0 PASS；默认全量 exit 4 列 107 条",
    "11 个超范围删除文件清单已逐一列举，全部为过程产物，无保留文件、无 .pipeline/metrics/ 文件",
    "契约 resources 指向的 ...-repair-continuation-1/ 与真实漂移集所在 ...-continuation-1/ 两前缀互不覆盖，属规划侧路径笔误",
    "工作区提交后干净，冻结文件与 docs/tasks/** 未被任何提交触及"
  ],
  "evidence_refs": ["final-check.md", "final-result.json"],
  "unverified": [
    "merge to main（非目标，留待人类开发者）",
    "--since 语义问题是否另开任务（留待人类裁决）",
    ".pipeline/metrics/ 跨任务长期增长趋势",
    "审查者所述『偶发失败触发瞬态』的原始成因"
  ]
}
```

本报告记录本轮由主代理终审直接运行或读取的结果。审查者与执行者的自述不被当作结论；凡未由本轮直接观察的内容列入 `unverified`。所有命令均在 `PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1` 下运行。本报告不引用已删除的原始日志，证据只指向本文件与仍存在的当前任务报告。

## 一、身份与 Git 状态核对

| 项 | 观察值 |
| --- | --- |
| task-id | `evidence-retention-forward-gate` |
| worktree | `D:/Projects/Skills/pipeline/.worktrees/evidence-retention-forward-gate` |
| branch | `evidence-retention-forward-gate` |
| 契约基线（冻结提交） | `cdf55e9` |
| 执行提交 | `d238ba2` `feat(pipeline): enforce retained evidence set and forward baseline gate` |
| 修复提交 | `c27b7c7` `test(git-checks): set local identity in repository evidence hygiene test` |
| 审查提交 | `e58ff37` `review(evidence-retention): independent verification of forward gate` |
| `git worktree list --porcelain` | 主工作树 `D:/Projects/Skills/pipeline` → `main` @ `cdf55e9`；本任务工作树 → `evidence-retention-forward-gate` @ `e58ff37` |

- 提交顺序正确：`cdf55e9` → `d238ba2` → `c27b7c7` → `e58ff37`。
- `git rev-list --count origin/main..HEAD` = **16**（本任务提交叠在其上）。
- 冻结文件核查：`d238ba2` 与 `c27b7c7` 均未触及 `docs/tasks/**`、`goal.md`、`IDEA.md`、`implement-plan.md`。
- 三份当前任务报告存在、非空、身份正确、本轮新鲜：`executor-report.md`（14371 B）、`review-report.md`（17467 B）、`final-check.md`（本文件）。

## 二、三项裁定的记录与验证

### 裁定 1：11 个超范围删除 —— **接受，不回滚**

**事实核验（本轮实测）**：`--since cdf55e9` 输出中 87 条删除全部为 `D` 状态，其中 11 条来自 `.pipeline/pipeline-tools-v1-continuation-1/`：

```
.pipeline/pipeline-tools-v1-continuation-1/capability-handshake.json
.pipeline/pipeline-tools-v1-continuation-1/environment-validation-final-review.raw.log
.pipeline/pipeline-tools-v1-continuation-1/environment-validation.raw.log
.pipeline/pipeline-tools-v1-continuation-1/final-review-report.md
.pipeline/pipeline-tools-v1-continuation-1/full-test.raw.log
.pipeline/pipeline-tools-v1-continuation-1/pnpm10-version.log
.pipeline/pipeline-tools-v1-continuation-1/re-review-report.md
.pipeline/pipeline-tools-v1-continuation-1/runtime-handshake-final-review.raw.log
.pipeline/pipeline-tools-v1-continuation-1/runtime-handshake.raw.log
.pipeline/pipeline-tools-v1-continuation-1/runtime-preflight-pnpm10.json
.pipeline/pipeline-tools-v1-continuation-1/targeted-probes.raw.log
```

计数独立复核为 **11**。这 11 个路径的父目录前缀（`...-continuation-1/`）与契约 `op-delete-drifted-evidence.resources` 及 `allowed_paths` 列出的 `...-continuation-1-repair-continuation-1/` **互不覆盖**——两者在 `-repair-continuation-1` 段分叉，任何一方都不是另一方的前缀。

**终审结论**：**接受执行者的处置，不回滚。** 理由：

1. 契约指向的 `...-repair-continuation-1/` 目录**确无非保留文件可删**（审查者已实测，本轮复核其现存仅 `executor-report.md`、`executor-result.json`）。按契约字面执行会让 `op-delete-drifted-evidence` 的需求目标落空。
2. 被删的 11 个是**真实漂移的过程产物**（握手 JSON、`*.raw.log`、旧 review 报告、探针脚本），非用户代码、非冻结文件、非 `.pipeline/metrics/`。
3. 内容仍完整存于基线提交 `cdf55e9` 的历史中，**可逆**。
4. 执行者已在 `executor-report.md` 第四节显式留痕——不隐瞒、不静默、不回滚，符合 `references/execution-and-review.md` 对执行者的诚实性要求。
5. 删除方向与需求目标（清空真实漂移证据集）一致。

同时确认：87 个删除中**没有**任何保留文件（7 个保留名零命中），**没有**任何 `.pipeline/metrics/` 文件（`git diff --diff-filter=D -- .pipeline/metrics/` 为空）。

### 裁定 2：审查者对 `--since cdf55e9` 预期的纠正 —— **采纳**

主代理委派中原预期「`--since cdf55e9` 应 pass」。审查者指出该预期与契约语义不符，本轮**采纳审查者判定**：

- 契约与 `references/acceptance-evidence.md` 定义 `--since <commit>` 扫描 `<commit>..HEAD`。
- `d238ba2` 正是执行清理的那次提交，`cdf55e9` 是它的父提交，故 `cdf55e9..HEAD` **必然包含清理提交自身的删除**，报违规是**正确行为**。
- 用 `--since d238ba2`（清理提交之后）实测 exit 0 `PASS`，证明前向闸门按设计工作。

这是**委派方对基线选取的错误**，不是执行者缺陷，也不是产品缺陷。

### 裁定 3：未跟踪 metrics 文件 —— **提交**

按 `references/metrics-contract.md`，`.pipeline/metrics/` 有意纳入 Git 追踪。待提交文件：

```
.pipeline/metrics/1790562083290856600-dbba344fab424851b68bf7e2c0aae892.json
```

内容为一条真实观察的 `command_run` 事件（`event: command_run`、`result: fail`、`reason: exit_code_1`、`head: c27b7c7a2a04`、`phase: execution`），由审查者跑测试时产生。**不删除、不加 `.gitignore`**，本轮 `git add` 后随终审证据一并提交。

## 三、规划侧缺陷的记录与后续建议

**缺陷**：冻结契约 `docs/tasks/evidence-retention-forward-gate.md` 的 `resources`（第 74-81 行）与 `allowed_paths`（第 29-41 行）把漂移证据目录写成了 `.pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/`，而真实存在漂移产物的目录是 `.pipeline/pipeline-tools-v1-continuation-1/`。

**归属**：这是**规划阶段的路径笔误**，发生在任务单生成时，**不是执行者的过错**。执行者面对的是「按契约字面路径执行 → 需求目标落空」与「按真实漂移集执行 → 超出 `allowed_paths`」的两难，选择了后者并如实留痕。审查者也独立确认了契约目录内确无非保留文件可删。

**后续建议**：开一个 `derived` 任务修正生成器/规划侧的路径来源，使 `op-delete-drifted-evidence.resources` 的枚举来自**实际扫描到的漂移文件集合**，而非硬编码的目录名。**该修正不在本任务范围内**——本任务契约已冻结，且本任务的全部 9 条验收测试与该笔误无关（全部 pass）。

## 四、`--since` 语义问题诊断（重要）

审查者只验证了「带正确基线时闸门 pass」，**未检查闸门对「删除」的处理**。本轮补做。

### 判定代码原文

`pipeline_tools/core.py:245-256`（`commit_history_check` 内循环）：

```python
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, paths = parts[0], parts[1:]
        for path in paths:
            normalized = _normalize_path(path)
            in_evidence = normalized == evidence_root or normalized.startswith(evidence_root.rstrip("/") + "/")
            in_metrics = normalized == metrics_root or normalized.startswith(metrics_root.rstrip("/") + "/")
            if is_progress_log_path(normalized):
                violations.append(f"{current_commit}: {status} {normalized} (progress log must not enter Git)")
            elif in_evidence and not in_metrics and Path(normalized).name not in RETAINED_EVIDENCE_NAMES:
                violations.append(f"{current_commit}: {status} {normalized}")
```

**回答 1**：会。第 248 行把 `status` 从 `--name-status` 行中取出，但**第 249-256 行的判定完全不使用 `status`**——`status` 只作为字符串前缀写进违规消息，不参与任何分支判断。因此 `D`（删除）、`A`（新增）、`M`（修改）走的是同一条判定路径。只要被删路径落在 `evidence_root` 下、不在 `metrics_root` 下、且文件名不在 `RETAINED_EVIDENCE_NAMES` 内，就会被 `violations.append` 记成违规。

### 实跑对比（两轮均本轮直接运行）

| 命令 | exit | 观察 |
| --- | --- | --- |
| `scope history . --evidence-root .pipeline --since cdf55e9` | **4** | 单行 `FAIL:`，逐条列出 `d238ba2` 的 **87** 条删除，全部为 `D` 状态（`grep` 计数：87 条 `: D .pipeline`，**0 条**其他状态） |
| `scope history . --evidence-root .pipeline --since d238ba2` | **0** | `PASS` |
| `scope history . --evidence-root .pipeline`（默认全量） | **4** | 列出 **107** 条（87 条本任务删除 + 20 条历史进度日志类违规） |

**关键观察**：`--since cdf55e9` 报的 87 条**全部是删除**，无一条新增。也就是说闸门把 `d238ba2` 这次**清理动作本身**当成了违规。

### 判断：**设计缺陷**（闸门无法区分「新增违规文件」与「删除违规文件」）

**分析**：

1. **语义错位**。该闸门的设计意图（见 `references/acceptance-evidence.md`「前向基线闸门」节）是阻止**新的**非保留证据文件进入 Git。而删除一个非保留证据文件恰恰是**朝正确方向**的动作——它减小漂移，不增大漂移。当前实现把两个方向相反的变更判成同一结果。

2. **可自证的矛盾**。本任务 `op-delete-drifted-evidence` 的**全部目标就是删除漂移证据**。而删除完成后，`--since cdf55e9` 反而报 87 条违规；`--since d238ba2` 才 PASS。这意味着：**一个提交只要做了闸门希望你做的事（清理漂移），就会被闸门拦下**，唯一的出路是把 `--since` 推到该提交之后。闸门对「执行其自身需求的提交」不具备可通行性。

3. **非预期行为的证据**。审查者与执行者的测试都只覆盖「新增违规 → 报错」与「基线之后 → pass」，没有任何测试断言「删除非保留证据应当 pass」。这说明删除路径既未被设计、也未被测试——属**遗漏**，而非有意取舍。

4. **成因定位**。`commit_history_check` 复用了 Git 的 `--name-status`，但只用它做「路径是否曾出现在历史里」的集合判断，丢弃了状态维度。修复方向是为判定加上方向性：对 `D` 状态仅当被删文件**属于保留集**时才判违规（删除保留文件是真正不可接受的），对 `A`/`M` 保持现有判定。

**为什么不改代码**：本次终审授权范围是诊断与记录，**明确不授权修改产品代码**。该修复超出本任务冻结契约（契约 `op-add-since-baseline-gate` 只要求新增可选 `--since` 基线，未要求区分删除方向），且会改变 `commit_history_check` 的判定语义与既有测试断言。**建议由用户在终审后决定是否另开任务**。

**不阻断本次接受的理由**：该问题不影响本任务 9 条验收测试的任何一条（全部 pass），不影响前向闸门在「正确基线」下的工作能力（`--since d238ba2` → exit 0），且本任务的实际清理动作已由执行者如实留痕并获终审接受。它是**闸门能力边界**的记录，不是本任务交付物的缺陷。

## 五、对执行与审查两阶段的总体确认

### 执行阶段（`executor-report.md`）

- 六个 operation 均有执行记录，与实际 diff 一致：`d238ba2` 为 `108 files changed, 484 insertions(+), 1409 deletions(-)`，`c27b7c7` 为 `5 files changed, 59 insertions(+), 1 deletion(-)`（审查者核验，本轮读取其结论并复核了提交存在性与顺序）。
- `RETAINED_EVIDENCE_NAMES` 单点定义（`core.py:26`）并被 `commit_history_check`（`:255`）与 `finalize_evidence`（`planning.py:2151` 附近）共用，满足「保留集单点定义」要求。
- 执行者报告第七节对测试 7 偶发失败的根因排查诚实：确定性复现了「全局 identity 缺失 → 必失败」，并对**未能归因的瞬态**明确写「不猜」。符合诚实性要求。

### 审查阶段（`review-report.md`）

- 审查者逐条独立重跑了 9 条验收测试（未采信执行者自述），并额外跑了 `validate_task_sheet.py`、三组 `scope history`、剥离全局 identity 的测试 7、全量 `discover`（`Ran 262 tests ... OK`）。
- 审查者**主动纠正了委派方的错误预期**（`--since cdf55e9`），而非顺从委派——这是独立审查应有的行为，本终审予以确认与采纳。
- 审查者对 11 个超范围删除的评估（「可接受但需终审确认」）与本次终审结论一致：审查者没有单方面豁免越界，正确地把裁决上升。
- 审查者正确地将未由自己观察的内容列入 `unverified`。

### 本轮独立验证（主代理第三层）

本轮**未抄写**审查者摘要，而是直接运行：

| 验证项 | 命令 | exit |
| --- | --- | --- |
| 4 条高风险验收测试（保留集契约、`--since` 忽略更早历史、默认全量扫描未变、CLI `--since`） | `python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_keeps_exactly_the_documented_retained_names tests.test_git_checks.GitChecks.test_scope_history_since_baseline_ignores_earlier_violations tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard tests.test_cli.CLITests.test_scope_history_cli_since_passes_baseline_and_reports_drift` | **0**（`Ran 4 tests ... OK`） |
| 任务单校验（schema 4） | `python scripts/validate_task_sheet.py docs/tasks/evidence-retention-forward-gate.md` | **0**（`OK: valid task sheet`） |
| 前向闸门三组对比 | 见第四节 | 4 / 0 / 4 |
| 生命周期阶段 | `lifecycle status . --task-id ... --evidence .pipeline/evidence-retention-forward-gate` | **0**，`phase: "final-check"`，`next_actions: ["run_final_check"]` |

**关于 `--evidence` 参数的说明**：首次以 `--evidence .pipeline` 调用时返回 `phase: "executor"` 且三份报告均为 `false`。改用 `--evidence .pipeline/evidence-retention-forward-gate`（即**任务证据目录**本身）后，`executor-report.md`、`review-report.md`、`executor-result.json`、`reviewer-result.json` 均为 `true`，`phase` 正确跃迁到 `final-check`。前者是**参数用法错误**（把证据根传成了任务目录的父目录），不是产品缺陷——已通过 `--help` 确认真实用法为 `lifecycle status <root> --task-id <id> --evidence <evidence-dir>`。

## 六、未验证项与需人类裁决项

### 未验证

- **合并到 `main` 未执行**，且按 `goal.md:26` 属非目标——合并是**人类开发者**的动作，本轮不执行、不 push、不 checkout main、不删 worktree。
- **`.pipeline/metrics/` 跨任务长期增长趋势**（`assumption-metrics-untracked-count-grows`）未做跨任务验证。
- **审查者所述「偶发失败触发瞬态」的原始成因**未复现、无法归因（执行者已如实声明；本轮亦无法归因，不猜）。
- ~~全量 262 测试依赖审查者记录~~ —— **本轮已独立执行全量套件**：`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests` → `Ran 262 tests in 211.158s`，`OK`，exit **0**。与审查者记录的 `Ran 262 tests` 一致，测试数无分歧。

### 需人类裁决

1. **是否合并本分支到 `main`**——本轮终审结论为 `ACCEPT`，但合并不自动执行。
2. **`--since` 语义问题是否另开任务**——建议另开，修复方向见第四节第 4 点。
3. **规划侧路径笔误是否另开 `derived` 任务**——建议另开，见第三节。
---

终审结论：**ACCEPT**。9 条验收测试全部 pass；三项裁定已记录并验证；一个设计边界问题（删除方向）与一个规划侧笔误已如实记录，均不构成对本任务交付物的阻断。