# Session — achantas-data photo fix, Switzerland trip, travel skill family

**Date:** 2026-04-27
**User:** Vamsee Achanta
**Working dir:** `/mnt/local-analysis/workspace-hub`
**Repos touched:** `vamseeachanta/achantas-data` (issues), `vamseeachanta/workspace-hub` (skills)

## Summary

Three pieces of work, each ~30 minutes:

1. **Diagnosed and fixed repeating/unrealistic photos** across 19 GitHub issues in `achantas-data` (#42–#66 cohort + parent trips). Root cause: prior draft used NPS regional homepage banners (intentionally generic) + mislabeled Florida photos. Fix: Wikimedia Commons API thumb URLs, one destination-specific photo per issue, all verified `200 image/jpeg` in the main session.
2. **Created a Switzerland 1-week trip plan** as new issue [#68](https://github.com/vamseeachanta/achantas-data/issues/68): 1 hotel + 2 Airbnb pattern, Zurich-anchored, train-based itinerary, ~$8,300–$13,000 family-of-4 budget. Also rendered to PDF at `~/Downloads/achantas-data-issue-68-switzerland-trip.pdf` (8 pp, 1.27 MB) via the `data:md-to-pdf` skill.
3. **Built a reusable travel-agent skill family** at `.claude/skills/travel/` — 8 sub-skills + 3 issue-body templates + a README, 1,215 lines total. Distilled hard rules from the trips above so future trip-planning sessions don't repeat the same mistakes. Committed at `0722fa994`.

## Issues changed in achantas-data

**Photo URL replaced (19):** #42, #43, #44, #45, #46, #50, #52, #54, #55, #56, #57, #58, #59, #61, #62, #63, #64, #65, #66.

**Untouched (already had destination-specific photos):** #41 Oklahoma, #47 Petit Jean, #48 Mount Magazine, #49 Lake Ouachita, #51 Devil's Den, #53 Kisatchie, #60 Henderson Beach.

**New:** #68 Switzerland trip plan.

## Mid-stream defects caught (worth remembering)

- **Subagent verification can be wrong.** Photo-research subagent claimed all 5 Switzerland Wikimedia URLs returned 200; main-session re-verify showed 2 returned 400. Root cause: 800px width was not a generated thumbnail size for those specific files; canonical was 960px (returned by API). Re-verification in the main session caught the defect — codified into `visual-review-board` skill.
- **Wikimedia + Python urllib = 403.** Wikimedia blocks Python's default User-Agent. Use curl with explicit UA, or set User-Agent header in Python.
- **PEP 668 blocks `pip install --user`** on this system's miniforge Python. Workaround: `uv run --with markdown python <script>` for ephemeral deps without touching the system interpreter.

## Travel skill family — what it codifies

Located at `.claude/skills/travel/` in workspace-hub:

```
trip-planner/             — entry orchestrator; trip archetype detection
itinerary-design/         — base count, jet-lag day, last-day = transit-only
lodging-selection/        — hotel-vs-Airbnb matrix, walk-distance gates
transport-and-passes/     — drive-time honesty, rail-pass selection, supplements
visual-review-board/      — Wikimedia API thumburl, no NPS regional banners
risk-and-redundancy/      — 8 watch-out categories, Plan B for load-bearing legs
booking-timeline/         — 4-month / 2-month / 6-week / 1-week cascade
cost-estimation/          — bucket structure, 2026 family-of-4 anchors
templates/
  ├── trip-issue-body.md       (parent trip / multi-destination)
  ├── destination-issue-body.md (single destination)
  └── ranking-matrix.md         (cross-trip comparison)
```

**Hard rules across the family:**

1. No fabricated specific Airbnb listings — describe search criteria.
2. No fabricated train schedules — direct readers to operator booking sites.
3. No NPS regional homepage banner photos.
4. Drive times honest, rounded up.
5. Verify image URLs in the main session, not subagent.
6. Every load-bearing leg has a named Plan B.
7. Tense discipline — proposed work in future tense.

## Commits

| SHA | Title |
|---|---|
| `0722fa994` | `feat(skill): travel-agent skill family for trip planning` (12 files, 1,215 lines) |

No achantas-data commits — issues were edited via `gh issue edit`, not git.

## Working-tree state at session end

`git status --short` shows pre-existing dirty files unrelated to this session (Hermes/auto-sync state under `.claude/state/corrections/`, `config/ai-tools/provider-*.json`, `queue/.watcher-state/`, `docs/sessions/2026-04-27-elements-drive-ingest-handoff.md`, `scripts/operations/agent-execution/`). Those belong to other workflows and were intentionally not touched. The travel-skill commit was scoped to `.claude/skills/travel/` only.

## Future-session continuation

If a future trip is requested:

- Invoke the `trip-planner` skill (auto-fires on phrases like "plan a trip", "weekend ideas").
- Trip-planner detects archetype (weekend / road trip / international rail / beach / ranking) and routes through the relevant sub-skills.
- Templates in `.claude/skills/travel/templates/` are filled per-section.
- All photo URLs go through the Wikimedia API workflow; main session re-verifies before the issue body is published.

## Files written / read this session

- 12 new files under `.claude/skills/travel/` (committed)
- 1 new GH issue #68 + 19 issue body edits in achantas-data (not in git)
- 1 PDF at `~/Downloads/achantas-data-issue-68-switzerland-trip.pdf` (not in git)
- 1 session log: this file
- Temp working files in `/tmp/achantas-photo-fix/` (ephemeral)
