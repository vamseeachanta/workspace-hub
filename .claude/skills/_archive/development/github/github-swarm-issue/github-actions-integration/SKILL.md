---
name: github-swarm-issue-github-actions-integration
description: 'Sub-skill of github-swarm-issue: GitHub Actions Integration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# GitHub Actions Integration

## GitHub Actions Integration


```yaml
# .github/workflows/issue-swarm.yml
name: Issue Swarm Handler
on:
  issues:
    types: [opened, labeled]
  issue_comment:
    types: [created]

jobs:
  process-new-issue:
    if: github.event.action == 'opened'
    runs-on: ubuntu-latest
    steps:
      - name: Auto-Triage Issue
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          TITLE="${{ github.event.issue.title }}"
          BODY="${{ github.event.issue.body }}"

          # Determine labels based on content
          LABELS=""
          if echo "$TITLE $BODY" | grep -qiE "bug|error"; then
            LABELS="bug"

*See sub-skills for full details.*
