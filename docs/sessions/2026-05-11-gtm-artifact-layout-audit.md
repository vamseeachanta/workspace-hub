---
date: 2026-05-11
session: GTM client-artifact location audit + cross-repo layout inconsistency filing
status: COMPLETE — memory captured, issue #2662 filed, handoff committed
session_kind: short single-thread recall query → cross-repo audit → governance issue
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
