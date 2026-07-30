---
name: feedback_always_update_equality_matrix
description: Always finish equality/fleet-related work by publishing the matrix to origin/main — the committed render is the canonical comparison surface and must never lag the work
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 56edf89f-ff7f-4c42-91a0-1a0b634d59e8
---

2026-07-02, user: "update the equality matrix always."

**Why:** the matrix is only useful if it reflects current fleet state; a session that fixes equality infrastructure or collects evidence but leaves the committed render stale defeats the purpose (the fleet compares against origin/main, not any box's working tree — see [[project_equality_matrix_reconcile_2026_07]]).

**How to apply:** after ANY work that changes equality evidence, collectors, verdicts, or machine state (installs, cron changes, provider fixes), end by running `bash scripts/readiness/publish-equality.sh --repo /mnt/local-analysis/workspace-hub --rebuild` (or the full `equality-matrix-cron.sh` when fresh collection is needed) so origin/main carries the updated render.

> **Gotcha (verified 2026-07-11): `--rebuild` alone can no-op and leave a STALE render.** `publish-equality.sh` gates on "local yaml `generated_at` strictly newer than origin's." If a scheduled curation already pushed today's yaml (e.g. the noon session-curation run) but did NOT re-render the HTML, the live matrix render lags its own evidence, yet `publish-equality.sh --rebuild` prints `nothing newer than origin/main; no commit needed` and refuses to rebuild. To force a fresh render in that state, run **`bash scripts/readiness/equality-matrix-cron.sh`** — its `collect-equality.sh` step regenerates THIS box's yaml with a new `generated_at`, which then satisfies the newer-than-origin gate so `publish --rebuild` re-renders + commits. `equality-matrix-cron.sh` reads the interactive checkout but does NOT `git switch`/`rebase`/`stash` it (unlike `refresh-equality-matrix.sh`), so it is safe to run from a diverged dev checkout. This is agent-runnable (script push to main is classifier-allowed; only raw `git push` to main is not). Refresh the user's local copy in `~/Downloads/` when they've been viewing it there. Canonical live URL: https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html. Infrastructure side: control-plane rebuild cron runs 6-hourly (bumped from daily 2026-07-02); every machine's own publish also re-renders.
