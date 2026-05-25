---
name: hermes-kanban-ecosystem
description: "Hermes kanban manifest covering 14 repos × 45 boards × 1536 cards lives at workspace-hub/.claude/memory/kanban/; loader is idempotent via gh:<owner>/<repo>#<num> keys"
metadata: 
  node_type: memory
  type: project
  originSessionId: 000d04a3-532a-4959-becb-59b1f1349fb3
---

The ecosystem-wide Hermes kanban is sourced from YAML at `workspace-hub/.claude/memory/kanban/` (git-tracked, cross-machine) and replayed into per-machine `~/.hermes/kanban.db` via `scripts/load.py`. 45 boards: 1 tier-0 ecosystem + 14 tier-1 repos + 30 tier-2 domains. 1536 cards mirroring 1516 open GH issues + 20 cross-repo strategic themes.

**Why:** Built 2026-05-22 to give Hermes ecosystem-level kanban visibility instead of per-repo isolated todos; replaces ad-hoc gh issue triage. Three-tier model gives both strategic (cross-repo themes) and operational (per-domain) granularity. Loader uses `--idempotency-key gh:<owner>/<repo>#<num>` so re-runs UPSERT without duplicates — any machine running `git pull && python3 scripts/load.py` reproduces the same Hermes state.

**How to apply:**
- For any new ecosystem-level kanban work, start from `.claude/memory/kanban/SCHEMA.yaml` and add to `boards/<slug>.yaml`. Re-run `python3 scripts/load.py` to provision.
- Loader currently uses `--initial-status blocked` but see [[hermes-blocked-status-auto-unblocked]] — those cards DO auto-promote. Treat live Hermes state as dispatchable, not as a manual review queue.
- Detected-gap cards in `gaps/<repo>.yaml` are intentionally NOT loaded — they sit as a planning artifact awaiting GH-issue promotion before becoming live tasks.
- As of 2026-05-23: local commits `d6f4fcf79` (manifest) + `908247944` (sync) NOT yet on origin/main due to push blockers; see handoff `.planning/handoffs/2026-05-23-kanban-push-blocked.md` for recommended push-as-feature-branch recovery.

Related: [[hermes-triage-is-pipeline-entry]], [[hermes-blocked-status-auto-unblocked]], [[autostash-lock-race-workspace-hub]].
