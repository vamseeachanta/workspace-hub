---
name: github-release-manager-1-coordinated-release-preparation
description: 'Sub-skill of github-release-manager: 1. Coordinated Release Preparation
  (+7).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Coordinated Release Preparation (+7)

## 1. Coordinated Release Preparation


```javascript
// Initialize release management swarm

// Orchestrate release preparation
    task: "Prepare release v1.0.72 with comprehensive testing and validation",
    strategy: "sequential",
    priority: "critical"
})
```

## 2. Create Release with gh CLI


```bash
# Create release branch
git checkout -b release/v1.0.72 main

# Get commits since last release
LAST_TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName')
COMMITS=$(gh api repos/owner/repo/compare/${LAST_TAG}...HEAD --jq '.commits[].commit.message')

# Generate changelog
echo "$COMMITS" > CHANGELOG_DRAFT.md

*See sub-skills for full details.*

## 3. Multi-Package Version Coordination


```bash
# Update package versions
cd ../ruv-swarm && npm version 1.0.12 --no-git-tag-version

# Run tests for all packages
npm test --workspaces

# Create coordinated release PR
gh pr create \
  --title "Release v1.0.72: GitHub Integration and Swarm Enhancements" \
  --head release/v1.0.72 \
  --base main \
  --body "## Release v1.0.72

## Package Updates


- **ruv-swarm**: v1.0.11 -> v1.0.12

## Changes


- GitHub workflow integration
- Enhanced swarm coordination
- Advanced MCP tools integration

## Validation


- [x] Unit tests passing
- [x] Integration tests: 89% success
- [x] Build verification successful"
```

## 4. Automated Release Validation


```bash
# Run comprehensive validation
npm install && npm test && npm run lint && npm run build

# Security audit
npm audit

# Create validation report
gh issue create \
  --title "Release Validation: v1.0.72" \

*See sub-skills for full details.*

## 5. Batch Release Workflow


```javascript
[Single Message - Complete Release Management]:
    // Initialize comprehensive release swarm

    // Create release branch
    Bash("git checkout -b release/v1.0.72 main")

    // Run comprehensive validation
    Bash("npm install && npm test && npm run lint && npm run build")


*See sub-skills for full details.*
