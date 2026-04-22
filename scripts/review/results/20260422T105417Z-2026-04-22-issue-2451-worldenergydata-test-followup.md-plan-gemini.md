### Verdict: APPROVE

### Summary
The plan is comprehensive, well-structured, and explicitly bounds its scope to the three identified test failure clusters. It correctly identifies dependencies, sets up clear conditional logic for remediation, and includes a solid TDD verification strategy.

### Issues Found
- None.

### Suggestions
- Verify if `uv sync --all-groups` is fully supported by the GitHub actions runner environment before relying on it.
- Ensure the follow-up issue for legacy NPV tests is created immediately upon plan approval to avoid losing track of the skipped coverage.

### Questions for Author
- Has the module owner been consulted yet regarding the preference for C-skip vs C-repoint?
- Is there a mechanism in place to ensure the `docs/plans/README.md` is updated in the subsequent consolidation run as planned?
