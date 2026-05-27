# Plan for #2827: Reconciler Phase 3 — per-machine Hermes loader cron

> **Status:** adversarial-reviewed; MAJOR resolved by user decision (park imports as blocked-with-reason) → ready for `plan-review` · **Complexity:** T1–T2 · **Date:** 2026-05-26
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

## Adversarial review — findings (2026-05-26; Claude + Codex MAJOR → RESOLVED, user decision 2026-05-26)
Verified against `origin/main`. The MAJOR was a safe-status contradiction; **user chose the simplest *safe* path → now plan-review.**

**The contradiction (Codex #1, verified):** `load.py:100` creates imports as `--initial-status blocked` (no reason, idempotency-keyed), but `load.py:4` docstring + `.claude/memory/kanban/README.md` say `triage`, and `kanban-autoload.sh`'s header says "real status, not triage". Crucially, BOTH claimed-safe options are actually UNSAFE on a machine running the Hermes gateway:
- `triage` is the **pipeline entry**, not a park (`feedback_hermes_triage_is_pipeline_entry`: 134 triage cards → 532 children + 260 workers).
- `blocked` **without a reason** is **auto-unblocked → ready → claimable** (`feedback_hermes_blocked_status_auto_unblocked`).

**RESOLVED — user decision (simplest safe path):** the loader must park imports as **blocked WITH a `blocked_reason`** (e.g. `--blocked-reason "kanban-import: promote manually"`) — blocked-with-reason **survives** (no auto-unblock, no pipeline entry), so a periodic trigger is safe on any machine. (`archive` is the alternative true-park; blocked+reason is the smaller change.)

**Scope additions (this brings a small loader fix in-scope):**
1. `load.py`: add `--blocked-reason` to the `hermes kanban create` call; keep the idempotency key.
2. Reconcile the code-vs-docs drift: fix the `load.py` docstring + `README.md` (they wrongly say `triage`/"safe") to state "blocked-with-reason park".
3. Timer wrapper captures its own pre/post SHA (don't rely on `--from-hook`'s `ORIG_HEAD..HEAD`, unreliable under a timer's `git pull`). (Codex #2)
4. Timer propagates loader failure — `kanban-autoload.sh` ends `... || true`, masking failures; the timer/installer must detect nonzero/log-based failure. (Codex #3)
5. Drop the old AC1 "idempotent loader assertion" wording; replace with: imports land as blocked-with-reason and are NOT auto-unblocked (assert). (Codex #4)

Artifacts: `scripts/review/results/2026-05-26-plan-2826-2827-2828-{claude,codex}.md`. **Note:** the earlier layman framing called triage a "safe holding pen" — corrected here per memory; the safe park is blocked-with-reason (or archive).
