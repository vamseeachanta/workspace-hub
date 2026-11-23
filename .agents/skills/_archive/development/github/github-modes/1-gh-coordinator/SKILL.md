---
name: github-modes-1-gh-coordinator
description: 'Sub-skill of github-modes: 1. gh-coordinator (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. gh-coordinator (+3)

## 1. gh-coordinator


**GitHub workflow orchestration and coordination**

```bash
# Coordinate multiple GitHub operations
gh issue create --title "Feature: New Integration" --body "Description here"
gh pr create --title "Implement feature" --body "Closes #123"
gh workflow run ci.yml
```

- **Coordination Mode**: Hierarchical
- **Max Parallel Operations**: 10
- **Best For**: Complex GitHub workflows, multi-repo coordination

## 2. pr-manager


**Pull request management and review coordination**

```bash
# Create PR with reviewers
gh pr create \
  --title "Feature implementation" \
  --body "## Summary\n- Feature 1\n- Feature 2" \
  --reviewer user1,user2 \
  --assignee @me


*See sub-skills for full details.*

## 3. issue-tracker


**Issue management and project coordination**

```bash
# Create structured issue
gh issue create \
  --title "Bug: Login failure" \
  --body "## Description\n...\n## Steps to Reproduce\n1. ..." \
  --label "bug,priority:high" \
  --assignee @me \
  --milestone "v2.0"

*See sub-skills for full details.*

## 4. release-manager


**Release coordination and deployment**

```bash
# Create release
gh release create v1.2.0 \
  --title "Release v1.2.0" \
  --notes "## What's New\n- Feature 1\n- Bug fix 2" \
  --target main

# Upload release assets

*See sub-skills for full details.*
