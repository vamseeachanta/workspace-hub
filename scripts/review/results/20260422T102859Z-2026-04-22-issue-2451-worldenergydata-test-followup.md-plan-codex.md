### Verdict: MAJOR

### Summary
The plan is well-evidenced and materially improved, but it still has two execution-contract gaps: its preferred Cluster A path is investigative rather than implementable, and the deliverable text still permits a partial outcome that conflicts with the issue’s stated remediation target. Tightening those points would make the plan actionable and testable.

### Issues Found
- [P1] Cluster A's preferred path (A1b) is not a complete implementation plan. The plan correctly avoids assuming a CI install bug, but if plugin autoload/environment isolation is the real cause, it does not define the bounded next actions, candidate files/config to inspect, or the decision point for 'stop and re-plan' versus 'fix in this issue'. A preferred path that is only 'diagnose first' is not sufficiently executable for plan approval.
- [P2] The Deliverable section is weaker than the Acceptance Criteria. It allows success to mean a 'materially reduced residual failure count' with follow-up issues, which could be read as resolving fewer than all three named #2451 clusters. Later acceptance criteria require all three failure signatures to be gone. Those two contracts should match.
- [P2] The default Cluster C skip path requires a follow-up owner/issue in the risk section, but that tracking artifact is not made explicit in Files to Change, TDD checks, or Acceptance Criteria. If coverage is intentionally reduced, the plan should require creation or linkage of the re-enable/delete follow-up so the skip does not become permanent drift.
- [P3] The testing section is strong on pytest verification, but it does not explicitly verify the workflow-flag branch for A1a against the runner toolchain before editing `ci.yml` (for example, confirming supported `uv sync` flags in the CI environment). The risk is noted, but the verification contract should include it directly.

### Suggestions
- Convert A1b into an explicit conditional branch with concrete inspection targets and an end state: either list the pytest/plugin config surfaces to audit and the exact acceptance for a fix, or state that confirming A1b blocks implementation and requires a revised plan.
- Rewrite the Deliverable section so it matches the acceptance contract: success means the three #2451 signatures are eliminated from the `Test` job, while unrelated residual failures may remain only if separately enumerated.
- If C-skip remains the default, add an explicit acceptance item and implementation artifact for the follow-up tracker that will own re-enablement or deletion of the legacy NPV tests.
- Add a verification step for A1a that proves the chosen `uv sync` flag is supported by the CI runner/tooling before committing the workflow change.

### Questions for Author
- If A1b is confirmed, what exact files/settings are in scope for investigation and fix under #2451, and at what point would you stop and re-plan instead of continuing implementation?
- Should the plan require creation/linkage of a concrete follow-up issue when Cluster C uses skips, so the temporary coverage loss is governed rather than implied?
