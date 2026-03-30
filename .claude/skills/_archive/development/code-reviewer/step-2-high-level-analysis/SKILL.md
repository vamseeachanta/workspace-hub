---
name: code-reviewer-step-2-high-level-analysis
description: 'Sub-skill of code-reviewer: Step 2: High-Level Analysis (+4).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Step 2: High-Level Analysis (+4)

## Step 2: High-Level Analysis


Scan for:
- Overall change scope
- Architectural impact
- Breaking changes
- New dependencies

## Step 3: Detailed Review


For each file:

```markdown

## [filename]


**Changes:** [summary]

**Findings:**
- [severity] [category]: [description]
  - Location: line X
  - Recommendation: [action]
```

## Step 4: Security Deep Dive


Special attention to:
- Authentication flows
- Data handling
- API endpoints
- Configuration files
- Environment variables

## Step 5: Test Verification


- Run existing tests
- Verify new test coverage
- Check test quality
- Identify missing tests
