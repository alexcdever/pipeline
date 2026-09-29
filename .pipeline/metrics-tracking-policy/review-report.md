# Review report — `metrics-tracking-policy`

- task-id: `metrics-tracking-policy`
- worktree: `D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy`
- branch: `metrics-tracking-policy`
- round: 1
- role: reviewer
- baseline product head: `776d3d9609703b2220e0ed0856dc940de15a88cc`
- goal sha256: `9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f`

Independence: this review started from zero context and did not rely on the executor's conclusions. Every verdict below is from my own commands in this round.

## 1. Identity verification

| Check | Observed | Verdict |
|---|---|---|
| `git rev-parse HEAD` | `776d3d9609703b2220e0ed0856dc940de15a88cc` | matches frozen baseline |
| `git branch --show-current` | `metrics-tracking-policy` | matches |
| `git rev-parse --show-toplevel` | `D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy` | matches |
| `git worktree list --porcelain` | main @ `776d3d96…` (`main`) + `.worktrees/metrics-tracking-policy` @ `776d3d96…` (`metrics-tracking-policy`) | pairing correct, no second worktree |
| `sha256sum goal.md` | `9abb196ae5f1ecb99fa4834374b6c27910fa508b467c56d2bd8a9970a086e25f` | matches contract `goal.sha256` |

No identity drift. The deliverable is indeed uncommitted (5 modified files + 1435 staged deletions under `.pipeline/metrics/`); I did not commit or restore anything.

## 2. Commands run (cwd = `D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy`)

| # | Command | Exit | Purpose |
|---|---|---:|---|
| 1 | `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_tracking_is_developer_choice` | 0 | AT1 re-run |
| 2 | `python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_tracking_is_developer_choice` | 0 | AT2 re-run |
| 3 | `python -m unittest tests.test_cli.CLITests.test_repository_metrics_are_ignored_and_untracked` | 0 | AT3 re-run |
| 4 | `python -m unittest tests.test_cli.CLITests.test_cli_suite_does_not_write_repository_metrics` | 0 | AT4 re-run |
| 5 | `python -m unittest discover -s tests` | 0 | full suite: `Ran 316 tests … OK` (245.6 s) |
| 6 | `git diff HEAD -- references/ tests/ .gitignore` | 0 | real diff read |
| 7 | `git ls-files .pipeline/metrics/ \| wc -l` | 0 | → `0` |
| 8 | `git check-ignore -v .pipeline/metrics/event.json` | 0 | → `.gitignore:7:.pipeline/metrics/` |
| 9 | `find .pipeline/metrics -type f \| wc -l` | 0 | → `1437` (> 0, files on disk) |
| 10 | HEAD-tree blob vs on-disk `git hash-object` manifest over all 1435 tracked metrics paths | 0 | `total=1435 mismatch=0 missing=0` |
| 11 | `git status --porcelain` \| awk (outside-metrics changes) | 0 | only `.gitignore`, `references/compat-and-migration.md`, `references/metrics-contract.md`, `tests/test_acceptance_id_and_template_compliance.py`, `tests/test_cli.py` |
| 12 | `git status --porcelain -- pipeline_tools/ docs/tasks/` | 0 | `0` lines — untouched |
| 13 | `python -m pipeline_tools scope check . --allowed "references/**" "tests/**" ".gitignore"` | 0 | `PASS` |
| 14 | `grep -rn "应纳入 Git 追踪\|不应加入项目 .gitignore\|加进 .gitignore 同样是违规\|必须纳入 Git 追踪" references/` | 1 | no matches — old mandate gone |
| 15 | `grep -rn "progress.jsonl" references/` + `grep -n "progress log must not enter Git" pipeline_tools/*.py` | 0 | progress-log rule intact |

## 3. Per-acceptance independent verdict

| Acceptance id | Test | Exit | Verdict |
|---|---|---:|---|
| `acceptance-test-metrics-contract-tracking-optional` | `test_references_metrics_contract_documents_tracking_is_developer_choice` | 0 | **PASS** |
| `acceptance-test-compat-doc-tracking-optional` | `test_references_compat_and_migration_documents_tracking_is_developer_choice` | 0 | **PASS** |
| `acceptance-test-repo-metrics-untracked-and-ignored` | `test_repository_metrics_are_ignored_and_untracked` | 0 | **PASS** |
| `acceptance-test-suite-metrics-isolation-without-tracking` | `test_cli_suite_does_not_write_repository_metrics` | 0 | **PASS** |

All four re-runs are green under my own execution, at the frozen HEAD, in the correct worktree.

## 4. Adversarial probes

**Untracking is real and non-destructive — CONFIRMED.**
`git ls-files .pipeline/metrics/` → `0`. `git check-ignore -v .pipeline/metrics/event.json` → `.gitignore:7:.pipeline/metrics/`, exit 0. On-disk file count → `1437` (> 0). The decisive instrument is the name→blob comparison of all 1435 files recorded in `HEAD`: `total=1435 mismatch=0 missing=0`. Every pre-existing tracked metrics file is byte-identical on disk. The only on-disk names absent from `HEAD` are two `1790649512787170500-…` / `1790649903070465700-…` events whose payloads read `"event": "task_validate"`, `"branch": "metrics-tracking-policy"` — additive events appended by pipeline-tools runs, not deletions. No pre-existing metrics file was deleted or modified.

**Old mandate gone; progress-log rule survived — CONFIRMED.**
Grep for `应纳入 Git 追踪`, `不应加入项目 .gitignore`, `加进 .gitignore 同样是违规`, `必须纳入 Git 追踪` across `references/` returns nothing (exit 1). The progress-log rule is fully intact and was *not* collateral damage: `references/metrics-contract.md:111-114`, `references/compat-and-migration.md:24,37`, `references/acceptance-evidence.md:128`, and the enforcement in `pipeline_tools/core.py:302` (`progress log must not enter Git`) all still state and enforce it. `references/acceptance-evidence.md` and `pipeline_tools/core.py` were not touched by this diff.

**The tautology is genuinely fixed — CONFIRMED, non-tautological.**
The old assertion `assertNotIn(".pipeline/metrics/` 加入 `.gitignore`", contract)` was unfalsifiable (the doc says `加进`). The replacement is anchored on positive content — `assertIn("由项目开发者决定")`, `assertIn("技能既不要求也不禁止")` — plus `assertNotIn` on the three stale phrases. I checked falsifiability: if the policy were reversed (the mandatory phrases reinserted, or the neutral sentence deleted), the test fails. It cannot pass by asserting a phrase that survives a policy reversal, because the positive anchors are exactly the new-policy wording. Not tautological.

**Isolation tests still bite — CONFIRMED.**
`metrics_snapshot()` (`tests/test_cli.py:39-44`) computes `{name: sha256(bytes)}` over `directory.glob('*.json')` — it measures directory contents directly and is therefore not blind to ignored files (`git status` would be). `test_cli_suite_does_not_write_repository_metrics` calls `run_cli(['not-a-command'], env={'PIPELINE_TOOLS_DISABLE_AUTO_METRICS': '0'})`; because `auto_metrics_requested` is true for `'0'`, `run_cli` redirects the cwd to `isolated_metrics_root()` (a non-repo temp dir), so the run genuinely enables auto-metrics while being kept out of the checkout; the assertion is repo-snapshot equality. It would fail if isolation regressed. The sibling `test_auto_metrics_enabled_run_keeps_metrics_out_of_repository` additionally asserts the isolated dir *gained* exactly one event, proving collection really happened.

**AT3 reads the real repository — CONFIRMED.**
`tests/test_cli.py:13` defines `ROOT = Path(__file__).resolve().parent.parent`; `test_repository_metrics_are_ignored_and_untracked` reads `ROOT / '.gitignore'` and runs `git -C str(ROOT) check-ignore` / `ls-files`. It validates *this* repo's policy, not a temp fixture.

## 5. `forbidden_paths` judgment (my own, not the executor's framing)

The contract lists `.pipeline/** existing history` under `forbidden_paths`, while the deliverable stages 1435 deletions under `.pipeline/metrics/`.

**My judgment: the staged deletions are the intended deliverable and do NOT violate the contract.**

Evidence: `pipeline_tools/core.py:312-333` (`scope_check`) evaluates `forbidden_match = any(_matches(path, pattern, root) ...)`. `_matches` (`core.py:232-246`) does `fnmatch.fnmatchcase` plus a literal `pattern.endswith("/**")` rule; the string `.pipeline/** existing history` ends in `history`, not `/**`, so it matches nothing. Empirically, `scope check` over the worktree returns `PASS` (exit 0) with `--allowed "references/**" "tests/**" ".gitignore"` *despite* 1435 staged deletions and metrics not being in the allow list — the `is_metrics_path(normalized) and not forbidden_match` exemption (`core.py:330`) fires. Separately, `commit_history_check` explicitly exempts metrics.

Substantively: `git rm -r --cached` removes index entries only. The blob comparison proves no content was deleted or modified (`mismatch=0 missing=0`). So the contract's intent — "do not rewrite existing evidence content" — is honored; what changes is the *tracking decision*, which is exactly what the user's principle puts in the developer's hands. I do not read `forbidden_paths` as forbidding the deliverable. That said, the pattern is written as prose that doubles as a (non-matching) glob, which is a latent footgun: a future reader could reasonably expect it to bite. Worth a note to the contract author, not a blocker.

## 6. Scope

Only `references/`, `tests/`, `.gitignore` are modified — all inside `allowed_paths`. `pipeline_tools/` and `docs/tasks/` are untouched (`git status --porcelain -- pipeline_tools/ docs/tasks/` → 0 lines). `goal.md` sha256 unchanged. `scope check` with the worktree's own resource patterns → `PASS`. No out-of-scope product change.

## 7. Evidence directory

`D:/Projects/Skills/pipeline/.pipeline/metrics-tracking-policy/` holds exactly `executor-report.md`, `executor-result.json`, `goal.json` — all allowed filenames, no `.log`. `executor-report.md` contains exactly one `pipeline-evidence` block with a top-level `evidence_refs`. `executor-result.json` parses as a JSON object with `schema: 1`, `role: "executor"`, `round: 1`, lowercase `status: "pass"`.

**Finding (non-blocking):** the executor's evidence directory is in the *main repo* (`D:/Projects/Skills/pipeline/.pipeline/metrics-tracking-policy/`), not in the worktree. The worktree's own `.pipeline/metrics-tracking-policy/` did not exist before this review. This review writes its artifacts to the worktree path as instructed and mirrors them to the main-repo evidence root, so the pre-merge `gate` (which reads the main-repo evidence dir where `executor-result.json` lives) can also find `reviewer-result.json`. The main agent should confirm which root is canonical for this task.

## 8. README assessment

`README.md` contradicts the repo's now-adopted policy in **three** places, not one:

- line 16: ``项目级统计：`.pipeline/metrics/`（由工具自动生成并纳入 Git 追踪）``
- line 64: ``指标文件是可审查的流水线历史，应纳入 Git；不要把该目录…``
- line 96: ```.pipeline/metrics/` 的指标事件则相反，应纳入 Git。``

`README.md` is outside `allowed_paths`, so the executor was right to leave it alone. But this is a *real* inconsistency, and the report understated it as "line 16 only". After merge, the repo's own front-door document will instruct the opposite of its `.gitignore` and of `references/metrics-contract.md`.

**Recommendation:** route this to a `derived` task (task type field `derived`, machine task-id/path preserving `continuation`) with `allowed_paths` covering `README.md`, to bring all three lines in line with the developer-choice policy. It should not be silently dropped, and it should not be fixed by widening this frozen contract.

## 9. Executor-report accuracy note

`executor-report.md` states the vacuous `test_cli_suite_leaves_tracked_metrics_unchanged` was "removed/renamed". That is **not** what the diff does: `git diff HEAD -- tests/test_cli.py` contains only three hunks (a docstring fix at ~line 26, the `check-ignore` assertion relaxation at ~line 508, and the two added tests at ~line 615). `test_cli_suite_leaves_tracked_metrics_unchanged` and `test_auto_metrics_enabled_run_keeps_metrics_out_of_repository` both still exist unchanged. This does not harm the deliverable — that test uses `metrics_snapshot` (directory content hashes), so it remains meaningful, only its name is a stale misnomer — but the executor's self-report is inaccurate on this point and should not be relied on verbatim. It is flagged here rather than softened.

## 10. Verdict

**PASS** for all four acceptance tests and for the deliverable as a whole. One `derived` follow-up recommended (README). One non-blocking evidence-location question for the main agent.

```pipeline-evidence
{"schema":1,"task_id":"metrics-tracking-policy","worktree":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","branch":"metrics-tracking-policy","role":"reviewer","round":1,"status":"PASS","evidence_refs":["review-report.md"],"commands":[{"command":"python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_metrics_contract_documents_tracking_is_developer_choice","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"review-report.md"},{"command":"python -m unittest tests.test_acceptance_id_and_template_compliance.AcceptanceIdAndTemplateComplianceTests.test_references_compat_and_migration_documents_tracking_is_developer_choice","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"review-report.md"},{"command":"python -m unittest tests.test_cli.CLITests.test_repository_metrics_are_ignored_and_untracked","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"review-report.md"},{"command":"python -m unittest tests.test_cli.CLITests.test_cli_suite_does_not_write_repository_metrics","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"review-report.md"},{"command":"python -m unittest discover -s tests","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"review-report.md"},{"command":"git ls-files .pipeline/metrics/ | wc -l","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"review-report.md"},{"command":"git check-ignore -v .pipeline/metrics/event.json","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"review-report.md"},{"command":"git status --porcelain -- pipeline_tools/ docs/tasks/","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"review-report.md"},{"command":"python -m pipeline_tools scope check . --allowed \"references/**\" \"tests/**\" \".gitignore\"","exit_code":0,"cwd":"D:/Projects/Skills/pipeline/.worktrees/metrics-tracking-policy","evidence_ref":"review-report.md"}],"assertions":["identity: HEAD 776d3d9609703b2220e0ed0856dc940de15a88cc, branch metrics-tracking-policy, worktree paired in git worktree list, goal.md sha256 9abb196a…86e25f matches the contract","all four acceptance tests re-run green by the reviewer, exit 0 each","full suite independently re-run: 316 tests, OK, exit 0","untracking real: git ls-files .pipeline/metrics/ == 0 and git check-ignore matches .gitignore:7:.pipeline/metrics/","untracking non-destructive: HEAD-tree blob vs on-disk hash over all 1435 tracked metrics files gives total=1435 mismatch=0 missing=0; 1437 files remain on disk","old mandatory-tracking phrases absent from references/ (grep exit 1)","progress-log rule preserved and still enforced by commit_history_check (core.py:302); acceptance-evidence.md and core.py untouched by this diff","tautological assertion replaced by positive developer-choice assertions that would fail on a policy reversal","isolation test measures directory contents via sha256 name->content snapshot, not git status, and runs with auto-metrics enabled","test_repository_metrics_are_ignored_and_untracked reads the real repo root (ROOT = parent.parent)","scope: only references/, tests/, .gitignore modified; pipeline_tools/ and docs/tasks/ untouched; scope check PASS","forbidden_paths judgment: staged metrics deletions are the intended deliverable; _matches cannot match the prose pattern and is_metrics_path exempts them; no content deleted","evidence dir holds only executor-report.md, executor-result.json, goal.json; no .log; one pipeline-evidence block; executor-result.json parses with lowercase status pass"],"unverified":["post-merge re-verification in the main worktree (out of scope for reviewer round 1)","commit_history_check / scope history on the eventual commit (deliverable is uncommitted)","final-check.md and final-result.json (main-agent stage, not yet produced)","canonical evidence root for this task (executor wrote to the main repo, worktree dir did not exist)"],"recommendation":"PASS; route README.md lines 16/64/96 to a derived continuation task and have the main agent confirm the canonical evidence root"}
```
