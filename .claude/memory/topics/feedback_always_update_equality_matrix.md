> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_always_update_equality_matrix.md

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

**How to apply:** after ANY work that changes equality evidence, collectors, verdicts, or machine state (installs, cron changes, provider fixes), end by running `bash scripts/readiness/publish-equality.sh --repo /mnt/local-analysis/workspace-hub --rebuild` (or the full `equality-matrix-cron.sh` when fresh collection is needed) so origin/main carries the updated render. This is agent-runnable (script push to main is classifier-allowed; only raw `git push` to main is not). Refresh the user's local copy in `~/Downloads/` when they've been viewing it there. Canonical live URL: https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html. Infrastructure side: control-plane rebuild cron runs 6-hourly (bumped from daily 2026-07-02); every machine's own publish also re-renders.
