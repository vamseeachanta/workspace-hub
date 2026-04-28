---
name: travel skill family location and entry point
description: Where the travel-agent skill family lives in workspace-hub and how to invoke it for trip planning
type: reference
originSessionId: 548f0fc8-ec3a-4bb0-8291-cc056d20468b
---
**Location:** `.claude/skills/travel/` in workspace-hub (committed 2026-04-27, SHA `0722fa994`)

**Entry skill:** `trip-planner` — auto-fires on trip-planning prompts ("plan a trip", "weekend ideas", "X-day trip to Y").

**Sub-skills:**
- `itinerary-design` — base counts, jet-lag day, last-day-transit
- `lodging-selection` — hotel-vs-Airbnb matrix, walk-distance gates
- `transport-and-passes` — drive-time honesty, rail passes, supplements
- `visual-review-board` — Wikimedia API thumburl workflow (NO NPS regional banners)
- `risk-and-redundancy` — Plan B for load-bearing legs
- `booking-timeline` — 4-month / 2-month / 6-week / 1-week cascade
- `cost-estimation` — bucket structure + 2026 family-of-4 anchors

**Templates:** `.claude/skills/travel/templates/{trip-issue-body,destination-issue-body,ranking-matrix}.md`

**How to apply:** When user requests trip planning (any archetype — weekend, road trip, international rail, beach, ranking matrix), invoke `trip-planner` first; it routes through the sub-skills. Default issue target = `vamseeachanta/achantas-data`.

**Calibration trips:** #41 (Beavers Bend = gold-standard domestic-cabin), #67 (ranking matrix), #68 (Switzerland = gold-standard international-rail). All in `vamseeachanta/achantas-data`.
