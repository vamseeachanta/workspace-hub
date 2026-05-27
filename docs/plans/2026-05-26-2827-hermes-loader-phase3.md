# Plan for #2827: Reconciler Phase 3 — per-machine Hermes loader cron

> **Status:** adversarial-reviewed (scope narrowed by discovery: loader + safe autoload-on-post-merge already exist; gap = time-based trigger) · **Complexity:** T1–T2 · **Date:** 2026-05-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2827 · **Parent:** #2802 · #2795 · **Client:** N/A

## Resource Intelligence Summary (CORRECTED 2026-05-26 — discovery vs origin/main)
- Board YAML under `.claude/memory/kanban/boards/*.yaml` is the **SSoT** (kept current by the reconciler once Phase 2 / #2826 is live).
- **The loader already exists and is re-runnable:** `.claude/memory/kanban/scripts/load.py` ("Re-runnable… reads boards/*.yaml, writes ~/.hermes/kanban.db via `hermes kanban`").
- **An automatic projection ALREADY exists, but only on `git pull`:** `scripts/memory/kanban-autoload.sh` is installed by `bootstrap-machine.sh` as a **post-merge git hook** + run once at bootstrap. It is **opt-in** (marker `~/.hermes/kanban-autoload.enabled`), idempotent (`--from-hook` runs only when the pull changed board YAML), and **safe** (loads cards at their real status, NOT forced triage — explicitly to avoid the `feedback_hermes_triage_is_pipeline_entry` runaway-spawn hazard; gated to Manual-orchestration machines).
- Memory: `feedback_cross_machine_execution` (per-machine via shared git, not SSH/rsync); `feedback_hermes_triage_is_pipeline_entry` (triage = pipeline entry, NOT a park).

## Problem (narrowed by discovery)
Most of Phase 3 is **already built**: loader + safe, idempotent, opt-in autoload-on-post-merge. The **real gap** is that the projection only refreshes when the machine does a `git pull` (the post-merge hook trigger). A machine that doesn't pull for a while shows a stale Hermes board. Need a **time-based** trigger so the projection stays current without a manual pull. (The draft's "consolidate the loader / add triage safety" scope is already done — do NOT re-implement it.)

## Approach (narrowed)
- Add a **per-machine, time-based** trigger (systemd timer or crontab) that runs `git -C <repo> pull --ff-only` then `kanban-autoload.sh --from-hook` periodically. Reuse the existing opt-in marker + idempotency — no new loader, no triage-safety rework.
- Installed by a small guarded installer (`--check`/`--dry-run`/teardown, mirroring `setup-codex-sandbox.sh`); per-machine opt-in (cf. `feedback_cross_machine_execution`), not fleet-pushed.
- Decide at implementation: extend `kanban-autoload.sh` with an interval mode vs a thin timer wrapper. Confirm whether a "manual mirror snapshot" still exists to decommission (the autoload hook may already have superseded it).

## Scope (narrowed)
In: a per-machine **time-based** trigger (timer/crontab) wrapping the EXISTING `kanban-autoload.sh`; a guarded installer (`--check`/`--dry-run`/teardown); reuse the existing opt-in marker; docs/coverage. Out: the loader (`load.py` — exists), the autoload hook + triage-safety (exists), the YAML SSoT, the reconciler (Phase 1/2). Sequenced after #2826 (board must be auto-current for a periodic projection to add value).

## Risks & mitigations
| Risk | Mitigation |
|---|---|
| Loader corrupts kanban.db on concurrent write | atomic write / transaction; lock; idempotent re-run |
| Stale git checkout on a machine | loader does `git pull` (or reads the SSoT path) before projecting; log the SHA projected |
| Per-machine drift in coverage | `--check` reports installed state; enumerate live machines (don't assume) |

## Acceptance criteria
1. Idempotent loader: running twice with unchanged YAML makes no DB change (assert).
2. Per-machine installer with `--check` + teardown; cron/timer installed on opt-in machines; projected SHA logged.
3. Manual mirror snapshot decommissioned (or documented as superseded).
4. Coverage table (per-machine installed / N/A) committed.

## Dependencies
Sequenced **after #2826** (board YAML must be auto-current for the projection to be meaningful).

## Adversarial review — findings (2026-05-26; Claude + Codex MAJOR → NEEDS-DECISION)
Verified against `origin/main`. Verdict: **MAJOR — stays draft/needs-decision** (do NOT advance to `plan-review`).
- **BLOCKER (needs user/domain decision):** the loaded card status is contradictory in the source — `load.py:100` passes `--initial-status blocked`, but `load.py:4` docstring AND `.claude/memory/kanban/README.md` say `triage`, while `kanban-autoload.sh`'s header says "real status (ready/blocked), not forced triage". `blocked`-without-reason auto-unblocks to ready (`feedback_hermes_blocked_status_auto_unblocked`) → claimable → spawns workers. A periodic (time-based) trigger amplifies this. **The actual loaded status + its gateway behavior must be resolved (and the code/docs reconciled) before a periodic trigger is safe.** (Codex #1; Claude over-trusted the autoload header.)
- Fix (fold once unblocked): the timer wrapper must capture pre/post SHA itself — `--from-hook` keys on `ORIG_HEAD..HEAD`, unreliable under a timer's `git pull`. (Codex #2)
- Fix: timer must propagate loader failure — `kanban-autoload.sh` ends `... || true`, masking failures as healthy. (Codex #3)
- Fix: AC1 (loader idempotency assertion) is inconsistent with "loader out of scope" — drop the AC. (Codex #4)
Artifacts: as above.
