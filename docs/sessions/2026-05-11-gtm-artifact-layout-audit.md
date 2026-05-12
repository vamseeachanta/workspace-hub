---
date: 2026-05-11
session: GTM client-artifact location audit + cross-repo layout inconsistency filing + branch/worktree cleanup
status: COMPLETE — memory captured, issue #2662 filed, codex/burn merged, 5 stale branches deleted, single-worktree single-branch state
session_kind: short single-thread recall query → cross-repo audit → governance issue → branch hygiene pass
---

# GTM artifact layout audit — 2026-05-11

## TL;DR

Started as a recall query ("where is the GTM material from 3 days ago / last week?"). Returned two of three actual bundles. User surfaced a missed third path (`digitalmodel/examples/demos/gtm/output/client_pdf_pack_2026-05-07/`) and asked me to document the inconsistency and file an issue. Captured auto-memory + filed [workspace-hub #2662](https://github.com/vamseeachanta/workspace-hub/issues/2662) with `status:needs-plan` + `domain:repo-cleanup`. No code changes in workspace-hub repo; the auto-memory file lives outside the repo.

## What was asked

1. "Location of the GTM material we prepared 3 days ago to release to clients" (2026-05-08).
2. "Location of the GTM material we prepared last week to release to clients" (2026-05-04 region).
3. "There are more here: `digitalmodel/examples/demos/gtm/output/client_pdf_pack_2026-05-07`; make a note that the files are not saved in a consistent manner nor consistent format across repositories; … Create gh issue for this inconsistent problem."

## What was returned

### Initial recall (incomplete — missed digitalmodel pack)

| Date | Bundle | Path |
|---|---|---|
| 2026-05-08 | Doris client follow-up + ecosystem flowchart | `docs/gtm/sendable-bundles/2026-05-08/` |
| 2026-05-04 | worldenergydata GTM reports (FDAS, decline, BSEE) | `worldenergydata/reports/gtm/2026-05-04-*.html` |

### Full picture after user correction

Four distinct GTM-artifact directory roots verified on disk under `/mnt/local-analysis/workspace-hub/`:

| # | Repo / scope | Path pattern | Convention | 2026-05-04..11 example |
|---|---|---|---|---|
| 1 | `worldenergydata` | `reports/gtm/` | filename prefix `YYYY-MM-DD-foo.html` | `2026-05-04-bsee-field-analysis-comprehensive.html` |
| 2 | `digitalmodel` | `examples/demos/gtm/output/<bundle>/` | dir suffix `client_pdf_pack_YYYY-MM-DD/`; HTML+PDF pairs + ZIP + index | `client_pdf_pack_2026-05-07/00_vessel_capability_gtm_pdf_pack_index.{html,pdf}` |
| 3 | workspace-hub (sendable) | `docs/gtm/sendable-bundles/<YYYY-MM-DD>/` | nested date directory; MD + HTML + PDF mix; no index | `2026-05-08/repo-ecosystem-flowchart.{html,pdf}` + `doris-follow-up-email-and-links.md` |
| 4 | workspace-hub (analysis) | `docs/reports/gtm/` | filename prefix; overlaps #1 convention but at hub level | `2026-04-29-vessel-capability-chart-storyboard.md` |

Additional GTM-adjacent (tooling, not artifacts): `docs/gtm/` (strategy planning), `scripts/gtm/`, `tests/gtm/`, `logs/gtm/`.

## What landed

### Memory (outside repo)

- `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_gtm_artifact_layout_inconsistency.md` — type `project`, lists all four paths + concrete inconsistency dimensions, links to #2662 and `[[project_worldenergydata_gtm_state]]`.
- `MEMORY.md` index updated under the Project section, next to the existing `worldenergydata GTM state` line.

### GitHub

- [workspace-hub #2662](https://github.com/vamseeachanta/workspace-hub/issues/2662) — `status:needs-plan`, `domain:repo-cleanup`. Body documents three layout roots, three date conventions, three bundle formats, and four concrete current paths. Solution direction explicitly NOT pre-committed — three candidate approaches (A: per-repo standardization, B: hub-level canonical bundle dir, C: per-send manifest) listed for the plan phase to weigh.
- Filing-summary comment posted (per "comment on issues" feedback rule).

### workspace-hub repo

- This session-handoff doc only. No GTM artifact moves or rewrites — those are deferred until #2662 is plan-approved.

## Why the original recall missed digitalmodel

Two compounding factors:

1. **Memory-driven recall** — `project_worldenergydata_gtm_state` is detailed and recent (6 days old), so it served as the seed for the search. It only documents one repo's pattern.
2. **Sparse-filesystem search timeouts** — `find /mnt/local-analysis/workspace-hub -maxdepth 5 -type d -name gtm` times out at ~30s on the overlay filesystem. I fell back to `ls -d <repo>/*/gtm` patterns *after* the user correction, which would have caught all four roots if run from the start.

Captured as actionable in the new memory entry: future "where is the GTM pack?" queries must enumerate all four layout patterns explicitly, not rely on memory recall of one.

## Follow-ups (not done this session, captured for next)

- **#2662 plan phase** — per project planning workflow, draft plan → adversarial review → `status:plan-review` → user approves → `status:plan-approved` → implement. Three candidate directions noted in issue body.
- **Verify worldenergydata branch state** — memory note (6 days old) says GTM deliverables are committed on `docs/handoff-2026-05-03-lt-epic-closed`. Did not re-verify; if #2662 plan touches worldenergydata files, re-check whether that branch is current or merged.
- **digitalmodel branch state** — did not check which branch `client_pdf_pack_2026-05-07` lives on. Same caveat: re-verify before plan execution.

## Cross-references

- Memory: `project_gtm_artifact_layout_inconsistency.md` (new this session).
- Memory: `project_worldenergydata_gtm_state.md` (existing, partial view — flagged in new memory as contributing to the original recall miss).
- Issue: [workspace-hub #2662](https://github.com/vamseeachanta/workspace-hub/issues/2662).
- Comment: [#2662#issuecomment-4426984070](https://github.com/vamseeachanta/workspace-hub/issues/2662#issuecomment-4426984070).

## Addendum — branch & worktree cleanup pass (same session)

After the issue was filed, user requested a full hygiene pass across worktrees, branches, and pending merges.

### Discovered state (before)

- **2 worktrees**: `workspace-hub` (main) + `codex-burn-20260511/workspace-hub-bundle` (codex/burn-...)
- **3 local branches**: `main`, `codex/burn-20260511-workspace-hub-bundle` (2 commits ahead, 15h old), `docs/issue-2653-session-logger-plan` (1 commit ahead, 5 days old)
- **6 remote branches**: above + `origin/main` + 3 `handoff/2026-05-10-repo-structure-exit{,-update,-final}` + `origin/routine/2026-05-09-session-signals`

### Key finding

`codex/burn-20260511-workspace-hub-bundle` carried the closed [#2523](https://github.com/vamseeachanta/workspace-hub/issues/2523) implementation (`scripts/preflight/*` Hermes preflight checker, ~600 LOC + tests + fixtures) that **was never merged to main**. Issue closed 2026-05-11 11:56 UTC with no associated PR. Classic "closed issue, unmerged implementation" antipattern — the kind of plan-vs-live-state divergence that [#2405 attestation](https://github.com/vamseeachanta/workspace-hub/issues/2405) is designed to surface.

### Actions taken

| Step | Operation | Result |
|---|---|---|
| 1 | `git merge --no-ff codex/burn-...` into main | Merge commit `40b12875c` — 18 files, +901/-41 |
| 2 | Verify branch fully contained in main (`rev-list --left-right main...branch`) | `13	0` — clean; no race-revert |
| 3 | `git push origin main` | `f194c57a2..40b12875c main -> main`; pre-push gate skipped (no tier-1 changes) |
| 4 | `git worktree remove codex-burn-20260511/workspace-hub-bundle` | Removed cleanly; gitlink-based worktree disposal worked |
| 5 | `git branch -d codex/burn-...` | Safe delete (merged into main) |
| 6 | `git branch -D docs/issue-2653-session-logger-plan` | Force delete; the unique file `docs/plans/2026-05-06-issue-2653-per-session-log-files.md` was already on main via a different commit, so the branch tip wasn't reachable |
| 7 | `git push origin --delete <5 branches>` | Deleted: `codex/burn-...`, 3× `handoff/2026-05-10-*`, `routine/2026-05-09-session-signals` |
| 8 | `git fetch --prune origin` | Local remote-tracking refs pruned |

### Final state (after)

- 1 worktree (`workspace-hub` on main)
- 1 local branch (`main`)
- 1 remote branch (`origin/main`)
- Working tree clean except known parallel-session/Hermes churn (`.claude/state/`, sibling-agent files)

### Parent dir left in place

`/mnt/local-analysis/codex-burn-20260511/` was NOT removed — it contains sibling burn-artifact subdirs for other repos (`assetutilities-bundle`, `worldenergydata-bundle`, `monitoring-evidence`, `logs`, `prompts`) that are out of workspace-hub scope.
