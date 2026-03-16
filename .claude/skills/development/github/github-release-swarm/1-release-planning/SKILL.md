---
name: github-release-swarm-1-release-planning
description: 'Sub-skill of github-release-swarm: 1. Release Planning (+4).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Release Planning (+4)

## 1. Release Planning


```bash
# Get commit history since last release
LAST_TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName')
COMMITS=$(gh api repos/owner/repo/compare/${LAST_TAG}...HEAD --jq '.commits')

# Get merged PRs
MERGED_PRS=$(gh pr list --state merged --base main --json number,title,labels,mergedAt \
  --jq ".[] | select(.mergedAt > \"$(gh release view $LAST_TAG --json publishedAt -q .publishedAt)\")")

# Plan release with commit analysis

*See sub-skills for full details.*

## 2. Generate Changelog


```bash
# Get all merged PRs between versions
PRS=$(gh pr list --state merged --base main --json number,title,labels,author,mergedAt \
  --jq ".[] | select(.mergedAt > \"$(gh release view v1.0.0 --json publishedAt -q .publishedAt)\")")

# Get contributors
CONTRIBUTORS=$(echo "$PRS" | jq -r '[.author.login] | unique | join(", ")')

# Get commit messages
COMMITS=$(gh api repos/owner/repo/compare/v1.0.0...HEAD --jq '.commits[].commit.message')

*See sub-skills for full details.*

## 3. Create Release with Assets


```bash
# Generate changelog from PRs and commits
CHANGELOG=$(gh api repos/owner/repo/compare/${LAST_TAG}...HEAD \
  --jq '.commits[].commit.message' | \
  npx ruv-swarm github generate-changelog)

# Create release draft
gh release create v2.0.0 \
  --draft \
  --title "Release v2.0.0" \

*See sub-skills for full details.*

## 4. Initialize Release Swarm


```javascript
// Initialize release swarm

// Orchestrate release
    task: "Complete release v2.0.0 with changelog, build, test, and deploy",
    strategy: "sequential",
    priority: "critical"
})
```

## 5. Multi-Repo Release


```bash
# Coordinate releases across repos
REPOS=("frontend:v2.0.0" "backend:v2.1.0" "cli:v1.5.0")

for entry in "${REPOS[@]}"; do
  IFS=':' read -r repo version <<< "$entry"

  # Create release in each repo
  gh release create "$version" \
    --repo "org/$repo" \

*See sub-skills for full details.*
