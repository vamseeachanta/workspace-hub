---
name: github-modes-automated-issue-management
description: 'Sub-skill of github-modes: Automated Issue Management.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Automated Issue Management

## Automated Issue Management


```bash
# Triage unlabeled issues
gh issue list --label "" --json number,title | \
  jq -r '.[] | "\(.number): \(.title)"'

# Bulk close stale issues
gh issue list --label "stale" --json number | \
  jq -r '.[].number' | while read num; do
    gh issue close $num --comment "Closing stale issue"
  done

*See sub-skills for full details.*
