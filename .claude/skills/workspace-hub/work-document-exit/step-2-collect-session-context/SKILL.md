---
name: work-document-exit-step-2-collect-session-context
description: "Sub-skill of work-document-exit: Step 2 \u2014 Collect Session Context."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 2 — Collect Session Context

## Step 2 — Collect Session Context


Gather the raw material for the handoff note. Run these commands and store results:

```bash
# Files changed since last commit (staged + unstaged)
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null)
STAGED_FILES=$(git diff --name-only --cached 2>/dev/null)

# Combined unique list
ALL_CHANGED=$(printf '%s\n%s\n' "$CHANGED_FILES" "$STAGED_FILES" \
  | sort -u | grep -v '^$')

# Last 5 commits on this branch for context
RECENT_COMMITS=$(git log --oneline -5 2>/dev/null)

# Current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

# Session date
SESSION_DATE=$(date -u +"%Y-%m-%d")
SESSION_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```
