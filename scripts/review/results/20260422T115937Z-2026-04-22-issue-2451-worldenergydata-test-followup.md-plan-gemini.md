### Verdict: APPROVE

### Summary
The plan is highly comprehensive, methodically addressing the three test failure clusters while prioritizing root-cause diagnosis over blind fixes. It establishes clear boundaries for scope, requires concrete evidence before execution, and appropriately defers complex legacy API restoration to a tracked follow-up.

### Issues Found
- None.

### Suggestions
- Ensure the follow-up issue for the legacy NPV tests is created as soon as possible to prevent the conditionally skipped tests from being forgotten.
- Consider providing a small helper script to parse the CI logs using the GitHub CLI to reduce human error during the manual diagnosis step for Cluster A.

### Questions for Author
- If issue creation is unavailable during the execution phase and only a code comment is left, what is the process to ensure the follow-up tracker is eventually created?
