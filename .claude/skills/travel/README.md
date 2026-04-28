# travel — skill family

A travel-agent skill bundle for planning leisure trips that ship with the no-surprises promise. Distilled from real trips planned in `vamseeachanta/achantas-data` (#19, #41–#67, #68) on 2026-04-27.

## Entry point

Invoke **`trip-planner`** when the user asks to plan, draft, or refine a leisure trip. It detects trip archetype and routes through the sub-skills below.

## Skill layout

```
.claude/skills/travel/
├── trip-planner/SKILL.md            ← entry orchestrator
├── itinerary-design/SKILL.md        — day-by-day construction
├── lodging-selection/SKILL.md       — hotel-vs-Airbnb decision matrix
├── transport-and-passes/SKILL.md    — rail passes, drive-time honesty
├── visual-review-board/SKILL.md     — photo sourcing (Wikimedia API)
├── risk-and-redundancy/SKILL.md     — Plan-B for every load-bearing leg
├── booking-timeline/SKILL.md        — 4-month / 2-month / 6-week / 1-week cascade
├── cost-estimation/SKILL.md         — bucket structure + 2026 anchors
└── templates/
    ├── trip-issue-body.md           — parent trip / multi-destination
    ├── destination-issue-body.md    — single destination
    └── ranking-matrix.md            — cross-trip comparison
```

## Hard rules across the family

1. No fabricated specific Airbnb listings — describe search criteria.
2. No fabricated train schedules — direct readers to operator booking sites.
3. No NPS regional homepage banner photos — they repeat across destinations.
4. Drive times honest, rounded up.
5. Verify image URLs in the main session, not subagent.
6. Every load-bearing leg has a named Plan B.
7. Tense discipline — proposed work in future tense.

## Trip archetypes

| Archetype | Sub-skills |
|---|---|
| Weekend domestic | itinerary-design (light), lodging-selection, risk-and-redundancy, cost-estimation |
| Domestic road trip | + visual-review-board, transport-and-passes (drive-time honesty) |
| International rail / multi-city | ALL sub-skills, booking-timeline + transport-and-passes load-bearing |
| Beach / single-resort | itinerary-design (light), lodging-selection, risk-and-redundancy (weather) |
| Idea / ranking | ranking-matrix template only |

## Reference past trips

Calibration anchors when in doubt:

- **#41 Beavers Bend** — gold standard domestic-cabin trip
- **#67 ranking matrix** — top-10 family trip comparison
- **#68 Switzerland 1-week** — gold standard international-rail trip

## Maintenance

When a trip turns up a new pattern, gotcha, or anchor not yet in these skills, update the relevant sub-skill — don't let it stay tribal knowledge. The "Reference patterns" section at the bottom of each SKILL.md is where new lessons land.
