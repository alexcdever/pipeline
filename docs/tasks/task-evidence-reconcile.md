# 任务：任务证据对账修复

<!-- Task ID: task-evidence-reconcile -->
<!-- 本任务只记录可由机械扫描和直接命令输出证明的事实；历史不足时保持 UNVERIFIED，不得伪造。 -->

```pipeline-contract
{
  "schema": 2,
  "task_id": "task-evidence-reconcile",
  "task_type": "repair",
  "implement_plan": {"path": "implement-plan.md"},
  "allowed_paths": ["pipeline_tools/**", "tests/**", "docs/tasks/**", "references/**"],
  "forbidden_paths": ["implement-plan.md", "IDEA.md", ".pipeline/**", ".pipeline/metrics/**"],
  "operations": [
    {
      "id": "repair-reconcile",
      "kind": "mechanical-evidence-reconciliation",
      "scope": "scan docs/tasks and .pipeline evidence, then update only evidence-backed task status",
      "acceptance_tests": [
        "acceptance-test-contract",
        "acceptance-test-dispatch",
        "acceptance-test-finalization",
        "acceptance-test-acceptance",
        "acceptance-test-reconcile"
      ]
    }
  ],
  "chain": {
    "entry": ["docs/tasks/*.md"],
    "interaction": ["pipeline_tools dispatch and freshness checks"],
    "application": ["pipeline_tools task/evidence lifecycle"],
    "domain": ["task identity and evidence status contract"],
    "persistence": [".pipeline/task-evidence-reconcile/ reports and evidence"],
    "readback": ["task-id/branch/worktree/HEAD/result/freshness/readiness/verify fields"],
    "recovery": ["UNVERIFIED for insufficient history; no fabricated PASS"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-contract",
      "evidence_level": 1,
      "test_ref": "tests/test_contract.py: ContractTests::test_schema2_planning_contract_is_valid",
      "command_ref": "python -m pytest tests/test_contract.py::ContractTests::test_schema2_planning_contract_is_valid"
    },
    {
      "id": "acceptance-test-dispatch",
      "evidence_level": 2,
      "test_ref": "tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests::test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume",
      "command_ref": "python -m pytest tests/test_derived_task_dispatch_recovery.py::DerivedTaskDispatchRecoveryTests::test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume"
    },
    {
      "id": "acceptance-test-finalization",
      "evidence_level": 2,
      "test_ref": "tests/test_evidence.py: EvidenceTests::test_gate_requires_pass_statuses",
      "command_ref": "python -m pytest tests/test_evidence.py::EvidenceTests::test_gate_requires_pass_statuses"
    },
    {
      "id": "acceptance-test-acceptance",
      "evidence_level": 1,
      "test_ref": "tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests::test_all_frozen_acceptance_ids_have_exact_test_references",
      "command_ref": "python -m pytest tests/test_acceptance_id_and_template_compliance.py::AcceptanceIdAndTemplateComplianceTests::test_all_frozen_acceptance_ids_have_exact_test_references"
    },
    {
      "id": "acceptance-test-reconcile",
      "evidence_level": 2,
      "test_ref": "tests/test_worktree_dispatch_identity.py: WorktreeDispatchIdentityTests::test_identity_drift_and_duplicate_worktree_are_blocked",
      "command_ref": "python -m pytest tests/test_worktree_dispatch_identity.py::WorktreeDispatchIdentityTests::test_identity_drift_and_duplicate_worktree_are_blocked"
    }
  ],
  "dependencies": [
    "dispatch repair",
    "finalization repair",
    "acceptance repair"
  ],
  "required_evidence_levels": [1, 2]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：schema2 证据修复与任务状态对账
- 用户结果或系统能力：机械核对任务单与 `.pipeline` 证据，避免把缺失、过期或漂移证据写成完成。
- 执行 worktree 约定：`<仓库根目录>/.worktrees/task-evidence-reconcile`；本任务为主工作树文档变更，不创建或派发实现 worktree。
- 状态：未开始

## 依赖与范围

### 前置条件

- dispatch repair、finalization repair、acceptance repair 已提供可读取的身份、结果、终结和验收证据契约；若依赖历史不足，标记 `UNVERIFIED`。
- 机械扫描对象为 `docs/tasks/**` 任务单及 `.pipeline/**` 任务证据；扫描不修改 `.pipeline`。

### 允许修改

- `pipeline_tools/**`
- `tests/**`
- `docs/tasks/**`
- `references/**`

### 明确不改

- `implement-plan.md`、`IDEA.md`、`.pipeline/**`（包括 `.pipeline/metrics/**`）
- 不伪造测试结果、报告、时间戳、HEAD、分支、worktree 或历史事实。

## 事实、假设与待决

### 已确认事实

- schema 2 contract 要求完整的 `acceptance-test-*`、七段 chain、operations、dependencies 和 evidence levels；由 `pipeline_tools/contract.py` 机械校验。
- 任务级状态只可写入当前任务单，并且只能引用本轮直接读取的文件、命令输出或测试产物。

### 未验证事实

- 任何任务的 dispatch、finalization、acceptance、freshness、readiness 或 verify 状态，在扫描前均为 `UNVERIFIED`。
- 历史证据若不能同时绑定 task-id、branch、worktree、HEAD、结果与时间新鲜度，不得推导为 PASS。

### 禁止猜测

- 不以通知、代理自述、旧报告存在、绿色测试数量或退出码单独推导任务完成。
- 不把依赖任务的状态复制为本任务状态；身份漂移、证据缺失或过期必须保留阻塞事实。

## 设计与行为契约

[触发] 运行 task validate 及证据对账流程
→ [处理] 机械扫描 `docs/tasks/**` 与 `.pipeline/**`，逐任务核对身份和阶段字段
→ [状态] 仅在任务单写入有直接证据支持的状态；不足则写 `UNVERIFIED`
→ [可见结果] 任务单具备可回溯的 task-id、branch、worktree、HEAD、result、freshness、readiness、verify 记录，且不产生伪造证据

- dispatch、finalization、acceptance 三类修复是前置依赖；依赖未满足不冒充最终通过。
- 任何字段的证据必须能回溯到同一 task-id 和同一证据目录；冲突保留为 BLOCKED/UNVERIFIED。
- 机械校验失败即停止该结论，不通过文字改写绕过。

## 环境前置

1. 从仓库根目录运行 `python -m pipeline_tools task validate docs/tasks/task-evidence-reconcile.md`。
2. 需要读取 `.pipeline` 时只读扫描；不得写入 `.pipeline` 或其 metrics。

## 验收测试

### 验收测试1：schema2 contract 可校验

- 触发：对本任务单执行 `task validate`。
- 断言：schema 2、完整 acceptance IDs、操作引用、七段 chain 和范围约束通过机械校验。
- 测试：`tests/test_contract.py: ContractTests::test_schema2_planning_contract_is_valid`
- 命令：`python -m pytest tests/test_contract.py::ContractTests::test_schema2_planning_contract_is_valid`
- 验收模式：单元
- 证据等级：1
- 结果要求：退出码 0；无占位符或缺失 contract 字段。

### 验收测试2：dispatch 身份漂移 fail-closed

- 触发：扫描缺失证据或 task identity 漂移。
- 断言：保留父任务历史并阻止恢复，不写 PASS。
- 测试：`tests/test_derived_task_dispatch_recovery.py: DerivedTaskDispatchRecoveryTests::test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume`
- 命令：`python -m pytest tests/test_derived_task_dispatch_recovery.py::DerivedTaskDispatchRecoveryTests::test_missing_evidence_and_identity_drift_preserve_parent_and_block_resume`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；漂移结论为阻塞或未验证。

### 验收测试3：finalization 只接受通过状态

- 触发：对终结证据执行 gate/readiness/verify 前置检查。
- 断言：非 PASS 的报告不能被终结闸门接受。
- 测试：`tests/test_evidence.py: EvidenceTests::test_gate_requires_pass_statuses`
- 命令：`python -m pytest tests/test_evidence.py::EvidenceTests::test_gate_requires_pass_statuses`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；缺失或非通过状态不被改写。

### 验收测试4：acceptance 引用完整且精确

- 触发：对所有冻结任务单检查 acceptance IDs 与测试引用。
- 断言：每个 ID 都是完整 `acceptance-test-*`，并绑定精确文件、方法和命令。
- 测试：`tests/test_acceptance_id_and_template_compliance.py: AcceptanceIdAndTemplateComplianceTests::test_all_frozen_acceptance_ids_have_exact_test_references`
- 命令：`python -m pytest tests/test_acceptance_id_and_template_compliance.py::AcceptanceIdAndTemplateComplianceTests::test_all_frozen_acceptance_ids_have_exact_test_references`
- 验收模式：单元
- 证据等级：1
- 结果要求：退出码 0；不存在缩写、重复或无目标引用。

### 验收测试5：worktree/branch/HEAD 身份核对

- 触发：对任务 evidence 执行身份对账。
- 断言：重复 worktree、身份漂移或未冻结任务被阻止。
- 测试：`tests/test_worktree_dispatch_identity.py: WorktreeDispatchIdentityTests::test_identity_drift_and_duplicate_worktree_are_blocked`
- 命令：`python -m pytest tests/test_worktree_dispatch_identity.py::WorktreeDispatchIdentityTests::test_identity_drift_and_duplicate_worktree_are_blocked`
- 验收模式：集成
- 证据等级：2
- 结果要求：退出码 0；task-id、branch、worktree、HEAD 不一致时不得报告通过。

## 外部操作

- 不执行提交、推送、合并、删除 worktree 或修改外部服务。
- 如需外部授权、凭据、真实浏览器/设备或依赖服务，停止并记录为 `BLOCKED`，不以本地扫描替代。

---

## 任务级进度（主代理维护）

> 只记录当前任务直接读取或运行得到的事实；历史不足统一标 `UNVERIFIED`。本任务按用户要求直接在主工作树创建，未创建执行 worktree。

### 任务锚点

- 基线 HEAD：UNVERIFIED
- 契约提交：不适用（用户要求不提交）
- 执行分支：UNVERIFIED
- 执行 worktree：主工作树（绝对路径待机械命令确认）

### 验收台账

| 验收测试 | 状态 | 当前测试/命令 | 最新证据 | 备注 |
|---|---|---|---|---|
| acceptance-test-contract | UNVERIFIED | - | - | 生成后待运行 |
| acceptance-test-dispatch | UNVERIFIED | - | - | 生成后待运行 |
| acceptance-test-finalization | UNVERIFIED | - | - | 生成后待运行 |
| acceptance-test-acceptance | UNVERIFIED | - | - | 生成后待运行 |
| acceptance-test-reconcile | UNVERIFIED | - | - | 生成后待运行 |

### 执行记录

| 时间/轮次 | 事件 | 结果 | 证据 | 后续 |
|---|---|---|---|---|
| 创建轮 | 任务单新增 | UNVERIFIED | `docs/tasks/task-evidence-reconcile.md` | 运行 task validate |
| 校验轮 | `python -m pipeline_tools task validate docs/tasks/task-evidence-reconcile.md` | PASS | 退出码 0，终端输出 `PASS` | 不提交；验收测试仍为 UNVERIFIED |

### 设计变更与延续任务索引

- 无。若发现依赖修复或契约需要改变，建立 continuation，不覆盖本任务历史。

### 最终结果

- 状态：通过（`python -m pipeline_tools task validate docs/tasks/task-evidence-reconcile.md` 退出码 0）；验收测试尚未运行，未提交
- 执行子代理：不适用
- 独立审查子代理：未开始
- 主代理最终检查：未开始
- 合并提交：不适用（用户明确要求不提交）
- 合并后复验：不适用
- 遗留项：运行校验后的退出码与输出；任何历史不足保持 `UNVERIFIED`
``` 

## 对账字段定义

机械扫描逐任务记录以下字段：`task-id`、`branch`、`worktree`、`HEAD`、`result`、`freshness`、`readiness`、`verify`。字段缺失、来源不一致、历史过期或无法绑定同一证据目录时，只能写 `UNVERIFIED` 或 `BLOCKED`，不得补值。

## 进度区更新规则

任务级状态只写有证据事实；每次更新必须保留命令、退出码、证据路径及身份锚点。扫描顺序固定为：读取任务单 → 读取 `.pipeline` 证据 → 核对身份 → 核对结果与新鲜度 → 核对 readiness/verify → 更新本任务进度区。不得另建项目级状态文档。

> 本任务单本身的 contract 与进度区是唯一任务事实源；`.pipeline` 仅作为被扫描的证据来源，禁止本任务写入。
``` 

## 备注

- `implement_plan.path` 保留 schema 2 必需字段；该文件同时列入禁止修改范围。
- 本文档创建后只运行 `task validate`，不提交。

---



## 决策点

1. 历史语义与模板冲突时保留原语义并标记 UNVERIFIED。
2. 产品行为或实现计划变化另开 continuation。
