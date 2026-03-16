---
name: github-swarm-pr-github-actions-integration
description: 'Sub-skill of github-swarm-pr: GitHub Actions Integration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# GitHub Actions Integration

## GitHub Actions Integration


```yaml
# .github/workflows/swarm-pr.yml
name: Swarm PR Handler
on:
  pull_request:
    types: [opened, labeled, synchronize]
  issue_comment:
    types: [created]

jobs:
  swarm-review:
    if: contains(github.event.pull_request.labels.*.name, 'swarm-review')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Analyze PR
        id: analyze
        run: |
          CHANGES=$(git diff --stat HEAD~1 | tail -1)
          echo "changes=$CHANGES" >> $GITHUB_OUTPUT

      - name: Post Swarm Analysis
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

*See sub-skills for full details.*
