---
name: github-modes-5-repo-architect
description: 'Sub-skill of github-modes: 5. repo-architect (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 5. repo-architect (+2)

## 5. repo-architect


**Repository structure and organization**

```bash
# Create repository
gh repo create my-project --public --description "Project description"

# Clone with specific options
gh repo clone owner/repo -- --depth=1

# Fork repository

*See sub-skills for full details.*

## 6. code-reviewer


**Automated code review and quality assurance**

```bash
# Get PR diff
gh pr diff 123

# Get changed files
gh pr view 123 --json files --jq '.files[].path'

# Add review comment

*See sub-skills for full details.*

## 7. branch-manager


**Branch management and workflow coordination**

```bash
# Create feature branch via API
gh api repos/:owner/:repo/git/refs \
  -f ref='refs/heads/feature/new-feature' \
  -f sha=$(gh api repos/:owner/:repo/git/refs/heads/main --jq '.object.sha')

# Delete branch
gh api repos/:owner/:repo/git/refs/heads/old-branch --method DELETE

*See sub-skills for full details.*
