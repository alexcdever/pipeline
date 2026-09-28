# 主代理最终检查：gate-deletion-semantics（终审 round 2）

本文件由主代理在独立上下文重写，取代 round 1（`12e302c`）版本。所有事实均本轮实跑，不抄执行者或审查者摘要。

## 一、范围膨胀的独立记录（本次终审首要事项）

冻结契约 `docs/tasks/gate-deletion-semantics.md` 只定义 3 个 operation：

1. `op-fix-deletion-status-branch`
2. `op-cover-deletion-semantics-with-tests`
3. `op-align-retention-gate-docs`

实际交付远超此范围。逐项列示如下。

| 交付项 | 是否在契约内 | 授权来源 |
|---|---|---|
| 删除语义修复（`commit_history_check` 的 `retained == deleting` 四象限） | **契约内** | `op-fix-deletion-status-branch`；acceptance 1/2/3 |
| 4 条被删命令的补回（`commit_history_check` docstring 与行为恢复） | **契约外** | 用户裁决「补回全部 + 改 gate」；执行者报告第九节 |
| `expected_exit_code` 新字段（`acceptance-evidence.md` + `templates/pipeline-evidence.json` + `core.py` gate_check） | **契约外** | 同上裁决；执行者报告第九节 |
| 证据块解析改为取第一个闭标记（`core.py`） | **契约外** | 用户裁决「改解析逻辑」；执行者报告第九节 |
| `pipeline_tools/reconcile.py` 的同步修复（`_machine_block` 取首个闭围栏） | **契约外** | 同上裁决；`89835f0` |
| `gate_check` 布尔边界守卫（`isinstance(expected, bool)` / `isinstance(exit_code, bool)`） | **契约外** | 核验发现的缺陷；执行者报告第十节；`b7ae0cc` |
| `.gitattributes` 新建（`* text=auto eol=lf` / `*.cmd`/`*.bat` `eol=crlf` / `docs/tasks/*.md -text`） | **契约外** | 用户裁决「接受并单独提交 renormalize」；`b7ae0cc` 建，`8d677b0` 补 `-text` |
| 15 个 `.pipeline/` 文件的行尾规范化（CRLF→LF） | **契约外** | 同上裁决；`8d677b0` |
| 测试断言收紧（`test_git_checks.py` 原 `len==2` 改为 `len==1` 并断言 ` A `） | **契约内测试 operation 的延伸** | `op-cover-deletion-semantics-with-tests`；acceptance 4 |

### 是否违反 `goal.md:41`

`goal.md:41`：「任务单冻结契约不可静默修改；过程记录写入角色进度日志，不写入任务单。」

判定：**不构成「静默修改」，属「记录在案的授权变更」。** 依据：

1. **冻结任务单字节未变**。本轮与每一轮修复后 `sha256sum docs/tasks/gate-deletion-semantics.md` = `ec0668e69513bf4443d958ec9506f15ab965efc0db51529834156a0adec212b0`，与基线 `692ee63` 冻结时完全一致；`git show 692ee63:docs/tasks/gate-deletion-semantics.md | sha256sum` 同值；`git log --oneline --all -- docs/tasks/gate-deletion-semantics.md` 仅 `692ee63` 一条。契约文本从未被改写。
2. **每次扩张都有用户明确授权**：范围膨胀的每一项都能追溯到用户裁决（「补回全部+改gate」「改解析逻辑」「接受并单独提交 renormalize」「用 `-text` 保护全部任务单」），且授权内容逐条写入 `executor-report.md` 第九、十、十一节，标注「授权来源」小节。
3. **过程记录写在角色进度日志与阶段报告，未写入任务单**：所有授权与偏差记录落在 `.pipeline/gate-deletion-semantics/executor-report.md`，正是 `goal.md:41` 要求的落点。

因此 `goal.md:41` 禁止的是「静默」——未授权、未记录地改写契约。本次是相反的形态：契约文本零改动，扩张全部显式授权并留痕。**结论：不违反。** 唯一可议之处是这些扩张本该走 `derived`/`continuation` 任务单（`references/merge-and-recovery.md:24` 第 5 条），而实际在同一任务内完成；这是流程完整性问题，不改变「非静默」的判定，已在「需人类裁决项」中单列。

## 二、三个待决项的裁定

### 待决 1：`references/metrics-contract.md:118` 未表述删除方向

- **在 `allowed_paths` 内**：是。冻结契约 `allowed_paths` = `["pipeline_tools/**", "tests/**", "references/**"]`，该文件属 `references/**`。
- **acceptance-test-5 是否指向它**：否。`test_ref` = `tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics`；其正文（该文件 `:241-249`，本轮已读）**只读 `references/acceptance-evidence.md`**，断言 `commit_history_check`、`保留集`、`` `A` ``、`` `D` `` 及一条同时含 `` `D` ``+`保留集`+`删除` 的行。完全不涉及 `metrics-contract.md`。
- **该行是否错误**：否，仅不完整。原文「只承认 7 个保留文件名」描述保留集成员；本任务未增删 `RETAINED_EVIDENCE_NAMES`，陈述仍为字面真，缺的只是方向性表述。

**裁定：本任务不交付，另开任务。** 理由：冻结契约的机械验收不覆盖它；`non_goals` 明确禁止改冻结任务单，顺手扩改 `metrics-contract.md` 属对冻结范围的越界；它既非错误也不影响本任务交付语义成立。不阻塞合并。

### 待决 2：`bin/pipeline-tools.cmd` 的 `eol=crlf`

- **是否标准 Windows 批处理**：是。前 6 行为 `@echo off` / `setlocal` / `set "ROOT=%~dp0.."` / `set "PYTHONPATH=%ROOT%;%PYTHONPATH%"` / `python -m pipeline_tools %*` / `exit /b %ERRORLEVEL%`，典型 `.cmd`。`file` 判为 `DOS batch file, ASCII text`。
- **当前实际字节**：`python` 读原始字节判定为 **LF**（无 `\r\n`）。
- **是否有测试调用**：是。`tests/test_cli.py:657` 用 `subprocess.run(['cmd', '/c', str(ROOT / 'bin' / 'pipeline-tools.cmd'), '--help'], ...)`；`README.md:108` 记载其为 Windows 入口。
- **未来行为变更**：`.gitattributes` 规定 `*.cmd text eol=crlf`，因此**下次签出该文件将变为 CRLF**（当前工作区仍是 LF，故本轮不触发差异）。

**裁定：安全，记录为已知项。** 依据：`.cmd` 在 Windows 上本就应为 CRLF，CRLF 是批处理解释器的原生行尾；`cmd /c` 对 LF 与 CRLF 均能执行（现有测试通过即证 LF 可用，CRLF 更无风险）；调用方是 `cmd /c`，非 POSIX shell，不受 LF→CRLF 影响。无功能风险，仅需在合并说明中记为「签出后 `.cmd` 行尾由 LF 变 CRLF」的已知未来变更，避免后续误判为漂移。

### 待决 3：renormalize（`8d677b0`）与报告记录（`2c88bad`）分两次提交

**裁定：合理，应当保持拆分。** 依据：`8d677b0` 的变更在 `--ignore-all-space` 下除 `.gitattributes` 外零差异，是**纯行尾变更**；`2c88bad` 只改 `executor-report.md`（+32 行）与 `executor-result.json`（1 行），是**纯内容变更**。二者混在一个提交会让「纯格式 churn」与「语义记录」不可分辨，正是 `references/merge-and-recovery.md:33`「先提交实现，再单独提交证据和状态文件」要避免的形态。拆分为审计提供了清晰的二分。

## 三、对执行与审查两阶段的确认

### 执行阶段

- 三份产物齐备、身份正确：`executor-report.md`（executor / round 1 / task_id 正确）、`executor-result.json`（本轮 `result verify` 见第五节）。
- 判定代码 `pipeline_tools/core.py` 的 `retained == deleting` 四象限与契约一致：`A`+非保留 → 违规；`A`/`M`+保留 → 放行；`D`+非保留 → 放行；`D`+保�� → 违规。本轮由 acceptance 1/2/3 三条实跑独立证实。
- 未越界：`RETAINED_EVIDENCE_NAMES` 未增删、`in_metrics` 豁免未动、`--since` 前向基线（`revision_range`）未动、进度日志分支仍在方向判定之前无条件命中。
- 未触碰冻结文件：`git diff 692ee63 HEAD --name-status -- docs/tasks/` 输出为空（exit 0）。
- 过程偏差（不阻塞）：多个执行提交把产品代码与证据文件合并提交，未严格按 `merge-and-recovery.md:33` 分两次；`12e302c` 还有 amend（`97c953b`→`12e302c`）只重写自己刚生成的提交，父仍为 `692ee63`，未越界。

### 审查阶段

- `review-report.md`（reviewer / round 1 / task_id 正确）与 `reviewer-result.json` 齐备，结论 `ACCEPT WITH CONDITIONS`。
- 审查者独立复跑：5 条 acceptance 自报 5/5 PASS、默认全量 `scope history` exit 4、`--since 8f1f1e0`/`--since 692ee63` exit 0、全量 OK，与本轮一致。
- 审查者两项条件均被接住：条件 1（identity）本轮改判为「需修但字段不同」，条件 2（`metrics-contract.md:118`）本轮改判为「另开任务」。
- 审查者记的 `R*` 未规定情形（`'R100'.startswith('D')` → False，重命名走非删除路径）本轮复核认可：不放宽闸门，`R065`/`R090`/`R100` 在默认全量中仍判违规。

## 四、核心事实的独立复核结果

| 项 | 命令 | 结果 |
|---|---|---|
| 提交序列 | `git log --oneline -8` | `2c88bad` → `8d677b0` → `b7ae0cc` → `89835f0` → `116b30c` → `ac4a165` → `9311e47` → `f15e77e` |
| 8d677b0 统计 | `git show --stat 8d677b0` | 16 files changed, 332 insertions(+), 331 deletions(-)（`.gitattributes` + 15 个 `.pipeline/` 文件） |
| 2c88bad 统计 | `git show --stat 2c88bad` | 2 files changed, 33 insertions(+), 1 deletion(-)（`executor-report.md` / `executor-result.json`） |
| 基线 | `git rev-parse 692ee63` | `692ee6387ea2e60d53d63680235906096ed90903` |
| 主工作树 main | `git worktree list --porcelain` | 主树 `main=692ee63`，未推进；任务树 `branch=gate-deletion-semantics, HEAD=2c88bad` |
| 工作区 | `git status --short --untracked-files=no` | 空 |
| 任务单 sha256 | `sha256sum docs/tasks/gate-deletion-semantics.md` | `ec0668e69513bf4443d958ec9506f15ab965efc0db51529834156a0adec212b0`（与基线一致） |
| `docs/tasks/` 变更 | `git diff 692ee63 HEAD --stat -- docs/tasks/` | **空输出，exit 0** —— renormalize 未触及任务单 |

### 五条 acceptance 逐条实跑（本轮独立）

| # | acceptance ID | exit | 结果 |
|---|---|---|---|
| 1 | `acceptance-test-delete-non-retained-evidence-not-a-violation` | 0 | PASS（`Ran 1 test in 1.116s OK`） |
| 2 | `acceptance-test-delete-retained-evidence-is-a-violation` | 0 | PASS（`Ran 1 test in 1.175s OK`） |
| 3 | `acceptance-test-add-non-retained-evidence-still-violates` | 0 | PASS（`Ran 1 test in 0.852s OK`） |
| 4 | `acceptance-test-forward-gate-guard-migrated` | 0 | PASS（`Ran 1 test in 1.400s OK`） |
| 5 | `acceptance-test-retention-gate-docs-aligned` | 0 | PASS（`Ran 1 test in 0.001s OK`） |

### 前向闸门对照（本任务核心价值，实跑）

| 命令 | exit | 输出 |
|---|---|---|
| `scope history . --evidence-root .pipeline --since cdf55e9` | **0** | `PASS` |
| `scope history . --evidence-root .pipeline`（默认全量） | **4** | `FAIL:`，报 `A` 非保留新增、`R*` 重命名、`-progress.jsonl` 删除 |

结论：**闸门未被整体放宽**——`--since cdf55e9` 由修复前的 4 变 0，默认全量仍为 4。

### 全量测试

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests
→ Ran 275 tests in 200.573s
→ OK
→ exit 0
```

计数 275 与基线 275 一致；执行者自报亦为 275。

### gate

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools gate pre-merge .pipeline/gate-deletion-semantics --task-id gate-deletion-semantics
→ PASS
→ exit 0
```

## 五、结论

**ACCEPT WITH CONDITIONS**

- 产品修复语义正确，四象限真值表与契约一致；`R*` 未规定情形沿用保守旧行为，不放宽闸门。
- 5 条 acceptance 本轮独立实跑 5/5 PASS；全量 275 条 OK；前向闸门对照成立（0 vs 4）。
- 未触碰冻结文件、未删 `.pipeline/metrics/`、worktree 与主分支身份正确、任务单字节未变。
- **条件（不阻塞）**：`references/metrics-contract.md:118` 缺删除方向表述，另开任务。
- **已知项**：`bin/pipeline-tools.cmd` 下次签出将由 LF 变 CRLF（`.gitattributes` 规定），安全，记录在案。

## 六、未验证项

- `merge to main` 与主工作树 post-merge gate（合并由人类开发者执行）。
- `finalization.json` 未产出（成功最终化阶段尚未执行）。
- `.gitattributes` 的 `eol=crlf` 实际生效需一次真实签出/克隆验证。
- 主工作树合并后的依赖与生成物加载复验。

```pipeline-evidence
{
  "schema": 1,
  "task_id": "gate-deletion-semantics",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics",
  "branch": "gate-deletion-semantics",
  "role": "main-final",
  "round": 2,
  "status": "READY-TO-MERGE",
  "commands": [
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_delete_non_retained_evidence_is_not_a_violation tests.test_git_checks.GitChecks.test_delete_retained_evidence_is_a_violation tests.test_git_checks.GitChecks.test_add_non_retained_evidence_still_violates", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics", "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_git_checks.GitChecks.test_commit_history_check_evidence_path_guard", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics", "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_acceptance_evidence_documents_deletion_semantics", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics", "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline --since cdf55e9", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics", "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools scope history . --evidence-root .pipeline", "exit_code": 4, "expected_exit_code": 4, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics", "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m unittest discover -s tests", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics", "evidence_ref": "final-check.md"},
    {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pipeline_tools gate pre-merge .pipeline/gate-deletion-semantics --task-id gate-deletion-semantics", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics", "evidence_ref": "final-check.md"},
    {"command": "git diff 692ee63 HEAD --stat -- docs/tasks/", "exit_code": 0, "cwd": "D:/Projects/Skills/pipeline/.worktrees/gate-deletion-semantics", "evidence_ref": "final-check.md"}
  ],
  "assertions": [
    "5 条 acceptance 由终审独立实跑 5/5 PASS",
    "全量 275 条测试 OK，exit 0",
    "前向闸门对照成立：--since cdf55e9 exit 0，默认全量 exit 4",
    "冻结任务单 sha256 未变，docs/tasks/ 无 diff",
    "gate pre-merge PASS"
  ],
  "evidence_refs": ["final-check.md", "final-result.json"],
  "unverified": ["merge to main", "post-merge gate", "finalization.json"],
  "baseline_head": "692ee6387ea2e60d53d63680235906096ed90903",
  "reviewed_commit": "8d677b073801a4094506497a26018fe7a15a9eb0",
  "review_evidence_head": "2c88bad356b66dbde1f7901af446de3725c2cf7c",
  "test_count": 275
}
```