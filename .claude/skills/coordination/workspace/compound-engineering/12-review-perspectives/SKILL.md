---
name: compound-engineering-12-review-perspectives
description: 'Sub-skill of compound-engineering: 12 Review Perspectives (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 12 Review Perspectives (+3)

## 12 Review Perspectives


| # | Perspective | Focus Area |
|---|-------------|------------|
| 1 | Security | OWASP top 10, injection, auth, secrets exposure |
| 2 | Performance | Time complexity, memory usage, N+1 queries, caching |
| 3 | Correctness | Logic errors, off-by-one, null handling, edge cases |
| 4 | Maintainability | Readability, naming, complexity, single responsibility |
| 5 | Testability | Coverage gaps, untested paths, test quality |
| 6 | Scalability | Bottlenecks, horizontal scaling, data growth |
| 7 | Accessibility | WCAG compliance, screen readers, keyboard navigation |
| 8 | Error Handling | Missing catches, error messages, recovery paths |
| 9 | Dependencies | Version risks, license issues, unnecessary additions |
| 10 | Consistency | Style match, pattern adherence, convention compliance |
| 11 | Documentation | Missing docs, outdated comments, API documentation |
| 12 | Deployment | Migration needs, feature flags, rollback safety |


## Parallel Review Execution


```
For each perspective (all 12 in parallel):
  Delegate: Task(subagent_type=general-purpose)
  - Read the diff/changed files
  - Evaluate ONLY from assigned perspective
  - Output: structured findings as JSON
    {
      "perspective": "<name>",
      "severity": "critical|warning|info",
      "findings": [
        {
          "file": "<path>",
          "line": <number>,
          "issue": "<description>",
          "suggestion": "<fix>",
          "severity": "critical|warning|info"
        }
      ],
      "verdict": "pass|conditional|fail"
    }
```


## Review Aggregation


After all 12 reviewers complete:

```
Delegate: core-reviewer (via Task)
- Collect all 12 perspective reports
- Deduplicate overlapping findings
- Prioritize by severity (critical > warning > info)
- Generate unified review report
- Output: .claude/compound-reviews/<session-id>.md
- Decision: pass (proceed) | fix (iterate work phase) | redesign (back to plan)
```


## Review Verdicts


| Verdict | Action |
|---------|--------|
| All pass | Proceed to Compound phase |
| Any conditional, no critical | Fix issues, re-review affected perspectives only |
| Any critical | Return to Work phase; if architectural → return to Plan phase |
