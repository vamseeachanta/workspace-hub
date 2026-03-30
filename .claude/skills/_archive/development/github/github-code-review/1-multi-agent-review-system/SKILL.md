---
name: github-code-review-1-multi-agent-review-system
description: 'Sub-skill of github-code-review: 1. Multi-Agent Review System (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Multi-Agent Review System (+3)

## 1. Multi-Agent Review System


```bash
# Get PR details
PR_DATA=$(gh pr view 123 --json files,additions,deletions,title,body)
PR_DIFF=$(gh pr diff 123)

# Initialize swarm with PR context
npx ruv-swarm github review-init \
  --pr 123 \
  --pr-data "$PR_DATA" \
  --diff "$PR_DIFF" \

*See sub-skills for full details.*

## 2. Security-Focused Review


```bash
# Get changed files
CHANGED_FILES=$(gh pr view 123 --json files --jq '.files[].path')

# Run security review
SECURITY_RESULTS=$(npx ruv-swarm github review-security \
  --pr 123 \
  --files "$CHANGED_FILES" \
  --check "owasp,cve,secrets,permissions" \
  --suggest-fixes)

*See sub-skills for full details.*

## 3. Initialize Review Swarm


```javascript
// Initialize code review swarm

// Orchestrate parallel review
    task: "Comprehensive code review covering security, performance, style, and architecture",
    strategy: "parallel",
    priority: "high"
})
```

## 4. Post Inline Comments


```bash
# Get diff with context
PR_DIFF=$(gh pr diff 123 --color never)
PR_FILES=$(gh pr view 123 --json files)

# Generate review comments
COMMENTS=$(npx ruv-swarm github review-comment \
  --pr 123 \
  --diff "$PR_DIFF" \
  --files "$PR_FILES" \

*See sub-skills for full details.*
