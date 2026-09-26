# Executor report

```pipeline-evidence
{
  "schema": 1,
  "task_id": "pipeline-evidence-lifecycle-migration-continuation-1",
  "worktree": "D:/Projects/Skills/pipeline/.worktrees/pipeline-evidence-lifecycle-migration-continuation-1",
  "branch": "pipeline-evidence-lifecycle-migration-continuation-1",
  "role": "executor",
  "round": 2,
  "status": "PASS",
  "commands": [
    {"command": "python -m unittest tests.test_planning_dispatch_integration.PlanningDispatchIntegrationTests.test_valid_planning_run_reaches_identity_verified_dispatch -v", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"},
    {"command": "python -m unittest tests.test_git_checks.GitChecks.test_commit_history_evidence_path_guard -v", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"},
    {"command": "python -m unittest tests.test_cli.CLITests.test_evidence_finalize_current_command_preserves_raw_on_block_and_is_idempotent -v", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"},
    {"command": "python -m unittest tests.test_cli.CLITests.test_evidence_verify_current_command_reports_machine_identity_and_finalization_state -v", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"},
    {"command": "python -m unittest tests.test_derived_task_dispatch_recovery.DerivedTaskDispatchRecoveryTests.test_continuation_is_unique_idempotent_and_does_not_rewrite_parent_history -v", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"},
    {"command": "python -m unittest discover -s tests -v", "exit_code": 0, "evidence_ref": ".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"}
  ],
  "assertions": ["All five frozen acceptance tests pass.", "Full regression suite passes: 152 tests.", "History guard detects evidence add/delete commits while metrics remain exempt.", "Finalize preserves raw evidence on block and is idempotent; finalized verify checks marker identity."],
  "evidence_refs": [".pipeline/pipeline-evidence-lifecycle-migration-continuation-1/finalization.json"],
  "unverified": []
}
```
