# Plan for #3593: ops(cron) — gpu-claw excluded from 8 cron jobs by legacy-machines conflict; decide per-job authority model

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-07-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3593
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-29-plan-3593-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/cron/cron_transaction.py:_task_selection` (lines 76–93) — implements the conflict model: when a task's `roles` intersect a machine's role set but the task's `machines` list exists and does NOT include the machine, the resolution is: `roles_authoritative: true` → roles win (machine selected); otherwise → legacy machines list wins (machine NOT selected). Conflicts are always reported.
- EXISTS: `config/scheduled-tasks/schedule-tasks.yaml` — canonical cron catalog. The `repository-sync` job already carries `gpu-claw` in its `machines:` list (added per #3592, per comment in file at line 867). The other 8 conflicting jobs do not yet enumerate gpu-claw.
- EXISTS: `config/workstations/registry.yaml` (lines 295–325) — gpu-claw: `harness_profile.roles: [sim-worker]`, `schedule_variant: contribute-minimal`, `capabilities.agent_clis: [claude]`, `storage.knowledge: null`, `storage.remote_mounts: []`.
- EXISTS: `scripts/cron/cron_apply.py` — transactional crontab cutover; reports conflicts via `print(f"  CONFLICT {cid}")`. No code changes needed (conflict resolution is data-driven via YAML fields).
- Gap: No per-job documentation of which jobs are intentionally machine-gated (explicit legacy list) vs. implicitly role-eligible (roles should suffice). This plan will establish that intent for gpu-claw.

### Standards
| Standard | Status | Source |
|---|---|---|
| Not applicable — this is an infrastructure config issue | — | — |

### LLM Wiki pages consulted
- No relevant wiki pages.

### Documents consulted

- Issue body #3593 — provides the 9-job conflict log from 2026-07-23 enrollment run: repository-sync, ecosystem-reconcile, licensed-run-alarm, drive-index-refresh-dde, session-curation, harness-update, quota-snapshot-refresh, solver-watch-results, solver-dashboard.
- Issue #3507 — gpu-claw cron enrollment checklist; provides the enrollment session context (2026-07-23) and notes that Tailscale is now live.
- Issue #3592 (closed) — equality epic close-out; the comment in `schedule-tasks.yaml` at line 865 says "gpu-claw added per #3592: scheduler_baseline declares repo_sync REQUIRED on every Linux execution box." Confirms repository-sync is already fixed.
- `config/scheduled-tasks/mutation-surfaces.yaml` line 262 — digest note: "repository-sync machines list (#3592 scheduler_baseline follow-on)." Confirms the update is tracked.

### Gaps identified

- No explicit record of which sim-worker-role jobs are intentionally gated to specific Linux boxes vs. intended for all sim-workers. This plan fills that gap for gpu-claw.
- `schedule_by_machine` block in `harness-update` does not enumerate gpu-claw — needs a per-machine schedule entry if added.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-29T00:00:00Z via `gh issue view`):
- `#3593` — OPEN — ops(cron): gpu-claw excluded from repository-sync — roles_authoritative unset
- `#3592` — CLOSED — ace-win-2 on-box equality epic (the PR that added gpu-claw to repository-sync.machines)
- `#3507` — OPEN (per-checklist progress) — ops(gpu-claw): enroll in machine-equivalence matrix

**File existence** (verified 2026-07-29 via live checkout at `/mnt/local-analysis/workspace-hub`):
- EXISTS: `config/scheduled-tasks/schedule-tasks.yaml`
- EXISTS: `config/workstations/registry.yaml`
- EXISTS: `scripts/cron/cron_transaction.py`
- EXISTS: `scripts/cron/cron_apply.py`

**Line excerpts** — 8 conflicting job definitions analyzed:

| Job id | machines list | roles | gpu-claw verdict |
|---|---|---|---|
| `repository-sync` | `[…, gpu-claw]` (already added) | `[control-plane, comms-dispatch, sim-worker]` | ✅ already enrolled |
| `ecosystem-reconcile` | `[ace-win-1, ace-win-2]` | `[sim-worker]` | ❌ Windows-only (powershell script); gpu-claw is Linux — DO NOT ADD |
| `licensed-run-alarm` | `[dev-secondary, ace-linux-2]` | `[comms-dispatch, sim-worker]` | ❌ requires `/mnt/local-analysis/deckhand-ops` mount and `.deckhand/licensed-run.env` — NOT present on gpu-claw — DO NOT ADD |
| `drive-index-refresh-dde` | `[dev-secondary, ace-linux-2]` | varies | ❌ references `/mnt/remote/ace-linux-2/dde` path — NOT present on gpu-claw (`remote_mounts: []`) — DO NOT ADD |
| `session-curation` | `[dev-primary, ace-linux-1, dev-secondary, ace-linux-2, ace-win-1, ace-win-2]` | `[control-plane, comms-dispatch, sim-worker]` | ✅ gpu-claw runs Claude CLI → generates session logs → should curate — ADD gpu-claw |
| `harness-update` | `[dev-primary, ace-linux-1, dev-secondary, ace-linux-2, ace-win-1, ace-win-2]` | `[control-plane, comms-dispatch, sim-worker]` | ✅ gpu-claw has `npm` → can update harness tools (codex, claude) — ADD gpu-claw |
| `quota-snapshot-refresh` | `[dev-secondary, ace-linux-2]` | `[sim-worker]` | ⚠️ could run but low value (gpu-claw is not a quota-monitoring box); defer to user — SKIP for now |
| `solver-watch-results` | `[ace-linux-1]` | `[sim-worker]` | ⚠️ solver queue is on ace-linux-1's local storage; gpu-claw has no solver queue path — DO NOT ADD |
| `solver-dashboard` | `[ace-linux-1]` | `[sim-worker]` | ⚠️ same as solver-watch-results — solver state is ace-linux-1-local — DO NOT ADD |

**Gap proofs**:
- `grep "gpu-claw" config/scheduled-tasks/schedule-tasks.yaml` → currently matches only `repository-sync` machines line → confirms 8 jobs still missing gpu-claw.

**Reproduction proofs**:
- Reproduced at: 2026-07-23 per issue body (enrollment run output in #3593).
- Failure mode: `cron_apply.py --machine gpu-claw --dry-run` shows 9 CONFLICTs with "roles_authoritative not set → legacy wins (not selected)".

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-29-issue-3593-gpu-claw-cron-authority-model.md |
| Config change | `config/scheduled-tasks/schedule-tasks.yaml` |
| Plan review — Claude | scripts/review/results/2026-07-29-plan-3593-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-29-plan-3593-codex.md |
| Plan review — Agy | scripts/review/results/2026-07-29-plan-3593-agy.md |

---

## Deliverable

`config/scheduled-tasks/schedule-tasks.yaml` updated to add `gpu-claw` to the `machines:` lists of `session-curation` and `harness-update`, with a `schedule_by_machine` entry for `harness-update`, so that re-running `cron_apply.py --machine gpu-claw --apply` produces 0 unexpected CONFLICTs (only the intentionally-excluded jobs remain as documented exclusions).

---

## Pseudocode

trivial — see files to change

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Add gpu-claw to session-curation and harness-update machines lists; add schedule_by_machine entry for harness-update on gpu-claw |
| Update | docs/plans/README.md | Add plan to index |

### Exact changes

**session-curation** — add `gpu-claw` to machines list:
```yaml
machines: [dev-primary, ace-linux-1, dev-secondary, ace-linux-2, ace-win-1, ace-win-2, gpu-claw]
```

**harness-update** — add `gpu-claw` to machines list and add per-machine schedule:
```yaml
machines: [dev-primary, ace-linux-1, dev-secondary, ace-linux-2, ace-win-1, ace-win-2, gpu-claw]
schedule_by_machine:
  dev-primary: "15 1 * * *"
  ace-linux-1: "15 1 * * *"
  dev-secondary: "45 1 * * *"
  ace-linux-2: "45 1 * * *"
  ace-win-1: "15 2 * * *"
  ace-win-2: "15 2 * * *"
  gpu-claw: "15 3 * * *"     # 03:15 — staggered after Windows
```

**No `roles_authoritative: true` approach** — the explicit machines list approach is preferred here because:
1. It makes the intent auditable per-job in the YAML.
2. It avoids enrolling future unknown sim-workers in jobs with machine-specific paths (licensed-run-alarm, deckhand mounts).
3. The conflict model's safety fence is correct behavior for most of these jobs.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_gpu_claw_session_curation_selected | session-curation is selected for gpu-claw after change | updated schedule-tasks.yaml + gpu-claw registry entry | selected=True, no CONFLICT |
| test_gpu_claw_harness_update_selected | harness-update is selected for gpu-claw after change | updated schedule-tasks.yaml + gpu-claw registry entry | selected=True, no CONFLICT |
| test_ecosystem_reconcile_still_excluded | ecosystem-reconcile remains excluded for gpu-claw | updated schedule-tasks.yaml | selected=False, CONFLICT reported (Windows-only) |
| test_licensed_run_alarm_still_excluded | licensed-run-alarm remains excluded for gpu-claw | updated schedule-tasks.yaml | selected=False, CONFLICT reported |
| test_dry_run_shows_zero_unexpected_conflicts | cron_apply.py --machine gpu-claw --dry-run shows only expected exclusions | updated YAML + live registry | output lists only ecosystem-reconcile, licensed-run-alarm, drive-index-refresh-dde, solver-watch-results, solver-dashboard as CONFLICTs (all intentional) |

The existing `cron_transaction.py` unit tests cover the `select_tasks`/`_task_selection` logic; new tests run `cron_apply.py --dry-run` end-to-end to verify the YAML changes take effect.

---

## Acceptance Criteria

- [ ] `python3 scripts/cron/cron_apply.py --machine gpu-claw --dry-run` shows `session-curation` and `harness-update` in the **selected** set (not in CONFLICTs)
- [ ] `ecosystem-reconcile`, `licensed-run-alarm`, `drive-index-refresh-dde`, `solver-watch-results`, `solver-dashboard` still appear as CONFLICTs (intentionally excluded, documented)
- [ ] `repository-sync` does not appear as a CONFLICT (already enrolled per #3592)
- [ ] `harness-update` has a `gpu-claw` entry in `schedule_by_machine` staggered at 03:15 (after Windows machines)
- [ ] All existing `cron_transaction.py` unit tests pass: `uv run pytest scripts/cron/tests/ -v`
- [ ] Review artifacts posted to `scripts/review/results/2026-07-29-plan-3593-*.md`

---

## Adversarial Review Summary

<!-- Filled in after adversarial review completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | — |
| Codex | TBD | — |
| Agy | TBD | — |

**Overall result:** TBD

---

## Risks and Open Questions

- **Risk:** `session-curation` runs `curate-session-memory.sh` which publishes a fingerprint to the `session-curation-state` git ref. Adding gpu-claw means a new publisher — verify the script is idempotent per-machine and does not conflict with ace-linux-1 pushes. If it uses `--force` or non-ff pushes, two concurrent runs could conflict.
- **Risk:** `harness-update` runs `scripts/maintenance/update-harness-tools.sh` which calls npm. gpu-claw's registry entry says `npm` is installed but `uv` is NOT yet installed (registry note: "uv NOT installed yet — onboarding step"). The harness-update `requires:` list is `[bash, git, npm]` — `uv` is NOT required — so this should work, but verify against the actual script.
- **Open:** Should `quota-snapshot-refresh` be added to gpu-claw? It is lightweight and provides live provider quota in the statusline. Low priority; deferred to user decision at approval time. If yes, add `gpu-claw` to its `machines:` list and `prefer: ace-linux-2` stays.
- **Open:** After this plan is implemented, run `cron_apply.py --machine gpu-claw --apply` ON-BOX (requires ssh to gpu-claw). The plan file changes are the data side; the on-box apply step is a separate HITL action that requires the user or a licensed-run dispatch.

---

## Complexity: T1

Config YAML only (two machines lists, one schedule_by_machine entry). No code changes. Clear enumeration of per-job decisions.
