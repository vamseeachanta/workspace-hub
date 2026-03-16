---
name: resource-intelligence-gap-ranking
description: 'Sub-skill of resource-intelligence: Gap Ranking.'
version: 1.1.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Gap Ranking

## Gap Ranking


- `P1`: blocks stage pass
- `P2`: weakens planning materially
- `P3`: enhancement only

Rubric:

- `P1`: the stage cannot safely continue — a required artifact, source, legal gate, or core context is missing or contradictory
- `P2`: the stage can continue, but planning quality or repeatability is materially weakened
- `P3`: the stage remains valid; the gap only improves ergonomics, automation depth, or future scale

If any unresolved `P1` gaps remain → `completion_status: pause_and_revise`.
If no unresolved `P1` gaps remain → `completion_status: continue_to_planning`.

---
