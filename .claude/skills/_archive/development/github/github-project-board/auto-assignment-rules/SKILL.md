---
name: github-project-board-auto-assignment-rules
description: 'Sub-skill of github-project-board: Auto-Assignment Rules (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Auto-Assignment Rules (+1)

## Auto-Assignment Rules


```bash
# Assign cards based on labels
gh project item-list $PROJECT_NUM --owner @me --format json | \
  jq -r '.items[] | select(.content.labels[]?.name == "frontend") | .id' | \
  while read -r item_id; do
    # Update assignment field
    gh project item-edit --project-id $PROJECT_ID --id $item_id \
      --field-id $ASSIGNEE_FIELD_ID --text "frontend-team"
  done
```

## Smart Card Movement


```bash
# Auto-move cards when PR is merged
gh pr list --state merged --json number,headRefName | \
  jq -r '.[] | select(.headRefName | startswith("feature/")) | .number' | \
  while read -r pr_num; do
    # Find linked issue and update project card
    ISSUE=$(gh pr view $pr_num --json body --jq '.body' | grep -oE '#[0-9]+' | head -1)
    if [ -n "$ISSUE" ]; then
      # Update card status to Done
      echo "Moving card for issue $ISSUE to Done"
    fi
  done
```
