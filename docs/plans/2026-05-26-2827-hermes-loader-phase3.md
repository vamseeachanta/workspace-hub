# Plan for #2827: Reconciler Phase 3 — per-machine Hermes loader cron

> **Status:** draft (needs adversarial review → user approval) · **Complexity:** T2 · **Date:** 2026-05-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2827 · **Parent:** #2802 · #2795 · **Client:** N/A

## Resource Intelligence Summary
- Board YAML under `.claude/memory/kanban/boards/*.yaml` is the **SSoT** (kept current by the reconciler once Phase 2 / #2826 is live).
- A **manual mirror snapshot** currently projects board YAML into each machine's `~/.hermes/kanban.db`. Verify the exact current loader path before planning the cron (likely a script under `scripts/` or a Hermes-side importer).
- Memory: `feedback_cross_machine_execution` (per-machine via shared git, not SSH/rsync); `feedback_hermes_*`.

## Problem
The board YAML is auto-current (post-#2826), but each machine's `~/.hermes/kanban.db` projection is updated **manually**, so the local Hermes view drifts until someone runs the mirror. Need an automatic, idempotent per-machine projection.

## Approach
- Identify/!consolidate the existing YAML→`kanban.db` loader into one idempotent script (re-run = no-op when YAML unchanged; safe on partial/locked DB).
- Add a **per-machine cron** (systemd timer or cron entry, installed by a small guarded installer like `setup-codex-sandbox.sh`) that pulls latest board YAML (git) and runs the loader.
- Per-machine, not fleet-pushed (cf. `feedback_cross_machine_execution`): each machine opts in; the installer is idempotent + reports state via a `--check` mode.

## Scope
In: idempotent loader consolidation; per-machine cron installer + `--check`/teardown; docs. Out: changing the YAML SSoT or the reconciler (that's Phase 1/2).

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
