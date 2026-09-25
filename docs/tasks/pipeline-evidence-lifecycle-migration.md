# 证据生命周期、提交护栏与旧版本迁移

<!-- Task ID: pipeline-evidence-lifecycle-migration -->
<!-- Contract section is frozen after commit. Lifecycle sections are maintained by the main agent. -->

```pipeline-contract
{
  "schema": 1,
  "task_id": "pipeline-evidence-lifecycle-migration",
  "allowed_paths": [
    "pipeline_tools/**",
    "tests/**",
    "SKILL.md",
    "README.md",
    "references/**",
    "templates/**",
    "docs/tasks/pipeline-evidence-lifecycle-migration.md",
    ".pipeline/metrics/**",
    ".pipeline/pipeline-evidence-lifecycle-migration/**"
  ],
  "forbidden_paths": [
    "**/.env",
    "**/*secret*",
    "**/*token*"
  ],
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 2,
      "test_ref": "tests/test_git_checks.py: commit-range evidence path guard cases",
      "command_ref": "python -m unittest tests.test_git_checks -v"
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: active/finalized evidence verification and finalization cases",
      "command_ref": "python -m unittest tests.test_evidence -v"
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 2,
      "test_ref": "tests/test_cli.py: commit check, evidence finalize and finalized gate cases",
      "command_ref": "python -m unittest tests.test_cli -v"
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 2,
      "test_ref": "tests/test_layout.py and tests/test_cli.py: legacy layout reconciliation cases",
      "command_ref": "python -m unittest tests.test_layout tests.test_cli -v"
    },
    {
      "id": "acceptance-test-5",
      "evidence_level": 1,
      "test_ref": "tests/: complete regression suite",
      "command_ref": "python -m unittest discover -s tests -v"
    },
    {
      "id": "acceptance-test-6",
      "evidence_level": 1,
      "test_ref": "SKILL.md, README.md, references and templates: script/LLM boundary and lifecycle policy",
      "command_ref": "python -m pipeline_tools task validate docs/tasks/pipeline-evidence-lifecycle-migration.md"
    }
  ]
}
```

## 任务身份

- 项目：programing-pipeline
- 领域或阶段：证据生命周期、提交护栏与旧版本兼容
- 用户结果或系统能力：子工作树可以提交产品代码和测试，但活动任务证据目录不能进入这些提交；主代理终审后可机械清理原始证据并只保留可验证的报告；旧 `.workflow` 项目可安全迁移到 `.pipeline`。
- 执行 worktree 约定：`D:/Projects/Skills/pipeline/.worktrees/pipeline-evidence-lifecycle-migration`
- 状态：未开始

## 依赖与范围

### 前置条件

- 现有 `pipeline_tools` 的任务契约、证据报告、合并闸门、metrics 和 `.workflow` 迁移能力。
- Python 3.11 标准库；不联网、不新增第三方依赖。

### 允许修改

- `pipeline_tools/**`：提交路径检查、证据最终化/验证、布局迁移与命令入口。
- `tests/**`：上述机械行为的临时 Git、文件系统和 CLI 测试。
- `SKILL.md`、`README.md`、`references/**`、`templates/**`：同步新生命周期、迁移和脚本/大语言模型职责边界。
- 本任务单及本任务最终保留的三份报告；`.pipeline/metrics/**` 继续按项目级规则追踪。

### 明确不改

- 不修改任何外部消费项目、产品代码或用户数据。
- 不让工具从报告散文推断产品是否实现正确，不自动生成或改写产品验收结论。
- 不删除历史任务的原始证据；旧项目迁移默认只做安全布局迁移，语义不明确的报告和任务单交给主代理处理。
- 不删除、清理或重解释 `.pipeline/metrics/**`。
- 不自动合并 Git 分支、不自动提交、不改写既有 Git 历史。

## 事实、假设与待决

### 已确认事实

- `scope_check` 目前只检查当前工作树，不能发现某个提交曾经修改过随后又删除的证据文件。
- 现有证据校验要求引用的文件存在，因此原始日志删除前必须完成报告引用收口。
- `.pipeline/metrics/**` 是项目级追踪目录，应独立于任务证据生命周期。
- 当前旧目录迁移以整个 `.workflow` 重命名为主，遇到 `.pipeline` 已存在会停止。

### 未验证事实

- 各消费项目的旧报告自然语言格式不统一，不能由机械工具判断旧报告是否语义自包含。
- 历史任务是否需要追溯性清理由消费项目维护者决定，本任务不追删历史原始文件。

### 禁止猜测

- 不把旧报告中出现“通过”、零退出码或文件存在当作新版本主代理终审通过。
- 不把旧任务单缺失的功能范围、路径允许列表或验收等级自动补全。
- 不把最终报告中的 `self_contained` 声明当作产品语义正确性的证明；脚本只检查结构和引用闭包。

## 设计与行为契约

[子工作树提交产品代码/测试/普通文档]
→ [机械提交检查] 当前活动 `.pipeline/<task-id>/**` 不出现在任一子分支提交中，`.pipeline/metrics/**` 明确豁免
→ [执行、独立审查、主代理终审] 由大语言模型和真实命令判断产品语义
→ [证据最终化脚本] 检查报告结构、终审状态、引用闭包，删除原始证据并写入保留报告哈希标记
→ [最终证据提交] 只包含三份报告和可选最终化标记，不包含原始日志
→ [合并前/后机械闸门] 分别验证提交历史、最终证据目录、冲突和主工作树状态
→ [旧版本迁移] 自动安全迁移 `.workflow` 布局；冲突、旧任务单和语义报告问题以结构化发现交给主代理

- 机械工具只判断 Git、路径、哈希、文件存在性、机器证据字段、退出码和引用闭包。
- 大语言模型负责产品需求覆盖、测试语义、失败分类、报告散文是否自包含、旧任务单语义映射和是否需要重新验收。
- 任何活动任务证据提交违规都必须阻止合并；逐提交检查，不能只比较最终净差异。
- 最终化失败时原始证据保持不变，不能留下“已最终化”的半完成状态。

## 环境前置

1. 在主工作树确认现有未提交修改不属于本任务；本任务不得覆盖 `IDEA.md` 的已有修改。
2. 提交任务契约后，从主工作树创建唯一 `.worktrees/pipeline-evidence-lifecycle-migration`。
3. 每条命令默认三分钟硬超时；全量测试使用明确的累计上限。
4. 临时 Git 仓库和迁移目录由测试创建并清理；不读取其他项目数据。

## 验收测试

### 验收测试1：活动任务证据提交护栏

- 触发：在临时 Git 仓库的任务分支中分别提交产品文件、活动任务证据文件、删除/重命名证据文件、metrics 文件和先添加后删除证据文件。
- 断言：产品提交和仅 metrics 提交通过；任何曾修改活动任务证据目录的提交均返回身份/范围漂移；检查逐提交历史，不被最终净差异绕过。
- 测试：`tests/test_git_checks.py`：提交范围检查用例。
- 命令：`python -m unittest tests.test_git_checks -v`
- 验收模式：临时真实 Git 仓库集成测试
- 证据等级：2
- 结果要求：不创建、不修改、不删除提交；错误指出提交和路径。

### 验收测试2：证据最终化与保留报告验证

- 触发：对含原始日志引用、非通过终审、完全自包含报告、仅引用三份保留报告的证据目录执行最终化和 finalized 验证。
- 断言：不满足条件时原始文件保持不变；满足条件时只保留 `executor-report.md`、`review-report.md`、`final-check.md` 和最终化标记，报告引用闭包成立，报告哈希与标记一致；metrics 文件不受影响；重复执行是安全幂等结果。
- 测试：`tests/test_evidence.py`：最终化、哈希、闭包、清理和幂等用例。
- 命令：`python -m unittest tests.test_evidence -v`
- 验收模式：本地文件系统集成测试
- 证据等级：2
- 结果要求：删除失败或校验失败不能报告成功。

### 验收测试3：CLI 与合并闸门接线

- 触发：执行 `commit check`、`evidence verify --phase finalized`、`evidence finalize`、`gate pre-merge` 和 `gate post-merge`。
- 断言：参数、退出码、JSON 输出和自动 metrics 身份稳定；pre-merge 能阻止活动证据提交；post-merge 默认验证最终化证据。
- 测试：`tests/test_cli.py`：新命令和闸门用例。
- 命令：`python -m unittest tests.test_cli -v`
- 验收模式：命令程序真实启动
- 证据等级：2
- 结果要求：metrics 自动记录失败不改变原命令退出码，不递归生成 metrics 事件。

### 验收测试4：旧版本布局自动迁移与冲突保护

- 触发：对只存在 `.workflow` 的旧项目、已迁移项目、`.workflow` 与 `.pipeline` 同时存在的项目、旧任务证据路径和旧 metrics 执行迁移/普通工具命令。
- 断言：无冲突时安全迁移且第二次运行不变；metrics 保持字节；双方目录同时存在或存在路径/特殊文件歧义时停止；不自动把旧散文报告或旧任务单升级为 PASS。
- 测试：`tests/test_layout.py` 和 `tests/test_cli.py`：迁移计划、应用、幂等和冲突用例。
- 命令：`python -m unittest tests.test_layout tests.test_cli -v`
- 验收模式：临时文件系统和命令程序集成测试
- 证据等级：2
- 结果要求：迁移失败不删除源目录，不写入重复目录。

### 验收测试5：全量回归

- 触发：执行完整测试套件。
- 断言：所有现有测试和新测试通过，旧 metrics 行为、报告结构校验、超时和脱敏行为不回归。
- 测试：`tests/` 全部测试。
- 命令：`python -m unittest discover -s tests -v`
- 验收模式：命令程序真实启动
- 证据等级：1
- 结果要求：每条命令有明确超时，退出码为 0。

### 验收测试6：文档和模板职责边界

- 触发：校验任务单、读取技能和工具说明、读取证据模板。
- 断言：文档明确脚本硬闸门与大语言模型语义判断的边界；新生命周期、metrics 豁免、迁移限制和失败恢复规则一致；模板支持最终保留报告引用，不要求永久原始日志。
- 测试：文档内容与 `task validate`。
- 命令：`python -m pipeline_tools task validate docs/tasks/pipeline-evidence-lifecycle-migration.md`
- 验收模式：命令程序和文档检查
- 证据等级：1
- 结果要求：无占位符、无互相矛盾的旧流程描述。

## 决策点

1. 旧报告若只有自然语言或其角色/任务身份无法机械确认，保留现场并交主代理，不合成机器 PASS。
2. 旧报告中的 `.workflow` 结构化路径是否重写，只能在目标唯一且不改变产品语义时执行；散文、原始日志和既有提交历史不做全局替换。
3. 历史任务的原始证据不因升级自动删除；需要清理时另行执行显式最终化并保留用户可追溯的迁移记录。

---

## 任务级进度（主代理维护）

> 以下内容不是新的设计权威。契约区在提交后冻结；此处记录进度、裁决和最终结果。

### 任务锚点

- 基线 HEAD：`1a691b5`
- 契约提交：待提交
- 执行分支：待创建
- 执行 worktree：`D:/Projects/Skills/pipeline/.worktrees/pipeline-evidence-lifecycle-migration`

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-1 | 未开始 | - | - | - |
| acceptance-test-2 | 未开始 | - | - | - |
| acceptance-test-3 | 未开始 | - | - | - |
| acceptance-test-4 | 未开始 | - | - | - |
| acceptance-test-5 | 未开始 | - | - | - |
| acceptance-test-6 | 未开始 | - | - | - |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| - | 任务单创建 | 未开始 | - | 契约提交后创建 worktree |

### 设计变更与延续任务索引

- 无。

### 最终结果

- 状态：未开始
- 执行子代理：未开始
- 独立审查子代理：未开始
- 主代理最终检查：未开始
- 合并提交：-
- 合并后复验：未开始
- 遗留项：-
