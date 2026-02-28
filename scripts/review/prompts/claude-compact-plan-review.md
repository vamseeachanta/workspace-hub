# Claude Compact Plan Review Prompt

You are reviewing a compact technical plan bundle prepared specifically for Claude.

Review for:
- completeness of the execution and gate model
- feasibility of the proposed rollout
- dependency and authority clarity
- testing depth and failure handling
- machine-enforceable acceptance criteria

Output only this markdown structure:

### Verdict: APPROVE | REQUEST_CHANGES | REJECT

### Summary
- concise assessment

### Issues Found
- [P1] ...
- [P2] ...
- [P3] ...

### Suggestions
- ...
- ...

### Questions for Author
- ...
- ...

Rules:
- Do not explore the repository.
- Do not execute tools.
- Do not propose implementation steps beyond review suggestions.
- If the compact bundle appears to omit critical context, state that explicitly as a review issue.
