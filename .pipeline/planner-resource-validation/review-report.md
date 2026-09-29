# planner-resource-validation：独立审查报告（round 1）

- **task_id**: `planner-resource-validation`
- **worktree**: `D:\Projects\Skills\pipeline\.worktrees\planner-resource-validation`
- **branch**: `planner-resource-validation`
- **role**: reviewer（独立上下文，从零开始）
- **round**: 1
- **被审 HEAD**: `5e9e754c6d3fde88f9f04348b1cfbec3b6745722`（= 冻结基线；产品改动**未提交**在工作树中，本次审查对象即该工作树状态）
- **结论**: **PASS**

---

## 1. 身份核对（全部一致）

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| task_id | `planner-resource-validation` | 任务单 `<!-- Task ID: planner-resource-validation -->` | 一致 |
| branch | `planner-resource-validation` | `git branch --show-current` = `planner-resource-validation` | 一致 |
| worktree | `.worktrees/planner-resource-validation` | `git rev-parse --show-toplevel` = `D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation` | 一致 |
| 基线提交 | `5e9e754c…` | `git rev-parse HEAD` = `5e9e754c6d3fde88f9f04348b1cfbec3b6745722` | 一致 |
| goal sha256 | `9abb196a…` | `sha256sum goal.md` = `9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f` | 一致 |

`git worktree list --porcelain` 显示：

```
worktree D:/Projects/Skills/pipeline                                          HEAD b5f7648  branch refs/heads/main
worktree D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation   HEAD 5e9e754  branch refs/heads/planner-resource-validation
worktree D:/Projects/Skills/pipeline/.worktrees/test-metrics-isolation        HEAD b5f7648  branch refs/heads/test-metrics-isolation
```

worktree / branch 配对正确，未发现身份漂移。

## 2. 生产代码差异（亲自读，非转述）

`git diff 5e9e754 --stat`：

```
 pipeline_tools/__main__.py                         |   2 +-
 pipeline_tools/planning.py                         | 119 ++++++++++++++++++++-
 references/compat-and-migration.md                 |  11 +-
 references/task-design.md                          |   9 ++
 tests/test_acceptance_id_and_template_compliance.py|  36 +++++++
 tests/test_cli.py                                  |  73 +++++++++++++
 tests/test_task_generation.py                      |  58 ++++++++++
 7 files changed, 303 insertions(+), 5 deletions(-)
```

核心实现（`pipeline_tools/planning.py`）：

- 新增 `DELETE_OPERATION_TOKENS`（delete/remove/purge 及其屈折形式共 11 个 token）、`RESERVED_EVIDENCE_SUFFIX = "-progress.jsonl"`。
- `_is_delete_operation(operation)`：对 `operation["kind"]` 做 `re.split(r"[^a-z0-9]+", kind.lower())`，任一 token 命中即判为删除类。
- `_pipeline_resource_path(value)`：仅当字符串规范后以 `.pipeline/` 开头**且**长度大于 `.pipeline/` 时返回该路径；否则 `None`。
- `_deletable_evidence_files(directory)`：`rglob("*")` 收集文件，排除 basename ∈ `RETAINED_EVIDENCE_NAMES` 或以 `-progress.jsonl` 结尾者。
- `_validate_pipeline_resource_existence(...)`：`operation is None` 时只查存在性；否则在目录不存在时报 `does not exist`，在删除类操作且无可删文件时报 `holds no deletable files`。
- `validate_task_plan` 中：仅当 `root is not None` 时，对 `task.resources`（operation=None）与每个 `operation.resources`（带 operation）各调用一次。
- `pipeline_tools/__main__.py`：`validate_task_plan(value, project_facts, requirement_facts, root=args.root)`，把 CLI `--root` 透传进 Python API。

代码风格与既有模块一致（`from .core import RETAINED_EVIDENCE_NAMES` 复用单点常量，未硬编码保留集清单；未硬编码任何目录名白名单）。docstring 已同步更新为「root 也用于检查手写 `.pipeline/<dir>/` 资源存在性」。

## 3. 验收测试逐条独立复验（我自己重跑）

每条命令均在 worktree 根目录执行，取 python 进程自身退出码：

| # | 验收 ID | 命令 | 结果 | 退出码 |
|---|---|---|---|---|
| 1 | `acceptance-test-planner-rejects-missing-pipeline-directory` | `python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_missing_pipeline_resource_directory` | OK, Ran 1 test | **0** |
| 2 | `acceptance-test-planner-rejects-delete-without-deletable-files` | `python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_delete_operation_without_deletable_files` | OK, Ran 1 test | **0** |
| 3 | `acceptance-test-planner-accepts-existing-pipeline-directory` | `python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_accepts_existing_pipeline_resource_directory` | OK, Ran 1 test | **0** |
| 4 | `acceptance-test-planner-resource-rules-documented` | `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_planner_resource_checks` | OK, Ran 1 test | **0** |
| 5 | `acceptance-test-task-plan-validate-cli-forwards-root` | `python -m unittest tests.test_cli.CLITests.test_task_plan_validate_cli_forwards_root_for_derived_parent` | OK, Ran 1 test | **0** |
| 6 | `acceptance-test-known-items-registered` | `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_known_items` | OK, Ran 1 test | **0** |

全量套件（我自己重跑）：

```
python -m unittest discover -s tests
Ran 309 tests in 227.721s
OK
FULLSUITE_EXIT=0
```

与主代理观察的 309 tests / OK / exit 0 一致。（套件运行中有一个测试自身会打印一行 `{"duration_s": …, "exit_code": 1, …}`，那是该测试内部子进程的 JSON 输出，不是套件结果；套件整体 OK 且退出码 0。）

## 4. 对抗性探针（重点验证中心主张）

### 4.1 是否在 `root` 提供时真正 fail-closed？

构造带 `.pipeline/nope/`（不存在）资源的 plan，直接调用 `validate_task_plan`：

```
root=None errors -> []
root=dir  errors -> ['task t resource .pipeline/nope/ names a .pipeline directory that does not exist',
                     'operation op resource .pipeline/nope/ names a .pipeline directory that does not exist']
```

**通过**：`root` 存在时确实报错（task 级 + operation 级各一条），不是静默 no-op。

### 4.2 CLI `--root` 转发是否真的改变行为？

我独立构造 derived-parent 场景（父任务单 `parent-run.md` 已提交进 git，plan 引用跨 run 父任务），分别跑 CLI：

```
planning task-plan-validate <plan> --root <root>
  rc=0  {"status": "pass", "errors": []}

planning task-plan-validate <plan>
  rc=2  {"status": "fail",
         "errors": ["derived task derived-task parent_task_id parent-run is outside this run
                     and root is unavailable to prove it exists"]}
```

**通过**：`--root` 的存在与否导致 rc 0 vs rc 2 的真实行为差异，`__main__.py` 的 `root=args.root` 透传确实生效，不是「只断言 flag 被接受」。同一处 `root` 也门控资源存在性检查，两者共用同一入参。

### 4.3 删除类判定是启发式，是否有未覆盖的缺口？

`_is_delete_operation` 是对自由文本 `kind` 的 token 启发式。实测：

```
'delete-evidence'   -> True     'delete_evidence'  -> True     'DELETE-EVIDENCE' -> True
'deletion-of-evidence' -> True  'evidence-delete'  -> True
'DeleteEvidence'    -> False    'rm-evidence'      -> False    'drop-evidence'   -> False
'clean-evidence'    -> False    'erase-evidence'   -> False    'noop'/'execute'/'add'/'create' -> False
{}/kind=None/kind=7 -> False
```

**缺口确认且已在文档中限定范围**：CamelCase（`DeleteEvidence`）与同义词（`rm`、`drop`、`clean`、`erase`）**不会**触发删除类检查。`references/task-design.md` 明确写出触发条件是「kind 含删除语义 token（`delete`、`remove`、`purge` 及其屈折形式）」，因此这不是被隐藏的行为，但它**没有显式声明反向边界**（即「未列出的同义词不触发」）。这是一个**有文档、但边界说明不完整**的启发式，不是缺陷。测试只覆盖 `delete-evidence` 这一个正例，未覆盖负例边界。

### 4.4 `root is None` 时是否保持惰性（非追溯保证）？

同一 plan，`root=None` 返回 `[]`（见 4.1），即不传 root 时新检查完全惰性。已冻结任务单由 `task validate` / gate 期校验负责，本规则不重跑它们——与 `references/task-design.md` 新增段落的表述一致。

### 4.5 `_deletable_evidence_files` 的保留集判定

用临时目录逐项验证：

```
空目录            -> []
7 个保留文件全放  -> []
+ 两个 -progress.jsonl -> []
+ raw.log         -> ['raw.log']
+ sub/handshake.json -> ['raw.log', 'sub\\handshake.json']
```

**通过**：只保留 `RETAINED_EVIDENCE_NAMES`（basename 匹配，与 `core.py` 语义一致）与 `*-progress.jsonl` 被排除，任意其它文件（含嵌套）算作可删。

## 5. 范围检查

`git diff --name-only 5e9e754`：仅 `pipeline_tools/planning.py`、`pipeline_tools/__main__.py`、`references/compat-and-migration.md`、`references/task-design.md`、`tests/test_{acceptance_id_and_template_compliance,cli,task_generation}.py`。

全部落在 `allowed_paths`（`pipeline_tools/`、`tests/`、`references/`、`pipeline_tools/__main__.py`）内，**无越界**。

`git diff 5e9e754 -- docs/` 为空 → **冻结任务单未被改动**。未触碰 `goal.md` / `IDEA.md`。

未跟踪文件仅 `.pipeline/metrics/*.json`（工作流元数据，`is_metrics_path` 豁免）与 `.pipeline/planner-resource-validation/`。

## 6. 新增文档契约测试的断言质量

两个新测试都是「读文件 + `assertIn` 一串具体 needle」：

- `test_references_task_design_documents_planner_resource_checks` 断言 `validate_task_plan`、`root=root`、`--root`、`pipeline_tools/planning.py`、`.pipeline/`、`RETAINED_EVIDENCE_NAMES`、`-progress.jsonl`、`does not exist`、`no deletable files`、`机械`、`白名单`、`不会追溯地让已冻结的任务单失效`。
- `test_references_compat_and_migration_documents_known_items` 断言 `已知项与后续跟进`、`evidence-retention-forward-gate`、`gate-deletion-semantics`、`_shares_test_root`、`metrics-contract.md`、`generate-task-sheets`、`assumptions`、`unknowns`、`潜在`、`当前`、`不要`。

**不是恒真断言**：needle 与文档真实内容一一对应（我核对了 diff 中的文档正文），且失败时会带出缺失 needle。属于合理的文档契约测试。

## 7. 证据目录检查

`.pipeline/planner-resource-validation/` 当前内容：

```
executor-report.md      (5650 B)
executor-result.json    (4231 B)
```

- **没有** `.log` 文件，**没有** `.jsonl`。
- **没有** `review-report.md`（正确——由本次审查创建，执行子代理不应代写）。
- 目录内无保留集之外的多余产物。

## 8. 未验证项 / 弱断言记录

1. 删除类 token 判定的**负向边界**（`DeleteEvidence`、`rm-evidence`、`drop-evidence`、`clean-evidence`、`erase-evidence` 不触发）没有任何测试覆盖；我手工探针确认了该行为，但它是否**有意**如此设计只能从文档推断，未获设计裁决确认。
2. `.PIPELINE/foo`（大写）不被识别为 `.pipeline/` 资源，因而跳过检查；`../.pipeline/x` 同样跳过（穿越引用，跳过合理）。这两条路径行为未在测试中覆盖。
3. `.pipeline//foo`（双斜杠）会被接受并传给 `Path` 拼接；Windows 上的解析行为我只做了静态阅读，未端到端运行。
4. 本次审查**不涉及合并**，也未在主工作树复验（属主代理最终检查/合并阶段职责）。
5. 未对全量套件的 309 个用例逐一与基线比对以确认没有任何既有用例被删改以凑绿；我只核对了 diff 中测试改动**全部为新增**（`git diff` 显示测试文件仅 `+` 无 `-`，除文件末尾空行变更）。

## 9. 结论

**PASS**。六条验收测试全部由我独立重跑并通过（退出码 0）；身份、范围、冻结任务单完整性、证据目录最小要求均满足；中心主张（删除类操作目标仅含保留证据时被拒绝；`root` 提供时 fail-closed，`root` 为 `None` 时惰性）经构造性对抗探针证实。上述未验证项均为**边界说明/覆盖度**层面的记录，不构成阻塞。
## 10. 机器证据块

```pipeline-evidence
{
  "schema": 1,
  "task_id": "planner-resource-validation",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
  "branch": "planner-resource-validation",
  "role": "reviewer",
  "round": 1,
  "status": "PASS",
  "commands": [
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_missing_pipeline_resource_directory",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_rejects_delete_operation_without_deletable_files",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_task_generation.TaskGenerationTests.test_task_generation_accepts_existing_pipeline_resource_directory",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_task_design_documents_planner_resource_checks",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_cli.CLITests.test_task_plan_validate_cli_forwards_root_for_derived_parent",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_known_items",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "review-report.md"
    },
    {
      "command": "python -m unittest discover -s tests",
      "exit_code": 0,
      "cwd": "D:/Projects/Skills/pipeline/.worktrees/planner-resource-validation",
      "evidence_ref": "review-report.md"
    }
  ],
  "assertions": [
    "六条验收测试由审查者独立重跑，全部 OK，退出码均为 0",
    "全量测试独立复跑：Ran 309 tests in 227.721s，OK，退出码 0",
    "validate_task_plan(plan, root=root) 对不存在的 .pipeline/<dir>/ 资源报 task 级与 operation 级两条错误，非静默 no-op",
    "validate_task_plan(plan) 在 root=None 时返回空错误列表，新检查惰性，满足不追溯失效约束",
    "构造性对比：CLI planning task-plan-validate 带 --root 时 rc=0/pass，不带 --root 时 rc=2/fail，--root 转发真实改变行为",
    "删除类 kind 为 token 启发式：delete/remove/purge 及屈折形式命中；DeleteEvidence、rm-evidence、drop-evidence、clean-evidence、erase-evidence 不命中，且该边界在 references/task-design.md 中已限定",
    "_deletable_evidence_files 对空目录、7 个保留文件、*-progress.jsonl 返回空；遇 raw.log 或嵌套文件才返回可删项",
    "改动仅 7 个文件且全部落在 allowed_paths 内；git diff -- docs/ 为空，冻结任务单未被改动",
    "证据目录无 .log / .jsonl；review-report.md 由审查者创建，executor 未代写",
    "两个新增文档契约测试断言的是文档真实内容，非恒真断言"
  ],
  "evidence_refs": ["review-report.md", "reviewer-result.json"],
  "unverified": [
    "删除类 token 判定的负向边界（DeleteEvidence、rm-evidence、drop-evidence、clean-evidence、erase-evidence 不触发）无测试覆盖，其有意性由文档推断而非设计裁决确认",
    ".PIPELINE/foo（大写前缀）不被识别为 pipeline 资源因而跳过检查；无测试覆盖",
    "../.pipeline/x 穿越引用被跳过，仅由代码阅读确认，未端到端运行",
    ".pipeline//foo（双斜杠）被接受并交给 Path 拼接，Windows 解析行为仅静态阅读",
    "未做合并与主工作树复验（非审查角色职责）",
    "全量 309 用例未逐条与基线 diff 比对，仅确认被审 diff 中测试改动为纯新增"
  ],
  "identity": {
    "product_head": "5e9e754c6d3fde88f9f04348b1cfbec3b6745722"
  },
  "recommendation": "ready_to_merge"
}
```