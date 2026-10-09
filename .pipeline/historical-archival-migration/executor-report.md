# 执行报告：historical-archival-migration

- task_id: `historical-archival-migration`
- role: executor
- worktree: `D:/Projects/Skills/pipeline/.worktrees/historical-archival-migration`
- branch: `historical-archival-migration`
- 基线提交: `de5c6c87225bcfcd094dbc6b5d452f82feb8625c`
- 轮次: 1
- observed_at_commit: `c063bbda9f2953be054466e7f524f45c10e133c2`（产生本证据时的分支尖端）
- 状态: **blocked**（5 条验收全绿；全量回归 2 红，红点位于本任务 `allowed_paths` 之外，见「决策点」）

## 1. 环境检查

- `git rev-parse HEAD` = `de5c6c87225bcfcd094dbc6b5d452f82feb8625c`（等于基线）；`git branch --show-current` = `historical-archival-migration`。
- `python -m pipeline_tools --help` 可运行。
- 可写 `.pipeline/historical-archival-migration/**`，可运行 pytest。
- 未改动 `pipeline_tools/**`、`.worktrees/**`、`docs/goal.md`（本 worktree 视角下 `.worktrees/` 不可见）。

## 2. 迁移执行（A）

分类只依据：显式在途排除清单 + `.pipeline/<task-id>/` 目录是否存在（不依赖 worktree 可见性）。

- 在途、留在 `docs/tasks/`：`historical-archival-migration`、`security-scan-repair-20261001`。
- 迁移前 `docs/tasks/*.md` 共 48 张；迁移 46 张（有证据目录 43 张 → `.pipeline/<id>/<id>.md`；无证据目录 3 张 → `.pipeline/archive/<id>.md`）。
- 每张迁移前后 `sha256` 相同；迁移后仍被 `git ls-files` 跟踪；原路径消失。
- 迁移后 `docs/tasks/*.md` 只剩 2 张在途单（+ 新增 `README.md`）。

无证据目录、入 `.pipeline/archive/` 的 3 张：`implement-plan-coverage-repair-continuation-1`、`pipeline-evidence-lifecycle-migration`、`repository-evidence-hygiene`。

### 迁移清单（id → 目标 → 前后 sha256）

| task-id | 目标 | sha256(前) | sha256(后) | 字节 |
| --- | --- | --- | --- | --- |
| `acceptance-id-and-template-compliance` | `.pipeline/acceptance-id-and-template-compliance/acceptance-id-and-template-compliance.md` | `2329761b3a99b07b95283c041c920a86f77c768f554bec9e7a55b0b92cc19a29` | `2329761b3a99b07b95283c041c920a86f77c768f554bec9e7a55b0b92cc19a29` | 一致 |
| `implement-plan-coverage-repair-continuation-1` | `.pipeline/archive/implement-plan-coverage-repair-continuation-1.md` | `252a1cdd52403835156d42bfac3b8594d974deedfeae74296c43ea0444e7b532` | `252a1cdd52403835156d42bfac3b8594d974deedfeae74296c43ea0444e7b532` | 一致 |
| `pipeline-evidence-lifecycle-migration` | `.pipeline/archive/pipeline-evidence-lifecycle-migration.md` | `aa9bae303557586b012d3cc8ee91c12669957082bdc0019528951270e675fe00` | `aa9bae303557586b012d3cc8ee91c12669957082bdc0019528951270e675fe00` | 一致 |
| `repository-evidence-hygiene` | `.pipeline/archive/repository-evidence-hygiene.md` | `cf458bd98ce870e433f0cce322b80eafb4961610f80bfdc0424075a25bdd20d9` | `cf458bd98ce870e433f0cce322b80eafb4961610f80bfdc0424075a25bdd20d9` | 一致 |
| `derived-creation-removal` | `.pipeline/derived-creation-removal/derived-creation-removal.md` | `ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd` | `ff027c6dc38d1b44ef1a0242b56ca5c5a9f9b37eb7d6b5d9dbe77ead2f544dbd` | 一致 |
| `derived-generation-support` | `.pipeline/derived-generation-support/derived-generation-support.md` | `16f776df56009bd87635a16eb0ddca04a69719292c01984138a235d8f6268135` | `16f776df56009bd87635a16eb0ddca04a69719292c01984138a235d8f6268135` | 一致 |
| `derived-task-dispatch-recovery` | `.pipeline/derived-task-dispatch-recovery/derived-task-dispatch-recovery.md` | `a36573f17a0f1384f7f8a019a2681afcc6117b3d3bebd368d62422176895bd16` | `a36573f17a0f1384f7f8a019a2681afcc6117b3d3bebd368d62422176895bd16` | 一致 |
| `dispatch-fail-closed-and-approval-semantics` | `.pipeline/dispatch-fail-closed-and-approval-semantics/dispatch-fail-closed-and-approval-semantics.md` | `c923b9894dcfc70f6c498da0f3cb868bad0ff43efdf3629b1f1d25f1ee1cdeae` | `c923b9894dcfc70f6c498da0f3cb868bad0ff43efdf3629b1f1d25f1ee1cdeae` | 一致 |
| `evidence-finalization-atomicity` | `.pipeline/evidence-finalization-atomicity/evidence-finalization-atomicity.md` | `96a648e276e2f1886b11185322f6fc0c83c7d7e5c243e04e12c29eccfd7a9763` | `96a648e276e2f1886b11185322f6fc0c83c7d7e5c243e04e12c29eccfd7a9763` | 一致 |
| `evidence-retention-forward-gate` | `.pipeline/evidence-retention-forward-gate/evidence-retention-forward-gate.md` | `d5734173c034da49a552433ff31bb9f7ab8599b791899f006d9cc75bf3d06021` | `d5734173c034da49a552433ff31bb9f7ab8599b791899f006d9cc75bf3d06021` | 一致 |
| `finalization-and-reconcile-phase` | `.pipeline/finalization-and-reconcile-phase/finalization-and-reconcile-phase.md` | `2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8` | `2bc3b589446d9dd671d214615199c75c587450fb9a1887bb95e20032bdfb6ce8` | 一致 |
| `finalization-hygiene` | `.pipeline/finalization-hygiene/finalization-hygiene.md` | `65f6e2069ad08e3edad532a1c728191b81a96020d6781d427a8b2da0494a552e` | `65f6e2069ad08e3edad532a1c728191b81a96020d6781d427a8b2da0494a552e` | 一致 |
| `finalization-marker-head-tolerance` | `.pipeline/finalization-marker-head-tolerance/finalization-marker-head-tolerance.md` | `b8af939a90f0e833f6b138499024bbb5e1ed8ac833bd009964372b7ba5f86f76` | `b8af939a90f0e833f6b138499024bbb5e1ed8ac833bd009964372b7ba5f86f76` | 一致 |
| `finalization-report-reader` | `.pipeline/finalization-report-reader/finalization-report-reader.md` | `7e8c6a5fb3ce0add707100e484c9dc6b022c58c50dc7a67852a5f41bdeceb4f1` | `7e8c6a5fb3ce0add707100e484c9dc6b022c58c50dc7a67852a5f41bdeceb4f1` | 一致 |
| `gate-deletion-semantics-continuation-1` | `.pipeline/gate-deletion-semantics-continuation-1/gate-deletion-semantics-continuation-1.md` | `1721091c5a2d7bb8776cce38e9c7bd9560e6d9f99ed6ca5198d9ca2b839b8129` | `1721091c5a2d7bb8776cce38e9c7bd9560e6d9f99ed6ca5198d9ca2b839b8129` | 一致 |
| `gate-deletion-semantics` | `.pipeline/gate-deletion-semantics/gate-deletion-semantics.md` | `ec0668e69513bf4443d958ec9506f15ab965efc0db51529834156a0adec212b0` | `ec0668e69513bf4443d958ec9506f15ab965efc0db51529834156a0adec212b0` | 一致 |
| `implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1` | `.pipeline/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1/implement-plan-completeness-repair-continuation-1-evidence-revalidation-continuation-1.md` | `16a61fc8050e90430ee34ab2d5ed6c70f389b305e2e9d006de8a31c135e60b46` | `16a61fc8050e90430ee34ab2d5ed6c70f389b305e2e9d006de8a31c135e60b46` | 一致 |
| `implement-plan-completeness-repair-continuation-1` | `.pipeline/implement-plan-completeness-repair-continuation-1/implement-plan-completeness-repair-continuation-1.md` | `4a4884c00b244d8de6caf73a248285735e55fe4de03414a9f76b0aef808ada33` | `4a4884c00b244d8de6caf73a248285735e55fe4de03414a9f76b0aef808ada33` | 一致 |
| `implement-plan-coverage-repair-continuation-2` | `.pipeline/implement-plan-coverage-repair-continuation-2/implement-plan-coverage-repair-continuation-2.md` | `87a4959d1837f264c0406744f5d08febef52166ed527e1494f08a2471b3be961` | `87a4959d1837f264c0406744f5d08febef52166ed527e1494f08a2471b3be961` | 一致 |
| `metrics-tracking-policy-continuation-1` | `.pipeline/metrics-tracking-policy-continuation-1/metrics-tracking-policy-continuation-1.md` | `739e0480c632d786a0b1e06b5298b3842575366fa208774f849d8aa1eb6d6d3f` | `739e0480c632d786a0b1e06b5298b3842575366fa208774f849d8aa1eb6d6d3f` | 一致 |
| `metrics-tracking-policy` | `.pipeline/metrics-tracking-policy/metrics-tracking-policy.md` | `7aa7f0f56c018fadf529c6c827a1912d6c88003a3d4ae79daac6d88d9960d2a5` | `7aa7f0f56c018fadf529c6c827a1912d6c88003a3d4ae79daac6d88d9960d2a5` | 一致 |
| `pipeline-evidence-lifecycle-migration-continuation-1` | `.pipeline/pipeline-evidence-lifecycle-migration-continuation-1/pipeline-evidence-lifecycle-migration-continuation-1.md` | `de7fad644d96a27968c782ce9483a9cf4ffe117b27f7c7228675352a67a9b702` | `de7fad644d96a27968c782ce9483a9cf4ffe117b27f7c7228675352a67a9b702` | 一致 |
| `pipeline-tools-v1-continuation-1-repair-continuation-1` | `.pipeline/pipeline-tools-v1-continuation-1-repair-continuation-1/pipeline-tools-v1-continuation-1-repair-continuation-1.md` | `b48d690282ebcf95fa0e7842f3f0cc11012f9c716ae4517983d17ffed2db4a60` | `b48d690282ebcf95fa0e7842f3f0cc11012f9c716ae4517983d17ffed2db4a60` | 一致 |
| `pipeline-tools-v1-continuation-1` | `.pipeline/pipeline-tools-v1-continuation-1/pipeline-tools-v1-continuation-1.md` | `2b14846bade8744ad2aa269622f17045a95cb799cec38a8f4a33c2eccc023065` | `2b14846bade8744ad2aa269622f17045a95cb799cec38a8f4a33c2eccc023065` | 一致 |
| `pipeline-tools-v1-current-identity-revalidation-continuation-1` | `.pipeline/pipeline-tools-v1-current-identity-revalidation-continuation-1/pipeline-tools-v1-current-identity-revalidation-continuation-1.md` | `fe5030e4f60dcf16da9e8e4777e2a75e8e510a056929efd90545029d8cd9adae` | `fe5030e4f60dcf16da9e8e4777e2a75e8e510a056929efd90545029d8cd9adae` | 一致 |
| `pipeline-tools-v1` | `.pipeline/pipeline-tools-v1/pipeline-tools-v1.md` | `308b5743615e936070781a4aaa5c9abc2d595e30338d43c76cc581d191e7b22a` | `308b5743615e936070781a4aaa5c9abc2d595e30338d43c76cc581d191e7b22a` | 一致 |
| `planner-resource-validation` | `.pipeline/planner-resource-validation/planner-resource-validation.md` | `e4b7807f6fd0170d3b669081b6f735728b6437127195ba9551a163b437d53a71` | `e4b7807f6fd0170d3b669081b6f735728b6437127195ba9551a163b437d53a71` | 一致 |
| `planning-driven-vertical-pipeline` | `.pipeline/planning-driven-vertical-pipeline/planning-driven-vertical-pipeline.md` | `e7c78f86e4cf098c8ad3f8b5b2308b852ac301d32d1b3feef71466bbb49ad498` | `e7c78f86e4cf098c8ad3f8b5b2308b852ac301d32d1b3feef71466bbb49ad498` | 一致 |
| `planning-facts-conflict-model` | `.pipeline/planning-facts-conflict-model/planning-facts-conflict-model.md` | `bcbcc8f21d3aa0a1f017b2cb5069225f43b686719c2022d0d690f7906d56f95d` | `bcbcc8f21d3aa0a1f017b2cb5069225f43b686719c2022d0d690f7906d56f95d` | 一致 |
| `planning-run-lifecycle` | `.pipeline/planning-run-lifecycle/planning-run-lifecycle.md` | `a60124e347ee6e9318561fbf4bcdc5bda9d69bbaa0f93dd1ba462c7fb11d724b` | `a60124e347ee6e9318561fbf4bcdc5bda9d69bbaa0f93dd1ba462c7fb11d724b` | 一致 |
| `planning-run-task-generation` | `.pipeline/planning-run-task-generation/planning-run-task-generation.md` | `831c1e1539f1ee08e211b32cac7ac54b081199f6c03815bdf36f137d02e19f42` | `831c1e1539f1ee08e211b32cac7ac54b081199f6c03815bdf36f137d02e19f42` | 一致 |
| `planning-to-dispatch-integration` | `.pipeline/planning-to-dispatch-integration/planning-to-dispatch-integration.md` | `b05bb8b58f98ad07ccbeeb4fddd1a15751428701e9e952ff009db829115a6f58` | `b05bb8b58f98ad07ccbeeb4fddd1a15751428701e9e952ff009db829115a6f58` | 一致 |
| `post-merge-evidence-identity` | `.pipeline/post-merge-evidence-identity/post-merge-evidence-identity.md` | `c32e3c23c23cb830ff867374e1be927880700fc8cd21a88c0654eff1a7dc91a9` | `c32e3c23c23cb830ff867374e1be927880700fc8cd21a88c0654eff1a7dc91a9` | 一致 |
| `repository-evidence-hygiene-current-identity-revalidation-continuation-1` | `.pipeline/repository-evidence-hygiene-current-identity-revalidation-continuation-1/repository-evidence-hygiene-current-identity-revalidation-continuation-1.md` | `1cfce16b13d4caac454ab46d670e917514f889e1b76bd30f06a58796d6899867` | `1cfce16b13d4caac454ab46d670e917514f889e1b76bd30f06a58796d6899867` | 一致 |
| `security-scan-repair-20261001-continuation-1` | `.pipeline/security-scan-repair-20261001-continuation-1/security-scan-repair-20261001-continuation-1.md` | `a8a6c5c38c3fb83921b1961660273e0881559326f9cd11cc1dd0a393f4352fa4` | `a8a6c5c38c3fb83921b1961660273e0881559326f9cd11cc1dd0a393f4352fa4` | 一致 |
| `status-vocabulary-unification` | `.pipeline/status-vocabulary-unification/status-vocabulary-unification.md` | `97e0c80b755ee75084e1b41f2ea1a6698a8739f1f295ce65ee317304835899a2` | `97e0c80b755ee75084e1b41f2ea1a6698a8739f1f295ce65ee317304835899a2` | 一致 |
| `task-design-corruption-fix` | `.pipeline/task-design-corruption-fix/task-design-corruption-fix.md` | `b4c3c687eaea292279c96b4581d0200f34191a0232fe7e68ff50612afc29864a` | `b4c3c687eaea292279c96b4581d0200f34191a0232fe7e68ff50612afc29864a` | 一致 |
| `task-evidence-reconcile` | `.pipeline/task-evidence-reconcile/task-evidence-reconcile.md` | `78fe435782e3b714e50576ac7906aef06820bb16c0b0fa648f739d5491fcda5e` | `78fe435782e3b714e50576ac7906aef06820bb16c0b0fa648f739d5491fcda5e` | 一致 |
| `task-plan-contract-consistency` | `.pipeline/task-plan-contract-consistency/task-plan-contract-consistency.md` | `de26063c0814c955250397852571dab1342fb9f0546080f54f3ac7848f587708` | `de26063c0814c955250397852571dab1342fb9f0546080f54f3ac7848f587708` | 一致 |
| `task-ref-verifiability` | `.pipeline/task-ref-verifiability/task-ref-verifiability.md` | `b8d196da40a0c8a746f1ffd25c1b3c86ed647b793255e8cf9c7caf8c89574adb` | `b8d196da40a0c8a746f1ffd25c1b3c86ed647b793255e8cf9c7caf8c89574adb` | 一致 |
| `task-sheet-archival` | `.pipeline/task-sheet-archival/task-sheet-archival.md` | `5f3c92d875e6b03d8fd6a4f314b5c3e6f2e5d7f80786493f15b52370a0040d54` | `5f3c92d875e6b03d8fd6a4f314b5c3e6f2e5d7f80786493f15b52370a0040d54` | 一致 |
| `task-sheet-revision-and-evidence-binding` | `.pipeline/task-sheet-revision-and-evidence-binding/task-sheet-revision-and-evidence-binding.md` | `a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783` | `a12f29a7f7322feeb22d2a5284b4e2069d02d645fdc4bbf199ab9586f6082783` | 一致 |
| `task-worktree-dispatch-identity` | `.pipeline/task-worktree-dispatch-identity/task-worktree-dispatch-identity.md` | `1bf214c914c12026b434d916c98cafa6c0279d9346dffc8298c2f159d701b0cf` | `1bf214c914c12026b434d916c98cafa6c0279d9346dffc8298c2f159d701b0cf` | 一致 |
| `test-metrics-isolation` | `.pipeline/test-metrics-isolation/test-metrics-isolation.md` | `d0f1f14853e8fbd06548bfecb7df5d2fe3f8812d7d0cf33041cea49adf2f6495` | `d0f1f14853e8fbd06548bfecb7df5d2fe3f8812d7d0cf33041cea49adf2f6495` | 一致 |
| `test-ref-narrowing-followup` | `.pipeline/test-ref-narrowing-followup/test-ref-narrowing-followup.md` | `c62bf7a506765d8ca90984f04064732654f5463be8654143633f2474927e9d93` | `c62bf7a506765d8ca90984f04064732654f5463be8654143633f2474927e9d93` | 一致 |
| `toolchain-freshness-fixes` | `.pipeline/toolchain-freshness-fixes/toolchain-freshness-fixes.md` | `8bcc46f11556b926222ff46fabe79d26ee8bdeccd79a78f9b76da67f18555584` | `8bcc46f11556b926222ff46fabe79d26ee8bdeccd79a78f9b76da67f18555584` | 一致 |

## 3. 孤儿证据目录说明单（B）

- 新建 `.pipeline/repository-evidence-hygiene-continuation-5/repository-evidence-hygiene-continuation-5.md`（历史说明单，非完整 schema 4）。
- 文件名 = `<task-id>.md`，可被三位置解析器按文件名找到。
- 迁移后 `planning preflight` 的 `task_scenes.leftover_evidence` 已为空（见 `preflight.log`）。

## 4. 工作清单约定文档（C）

- 新建 `docs/tasks/README.md`：此处只放进行中或待派发的任务单；已终态的单子在其证据目录 `.pipeline/<task-id>/<task-id>.md`，没有证据目录时在 `.pipeline/archive/<task-id>.md`。
- `README.md`、`SKILL.md`、`references/merge-and-recovery.md` 以一致口径记录该约定（均新增指向 `docs/tasks/README.md` 与「进行中或待派发」的表述）。
- 一致性用例 `test_lifecycle_and_evidence_documentation_matches_current_contract` 已**扩展**：`docs/tasks/README.md` 缺失、或缺「只放/进行中或待派发/两个终态路径」任一表述、或三份文档口径不一致时失败。

## 5. 验收命令（全部经 `python -m pipeline_tools command run --cwd . --task-id historical-archival-migration`）

| 验收 | 命令 | 退出码 | 关键断言 |
| --- | --- | --- | --- |
| acceptance-test-1 | `python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked` | 0 | 夹具内迁移：sha256 逐张不变、仍被 `git ls-files` 跟踪、原路径消失、有目录进 `<id>/<id>.md`、无目录进 `archive/<id>.md` |
| acceptance-test-2 | `python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree` | 0 | 默认夹具中终态单不再计入 `sheets_without_worktree`；`leftover_evidence` 为空；**未**断言真实仓库该集合为空 |
| acceptance-test-3 | `python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover` | 0 | 补入 `<id>.md` 后该目录不再出现在 `leftover_evidence`，且 `task_sheet_resolution` 能找到它 |
| acceptance-test-4 | `python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract` | 0 | 文档一致性通过；`docs/tasks/README.md` 与三份文档口径一致断言已新增 |
| acceptance-test-5 | `python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration` | 0 | 3 个已最终化任务 `git mv` 迁入其证据目录后，`verify_finalization_snapshot` 不含 `finalization retained evidence hash mismatch` |

原始日志：`acceptance-1.log` … `acceptance-5.log`（本目录）。

验收命令退出码：1→0，2→0，3→0，4→0，5→0。

## 6. 全量回归

```
PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q
2 failed, 397 passed, 30 subtests passed in 363.16s
```

- 基线 395 passed；本任务新增 4 个用例 → 399；其中 2 个既有用例变红（见下），故 397 passed。
- 红的两个都在 `tests/test_cli.py`：`test_json_output_has_common_envelope_and_can_be_saved`、`test_task_validate_real_sheet`，原因是它们硬编码 `ROOT/'docs'/'tasks'/'pipeline-tools-v1.md'`，而该单已按契约迁到 `.pipeline/pipeline-tools-v1/pipeline-tools-v1.md`。
- 其余所有用例（含 `tests/test_acceptance_id_and_template_compliance.py` 全 28 项）全绿。

## 7. 决策点 / 阻塞

1. **`tests/test_cli.py` 不在 `allowed_paths`**：迁移必然使上述 2 个用例失败，修复需要改 `tests/test_cli.py`——本任务 `allowed_paths` 未列出该文件（`fail` 于禁止清单，改动会在 scope 闸门被判越界）。故未改，报 BLOCKED。建议：把 `tests/test_cli.py` 加入 `allowed_paths`（或允许在 2 处把 `docs/tasks/pipeline-tools-v1.md` 改为经 `task_sheet_resolution` 解析），随后修复即全绿。
2. **`docs/tasks/README.md` 被 `planning preflight` 当作任务单**：契约要求的 `docs/tasks/README.md` 会被 `_task_scene_facts` 的 `docs/tasks/*.md` 扫描命名成一个叫 `README` 的「进行中单子」。迁移后真实仓库 `task_scenes.sheets_without_worktree = ['README', 'historical-archival-migration', 'security-scan-repair-20261001']`（见 `preflight.log`）。要让 preflight 不产生这个假阳性需要改 `pipeline_tools/`（禁止），故未改。`leftover_evidence` 已为空（孤儿目录已修复）。
3. **一处单子文件名与契约 id 不符（已按机械判据处理并记录）**：迁移前的 `docs/tasks/repository-evidence-hygiene.md` 其契约内 `task_id` 实为 `repository-evidence-hygiene-continuation-5`；因此按文件名判它无证据目录 → 归档到 `.pipeline/archive/repository-evidence-hygiene.md`，而 `.pipeline/repository-evidence-hygiene-continuation-5/` 看起来「有目录无单」。这正是需要补历史说明单的原因；说明单已写明来历。此点与契约 assumption-2 一致（按目录存在性 + 文件名机械判定），未擅自改名或改动单子内容。

## 8. 未改动项（契约要求）

- 未编辑任何任务单**内容**：46 张只 `git mv`，逐张 sha256 不变。
- 未改动任何 `finalization.json` 或保留集文件。
- 未改 `pipeline_tools/**`、`docs/goal.md`。
- 未创建/删除/修改任何 `.worktrees/**`；未删除分支。

## 机器证据

```pipeline-evidence
{"schema": 2, "task_id": "historical-archival-migration", "worktree": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "branch": "historical-archival-migration", "role": "executor", "round": 1, "status": "BLOCKED", "head": "c063bbda9f2953be054466e7f524f45c10e133c2", "observed_at_commit": "c063bbda9f2953be054466e7f524f45c10e133c2", "sheet_revision": 1, "sheet_sha256": "d705b76388562fce76ed30cdfb806d0b505ebb9a453d7e17b413de8b71cbc2f5", "generated_at": "2026-10-09T00:00:00+00:00", "commands": [{"command": "git rev-parse HEAD", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git rev-parse --show-toplevel", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "git branch --show-current", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "sha256sum docs/tasks/*.md", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migrated_sheets_keep_their_bytes_and_are_tracked", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k migration_leaves_no_active_sheet_without_a_worktree", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_planning.py -k orphan_evidence_directory_is_no_longer_leftover", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_acceptance_id_and_template_compliance.py -k documentation_matches_current_contract", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pytest -q tests/test_evidence.py -k closed_task_markers_still_verify_after_the_migration", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "python -m pipeline_tools planning preflight .", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 0, "evidence_ref": "executor-report.md"}, {"command": "PIPELINE_TOOLS_DISABLE_AUTO_METRICS=1 python -m pytest -q", "cwd": "D:\\Projects\\Skills\\pipeline\\.worktrees\\historical-archival-migration", "exit_code": 1, "evidence_ref": "executor-report.md", "expected_exit_code": 1, "note": "2 failed (tests/test_cli.py hardcoded moved path), 397 passed"}], "assertions": ["46 terminal sheets were moved with git mv: 43 into .pipeline/<id>/<id>.md and 3 into .pipeline/archive/<id>.md; every sheet's sha256 is byte-identical before and after and every moved sheet is still tracked by git ls-files", "docs/tasks/ holds only the two in-flight sheets after the migration (historical-archival-migration, security-scan-repair-20261001)", "the orphan evidence directory .pipeline/repository-evidence-hygiene-continuation-5/ now resolves by filename and task_scenes.leftover_evidence is empty", "all five acceptance commands exit 0 and no finalization marker reports a retained evidence hash mismatch for the three migrated closed tasks", "the full suite is red only on two tests in tests/test_cli.py, which hardcode docs/tasks/pipeline-tools-v1.md and live outside this task's allowed_paths"], "evidence_refs": ["executor-report.md", "executor-result.json", "migration-map.json", "acceptance-1.log", "acceptance-2.log", "acceptance-3.log", "acceptance-4.log", "acceptance-5.log", "preflight.log"], "unverified": ["full regression is red: 2 failed, 397 passed, 30 subtests passed; both failures are tests/test_cli.py (test_json_output_has_common_envelope_and_can_be_saved, test_task_validate_real_sheet) which hardcode ROOT/'docs'/'tasks'/'pipeline-tools-v1.md', a path the contract requires migrating to .pipeline/pipeline-tools-v1/pipeline-tools-v1.md; tests/test_cli.py is not in this task's allowed_paths so it was left untouched and this is reported as a decision point", "docs/tasks/README.md is required by the contract but planning preflight scans docs/tasks/*.md as task sheets, so the real repository now reports sheets_without_worktree = ['README', 'historical-archival-migration', 'security-scan-repair-20261001']; suppressing the README false positive needs a pipeline_tools change, which is forbidden, so it is reported rather than fixed", "docs/tasks/repository-evidence-hygiene.md carried the contract of task repository-evidence-hygiene-continuation-5 inside it; the mechanical filename rule put it in .pipeline/archive/repository-evidence-hygiene.md and the historical note was added under the continuation-5 id, matching assumption-2 rather than renaming or editing the sheet"]}
```
