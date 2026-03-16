---
name: workflow-html-6-mandatory-usage
description: 'Sub-skill of workflow-html: 6. Mandatory Usage.'
version: 2.3.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# 6. Mandatory Usage

## 6. Mandatory Usage


| Stage | Trigger | Action |
|-------|---------|--------|
| 5 | After `user-review-plan-draft.yaml` | `generate-html-review.py WRK-NNN --lifecycle` |
| 7 | After `user-review-plan-final.yaml` | `generate-html-review.py WRK-NNN --lifecycle` |
| 11 | After execution phase | `generate-html-review.py WRK-NNN --lifecycle` |
| 17 | Before user close review | `generate-html-review.py WRK-NNN --lifecycle` |
| 19 | Auto-called by `close-item.sh` | `generate-html-review.py WRK-NNN --lifecycle` |

```bash
xdg-open .claude/work-queue/assets/WRK-NNN/WRK-NNN-lifecycle.html
# log: via scripts/work-queue/log-user-review-browser-open.sh
```

---
