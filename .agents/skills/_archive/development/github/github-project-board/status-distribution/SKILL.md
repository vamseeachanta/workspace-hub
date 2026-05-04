---
name: github-project-board-status-distribution
description: 'Sub-skill of github-project-board: Status Distribution.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Status Distribution

## Status Distribution


$(echo "$METRICS" | jq -r '.by_status[] | "- \(.status): \(.count)"')
