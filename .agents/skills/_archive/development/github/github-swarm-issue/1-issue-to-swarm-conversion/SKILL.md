---
name: github-swarm-issue-1-issue-to-swarm-conversion
description: 'Sub-skill of github-swarm-issue: 1. Issue-to-Swarm Conversion (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Issue-to-Swarm Conversion (+1)

## 1. Issue-to-Swarm Conversion


```bash
# Get complete issue context
ISSUE=$(gh issue view 456 --json title,body,labels,assignees,comments,projectItems)

# Analyze issue complexity
BODY=$(echo "$ISSUE" | jq -r '.body')
LABEL_COUNT=$(echo "$ISSUE" | jq '.labels | length')
COMMENT_COUNT=$(echo "$ISSUE" | jq '.comments | length')

# Determine swarm topology based on complexity
if [ $LABEL_COUNT -gt 3 ] || [ ${#BODY} -gt 1000 ]; then
  TOPOLOGY="hierarchical"
  MAX_AGENTS=8
elif echo "$BODY" | grep -qE "(\[ \]|1\.|step)" ; then
  TOPOLOGY="mesh"
  MAX_AGENTS=5
else
  TOPOLOGY="ring"
  MAX_AGENTS=3
fi

echo "Issue #456: Using $TOPOLOGY topology with $MAX_AGENTS agents"

# Initialize swarm comment
gh issue comment 456 --body "## Swarm Initialized

**Topology**: $TOPOLOGY
**Agents**: $MAX_AGENTS

Processing issue for task decomposition..."
```


## 2. Task Decomposition


```bash
# Get issue body
ISSUE_BODY=$(gh issue view 456 --json body --jq '.body')

# Extract tasks from issue body (markdown checklist items)
TASKS=$(echo "$ISSUE_BODY" | grep -E '^\s*-\s*\[ \]' | sed 's/.*\[ \]//')

# Create subtask checklist
SUBTASK_LIST=""
TASK_NUM=1
echo "$TASKS" | while read -r task; do
  SUBTASK_LIST+="- [ ] $TASK_NUM. $task\n"
  TASK_NUM=$((TASK_NUM + 1))
done

# Update issue with structured subtasks
UPDATED_BODY="$ISSUE_BODY
