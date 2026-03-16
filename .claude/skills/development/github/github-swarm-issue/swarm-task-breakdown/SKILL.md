---
name: github-swarm-issue-swarm-task-breakdown
description: 'Sub-skill of github-swarm-issue: Swarm Task Breakdown.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Swarm Task Breakdown

## Swarm Task Breakdown


$SUBTASK_LIST

---
Decomposed by Swarm Agent"

gh issue edit 456 --body "$UPDATED_BODY"

# Create linked issues for major subtasks
gh issue create \
  --title "Subtask: Implement authentication" \
  --body "Part of #456
