---
name: work-queue-complexity-routing
description: 'Sub-skill of work-queue: Complexity Routing.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Complexity Routing

## Complexity Routing


| Complexity | Criteria | Route |
|------------|----------|-------|
| Simple | Single change, clear files, <50 words, 1 repo | A — light execution |
| Medium | Clear outcome, 1-2 repos, 50-200 words | B — standard execution |
| Complex | Architectural, 3+ repos, >200 words | C — deep + stricter closure |

All routes share stages 1-9 and 13-20. Routes differ in execution depth (10-12).
Route A: single cross-review pass at Stage 6.
Route B/C: multi-provider cross-review (Claude + Codex + Gemini).

See `work-queue-workflow/SKILL.md` §Complexity Routing for full detail.
