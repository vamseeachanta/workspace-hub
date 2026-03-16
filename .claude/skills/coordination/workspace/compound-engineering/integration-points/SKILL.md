---
name: compound-engineering-integration-points
description: 'Sub-skill of compound-engineering: Integration Points.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Integration Points

## Integration Points


| Skill | Phase | Integration |
|-------|-------|-------------|
| knowledge-manager | Plan | `/knowledge advise` retrieves prior learnings |
| knowledge-manager | Compound | `/knowledge capture` stores new learnings |
| work-queue | Plan | Items with `compound: true` route here |
| core-planner | Plan | Delegates plan synthesis |
| core-coder | Work | Delegates TDD implementation |
| core-reviewer | Review | Delegates finding aggregation |
| skill-learner | Compound | Triggers if pattern score > 0.7 |
| claude-reflect | All | Daily reflection incorporates session data |
