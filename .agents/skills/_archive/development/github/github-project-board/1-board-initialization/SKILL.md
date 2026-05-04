---
name: github-project-board-1-board-initialization
description: 'Sub-skill of github-project-board: 1. Board Initialization (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Board Initialization (+3)

## 1. Board Initialization


```bash
# Create a new project board
gh project create --owner @me --title "Development Board"

# Get the project number
PROJECT_NUM=$(gh project list --owner @me --format json | \
  jq -r '.projects[] | select(.title == "Development Board") | .number')

# Add custom fields for swarm tracking
gh project field-create $PROJECT_NUM --owner @me \
  --name "Swarm Status" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "pending,in_progress,review,completed"

gh project field-create $PROJECT_NUM --owner @me \
  --name "Agent Type" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "coder,tester,analyst,architect,reviewer"

gh project field-create $PROJECT_NUM --owner @me \
  --name "Priority" \
  --data-type "SINGLE_SELECT" \
  --single-select-options "critical,high,medium,low"
```


## 2. Task Synchronization


```bash
# Import issues with specific label to project
gh issue list --label "enhancement" --json number,title,url | \
  jq -r '.[].url' | while read -r url; do
    gh project item-add $PROJECT_NUM --owner @me --url "$url"
  done

# Update item status based on issue state
gh project item-list $PROJECT_NUM --owner @me --format json | \
  jq -r '.items[] | select(.content.type == "Issue") | "\(.id) \(.content.number)"' | \
  while read -r item_id issue_num; do
    STATE=$(gh issue view $issue_num --json state --jq '.state')
    if [ "$STATE" == "CLOSED" ]; then
      gh project item-edit --project-id $PROJECT_ID --id $item_id \
        --field-id $STATUS_FIELD_ID --single-select-option-id $COMPLETED_ID
    fi
  done
```


## 3. Progress Tracking


```bash
# Get project progress summary
gh project item-list $PROJECT_NUM --owner @me --format json | \
  jq '{
    total: .items | length,
    completed: [.items[] | select(.fieldValues[]?.name == "completed")] | length,
    in_progress: [.items[] | select(.fieldValues[]?.name == "in_progress")] | length,
    pending: [.items[] | select(.fieldValues[]?.name == "pending")] | length
  }'

# Post progress comment to tracking issue
PROGRESS=$(gh project item-list $PROJECT_NUM --owner @me --format json | \
  jq -r '"## Sprint Progress\n- Total: \(.items | length)\n- Completed: \([.items[] | select(.status == "Done")] | length)"')

gh issue comment $TRACKING_ISSUE --body "$PROGRESS"
```


## 4. Sprint Management


```bash
# Create sprint milestone
gh api repos/:owner/:repo/milestones \
  -f title="Sprint 24" \
  -f description="Sprint 24 - Jan 6-19, 2026" \
  -f due_on="2026-01-19T23:59:59Z"

# Assign issues to sprint
gh issue edit 123 --milestone "Sprint 24"
gh issue edit 124 --milestone "Sprint 24"

# Get sprint burndown data
gh issue list --milestone "Sprint 24" --state all --json number,state,closedAt,createdAt | \
  jq 'group_by(.state) | map({state: .[0].state, count: length})'
```
