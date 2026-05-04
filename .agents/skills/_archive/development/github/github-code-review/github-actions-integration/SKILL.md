---
name: github-code-review-github-actions-integration
description: 'Sub-skill of github-code-review: GitHub Actions Integration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# GitHub Actions Integration

## GitHub Actions Integration


```yaml
# .github/workflows/auto-review.yml
name: Automated Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  swarm-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup GitHub CLI
        run: echo "${{ secrets.GITHUB_TOKEN }}" | gh auth login --with-token

      - name: Run Review Swarm
        run: |
          PR_NUM=${{ github.event.pull_request.number }}
          PR_DATA=$(gh pr view $PR_NUM --json files,title,body,labels)

          REVIEW_OUTPUT=$(npx ruv-swarm github review-all \
            --pr $PR_NUM \

*See sub-skills for full details.*
