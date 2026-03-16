---
name: skill-learner-1-commit-analysis
description: 'Sub-skill of skill-learner: 1. Commit Analysis.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Commit Analysis

## 1. Commit Analysis


**Analyzes Last Commit:**
```bash
# Extract commit metadata
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
COMMIT_AUTHOR=$(git log -1 --pretty=%an)
COMMIT_DATE=$(git log -1 --pretty=%ai)

# Get changed files
git diff-tree --no-commit-id --name-only -r HEAD

*See sub-skills for full details.*
