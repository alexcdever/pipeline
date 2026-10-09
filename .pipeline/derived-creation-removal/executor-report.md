# executor-report：derived-creation-removal（round 3，revision 3 重做证据）

## 任务身份

- task-id：`derived-creation-removal`
- task-type：`repair`
- worktree：`D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal`
- branch：`derived-creation-removal`
- 分支尖端（本轮起点）：`d0299382b65d1de6899e9ff4ff9da12d65eac5af`
- 实现提交（两轮未变）：`b4ca1179f30b054493e0c5227bcb86f3f6602e6b`
- role：executor，round **3**
- sheet_revision：**3**
- sheet_sha256：`ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd`

**本轮实现一字未动**：`git status` 全程干净，`git diff b4ca117..d029938` 里唯一的非 `.pipeline/` 路径是任务单自己的 4 行（revision 3 改 `test_ref`）；`pipeline_tools/**`、`tests/**`、`SKILL.md`、`README.md`、`references/**` 均无改动。

## 本轮的触发原因：revision 2 → 3 修正 `test_ref` 类名笔误

- revision 2 的 `acceptance-test-4.test_ref` 写作 `tests/test_cli.py: CliTests.test_dispatch_derived_create_is_no_longer_exposed`，而 `tests/test_cli.py` 定义的类是 **`CLITests`**（第 77 行，全文件唯一类）。
- `pytest -k` 只匹配方法名、不看类名，所以 round 2 的五条验收命令全绿；但 gate 期的 `test_ref` 位置校验要求「符号确实在该文件的该类里声明」，于是报 `acceptance test acceptance-test-4 test_ref method is absent from tests/test_cli.py: CliTests.test_dispatch_derived_create_is_no_longer_exposed`。
- 主代理 `task amend` 登记 revision 3（`verification_surface_changed: true`），`test_ref` 改为 `CLITests.test_dispatch_derived_create_is_no_longer_exposed`。amendments.json 记录：`previous_sheet_sha256: ad9dfd97…de6fc` → `sheet_sha256: ff027c6d…4dbd`，`changes.acceptance_tests.modified: [{'id': 'acceptance-test-4', 'fields': {'test_ref': {'from': 'tests/test_cli.py: CliTests.…', 'to': 'tests/test_cli.py: CLITests.…'}}}]`。
- 按「验证面变更即作废」规则，上一轮证据失效，本轮在 revision 3 下原样重跑并重做证据。

## `acceptance-test-4` 的 `test_ref` 解析确认

做了三件事，逐条记录：

1. **静态读源码**：`grep -n "^class .*Tests\|def test_dispatch_derived_create_is_no_longer_exposed" tests/test_cli.py` → `77:class CLITests(unittest.TestCase):`、`249:    def test_dispatch_derived_create_is_no_longer_exposed(self):`；全文件只有 `CLITests` 一个类。
2. **AST 归属核对**：解析 `tests/test_cli.py`，`class CLITests (line 77) methods=67`，其中含 `test_dispatch_derived_create_is_no_longer_exposed` → **True**。（同时确认该文件没有第二个类，因此方法确实在 `CLITests` 名下。）
3. **走 pipeline 自己的 gate 校验路径**（决定性）：加载任务单契约后直接调用 `pipeline_tools.core._acceptance_test_ref_position_errors(root, contract)` ——这正是 gate 判 `test_ref method is absent` 用的函数。结果：

```
test_ref position errors (pipeline's own gate path): []
```

五条 `test_ref` 全部解析成功，其中：

```
acceptance-test-4: test_ref='tests/test_cli.py: CLITests.test_dispatch_derived_create_is_no_longer_exposed'
  -> path='tests/test_cli.py' symbol='CLITests.test_dispatch_derived_create_is_no_longer_exposed'
CLITests in classes: True
CLITests.test_dispatch_derived_create_is_no_longer_exposed in methods: True
```

即：`test_ref` 已能解析到 `tests/test_cli.py` 里 `CLITests` 类下的真实方法声明。

## `gate pre-merge` 完整输出

命令（cwd = worktree 根）：

```
python -m pipeline_tools gate pre-merge .pipeline/derived-creation-removal --task-id derived-creation-removal --branch derived-creation-removal
```

输出（本报告提交前，HEAD = `d0299382b65d1de6899e9ff4ff9da12d65eac5af`）：

```
FAIL: executor-report.md head does not match current Git identity; review-report.md head does not match current Git identity; final-check.md head does not match current Git identity
UNVERIFIED: goal hash unrecorded: docs/goal.md
exit=3
```

**确认：那条 `acceptance test acceptance-test-4 test_ref method is absent from tests/test_cli.py: CliTests.…` 已消失**——gate 不再报任何 `test_ref` 相关错误（gate 会聚合错误后一起打印，且上面的 `_acceptance_test_ref_position_errors` 直接调用返回 `[]`，两路一致）。

**余下的 FAIL 与预期不同，需要主代理注意**：它不是「缺 `final-check.md`」这类主代理阶段项（三份报告均已存在），而是**三份报告的 `head` 都判为过期**。原因是 `pipeline_tools/core.py:2563` 的 `head_advanced_by_evidence_only`：报告记录的 `head`（三份都是实现提交 `b4ca117`）到当前 `HEAD`（`d029938`）之间，`git diff b4ca117 d029938` 含一个**非 `.pipeline/` 路径**——任务单自身 `docs/tasks/derived-creation-removal.md`（revision 3 的 4 行改动）。`evidence_only_paths` 只认 `.pipeline/**` 与 metrics 路径，所以该区间被判为「非仅证据提交」。这是**修订本身**造成的系统性结果，`executor-report.md`、`review-report.md`、`final-check.md` 三份都一样，不是本轮报告单独引入的。请主代理决定处置（重跑 reviewer/final 以把 `head` 重绑到当前 HEAD，或按项目规则另行裁定）。

`UNVERIFIED: goal hash unrecorded: docs/goal.md` 与 round 2 相同（本任务未改 `docs/goal.md`，也无写入 goal 哈希的动作）。

## 验收测试（逐条，命令见契约 `acceptance_tests[].command_ref`，cwd = worktree 根）

| ID | 命令 | 退出码 | 观察 |
|---|---|---|---|
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type` | 0 | 1 passed, 53 deselected |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived` | 0 | 1 passed, 53 deselected |
| acceptance-test-3 | `python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate` | 0 | 1 passed, 2 subtests passed |
| acceptance-test-4 | `python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed` | 0 | 1 passed, 63 deselected |
| acceptance-test-5 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | 1 passed, 27 deselected |

## 全量测试

`python -m pytest -q`（cwd = worktree 根，`PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1`）→ 退出码 0，**388 passed, 30 subtests passed**。与 round 2 完全一致（实现未变，只重跑）。

## 其它检查（cwd = worktree 根）

- `python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md` → 退出码 0（PASS）。
- `python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor` → 退出码 0（PASS）。
- `python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed <revision 3 allowed_paths> --forbidden <revision 3 forbidden_paths>` → 退出码 0（PASS）。
- `git diff --check` → 退出码 0。
- `sha256sum docs/tasks/derived-creation-removal.md` = `ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd`，与 `.pipeline/derived-creation-removal/goal.json` 的 `task_sheet_sha256` 及 amendments.json 的 revision 3 记录逐字一致。
- 未改任何实现/测试/文档文件、未回退任何提交、未动主工作树与其它任务证据目录（`git status` 全程干净，证据提交前唯一改动是本任务证据目录）。

## 硬性约束核对

- 冻结契约未改（revision 3 由主代理 amend；本轮的 sha256 与 amendments.json 记录一致）。
- 未新建 worktree、未动主工作树。
- 本回合唯一写入是 `.pipeline/derived-creation-removal/executor-report.md` 与 `executor-result.json`。

```pipeline-evidence
{"schema": 2, "task_id": "derived-creation-removal", "worktree": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "branch": "derived-creation-removal", "role": "executor", "round": 3, "status": "PASS", "head": "b4ca1179f30b054493e0c5227bcb86f3f6602e6b", "sheet_revision": 3, "sheet_sha256": "ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd", "observed_at_commit": "b4ca1179f30b054493e0c5227bcb86f3f6602e6b", "generated_at": "2026-10-09T04:26:40+00:00", "commands": [{"command": "git rev-parse --show-toplevel", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git branch --show-current", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git rev-parse HEAD", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "sha256sum docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools task validate docs/tasks/derived-creation-removal.md", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k new_task_plan_rejects_the_derived_type", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k generated_sheets_never_declare_derived", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_derived_task_dispatch_recovery.py -k historical_derived_contracts_still_validate", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_cli.py -k dispatch_derived_create_is_no_longer_exposed", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -c \"from pipeline_tools.contract import load_contract; from pipeline_tools.core import _acceptance_test_ref_position_errors; ... print(_acceptance_test_ref_position_errors(root, contract))\"  # pipeline's own gate test_ref resolution path", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools gate pre-merge .pipeline/derived-creation-removal --task-id derived-creation-removal --branch derived-creation-removal", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 3, "expected_exit_code": 3, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools result verify .pipeline/derived-creation-removal/executor-result.json --task-id derived-creation-removal --role executor", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools scope check . --task-id derived-creation-removal --allowed pipeline_tools/core.py pipeline_tools/planning.py pipeline_tools/__main__.py tests/test_planning.py tests/test_task_generation.py tests/test_derived_task_dispatch_recovery.py tests/test_security_repairs.py tests/test_cli.py tests/test_acceptance_id_and_template_compliance.py SKILL.md README.md references/task-design.md references/compat-and-migration.md docs/tasks/derived-creation-removal.md .pipeline/derived-creation-removal/** --forbidden docs/goal.md pipeline_tools/contract.py .pipeline/task-sheet-revision-and-evidence-binding/** .pipeline/post-merge-evidence-identity/** .pipeline/finalization-and-reconcile-phase/** .pipeline/finalization-marker-head-tolerance/** .pipeline/finalization-report-reader/** .pipeline/finalization-hygiene/** .env credentials/**", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git diff --check", "cwd": "D:/Projects/Skills/pipeline/.worktrees/derived-creation-removal", "exit_code": 0, "evidence_ref": "executor-report.md"}], "assertions": ["no implementation, test or documentation file was changed this round: git status stayed clean and the only non-.pipeline path between the implementation commit and the branch tip is the task sheet itself", "acceptance-test-4 test_ref now resolves: tests/test_cli.py declares exactly one class, CLITests, and CLITests.test_dispatch_derived_create_is_no_longer_exposed exists among its 67 methods", "the pipeline's own gate resolution path, _acceptance_test_ref_position_errors, returns an empty error list for all five acceptance test_refs", "the gate pre-merge output no longer contains any test_ref is absent error; the previous acceptance-test-4 CliTests failure is gone", "all five acceptance commands exit 0 and the full suite is green at 388 passed, 30 subtests passed, identical to round 2", "the remaining gate failure is three pre-merge reports whose recorded head b4ca117 is no longer evidence-only reachable from HEAD because the revision 3 amendment touched docs/tasks/derived-creation-removal.md, a product path"], "evidence_refs": ["executor-report.md", "executor-result.json"], "unverified": ["revision 2 to 3 corrected the acceptance-test-4 test_ref class name from CliTests to CLITests; round 3 re-runs and re-does the evidence under revision 3, with the implementation unchanged at b4ca117", "the gate pre-merge run reports head staleness for all three pre-merge reports (executor, reviewer, final), not a missing main-agent stage item; this is caused by the revision 3 amendment touching docs/tasks/derived-creation-removal.md, which evidence_only_paths does not treat as an evidence path, and it is the main agent's call how to resolve it", "UNVERIFIED goal hash unrecorded: docs/goal.md is reported by the gate and is unchanged from round 2; this task neither modified nor recorded a hash for docs/goal.md", "the round 3 gate pre-merge run predates this evidence commit, so its head comparison used d029938 as the current HEAD", "no new runtime behaviour was observed beyond re-running the same commands, because the implementation is byte-identical to round 2"]}
```
