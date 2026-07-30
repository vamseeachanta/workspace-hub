# Plan for #3708: Safe Crontab Re-Apply Path

> **Status:** adversarial-reviewed
> **Complexity:** T3
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3708
> **Blocks:** https://github.com/vamseeachanta/workspace-hub/issues/3707
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-07-30-plan-3708-codex-r1.md

---

## Resource Intelligence Summary

Execution mode for this issue will be `single-lane` implementation after approval because the code will touch the shared cron transaction path. Planning evidence gathering will be read-only. Live scheduler mutation will remain forbidden until an approved implementation will satisfy the scheduler mutation safety rule.

### Existing Repo Code

- `scripts/cron/setup-cron.sh` will be the operator entrypoint. It will currently reject `--replace`, bind `--machine` to the physical host, skip Windows by registry `os`, and delegate to `scripts/cron/cron_apply.py`.
- `scripts/cron/cron_apply.py` will already contain the core Linux transaction shape: lock, baseline read, dry-run plan, durable backup, pre-write compare-and-swap, exact post-write verification, and compare-and-swap rollback.
- `scripts/cron/cron_render.py` will already add a `mkdir -p ... &&` prefix from the task `log:` field before command expansion. The future fix will keep that responsibility in the renderer.
- `scripts/cron/cron_identity.py` and `scripts/cron/cron_line_model.py` will currently use exact rendered lines plus declared legacy exact lines for destructive ownership; fingerprint rows will preserve external lines but will not grant deletion authority.
- `config/workstations/harness-state-classes.yaml` will already preserve the llm-wiki corpus ingest and will already contain ace1 legacy exact rows for `session-curation`, `equality-matrix-refresh`, and `notification-purge`.
- `tests/cron/test_a1_preserved.py`, `tests/cron/test_cron_audit.py`, `tests/cron/test_cron_apply.py`, and `tests/cron/test_cron_transaction.py` will already cover pieces of legacy exact ownership, notification-purge dedupe, and rollback, but they will not yet cover the 44-line `$WORKSPACE_HUB` mkdir-prefix normalization class.

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue planning workflow | active | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Scheduler mutation safety | active | `.claude/rules/scheduler-mutation-safety.md` |
| Mutation surface registry | active | `config/scheduled-tasks/mutation-surfaces.yaml` |
| Parallel-first execution | active | `docs/standards/PARALLEL_FIRST_EXECUTION.md` |

### LLM Wiki Pages Consulted

- No relevant wiki page will apply; this will be workspace-hub harness and scheduler infrastructure work.

### Documents Consulted

- GitHub issue `#3708` will define the crontab re-apply blocker, the 47 uncataloged ace1 lines, and the requirement that unknown lines stay fail-closed.
- GitHub issue `#3707` will define the success criterion: `daily-cleanup` will not become clockwork until #3708 will let the system crontab be regenerated safely.
- `docs/plans/2026-07-30-issue-3707-cron-upkeep-clockwork.md` on branch `plan/3707-cron-upkeep-clockwork` will state that #3707 will consume the #3708 apply path and will not bypass it.
- `/private/tmp/claude-501/-Users-krishna-Developer-ws/37e3e642-de6b-4825-b67e-872f62f6b3b9/scratchpad/ace1-cron.txt` will provide the ace-linux-1 live crontab snapshot and `cron-audit.py --json` output. No SSH or live crontab command will be used for this plan.
- `.claude/rules/scheduler-mutation-safety.md` will require baseline snapshot, durable backup, pre-write compare-and-swap, exact post-write verification, compare-and-swap rollback under the declared lock, and explicit execution-host binding.
- `config/scheduled-tasks/mutation-surfaces.yaml` will already register `cron_apply.py` as the direct crontab owner and `setup-cron.sh` as a transitive entrypoint; Windows Task Scheduler writers will remain separate non-compliant surfaces and must not be pulled into the Linux cron fix.
- Drive-index query `cron crontab reapply scheduler mutation` will return no relevant results and will report the configured drive indexes as unreachable or stale, so tracked repo evidence will remain authoritative.

### Gaps Identified

- No ownership identity will normalize the ace1 legacy `$WORKSPACE_HUB` mkdir-prefix form against the current rendered absolute mkdir-prefix form.
- No generic command-only ownership matcher will promote cataloged command-only tasks such as `notification-purge` without a one-off exact legacy line.
- No test will prove that a semantically equivalent drifted line will become cataloged while a genuinely unknown line will still block cutover.
- No test will prove the exact mid-write rollback behavior for the intended #3708 cutover scenario rather than only smaller transaction seams.
- No per-box reconciliation workflow will explicitly resolve ace1 and ace2 before #3707 will consume the apply path.

### Evidence

**Issue statuses**:
- `#3708` will be OPEN with `status:needs-plan` before this plan will be pushed and moved to `status:plan-review`.
- `#3707` will be OPEN with `status:plan-review` and will remain blocked on #3708 for live system-cron deployment.

**File existence**:
- `scripts/cron/setup-cron.sh`
- `scripts/cron/cron_apply.py`
- `scripts/cron/cron_transaction.py`
- `scripts/cron/cron_render.py`
- `scripts/cron/cron_identity.py`
- `scripts/cron/cron_line_model.py`
- `config/scheduled-tasks/schedule-tasks.yaml`
- `config/scheduled-tasks/mutation-surfaces.yaml`
- `config/workstations/harness-state-classes.yaml`
- `.claude/rules/scheduler-mutation-safety.md`
- `docs/plans/_template-issue-plan.md`
- `docs/plans/2026-07-30-issue-3707-cron-upkeep-clockwork.md` on branch `plan/3707-cron-upkeep-clockwork`
- captured ace1 evidence file under `/private/tmp/.../ace1-cron.txt`

**Reproduction proofs**:

Runtime reproduction will be read-only and will use the captured ace1 JSON, not live `crontab`, `setup-cron.sh`, or SSH. A local parser over the captured file will classify the 47 uncataloged JSON rows as:

| Group | Count | Why the live line will fail exact ownership today | Required disposition |
|---|---:|---|---|
| A. `$WORKSPACE_HUB` mkdir-prefix versus rendered absolute mkdir-prefix | 44 | The task script, schedule, command body, cd path, and redirect will match the current catalog after only `mkdir -p $WORKSPACE_HUB/<logdir>` will normalize to `mkdir -p /mnt/local-analysis/workspace-hub/<logdir>`. | Normalize the installed line during identity comparison, and keep the renderer-owned mkdir prefix. No YAML behavior change will be required for these 44. |
| B. Catalog task command-content drift | 2 | The live line will reference a catalog task script but the command body will differ from current YAML beyond the mkdir prefix. | Per-task reconciliation will be required before cutover. `hermes-claude-bridge` will need old no-`--commit` live form reconciled to current YAML; `repository-sync` will need the current runtime/log contract reconciled against the installed redirect. These will not be silently normalized. |
| C. Obsolete equality-report implementation | 1 | The live line will run `collect-equality.sh && build-equality-matrix.py`; current `equality-report` will run `equality-matrix-cron.sh`, and the script token will not match a current catalog task. | Genuinely unresolved until per-box evidence will decide whether to promote a legacy exact catalog-owned variant, update YAML, or keep blocking. Installed crontab will be treated as truth for cadence during reconciliation. |
| D. Preserved external | 0 of the 47, plus 1 non-uncataloged line | The llm-wiki corpus ingest will already classify as `preserved_external`. | Keep verbatim; workspace-hub cutover will never reap it. |
| E. Command-only duplicate, currently non-uncataloged through an exact legacy row | 0 of the 47, plus 2 installed copies | `notification-purge` will have no script basename and will be installed twice. Current code will rely on an ace1 exact legacy row; the future matcher will need a catalog command-only identity. | Add generic command-only matching for selected catalog tasks and dedupe to one rendered catalog line. |

The 47-line classification detail will be:

| # | Catalog task / status | Live key | Group | Future action |
|---:|---|---|---|---|
| 1 | `agent-memory-backup` | `scripts/cron/memory-backup.sh` | A | Normalize installed line. |
| 2 | `agent-radar` | `scripts/ai/generate-agent-radar.py` | A | Normalize installed line. |
| 3 | `ai-credit-utilization-weekly` | `scripts/ai/credit-utilization-tracker.py` | A | Normalize installed line. |
| 4 | `ai-tools-status` | `scripts/maintenance/ai-tools-status.sh` | A | Normalize installed line. |
| 5 | `architecture-scan` | `scripts/cron/architecture-scan-weekly.sh` | A | Normalize installed line. |
| 6 | `benchmark-regression` | `scripts/testing/run-benchmarks.sh` | A | Normalize installed line. |
| 7 | `claude-plugin-audit` | `scripts/maintenance/claude-plugin-audit.sh` | A | Normalize installed line. |
| 8 | `compliance-daily` | `scripts/enforcement/compliance-cron.sh` | A | Normalize installed line. |
| 9 | `compliance-weekly-report` | `scripts/enforcement/compliance-weekly-report.sh` | A | Normalize installed line. |
| 10 | `comprehensive-learning` | `scripts/cron/comprehensive-learning-nightly.sh` | A | Normalize installed line. |
| 11 | `consistency-weekly-check` | `scripts/cron/consistency-weekly-check.sh` | A | Normalize installed line. |
| 12 | `cron-health` | `scripts/monitoring/cron-health-check.sh` | A | Normalize installed line. |
| 13 | `daily-today` | `scripts/productivity/daily_today.sh` | A | Normalize installed line. |
| 14 | `dep-health` | `scripts/quality/dep-health.sh` | A | Normalize installed line. |
| 15 | `dispatch-leader-watch` | `scripts/cron/dispatch-leader-watch.sh` | A | Normalize installed line; ensure Linux task, not Windows sibling, owns it. |
| 16 | `doc-drift` | `scripts/quality/check_doc_drift.py` | A | Normalize installed line. |
| 17 | unresolved `equality-report` legacy body | `scripts/readiness/collect-equality.sh` | C | Stay blocked until per-box reconciliation will classify this exact line. |
| 18 | `equivalence-sentinel` | `scripts/monitoring/equivalence-sentinel.sh` | A | Normalize installed line. |
| 19 | `flywheel-review` | `scripts/cron/flywheel-review.py` | A | Normalize installed line. |
| 20 | `gemini-nightly-batch` | `scripts/cron/gemini-nightly-batch.sh` | A | Normalize installed line. |
| 21 | `git-lock-reaper` | `scripts/maintenance/git-lock-reaper.sh` | A | Normalize installed line. |
| 22 | `gsd-researcher` | `scripts/cron/gsd-researcher-nightly.sh` | A | Normalize installed line. |
| 23 | `gtm-job-market-scan` | `scripts/gtm/weekly-scan-refresh.sh` | A | Normalize installed line. |
| 24 | `harness-install-doctor` | `scripts/maintenance/harness-install-doctor.sh` | A | Normalize installed line. |
| 25 | `harness-lean-out` | `scripts/cron/harness-lean-out.sh` | A | Normalize installed line. |
| 26 | `harness-update` | `scripts/maintenance/update-harness-tools.sh` | A | Normalize installed line. |
| 27 | `hermes-claude-bridge` | `scripts/memory/bridge-hermes-claude.sh` | B | Reconcile old no-`--commit` line against current YAML; do not normalize as equivalent. |
| 28 | `memory-health-check` | `scripts/memory/eval-memory-quality.py` | A | Normalize installed line. |
| 29 | `model-ids` | `scripts/cron/update-model-ids.sh` | A | Normalize installed line. |
| 30 | `parity-sentinel` | `scripts/ai/parity-sentinel.sh` | A | Normalize installed line. |
| 31 | `provider-dream-bridge` | `scripts/memory/bridge-providers-to-dream.sh` | A | Normalize installed line; ensure Linux task, not Windows sibling, owns it. |
| 32 | `provider-session-ecosystem-audit` | `scripts/cron/provider-session-ecosystem-audit.sh` | A | Normalize installed line. |
| 33 | `provider-utilization-refresh` | `scripts/cron/provider-utilization-refresh.sh` | A | Normalize installed line. |
| 34 | `queue-refresh-weekly` | `scripts/cron/queue-refresh-weekly.sh` | A | Normalize installed line. |
| 35 | `repo-ecosystem-hygiene` | `scripts/cron/repo-ecosystem-hygiene-audit.sh` | A | Normalize installed line. |
| 36 | `repository-sync` | `scripts/cron-repository-sync.sh` | B | Reconcile live redirect to `logs/quality/cron-wrapper.log` against current runtime/log YAML; do not normalize as equivalent. |
| 37 | `research-staleness` | `scripts/cron/research-staleness-check.sh` | A | Normalize installed line. |
| 38 | `return-to-main-guard` | `scripts/maintenance/return-to-main-guard.sh` | A | Normalize installed line. |
| 39 | `review-audit` | `scripts/maintenance/review-audit.sh` | A | Normalize installed line. |
| 40 | `skills-curation` | `scripts/cron/skills-curation.sh` | A | Normalize installed line. |
| 41 | `solver-dashboard` | `scripts/cron/solver-dashboard-daily.sh` | A | Normalize installed line. |
| 42 | `solver-watch-results` | `scripts/solver/watch-results.sh` | A | Normalize installed line. |
| 43 | `staleness-scan` | `scripts/cron/staleness-scan-weekly.sh` | A | Normalize installed line. |
| 44 | `tier1-indexing-freshness` | `scripts/cron/tier1-indexing-freshness.sh` | A | Normalize installed line. |
| 45 | `weekly-governance-check` | `scripts/knowledge/weekly-governance-check.sh` | A | Normalize installed line. |
| 46 | `weekly-hermes-parity-review` | `scripts/cron/weekly-hermes-parity-review.sh` | A | Normalize installed line. |
| 47 | `wiki-ingest-nightly` | `scripts/knowledge/wiki-ingest-cron.sh` | A | Normalize installed line. |

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-30-issue-3708-crontab-reapply-path.md` |
| Plan review | `scripts/review/results/2026-07-30-plan-3708-codex-r1.md` |
| Linux cron transaction tests | `tests/cron/test_cron_transaction.py`, `tests/cron/test_cron_apply.py`, `tests/cron/test_cron_audit.py`, `tests/cron/test_a1_preserved.py` |
| Renderer tests | `tests/cron/test_cron_render.py` |
| Windows scheduler guard tests | `tests/readiness/test_windows_scheduler_single_source.py`, `tests/cron/tests/test_validate_schedule.py` |
| Implementation surfaces | `scripts/cron/cron_render.py`, `scripts/cron/cron_identity.py`, `scripts/cron/cron_line_model.py`, `scripts/cron/cron_transaction.py`, `scripts/cron/cron_apply.py`, `scripts/cron/setup-cron.sh`, `config/workstations/harness-state-classes.yaml`, `config/scheduled-tasks/schedule-tasks.yaml` |
| Mutation registry evidence | `config/scheduled-tasks/mutation-surfaces.yaml`, generated `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |

## Deliverable

A fail-closed crontab re-apply path will classify semantically equivalent drifted catalog lines, preserve genuinely external lines, block genuinely unknown lines, dedupe catalog-owned duplicates, and let #3707 safely add `daily-cleanup` to system cron after user approval.

## Pseudocode

```
function canonicalize_log_dir_prefix(line, workspace_hub):
    parse the cron schedule prefix and command body without executing shell
    replace only a leading renderer-owned "mkdir -p $WORKSPACE_HUB/<logs-dir> &&" prefix
        with the equivalent absolute workspace path form
    require the normalized log dir to equal the selected task's declared log parent
    leave all other command text byte-for-byte unchanged
    return normalized line plus an audit reason
```

```
function build_line_identities(catalog, registry, state_classes, machine):
    render selected tasks for the physical machine
    bind canonical exact rendered lines
    bind selected legacy exact catalog-owned lines
    bind catalog-owned normalized variants only when the canonicalized live line equals a rendered selected task
    bind selected command-only identities only when command tokens are unambiguous and cwd is workspace-hub
    preserve external fingerprints separately without granting deletion authority
    reject collisions or ambiguous command-only matches
```

```
function classify_line_detail(line, ownership_context):
    ignore comments, blank lines, and env assignments
    if exact line identity exists: return cataloged
    if normalized line identity exists: return cataloged with reason normalized-catalog-line
    if command-only identity exists and selected task id matches: return cataloged
    if preservation fingerprint matches: return preserved_external
    return uncataloged
```

```
function plan_safe_cutover(current_text, selected_tasks, ownership_context):
    parse current crontab and reject unbalanced managed markers
    classify every unmanaged and managed-block line
    abort if any line is uncataloged
    rebuild one managed block from selected rendered tasks
    drop cataloged duplicates outside the new block
    keep preserved_external lines verbatim
    return planned exact text plus classification report
```

```
function apply_safe_cutover(machine_id, host_binding):
    require host_binding == physical-local unless explicit-remote-transport is declared
    acquire the declared crontab lock
    read baseline A and build a durable snapshot record
    write durable backup of A before any crontab write
    re-read current B under lock and abort unless B == A
    write planned crontab C
    re-read observed D and require D == C exactly
    on mismatch or partial write, rollback only if current still equals D under the same lock
    verify rollback restored A exactly
```

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `tests/cron/test_cron_transaction.py` | Add RED tests for normalized `$WORKSPACE_HUB` mkdir-prefix equivalence, genuinely unknown blocking, command-only matching, and collision rejection. |
| Modify | `tests/cron/test_cron_audit.py` | Add captured ace1-style audit fixtures that will classify the 44 prefix-only lines as cataloged while leaving B/C unresolved until explicit fixtures will be added. |
| Modify | `tests/cron/test_cron_apply.py` | Add rollback-on-mid-write and CAS rollback tests with the exact #3708 transaction states. |
| Modify | `tests/cron/test_a1_preserved.py` | Expand ace1 fixture coverage so notification-purge duplicate dedupe will not depend only on one exact legacy line. |
| Modify | `tests/cron/test_cron_render.py` | Lock renderer behavior for log-dir prefix ownership and placeholder expansion. |
| Modify | `scripts/cron/cron_render.py` | Keep renderer-owned log-dir prefixing; make its exact representation stable or expose canonicalization metadata for ownership comparison. |
| Modify | `scripts/cron/cron_identity.py` | Bind normalized catalog-equivalent line identities and command-only catalog identities without granting substring deletion authority. |
| Modify | `scripts/cron/cron_line_model.py` | Return explicit reasons for normalized catalog matches, command-only matches, preserved external matches, and no-match blocks. |
| Modify | `scripts/cron/cron_transaction.py` | Preserve fail-closed cutover planning while deduping catalog-owned duplicate lines into one rendered block. |
| Modify | `scripts/cron/cron_apply.py` | Tighten transaction reporting and tests around durable snapshot/backup/CAS/exact verify/rollback requirements if any gap will remain. |
| Modify | `scripts/cron/setup-cron.sh` | Replace the hard `--replace` dead-end only after the audited transaction will satisfy the rule; keep physical-host binding and Windows skip behavior. |
| Modify | `config/workstations/harness-state-classes.yaml` | Add only reviewed legacy exact rows for B/C lines that per-box evidence will prove catalog-owned; never add broad fingerprints as deletion authority. |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Reconcile `hermes-claude-bridge`, `repository-sync`, `equality-report`, and `daily-cleanup` only after per-box truth will be verified; do not use YAML as sole truth. |
| Modify | `config/scheduled-tasks/mutation-surfaces.yaml` | Update source attestations only if implementation changes the transitive setup-cron modes or direct transaction guarantees. |
| Update | `docs/plans/README.md` | Index this plan. |

## Mkdir-Prefix Decision

The `mkdir -p ... &&` log-directory prefix will belong in the renderer, not in each YAML command and not as unmanaged installed-line residue. The renderer can derive the directory from the structured `log:` field, apply it consistently to every cron task, and keep YAML commands focused on the task action. Dropping the prefix from installed lines would make redirects fail when a log parent directory is missing, which will turn a working job into a silent no-log job that cron-health may report as missing. Putting the prefix in YAML would duplicate boilerplate across dozens of tasks and would make command drift easier.

The future implementation will either make the renderer emit one stable canonical prefix form or make the identity layer treat `$WORKSPACE_HUB` and the resolved workspace path as equivalent only for the renderer-owned leading mkdir prefix. It will not normalize arbitrary `$WORKSPACE_HUB` occurrences in command bodies.

## Cutover Design

The safe cutover will not reopen old whole-crontab replacement. It will expose one reviewed path through `setup-cron.sh` to `cron_apply.py`:

1. It will declare the scheduler identity as `local-current-user-crontab`, target kind as `current-user-cron`, and execution-host binding as `physical-local`.
2. It will reject remote machine arguments unless a future explicit-remote-transport mode will be designed, registered, and tested. This issue will not add remote mutation.
3. It will skip Linux cron reconciliation for registry `os: windows`; Windows Task Scheduler paths under `scripts/windows/` will remain out of scope except for tests proving they are not mutated by the Linux cutover.
4. It will read baseline crontab text `A` under the planned transaction and record a durable snapshot summary.
5. It will build the planned crontab `C` only after every live line will classify as `cataloged`, `preserved_external`, or `ignore`; any `uncataloged` line will abort.
6. It will create a durable backup of `A` under `logs/cron-backups/` with a unique tag before any write.
7. It will acquire and hold the declared lock for the pre-write critical section, re-read `B`, and abort unless `B == A`.
8. It will write `C`, re-read `D`, and require exact byte-for-byte equality with `C`.
9. If write or verification will fail, it will attempt rollback only after a rollback CAS under the same lock; if current text no longer equals the observed failed state, rollback will abort fail-closed rather than overwrite a concurrent change.
10. It will verify rollback restored `A` exactly, and it will report `rolled-back`, `rollback-aborted`, `rollback-failed`, or `rollback-indeterminate` distinctly.

This will satisfy `.claude/rules/scheduler-mutation-safety.md` without weakening the audit. The llm-wiki corpus ingest line will remain `preserved_external` and will be copied verbatim outside the managed block.

## Per-Box Reconciliation

The future implementation will require read-only verification for each target box before live apply:

- ace-linux-1 will need the 47-line classification above, plus explicit reconciliation for `hermes-claude-bridge`, `repository-sync`, and the obsolete `equality-report` body.
- ace-linux-2 will need its own dry-run audit even though issue evidence will say 14/14 declared tasks are installed. The smaller task set must not inherit ace1 assumptions.
- Windows boxes will not use the Linux crontab path. Any Task Scheduler changes will remain governed by the existing Windows writer issues and mutation-surface registry.
- The equality-report conflict will be resolved by comparing installed crontab cadence, published `generated_at` stamps, and current YAML. Because published stamps will show a 6-hourly cadence while YAML line 33 will declare weekly, installed/runtime evidence will be treated as truth until YAML and docs will be reconciled.

## TDD Test List

Every row will be written before implementation and will fail against the current behavior where applicable.

| Test name | What it will verify | Expected input | Expected output |
|---|---|---|---|
| `test_mkdir_workspace_hub_prefix_variant_classifies_cataloged` | Drifted but semantically equivalent `$WORKSPACE_HUB` mkdir-prefix line will classify as cataloged. | ace1 `benchmark-regression` style line with `$WORKSPACE_HUB` mkdir prefix and absolute cd/log paths | `cataloged`, reason `normalized-catalog-line`, task id preserved |
| `test_normalization_only_applies_to_renderer_owned_mkdir_prefix` | Arbitrary command-body `$WORKSPACE_HUB` changes will not be normalized. | line with changed script args or changed redirect but same script basename | `uncataloged` |
| `test_unknown_live_line_still_blocks_cutover` | Fail-closed property will survive. | `0 * * * * cd /tmp && bash unknown.sh` | audit/cutover aborts nonzero with `uncataloged` |
| `test_hermes_bridge_without_commit_is_not_equivalent` | Command-content drift will not be swallowed by script basename. | live `bridge-hermes-claude.sh` without `--commit` | `uncataloged` until a reviewed exact legacy or YAML reconciliation exists |
| `test_repository_sync_redirect_drift_is_not_equivalent` | Runtime/log contract drift will stay explicit. | live repository-sync with `>> cron-wrapper.log`, current YAML without redirect | `uncataloged` until reconciled |
| `test_equality_report_legacy_collect_build_stays_blocked_until_reconciled` | Obsolete equality-report body will not be mistaken for current `equality-matrix-cron.sh`. | live `collect-equality.sh && build-equality-matrix.py` line | `uncataloged` |
| `test_command_only_notification_purge_matches_selected_catalog_task` | Command-only line with no script basename will classify as cataloged. | `cd <workspace> && find logs/notifications/ ... -delete` | `cataloged`, task `notification-purge` |
| `test_command_only_unknown_find_does_not_match` | Generic command-only matcher will not become substring warn-only. | unrelated `find logs/other -delete` | `uncataloged` |
| `test_duplicate_notification_purge_dedupes_to_one_rendered_line` | Duplicate catalog-owned command-only lines will collapse into one managed copy. | two installed notification-purge lines | planned text contains exactly one purge line |
| `test_preserved_external_llm_wiki_survives_cutover_verbatim` | Other-repo-owned line will never be reaped. | llm-wiki corpus ingest plus generated block | planned text retains exact llm-wiki line outside block |
| `test_cutover_mid_write_mismatch_rolls_back_under_cas` | Mid-write or verification mismatch will roll back correctly. | fake crontab writes corrupt text then re-read returns corrupt state | rollback writes baseline and verifies exact baseline |
| `test_cutover_rollback_aborts_on_concurrent_change` | Rollback will not overwrite a third-party edit. | fake crontab changes after failed write before rollback CAS | status `rollback-aborted`; third-party text preserved |
| `test_setup_replace_routes_to_transaction_not_legacy_replace` | `--replace` will no longer be a disabled dead-end only after transaction tests pass. | fixture `setup-cron.sh --replace --dry-run` | delegates to dry-run transaction or rejects invalid mode without mutation |
| `test_setup_rejects_remote_machine_without_explicit_transport` | Physical-local binding will stay explicit. | physical host `dev-primary`, requested `ace-linux-2` | nonzero remote-rejection before any crontab read/write |
| `test_setup_skips_windows_without_linux_cron_mutation` | Windows Task Scheduler paths will not be affected. | registry machine with `os: windows` | setup exits skip; no `cron_apply.py --apply` |
| `test_scheduler_mutation_surface_report_stays_compliant` | Mutation registry and generated report will remain aligned. | `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` and report check | pass |
| `test_ace2_fixture_requires_its_own_selected_task_set` | ace2 will not inherit ace1 task assumptions. | ace2 fixture with 14 selected tasks and no ace1-only tasks | dry-run planned text contains only ace2 selected tasks |
| `test_no_vacuous_captured_fixture` | Captured ace1 fixture will actually exercise all groups. | fixture parser over captured JSON | asserts 44 A, 2 B, 1 C, 1 preserved external, 2 notification-purge installs |

## Acceptance Criteria

- [ ] Audit will classify the 44 ace1 prefix-only lines as cataloged through a reviewed exact normalization rule.
- [ ] Audit will keep `hermes-claude-bridge`, `repository-sync`, and obsolete `equality-report` blocked until explicit per-task reconciliation will happen.
- [ ] `notification-purge` will match as a selected command-only catalog task and duplicate installed copies will dedupe to one rendered line.
- [ ] Genuinely unknown lines will still make `cron-audit.py` and cutover planning exit nonzero.
- [ ] llm-wiki corpus ingest will remain `preserved_external` and verbatim after dry-run planning.
- [ ] `setup-cron.sh --replace` will either route through the compliant transaction or be replaced by an explicitly named reviewed apply mode; no legacy replace path will return.
- [ ] The transaction will provide baseline snapshot, durable backup, pre-write CAS, exact post-write verification, CAS rollback under the declared lock, and exact rollback verification.
- [ ] Execution-host binding will remain `physical-local`; no remote scheduler mutation will be inferred from machine aliases or workspace paths.
- [ ] Windows Task Scheduler mutation paths will remain out of scope and covered by non-mutation tests.
- [ ] ace1 and ace2 will each require read-only dry-run audit evidence before any live apply.
- [ ] #3707 will be able to add `daily-cleanup` only after this path will pass dry-run and reviewed apply gates.
- [ ] No implementation will occur before user approval and `status:plan-approved`.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex self-review r1 | MINOR | The plan will need implementation-time care around exact shell parsing and around the equality-report ground-truth conflict, but no MAJOR blocker will remain after this draft will explicitly keep B/C lines blocked and isolate Windows Task Scheduler. |

**Overall result:** PASS with MINOR residual risks; implementation will remain blocked pending user approval.

Revisions made based on review:
- The classification will split the 47 lines into 44 prefix-only, 2 command-content drift, and 1 unresolved obsolete equality-report body instead of treating all script matches as equivalent.
- The notification-purge requirement will be phrased as a generic command-only matcher, not as acceptance of the current ace1 exact legacy workaround.
- The cutover design will explicitly include rollback CAS under the same lock and exact rollback verification.
- The per-box section will require ace2 verification and will keep Windows Task Scheduler paths out of scope.
- The equality-report cadence conflict will remain an explicit reconciliation gate rather than trusting YAML.

## Risks and Open Questions

- **Risk:** Shell normalization can become too broad. The implementation will only normalize the leading renderer-owned mkdir prefix and will test that changed args, redirects, or script bodies still block.
- **Risk:** B/C lines may need owner decisions. The plan will keep those lines blocked until per-box evidence will prove whether YAML or installed text should change.
- **Risk:** Existing tests may pass vacuously if they use synthetic one-line fixtures only. The future test suite will include a captured ace1 fixture summary asserting all classification groups.
- **Risk:** The scheduler mutation registry and generated report may drift after code changes. Acceptance will require the checker and report parity command named by the rule.
- **Open:** Whether `repository-sync` should regain an explicit redirect in YAML or rely only on `runtime`/cron-health evidence will be decided during reconciliation.

## Complexity: T3

**T3** — this issue will change scheduler ownership identity, fail-closed audit behavior, transactional crontab apply semantics, cross-machine reconciliation, and #3707 deployment gating.
