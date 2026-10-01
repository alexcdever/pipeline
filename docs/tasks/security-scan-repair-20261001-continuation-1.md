# security-scan-repair-20261001-continuation-1：派生任务单

<!-- Task ID: security-scan-repair-20261001-continuation-1 -->

```pipeline-contract
{
  "schema": 4,
  "task_id": "security-scan-repair-20261001-continuation-1",
  "task_type": "derived",
  "project_type": "service",
  "risk": "high",
  "goal": {
    "path": "docs/goal.md"
  },
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
    "\u4e0d\u4fee\u6539\u5386\u53f2\u626b\u63cf\u62a5\u544a\u6216\u5df2\u6709\u4efb\u52a1\u8bc1\u636e",
    "\u4e0d\u6269\u5927\u4e3a\u5168\u4ed3\u5e93\u5b89\u5168\u91cd\u6784",
    "\u4e0d\u5ba3\u79f0\u672a\u7ecf\u9a8c\u8bc1\u7684\u8fdc\u7a0b\u53ef\u5229\u7528\u6027"
  ],
  "operations": [
    {
      "id": "secure-path-sinks",
      "kind": "repair",
      "scope": "capability handshake and derived dispatch filesystem paths",
      "resources": [
        "pipeline_tools/core.py",
        "pipeline_tools/__main__.py"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-1"
      ]
    },
    {
      "id": "secure-evidence-gates",
      "kind": "repair",
      "scope": "evidence reference resolution, identity binding, and scope enforcement",
      "resources": [
        "pipeline_tools/core.py",
        "tests/test_security_repairs.py"
      ],
      "resource_mode": "batch",
      "acceptance_tests": [
        "acceptance-test-2"
      ]
    }
  ],
  "chain": {
    "entry": [
      "pipeline_tools/__main__.py: runtime handshake and derived dispatch CLI"
    ],
    "interaction": [
      "pipeline_tools/core.py: capability_handshake and create_derived_dispatch"
    ],
    "application": [
      "pipeline_tools/core.py: evidence and gate validation"
    ],
    "domain": [
      "path containment, Git identity, and contract scope invariants"
    ],
    "persistence": [
      "capability-handshake.json, worktree/task/evidence paths"
    ],
    "readback": [
      "tests/test_security_repairs.py"
    ],
    "recovery": [
      "derived dispatch rollback and gate failure without side effects"
    ]
  },
  "acceptance_tests": [
    {
      "id": "acceptance-test-1",
      "evidence_level": 3,
      "test_ref": "tests/test_security_repairs.py: SecurityRepairTests.test_path_inputs_are_rejected_before_filesystem_side_effects",
      "command_ref": "python -m pytest -q tests/test_security_repairs.py -k path_inputs",
      "assertions": [
        "absolute, traversal, symlink and unsafe child identifiers are rejected before writes or worktree creation"
      ]
    },
    {
      "id": "acceptance-test-2",
      "evidence_level": 3,
      "test_ref": "tests/test_security_repairs.py: SecurityRepairTests.test_evidence_identity_and_scope_are_enforced",
      "command_ref": "python -m pytest -q tests/test_security_repairs.py -k evidence_identity_scope",
      "assertions": [
        "bare and qualified evidence references use one rule, schema-1 reports cannot pass merge gates, and scope policy is enforced"
      ]
    },
    {
      "id": "acceptance-test-3",
      "evidence_level": 3,
      "test_ref": "tests/test_security_repairs.py: SecurityRepairTests.test_valid_secure_paths_and_references_still_work",
      "command_ref": "python -m pytest -q tests/test_security_repairs.py -k valid_secure",
      "assertions": [
        "authorized paths and evidence references retain expected behavior"
      ]
    },
    {
      "id": "acceptance-test-4",
      "evidence_level": 3,
      "test_ref": "tests/test_security_repairs.py: SecurityRepairTests.test_full_security_regression_suite",
      "command_ref": "python -m pytest -q tests/test_security_repairs.py",
      "assertions": [
        "all security regression tests pass with exit code 0"
      ]
    }
  ],
  "dependencies": [
    "security-scan-repair-20261001"
  ],
  "required_evidence_levels": [
    3
  ],
  "assumptions": [
    {
      "id": "assumption-1",
      "statement": "The approved remediation binds workflow artifacts to the repository root rather than permitting arbitrary external workflow directories."
    }
  ],
  "unknowns": [
    {
      "id": "unknown-1",
      "statement": "Platform-specific symlink behavior must be verified in the execution environment."
    }
  ],
  "derived_from": {
    "task_id": "security-scan-repair-20261001",
    "commit": "43793b50f6167cf76df4b2d6ba51858ad6142a62",
    "branch": "main",
    "parent_task_type": "repair"
  }
}
```
