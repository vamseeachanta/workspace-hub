### Verdict: APPROVE

### Summary
The plan is exceptionally detailed, well-structured, and provides clear, conditional execution paths for each of the three test failure clusters. It effectively bounds the scope, explicitly deferring unrelated test failures and outlining rigorous pre- and post-implementation verification steps.

### Issues Found
- [P3] Minor: The plan relies heavily on manual verification of CI logs (e.g., `gh run view`) to determine the root cause of the benchmark fixture issue, which could be error-prone if logs are truncated or expired.
- [P3] Minor: The conditional logic for Cluster B (fixture promotion) depends on the outcome of Cluster C (legacy API skip), which might complicate the execution flow if not tracked carefully.

### Suggestions
- Consider adding a fallback script to automatically parse and verify the CI logs for the missing benchmark fixture to reduce manual error.
- Ensure that the tracker issue created for Cluster C clearly references the removed code paths so the module owner has full context for re-implementation.

### Questions for Author
- If the runner `uv` version does not support `--all-groups` or `--group benchmark`, what is the exact fallback command to ensure `pytest-benchmark` is installed?
- Is there a specific timeline or milestone for when the module owner is expected to address the deferred legacy NPV tests (Cluster C)?
