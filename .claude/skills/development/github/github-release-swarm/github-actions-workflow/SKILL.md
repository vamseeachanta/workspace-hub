---
name: github-release-swarm-github-actions-workflow
description: 'Sub-skill of github-release-swarm: GitHub Actions Workflow.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# GitHub Actions Workflow

## GitHub Actions Workflow


```yaml
name: Release Workflow
on:
  push:
    tags: ['v*']

jobs:
  release-swarm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup GitHub CLI
        run: echo "${{ secrets.GITHUB_TOKEN }}" | gh auth login --with-token

      - name: Initialize Release Swarm
        run: |
          RELEASE_TAG=${{ github.ref_name }}
          PREV_TAG=$(gh release list --limit 2 --json tagName -q '.[1].tagName')

          PRS=$(gh pr list --state merged --base main --json number,title,labels,author \
            --search "merged:>=$(gh release view $PREV_TAG --json publishedAt -q .publishedAt)")


*See sub-skills for full details.*
