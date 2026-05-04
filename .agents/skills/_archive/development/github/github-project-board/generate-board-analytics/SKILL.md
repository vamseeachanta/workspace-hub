---
name: github-project-board-generate-board-analytics
description: 'Sub-skill of github-project-board: Generate Board Analytics.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Generate Board Analytics

## Generate Board Analytics


```bash
# Collect metrics
METRICS=$(gh project item-list $PROJECT_NUM --owner @me --format json | jq '{
  total_items: .items | length,
  by_status: .items | group_by(.status) | map({status: .[0].status, count: length}),
  by_assignee: .items | group_by(.assignee) | map({assignee: .[0].assignee, count: length}),
  avg_cycle_time: "5.2 days"
}')

# Create analytics report
cat << EOF > sprint-report.md
# Sprint Analytics Report
