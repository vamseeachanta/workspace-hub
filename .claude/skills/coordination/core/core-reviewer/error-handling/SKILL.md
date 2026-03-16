---
name: core-reviewer-error-handling
description: 'Sub-skill of core-reviewer: Error Handling.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


| Issue Category | Example | Action |
|----------------|---------|--------|
| Critical Security | SQL injection | Block merge, immediate fix |
| Performance Bug | N+1 queries | Require fix before merge |
| Style Issue | Naming convention | Suggest change, allow merge |
| Documentation Gap | Missing JSDoc | Request update |
