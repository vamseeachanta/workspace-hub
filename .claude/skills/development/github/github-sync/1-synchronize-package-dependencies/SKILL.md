---
name: github-sync-1-synchronize-package-dependencies
description: 'Sub-skill of github-sync: 1. Synchronize Package Dependencies (+4).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Synchronize Package Dependencies (+4)

## 1. Synchronize Package Dependencies


```bash
# Read current package states
REPO1_PKG=$(gh api repos/org/repo1/contents/package.json --jq '.content' | base64 -d)
REPO2_PKG=$(gh api repos/org/repo2/contents/package.json --jq '.content' | base64 -d)

# Create synchronization branch
gh api repos/org/repo1/git/refs \
  -f ref='refs/heads/sync/deps-alignment' \
  -f sha=$(gh api repos/org/repo1/git/refs/heads/main --jq '.object.sha')


*See sub-skills for full details.*

## 2. Documentation Synchronization


```bash
# Get source documentation
SOURCE_DOC=$(gh api repos/org/primary-repo/contents/CLAUDE.md --jq '.content' | base64 -d)

# Create sync branch on target repo
gh api repos/org/secondary-repo/git/refs \
  -f ref='refs/heads/sync/documentation' \
  -f sha=$(gh api repos/org/secondary-repo/git/refs/heads/main --jq '.object.sha')

# Update target documentation

*See sub-skills for full details.*

## 3. Cross-Package Feature Integration


```bash
# Push multiple files to feature branch
gh api repos/org/monorepo/contents/package-a/src/feature.js \
  --method PUT \
  -f message="feat: Add cross-package feature" \
  -f branch="feature/cross-package" \
  -f content="$(cat feature-a.js | base64)"

gh api repos/org/monorepo/contents/package-b/src/integration.js \
  --method PUT \

*See sub-skills for full details.*

## Changes


- package-a: Core feature implementation
- package-b: Integration hooks

## Testing


- [x] Package dependency verification
- [x] Integration test suite
- [x] Cross-package compatibility"
```
