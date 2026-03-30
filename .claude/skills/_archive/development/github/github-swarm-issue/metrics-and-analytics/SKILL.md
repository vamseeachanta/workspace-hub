---
name: github-swarm-issue-metrics-and-analytics
description: 'Sub-skill of github-swarm-issue: Metrics and Analytics.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Metrics and Analytics

## Metrics and Analytics


```bash
# Issue resolution metrics
generate_metrics() {
  # Get closed issues from last 30 days
  gh issue list --state closed --json number,title,createdAt,closedAt,labels | \
    jq '{
      total_closed: length,
      avg_resolution_days: ([.[].createdAt, .[].closedAt] | map(fromdateiso8601) | . as $dates | (($dates[1] - $dates[0]) / 86400)) | add / length,
      by_label: group_by(.labels[].name) | map({label: .[0].labels[0].name, count: length})
    }'
}

generate_metrics
```
