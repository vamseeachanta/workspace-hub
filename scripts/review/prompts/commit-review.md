# Commit Review Prompt

You are reviewing a git commit (or set of commits) before they are pushed. Evaluate:

## Review Criteria

1. **Commit message**: Does it follow conventional commits format? Is it descriptive?
2. **Scope**: Is the commit focused on a single concern? Should it be split?
3. **Completeness**: Are all related changes included? Are there missing files?
4. **Reversibility**: Can this commit be safely reverted if needed?
5. **Breaking changes**: Does this introduce breaking changes? Are they documented?
6. **Secrets**: Are there any hardcoded secrets, API keys, or credentials?

## Output Format

### Verdict: APPROVE | REQUEST_CHANGES | REJECT

### Summary
[1-3 sentence assessment]

### Issues Found
- [P1] Critical: [description]
- [P2] Important: [description]

### Commit Message Suggestion
[improved commit message if needed]
