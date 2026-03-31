# Plan Review Prompt

You are reviewing a technical plan/specification for a software engineering project. Evaluate the following aspects:

## Review Criteria

1. **Completeness**: Are all requirements addressed? Are there missing acceptance criteria?
2. **Feasibility**: Is the proposed approach technically sound? Are there hidden complexities?
3. **Dependencies**: Are all dependencies identified? Are there circular or missing dependencies?
4. **Risk**: What are the top 3 risks? Are mitigation strategies adequate?
5. **Scope**: Is the scope well-defined? Is there scope creep risk?
6. **Testing**: Is the test strategy adequate? Are edge cases considered?

## Output Format

Provide your review as:

### Verdict: APPROVE | REQUEST_CHANGES | REJECT

### Summary
[1-3 sentence overall assessment]

### Issues Found
- [P1] Critical: [issue description]
- [P2] Important: [issue description]
- [P3] Minor: [issue description]

### Suggestions
- [suggestion 1]
- [suggestion 2]

### Questions for Author
- [question 1]
- [question 2]
