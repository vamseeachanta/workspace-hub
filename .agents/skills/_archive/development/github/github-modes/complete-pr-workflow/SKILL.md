---
name: github-modes-complete-pr-workflow
description: 'Sub-skill of github-modes: Complete PR Workflow.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Complete PR Workflow

## Complete PR Workflow


```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: Add new feature"
git push -u origin feature/new-feature

# 3. Create PR with full metadata
gh pr create \
  --title "feat: Add new feature" \
  --body "## Summary
- Implements feature X
- Adds tests for Y
