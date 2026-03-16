---
name: work-document-exit-step-5-clear-active-wrk-state
description: "Sub-skill of work-document-exit: Step 5 \u2014 Clear Active WRK State."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 5 — Clear Active WRK State

## Step 5 — Clear Active WRK State


```bash
ACTIVE_WRK_FILE=".claude/state/active-wrk"
if [[ -f "$ACTIVE_WRK_FILE" ]]; then
  rm "$ACTIVE_WRK_FILE"
  echo "Cleared .claude/state/active-wrk"
fi
```
