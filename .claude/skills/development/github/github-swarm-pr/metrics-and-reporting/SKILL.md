---
name: github-swarm-pr-metrics-and-reporting
description: 'Sub-skill of github-swarm-pr: Metrics and Reporting.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Metrics and Reporting

## Metrics and Reporting


```bash
# Generate PR swarm report
generate_report() {
  local PR_NUM=$1

  gh pr view $PR_NUM --json \
    title,additions,deletions,reviews,comments,createdAt,updatedAt | \
  jq '{
    title: .title,
    size: (.additions + .deletions),
    reviews: (.reviews | length),
    comments: (.comments | length),
    age_hours: ((now - (.createdAt | fromdateiso8601)) / 3600 | floor)
  }'
}

generate_report 123
```
