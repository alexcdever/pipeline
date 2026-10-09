# 执行报告：historical-archival-migration（revision 2）

- task_id: `historical-archival-migration`
- role: executor
- worktree: `D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration`
- branch: `historical-archival-migration`
- 基线提交: `de5c6c87225bcfcd094dbc6b5d452f82feb8625c`
- 任务单: revision 2，sha256 `4b43c666817ffeaa4d4518addc65524b448469aba88498c0dc5e5684c06ed497`
- 轮次: 2（`verification_surface_changed=true`，上一轮证据作废后按 rev2 重跑重写）
- observed_at_commit: `f552b13179b5783fea742d1434fc6514b6d8a0f0`（产生本证据时的分支尖端）
- 状态: **pass**（5 条验收退出码 0；全量回归 399 passed, 0 failed）

## 1. 环境检查

- worktree 内 `git rev-parse HEAD` = `f552b13179b5783fea742d1434fc6514b6d8a0f0`；分支 `historical-archival-migration`。
- `python -m pipeline_tools --help` 可运行；未改 `pipeline_tools/**`、`.worktrees/**`、`docs/goal.md`。
- `.worktrees/**` 在任务 worktree 视角不可见，分类未依赖它。

## 2. 按声明 id 归档（rev2 机械判据）

rev2 判据：对每张终态单先取其**声明 id**（`<!-- Task ID: -->`）；`.pipeline/<声明 id>/` 存在 → 移到 `.pipeline/<声明 id>/<声明 id>.md`；否则移到 `.pipeline/archive/<声明 id>.md`。文件名与声明 id 不符时以声明 id 为准改名到位。

- 在途 2 张留在 `docs/tasks/`：`historical-archival-migration`、`security-scan-repair-20261001`。
- 终态单共 46 张：**44** 张进声明 id 的证据目录，**2** 张进 `.pipeline/archive/`。
- 文件名 ≠ 声明 id 的 **1** 张：`docs/tasks/repository-evidence-hygiene.md` 声明 id 为 `repository-evidence-hygiene-continuation-5`，改名归位到 `.pipeline/repository-evidence-hygiene-continuation-5/repository-evidence-hygiene-continuation-5.md`（round 1 曾误入 archive 并误建说明单，本轮撤销并归位）。
- archive 现有且仅有 2 张：`implement-plan-coverage-repair-continuation-1.md`、`pipeline-evidence-lifecycle-migration.md`。
- 每张迁移前后 sha256 相同（改的是路径/文件名，不是内容），迁移后仍被 `git ls-files` 跟踪，原路径消失。

### 迁移清单（原路径 → 声明 id → 目标 → sha256 前 → 字节）

| 原路径 | 声明 id | 目标 | sha256(前) | 字节 |
| --- | --- | --- | --- | --- |
| `docs/tasks/acceptance-id-and-template-compliance.md` | `acceptance-id-and-template-compliance` | `.pipeline/acceptance-id-and-template-compliance/acceptance-id-and-template-compliance.md` | `2329761b3a99b07b95283c041c920a86f77c768f554bec9e7a55b0b92cc19a29` | 一致 |
| `docs/tasks/implement-plan-coverage-repair-continuation-1.md` | `implement-plan-coverage-repair-continuation-1` | `.pipeline/archive/implement-plan-coverage-repair-continuation-1.md` | `252a1cdd52403835156d42bfac3b8594d974deedfeae74296c43ea0444e7b532` | 一致 |
| `docs/tasks/pipeline-evidence-lifecycle-migration.md` | `pipeline-evidence-lifecycle-migration` | `.pipeline/archive/pipeline-evidence-lifecycle-migration.md` | `aa9bae303557586b012d3cc8ee91c12669957082bdc0019528951270e675fe00` | 一致 |
| `docs/tasks/derived-creation-removal.md` | `derived-creation-removal` | `.pipeline/derived-creation-removal/derived-creation-removal.md` | `ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd` | 一致 |
| `docs/tasks/derived-generation-support.md` | `derived-generation-support` | `.pipeline/derived-generation-support/derived-generation-support.md` | `16f776df56009bd87635a16eb0ddca04a69719292c01984138a235d8f6268135` | 一致 |
| `docs/tasks/derived-task-dispatch-recovery.md` | `derived-task-dispatch-recovery` | `.pipeline/derived-task-dispatch-recovery/derived-task-dispatch-recovery.md` | `a36573f17a0f1384f7f8a019a2681afcc6117b3d3bebd368d62422176895bd16` | 一致 |
| `docs/tasks/dispatch-fail-closed-and-approval-semantics.md` | `dispatch-fail-closed-and-approval-semantics` | `.pipeline/dispatch-fail-closed-and-approval-semantics/dispatch-fail-closed-and-approval-semantics.md` | `c923b9894dcfc70f6c498da0f3cb868bad0ff43efdf3629b1f1d25f1ee1cdeae` | 一致 |
| `docs/tasks/evidence-finalization-atomicity.md` | `evidence-finalization-atomicity` | `.pipeline/evidence-finalization-atomicity/evidence-finalization-atomicity.md` | `96a648e276e2f1886b11185322f6fc0c83c7d7e5c243e04e12c29eccfd7a9763` | 一致 |
| `docs/tasks/evidence-retention-forward-gate.md` | `evidence-retention-forward-gate` | `.pipeline/evidence-retention-forward-gate/evidence-retention-forward-gate.md` | `d5734173c034da49a552433ff31bb9f7ab8599b791899f006d9cc75bf3d06021` | 一致 |
| `docs/tasks/finalization-and-reconcile-phase.md` | `finalization-and-reconcile-phase` | `.pipeline/finalization-and-reconcile-phase/finalization-and-reconcile-phase.md` | `2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8` | 一致 |
| `docs/tasks/finalization-hygiene.md` | `finalization-hygiene` | `.pipeline/finalization-hygiene/finalization-hygiene.md` | `65f6e2069ad08e3edad532a1c728191b81a96020d6781d427a8b2da0494a552e` | 一致 |
| `docs/tasks/finalization-marker-head-tolerance.md` | `finalization-marker-head-tolerance` | `.pipeline/finalization-marker-head-tolerance/finalization-marker-head-tolerance.md` | `b8af939a90f0e833f6b138499024bbb5e1ed8ac833bd009964372b7ba5f86f76` | 一致 |
| `docs/tasks/finalization-report-reader.md` | `finalization-report-reader` | `.pipeline/finalization-report-reader/finalization-report-reader.md` | `7e8c6a5fb3ce0add707100e484c9dc6b022c58c50dc7a67852a5f41bdeceb4f1` | 一致 |
| `docs/tasks/gate-deletion-semantics-continuation-1.md` | `gate-deletion-semantics-continuation-1` | `.pipeline/gate-deletion-semantics-continuation-1/gate-deletion-semantics-continuation-1.md` | `1721091c5a2d7bb8776cce38e9c7bd9560e6d9f99ed6ca5198d9ca2b839b8129` | 一致 |
| `docs/tasks/gate-deletion-semantics.md` | `gate-deletion-semantics` | `.pipeline/gate-deletion-semantics/gate-deletion-semantics.md` | `ec0668e69513bf4443d958ec9506f15ab965efc0db51529834156a0adec212b0` | 一致 |
| `docs/tasks/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md` | `implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1` | `.pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md` | `16a61fc8050e90430ee34ab2d5ed6c70f389b305e2e9d006de8a31c135e60b46` | 一致 |
| `docs/tasks/implement-plan-completeness-repair-continuation-1.md` | `implement-plan-completeness-repair-continuation-1` | `.pipeline/implement-plan-completeness-repair-continuation-1/implement-plan-completeness-repair-continuation-1.md` | `4a4884c00b244d8de6caf73a248285735e55fe4de03414a9f76b0aef808ada33` | 一致 |
| `docs/tasks/implement-plan-coverage-repair-continuation-2.md` | `implement-plan-coverage-repair-continuation-2` | `.pipeline/implement-plan-coverage-repair-continuation-2/implement-plan-coverage-repair-continuation-2.md` | `87a4959d1837f264c0406744f5d08febef52166ed527e1494f08a2471b3be961` | 一致 |
| `docs/tasks/metrics-tracking-policy-continuation-1.md` | `metrics-tracking-policy-continuation-1` | `.pipeline/metrics-tracking-policy-continuation-1/metrics-tracking-policy-continuation-1.md` | `739e0480c632d786a0b1e06b5298b3842575366fa208774f849d8aa1eb6d6d3f` | 一致 |
| `docs/tasks/metrics-tracking-policy.md` | `metrics-tracking-policy` | `.pipeline/metrics-tracking-policy/metrics-tracking-policy.md` | `7aa7f0f56c018fadf529c6c827a1912d6c88003a3d4ae79daac6d88d9960d2a5` | 一致 |
| `docs/tasks/pipeline-evidence-lifecycle-migration-continuation-1.md` | `pipeline-evidence-lifecycle-migration-continuation-1` | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/pipeline-evidence-lifecycle-migration-continuation-1.md` | `de7fad644d96a27968c782ce9483a9cf4ffe117b27f7c7228675352a67a9b702` | 一致 |
| `docs/tasks/pipeline-tools-v1-continuation-1-repair-continuation-1.md` | `pipeline-tools-v1-continuation-1-repair-continuation-1` | `.pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/pipeline-tools-v1-continuation-1-repair-continuation-1.md` | `b48d690282ebcf95fa0e7842f3f0cc11012f9c716ae4517983d17ffed2db4a60` | 一致 |
| `docs/tasks/pipeline-tools-v1-continuation-1.md` | `pipeline-tools-v1-continuation-1` | `.pipeline/pipeline-tools-v1-continuation-1/pipeline-tools-v1-continuation-1.md` | `2b14846bade8744ad2aa269622f17045a95cb799cec38a8f4a33c2eccc023065` | 一致 |
| `docs/tasks/pipeline-tools-v1-current-identity-revalidation-continuation-1.md` | `pipeline-tools-v1-current-identity-revalidation-continuation-1` | `.pipeline/pipeline-tools-v1-current-identity-revalidation-continuation-1/pipeline-tools-v1-current-identity-revalidation-continuation-1.md` | `fe5030e4f60dcf16da9e8e4777e2a75e8e510a056929efd90545029d8cd9adae` | 一致 |
| `docs/tasks/pipeline-tools-v1.md` | `pipeline-tools-v1` | `.pipeline/pipeline-tools-v1/pipeline-tools-v1.md` | `308b5743615e936070781a4aaa5c9abc2d595e30338d43c76cc581d191e7b22a` | 一致 |
| `docs/tasks/planner-resource-validation.md` | `planner-resource-validation` | `.pipeline/planner-resource-validation/planner-resource-validation.md` | `e4b7807f6fd0170d3b669081b6f735728b6437127195ba9551a163b437d53a71` | 一致 |
| `docs/tasks/planning-driven-vertical-pipeline.md` | `planning-driven-vertical-pipeline` | `.pipeline/planning-driven-vertical-pipeline/planning-driven-vertical-pipeline.md` | `e7c78f86e4cf098c8ad3f8b5b2308b852ac301d32d1b3feef71466bbb49ad498` | 一致 |
| `docs/tasks/planning-facts-conflict-model.md` | `planning-facts-conflict-model` | `.pipeline/planning-facts-conflict-model/planning-facts-conflict-model.md` | `bcbcc8f21d3aa0a1f017b2cb5069225f43b686719c2022d0d690f7906d56f95d` | 一致 |
| `docs/tasks/planning-run-lifecycle.md` | `planning-run-lifecycle` | `.pipeline/planning-run-lifecycle/planning-run-lifecycle.md` | `a60124e347ee6e9318561fbf4bcdc5bda9d69bbaa0f93dd1ba462c7fb11d724b` | 一致 |
| `docs/tasks/planning-run-task-generation.md` | `planning-run-task-generation` | `.pipeline/planning-run-task-generation/planning-run-task-generation.md` | `831c1e1539f1ee08e211b32cac7ac54b081199f6c03815bdf36f137d02e19f42` | 一致 |
| `docs/tasks/planning-to-dispatch-integration.md` | `planning-to-dispatch-integration` | `.pipeline/planning-to-dispatch-integration/planning-to-dispatch-integration.md` | `b05bb8b58f98ad07ccbeeb4fddd1a15751428701e9e952ff009db829115a6f58` | 一致 |
| `docs/tasks/post-merge-evidence-identity.md` | `post-merge-evidence-identity` | `.pipeline/post-merge-evidence-identity/post-merge-evidence-identity.md` | `c32e3c23c23cb830ff867374e1be927880700fc8cd21a88c0654eff1a7dc91a9` | 一致 |
| `docs/tasks/repository-evidence-hygiene.md` | `repository-evidence-hygiene-continuation-5`（改名归位） | `.pipeline/repository-evidence-hygiene-continuation-5/repository-evidence-hygiene-continuation-5.md` | `cf458bd98ce870e433f0cce322b80eafb4961610f80bfdc0424075a25bdd20d9` | 一致 |
| `docs/tasks/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md` | `repository-evidence-hygiene-current-identity-revalidation-continuation-1` | `.pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md` | `1cfce16b13d4caac454ab46d670e917514f889e1b76bd30f06a58796d6899867` | 一致 |
| `docs/tasks/security-scan-repair-20261001-continuation-1.md` | `security-scan-repair-20261001-continuation-1` | `.pipeline/security-scan-repair-20261001-continuation-1/security-scan-repair-20261001-continuation-1.md` | `a8a6c5c38c3fb83921b1961660273e0881559326f9cd11cc1dd0a393f4352fa4` | 一致 |
| `docs/tasks/status-vocabulary-unification.md` | `status-vocabulary-unification` | `.pipeline/status-vocabulary-unification/status-vocabulary-unification.md` | `97e0c80b755ee75084e1b41f2ea1a6698a8739f1f295ce65ee317304835899a2` | 一致 |
| `docs/tasks/task-design-corruption-fix.md` | `task-design-corruption-fix` | `.pipeline/task-design-corruption-fix/task-design-corruption-fix.md` | `b4c3c687eaea292279c96b4581d0200f34191a0232fe7e68ff50612afc29864a` | 一致 |
| `docs/tasks/task-evidence-reconcile.md` | `task-evidence-reconcile` | `.pipeline/task-evidence-reconcile/task-evidence-reconcile.md` | `78fe435782e3b714e50576ac7906aef06820bb16c0b0fa648f739d5491fcda5e` | 一致 |
| `docs/tasks/task-plan-contract-consistency.md` | `task-plan-contract-consistency` | `.pipeline/task-plan-contract-consistency/task-plan-contract-consistency.md` | `de26063c0814c955250397852571dab1342fb9f0546080f54f3ac7848f587708` | 一致 |
| `docs/tasks/task-ref-verifiability.md` | `task-ref-verifiability` | `.pipeline/task-ref-verifiability/task-ref-verifiability.md` | `b8d196da40a0c8a746f1ffd25c1b3c86ed647b793255e8cf9c7caf8c89574adb` | 一致 |
| `docs/tasks/task-sheet-archival.md` | `task-sheet-archival` | `.pipeline/task-sheet-archival/task-sheet-archival.md` | `5f3c92d875e6b03d8fd6a4f314b5c3e6f2e5d7f80786493f15b52370a0040d54` | 一致 |
| `docs/tasks/task-sheet-revision-and-evidence-binding.md` | `task-sheet-revision-and-evidence-binding` | `.pipeline/task-sheet-revision-and-evidence-binding/task-sheet-revision-and-evidence-binding.md` | `a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783` | 一致 |
| `docs/tasks/task-worktree-dispatch-identity.md` | `task-worktree-dispatch-identity` | `.pipeline/task-worktree-dispatch-identity/task-worktree-dispatch-identity.md` | `1bf214c914c12026b434d916c98cafa6c0279d9346dffc8298c2f159d701b0cf` | 一致 |
| `docs/tasks/test-metrics-isolation.md` | `test-metrics-isolation` | `.pipeline/test-metrics-isolation/test-metrics-isolation.md` | `d0f1f14853e8fbd06548bfecb7df5d2fe3f8812d7d0cf33041cea49adf2f6495` | 一致 |
| `docs/tasks/test-ref-narrowing-followup.md` | `test-ref-narrowing-followup` | `.pipeline/test-ref-narrowing-followup/test-ref-narrowing-followup.md` | `c62bf7a506765d8ca90984f04064732654f5463be8654143633f2474927e9d93` | 一致 |
| `docs/tasks/toolchain-freshness-fixes.md` | `toolchain-freshness-fixes` | `.pipeline/toolchain-freshness-fixes/toolchain-freshness-fixes.md` | `8bcc46f11556b926222ff46fabe79d26ee8bdeccd79a78f9b76da67f18555584` | 一致 |

## 3. 撤销的 round 1 产物

- 删除 `docs/tasks/README.md`（避免工作清单扫描产生幻影单 `README`）。
- 删除 round 1 新建的 `.pipeline/repository-evidence-hygiene-continuation-5/repository-evidence-hygiene-continuation-5.md` 说明单；该位置现由按声明 id 归位的真实单子占用。
- 上一轮误提交在证据目录里的非保留名文件（`acceptance-*.log`、`migration-map.json`、`preflight.log` 等）已移除；证据目录现只含保留名 `executor-report.md`、`executor-result.json`（原始日志改写到系统临时目录）。

## 4. 工作清单约定文档（验收测试4）

- `README.md`、`SKILL.md`、`references/merge-and-recovery.md` 三处均写明：`docs/tasks/` 只放进行中或待派发的任务单（`docs/tasks/*.md` 一律按任务单处理，不放 README 之类说明文件）；已终态的单子在其证据目录 `.pipeline/<task-id>/<task-id>.md`，没有证据目录时在 `.pipeline/archive/<task-id>.md`；终态单子按声明 id 归档，文件名与声明 id 不符时以声明 id 为准。
- 三处均不再提 `docs/tasks/README.md`；该文件不存在。
- 一致性用例 `test_lifecycle_and_evidence_documentation_matches_current_contract` 已扩展：三处文档缺任一约定表述、或 `docs/tasks/README.md` 存在时失败。

## 5. 验收命令（经 `python -m pipeline_tools command run --cwd . --task-id historical-archival-migration`）

| 验收 | 命令 | 退出码 | 关键断言 |
| --- | --- | --- | --- |
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked` | 0 | 夹具内迁移：sha256 逐张不变、仍被跟踪、原路径消失、有目录进 `<id>/<id>.md`、无目录进 `archive/<id>.md` |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree` | 0 | 夹具中终态单不再计入 `sheets_without_worktree`；未断言真实仓库该集合为空 |
| acceptance-test-3 | `python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover` | 0 | 文件名 ≠ 声明 id 的单子按声明 id 归位到已有证据目录后，`leftover_evidence` 清空，解析器按声明 id 找到它 |
| acceptance-test-4 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | 三处文档口径一致；`docs/tasks/README.md` 不存在 |
| acceptance-test-5 | `python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration` | 0 | 3 个已最终化任务迁移后 `verify_finalization_snapshot` 不含保留集哈希失配 |

退出码：1→0，2→0，3→0，4→0，5→0。原始日志在系统临时目录 `%TEMP%/pipeline-tools/historical-archival-migration/acceptance-N.log`。

## 6. 全量回归

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q
399 passed, 30 subtests passed in 444.68s
```

- 基线 395 passed；本任务新增 4 个用例 → **399 passed，0 failed**。
- 说明：把全量回归放进 `command run` 会触发其 180s 默认超时（`timed_out=true`），因此全量数字取自直接运行；5 条验收命令均远低于超时，退出码以 `command run` 记录为准。

## 7. 其它检查

- `python -m pipeline_tools planning preflight .` → `status=pass`；`task_scenes.sheets_without_worktree = ['historical-archival-migration','security-scan-repair-20261001']`（只有 2 张在途单，无幻影 `README`）；`leftover_evidence = []`。
- `python -m pipeline_tools scope check . --task-id historical-archival-migration` → PASS。

## 8. 未改动项

- 未编辑任何任务单内容：46 张只移动/改名，逐张 sha256 不变。
- 未改动任何 `finalization.json` 或保留集文件。
- 未改 `pipeline_tools/**`、`docs/goal.md`；未创建/删除/修改 `.worktrees/**`；未删除分支。

## 机器证据

```pipeline-evidence
{"schema": 2, "task_id": "historical-archival-migration", "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "branch": "historical-archival-migration", "role": "executor", "round": 2, "status": "PASS", "head": "f552b13179b5783fea742d1434fc6514b6d8a0f0", "observed_at_commit": "f552b13179b5783fea742d1434fc6514b6d8a0f0", "sheet_revision": 1, "sheet_sha256": "4b43c666817ffeaa4d4518addc65524b448469aba88498c0dc5e5684c06ed497", "generated_at": "2026-10-09T00:00:00+00:00", "commands": [{"command": "git rev-parse HEAD", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools planning preflight .", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools scope check . --task-id historical-archival-migration", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}], "assertions": ["all 46 terminal sheets are filed under their declared id: 44 in .pipeline/<declared-id>/<declared-id>.md and 2 in .pipeline/archive/<declared-id>.md; every sheet's sha256 is byte-identical before and after and each is still tracked", "docs/tasks/repository-evidence-hygiene.md declares repository-evidence-hygiene-continuation-5 and was renamed into that task's evidence directory, so .pipeline/archive/ holds only implement-plan-coverage-repair-continuation-1.md and pipeline-evidence-lifecycle-migration.md", "docs/tasks/ holds only the two in-flight sheets and no README, and planning preflight reports sheets_without_worktree = ['historical-archival-migration', 'security-scan-repair-20261001'] and leftover_evidence = [] with status pass", "all five acceptance commands exit 0 and the full suite is green at 399 passed, 30 subtests passed (0 failed)", "the tracked evidence directory contains only retained names (executor-report.md, executor-result.json); the previous round's scratch logs were removed and rewritten to the system temporary directory"], "evidence_refs": ["executor-report.md", "executor-result.json"], "unverified": ["the full regression cannot run inside command run without hitting its 180s default timeout, so the green number (399 passed) is taken from a direct run of PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q; the five acceptance commands each finished well inside the timeout", "raw acceptance logs were written to the system temporary directory rather than the evidence directory, so they are not committed: tracking scratch files under .pipeline/<task-id>/ would violate the retained-names invariant checked by tests/test_acceptance_id_and_template_compliance.py", "goal hash for docs/goal.md is unrecorded; this task neither modified docs/goal.md nor recorded a hash for it"]}
```
