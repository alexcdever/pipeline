# 安全扫描漏洞修复

<!-- Task ID: security-scan-repair-20261001 -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "security-scan-repair-20261001",
  "task_type": "repair",
  "project_type": "service",
  "risk": "high",
  "goal": {"path": "docs/goal.md"},
  "allowed_paths": [
    "pipeline_tools/core.py",
    "pipeline_tools/__main__.py",
    "tests/test_security_repairs.py",
    "docs/tasks/security-scan-repair-20261001.md",
    ".pipeline/security-scan-repair-20261001/**"
  ],
  "forbidden_paths": [
    "pipeline_tools/**/secrets/**",
    ".env",
    "credentials/**"
  ],
  "non_goals": [
    "不修改历史扫描报告或已有任务证据",
    "不扩大为全仓库安全重构",
    "不宣称未经验证的远程可利用性"
  ],
  "operations": [
    {
      "id": "secure-path-sinks",
      "kind": "repair",
      "scope": "capability handshake and derived dispatch filesystem paths",
      "resources": ["pipeline_tools/core.py", "pipeline_tools/__main__.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-1"]
    },
    {
      "id": "secure-evidence-gates",
      "kind": "repair",
      "scope": "evidence reference resolution, identity binding, and scope enforcement",
      "resources": ["pipeline_tools/core.py", "tests/test_security_repairs.py"],
      "resource_mode": "batch",
      "acceptance_tests": ["acceptance-test-2"]
    }
  ],
  "chain": {
    "entry": ["pipeline_tools/__main__.py: runtime handshake and derived dispatch CLI"],
    "interaction": ["pipeline_tools/core.py: capability_handshake and create_derived_dispatch"],
    "application": ["pipeline_tools/core.py: evidence and gate validation"],
    "domain": ["path containment, Git identity, and contract scope invariants"],
    "persistence": ["capability-handshake.json, worktree/task/evidence paths"],
    "readback": ["tests/test_security_repairs.py"],
    "recovery": ["derived dispatch rollback and gate failure without side effects"]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_security_repairs.py: SecurityRepairTests.test_path_inputs_are_rejected_before_filesystem_side_effects",
      "command_ref": "python -m pytest -q tests/test_security_repairs.py -k path_inputs",
      "assertions": ["absolute, traversal, symlink and unsafe child identifiers are rejected before writes or worktree creation"]
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_security_repairs.py: SecurityRepairTests.test_evidence_identity_and_scope_are_enforced",
      "command_ref": "python -m pytest -q tests/test_security_repairs.py -k evidence_identity_scope",
      "assertions": ["bare and qualified evidence references use one rule, schema-1 reports cannot pass merge gates, and scope policy is enforced"]
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_security_repairs.py: SecurityRepairTests.test_valid_secure_paths_and_references_still_work",
      "command_ref": "python -m pytest -q tests/test_security_repairs.py -k valid_secure",
      "assertions": ["authorized paths and evidence references retain expected behavior"]
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_security_repairs.py: SecurityRepairTests.test_full_security_regression_suite",
      "command_ref": "python -m pytest -q tests/test_security_repairs.py",
      "assertions": ["all security regression tests pass with exit code 0"]
    }
  ],
  "dependencies": [],
  "required_evidence_levels": [3],
  "assumptions": [{"id": "assumption-1", "statement": "The approved remediation binds workflow artifacts to the repository root rather than permitting arbitrary external workflow directories."}],
  "unknowns": [{"id": "unknown-1", "statement": "Platform-specific symlink behavior must be verified in the execution environment."}]
}
```

## 任务身份

- 项目：pipeline
- 领域或阶段：安全扫描修复
- 任务类型：`repair`
- 用户结果或系统能力：扫描确认的路径越界、证据完整性和范围闸门漏洞被修复并由回归测试证明
- 执行 worktree 约定：`.worktrees/security-scan-repair-20261001`

## 依赖与范围

### 允许修改

- `pipeline_tools/core.py`
- `pipeline_tools/__main__.py`（仅在 CLI 边界需要安全校验时）
- `tests/test_security_repairs.py`
- 本任务的正式 evidence

### 明确不改

- 历史扫描临时目录和已有 `.pipeline` 任务证据
- `docs/goal.md`
- 与本扫描 finding 无关的产品行为

## 事实与待决

### 已确认事实

- 聚合扫描基线为 `0bd151ad1e67f36ab70e237e873374f64011fcd6`。
- 发现涉及 `create_derived_dispatch`、`capability_handshake`、evidence reference resolution、schema-1 identity binding 和 `gate_check` scope enforcement。
- 当前工作树在任务创建前 clean。

### 未验证事实

- 尚未在实现 worktree 中运行新增测试或全量测试。
- 尚未验证 Windows 环境下 symlink 创建的具体权限行为。

## 设计与行为契约

调用者提供的任务 ID、分支和 workflow 路径必须先通过安全语法与授权根目录 containment 校验，再进行任何 Git、目录创建或文件写入。证据引用统一按任务 evidence 目录解析裸引用、按项目根解析 `.pipeline/...` 引用。schema-1 只保留历史读取兼容，不得通过正式 pre-merge/post-merge gate。gate 必须自动依据当前任务契约检查允许/禁止范围；失败只返回阻断结果，不创建越界副作用。

## 环境前置

1. Python、Git 和 pytest 可执行。
2. 在执行 worktree 中运行聚焦和全量测试。

## 验收测试

详见机器契约中的 `acceptance_tests`；执行报告必须记录完整命令、退出码、断言和 evidence reference。

## 决策点

若现有调用方依赖 workflow 目录位于仓库外，必须暂停并请求用户裁决；本任务默认按扫描 remediation 采用仓库根目录 containment。
