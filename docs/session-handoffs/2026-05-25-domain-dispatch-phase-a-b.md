# Session Handoff — Domain-Categorized Boards + Machine/Provider Dispatch (Phase A + B)

**Date:** 2026-05-25 · **Machine:** ace-linux-1 (dispatch name: `dev-primary`) · **Branch:** `feat/2795-domain-dispatch`

## What this session delivered

GitHub-centered dispatch architecture for the ecosystem kanban: every repo categorized by domain, every open issue assigned a machine + dispatch state, with pull-based per-machine queues. GitHub labels are the source of truth.

### Outcomes
- **1,485 open issues labeled** across 12 repos (`machine:` / `dispatch:ready` / `domain:` where applicable / `ai:` for non-default providers). 0 errors.
- **Machine roster adopted from the pre-existing in-the-wild scheme** (0 relabeling): `dev-primary`, `dev-secondary`, `licensed-win-1`, `licensed-win-2` (== `ace-win-2`), `home-win`, `macbook-portable`, `multi`. Aliases fold `ace-linux-1/2`→`dev-primary/secondary`.
- **Provider capacity model:** claude/codex = workhorse; **hermes shares codex quota** (one WIP pool); gemini scarce/manual-only.
- **workspace-hub reconciliation:** its 162 fine `domain:` labels mapped → 6 coarse board-domains (`domain-map-workspace-hub.yaml`); coarse writes suppressed so the existing taxonomy is preserved.
- **worldenergydata:** `ingestion`→`ingest` rename (board + manifest + domains.yaml; live label renamed in place, 22 issues moved). `bsee`/`hse` boards added (no cards yet).
- **Per-machine queues** materialized: `.claude/dispatch/<machine>.yaml` (full backlog + `wip_eligible` flag), git-tracked.
- **Session monitoring tooling** (earlier in session): `scripts/monitoring/monitor-sessions.sh`, `agents-board.sh`.

### Key artifacts
| Artifact | Path |
|---|---|
| Spec (HTML) | `docs/governance/2026-05-25-domain-dispatch-architecture.html` |
| Schema + taxonomy | `.claude/memory/kanban/{SCHEMA,domains,routing-rules,domain-map-workspace-hub}.yaml` |
| Dispatch tooling | `scripts/dispatch/{route,dispatch,build-wh-domain-map}.py` |
| Queues | `.claude/dispatch/<machine>.yaml` (7 files) |

### Tracking
- Umbrella: [#2795](https://github.com/vamseeachanta/workspace-hub/issues/2795) (`status:plan-approved`) — Phase A+B closeout comments posted.
- PR: [#2796](https://github.com/vamseeachanta/workspace-hub/pull/2796) — OPEN, MERGEABLE, "Part of #2795" (does not auto-close umbrella).
- Refinement: [#2797](https://github.com/vamseeachanta/workspace-hub/issues/2797) — living routing/capability tuning.

## Repo state at exit
- Branch `feat/2795-domain-dispatch` pushed; local == remote (`98d6d7e05`). Working tree clean for all session paths.
- **Dirty exception:** ~40 other files dirty in the working tree from *other/parallel* sessions — intentionally untouched (never `git add -A`; all commits pathspec-scoped).
- **External actions taken & verified:** GitHub label writes on 1,485 issues + one label rename (worldenergydata `domain:ingestion`→`ingest`). No further external actions pending.

## Next steps (none blocking; for whoever resumes)
1. **Code-stage adversarial review + merge PR #2796** (user gate — not self-mergeable).
2. **Rebalance `dev-primary`** — it holds 1,354 of 1,485 cards as the default catch-all; its queue file is ~412 KB and churns per `dispatch.py --write`. Top item on #2797.
3. **Mirror refresh + idempotent re-run** to label issues created since the 2026-05-22 snapshot (~1-2 per repo).
4. **Categorize cards into `bsee`/`hse`** worldenergydata domains (boards exist, empty).

## Resume commands
```bash
cd /mnt/local-analysis/workspace-hub
git switch feat/2795-domain-dispatch
python3 scripts/dispatch/route.py                      # dry-run assignment summary
python3 scripts/dispatch/dispatch.py --capacity        # supply vs demand
python3 scripts/dispatch/route.py --repo <owner/name> --apply --yes   # idempotent re-apply
```
