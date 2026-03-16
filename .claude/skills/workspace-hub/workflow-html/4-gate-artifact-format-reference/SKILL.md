---
name: workflow-html-4-gate-artifact-format-reference
description: 'Sub-skill of workflow-html: 4. Gate Artifact Format Reference.'
version: 2.3.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# 4. Gate Artifact Format Reference

## 4. Gate Artifact Format Reference


| Gate | Expected file | Key fields |
|------|--------------|-----------|
| Plan confirmation | `WRK-NNN-lifecycle.html` Stage 7 | `confirmed_by:`, `confirmed_at:`, `decision: passed` |
| Browser-open | `evidence/user-review-browser-open.yaml` | `stage: plan_draft\|plan_final\|close_review` |
| Cross-review | `review.md` or `review.html` | verdict field |
| Stage evidence | `evidence/stage-evidence.yaml` | all 20 stages with status |
| Resource intel | `evidence/resource-intelligence.yaml` | `completion_status`, `skills.core_used` ≥3 |
| Future work | `evidence/future-work.yaml` | `recommendations[]` with `captured: true` |

---
