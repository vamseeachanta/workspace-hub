### Verdict: MAJOR

### Summary
The plan is well-evidenced and substantially tighter than a typical CI-remediation spec, but it still leaves two important governance/testing gaps that can produce a merged fix without a clean audit trail or any replacement coverage for the NPV path being skipped. Those gaps should be closed before approval.

### Issues Found
- [P2] Important: Cluster A allows a temporary diagnostic CI change to distinguish A1a vs A1b, but the plan never requires that diagnostic to be removed from the final branch/PR or recorded as non-mergeable. That creates scope and audit risk: the execution branch can accumulate workflow-only debug noise that is unrelated to the final fix.
- [P2] Important: Cluster C's default close path is skip-based, yet the plan does not require any replacement smoke verification against the current financial-module API before closure. As written, the issue can be closed after suppressing legacy failures even if the refactored NPV path is still untested in CI, which is a meaningful testing-completeness gap.
- [P3] Minor: The full-suite run is marked observational, but the plan does not define a crisp rule for when newly surfaced failures in the same touched benchmark/NPV area remain in-scope versus being spun out as follow-ups. That leaves closure criteria vulnerable to judgment calls during execution.

### Suggestions
- Add an explicit requirement that any temporary diagnostic workflow edit used for Cluster A must be removed before merge, with the deciding CI evidence copied into execution notes or the PR body.
- If Cluster C stays on the skip path, require at least one bounded smoke check against the currently supported financial-module entry point once it is identified, or explicitly state that no such API exists yet and elevate that as a tracked blocker rather than silent deferral.
- Define an in-scope boundary rule for residual failures: failures in untouched areas may be follow-ups, but any new failure in the edited benchmark/NPV paths or caused by the workflow/test changes blocks closure.

### Questions for Author
- If A0b needs a temporary diagnostic CI commit, do you want that treated as a non-mergeable investigation commit that must be dropped before the final PR?
- For Cluster C, is the intent truly 'CI unblock only,' or do you want a minimum supported-path NPV smoke test before allowing the legacy tests to be skipped and the issue closed?
