---
name: github-project-board-summary
description: 'Sub-skill of github-project-board: Summary.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Summary

## Summary


$(echo "$METRICS" | jq -r '"- Total Items: \(.total_items)"')
