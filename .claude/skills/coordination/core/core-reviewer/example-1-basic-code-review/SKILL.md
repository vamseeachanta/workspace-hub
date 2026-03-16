---
name: core-reviewer-example-1-basic-code-review
description: 'Sub-skill of core-reviewer: Example 1: Basic Code Review (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Example 1: Basic Code Review (+1)

## Example 1: Basic Code Review


```javascript
// Spawn reviewer for PR review
Task("Reviewer", "Review PR #123 for security and code quality", "reviewer")

// Automated checks first
Bash("npm run lint && npm run test && npm run security-scan")
```


## Example 2: Security Audit


```javascript
// Deep security review
Task("Security Reviewer", "Audit authentication module for vulnerabilities", "reviewer")

// Use analysis tools
  repo: "current",
  analysis_type: "security"
}
```
