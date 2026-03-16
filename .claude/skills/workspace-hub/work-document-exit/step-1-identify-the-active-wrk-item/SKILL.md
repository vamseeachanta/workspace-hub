---
name: work-document-exit-step-1-identify-the-active-wrk-item
description: "Sub-skill of work-document-exit: Step 1 \u2014 Identify the Active WRK\
  \ Item."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 1 — Identify the Active WRK Item

## Step 1 — Identify the Active WRK Item


Check these sources in order, use the first that resolves:

```bash
# Source A: explicit active-wrk state file
ACTIVE_WRK_FILE=".claude/state/active-wrk"
if [[ -f "$ACTIVE_WRK_FILE" ]]; then
  WRK_ID=$(cat "$ACTIVE_WRK_FILE" | tr -d '[:space:]')
fi

# Source B: most recently modified working/ item
if [[ -z "$WRK_ID" ]]; then
  WRK_ID=$(ls -t .claude/work-queue/working/*.md 2>/dev/null \
    | head -1 \
    | xargs basename 2>/dev/null \
    | sed 's/\.md$//')
fi

# Source C: git status — infer from branch name
if [[ -z "$WRK_ID" ]]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
  WRK_ID=$(echo "$BRANCH" | grep -oE 'WRK-[0-9]+' | head -1)
fi

# Source D: no active WRK — document general session state
if [[ -z "$WRK_ID" ]]; then
  echo "No active WRK item found. Documenting general session state."
  WRK_ID="general"
fi
```

If `WRK_ID` is a real ID (not "general"), locate the WRK file:

```bash
WRK_FILE=$(find .claude/work-queue/ -name "${WRK_ID}.md" 2>/dev/null | head -1)
if [[ -z "$WRK_FILE" ]]; then
  WRK_FILE=$(find .claude/work-queue/ -name "${WRK_ID}-*.md" 2>/dev/null | head -1)
fi
```
