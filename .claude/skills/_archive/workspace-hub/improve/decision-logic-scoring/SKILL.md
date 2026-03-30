---
name: improve-decision-logic-scoring
description: 'Sub-skill of improve: Decision Logic (Scoring).'
version: 1.4.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Decision Logic (Scoring)

## Decision Logic (Scoring)


| Factor | Weight | Criteria |
|---|---|---|
| Recurrence | 40% | Same pattern N times (1x=0.2, 2x=0.5, 3+=0.8) |
| Severity | 30% | Blocked work (1.0), warning (0.5), info (0.2) |
| Freshness | 15% | This session (1.0), last 7 days (0.7), older (0.3) |
| Specificity | 15% | Actionable (1.0), vague (0.3) |

**Thresholds**:
- Score >= 0.6: Apply immediately
- Score 0.3–0.59: Stage for accumulation (may trigger next session)
- Score < 0.3: Discard

**Exceptions** (bypass scoring):
- Direct user statements ("remember this", "always do X") → apply immediately
- Skill deprecation → requires 90-day inactivity evidence regardless of score
