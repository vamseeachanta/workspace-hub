### Verdict: MAJOR

### Summary
The plan is well researched and mostly executable, but it still has a few specification gaps around skip scope, conditional verification, and the preferred Cluster A branch. Those gaps should be tightened before approval so implementation stays bounded and does not discard useful coverage.

### Issues Found
- [P1] Critical: Cluster C proposes a module-level skip in `test_current_npv_implementation.py` without evidence that the entire file is legacy-only. The plan proves one broken import at line 23, but not that every test in that module should be deferred; approving a whole-file skip on that basis risks hiding unrelated coverage.
- [P2] Important: Cluster B conditionality is not fully carried through the verification section. The plan says fixture promotion is only needed if a remaining non-skipped test still fails after Cluster C handling, but `verify_cashflow_no_duplicate_fixture` and parts of the verification flow still read like the fixture move/removal is expected unconditionally.
- [P2] Important: The preferred Cluster A path (`A1b`) is still underspecified. The plan says to diagnose plugin autoload/environment isolation first, but the actual bounded probes, decision cutoff, and concrete success/failure criteria for that branch are not defined tightly enough, so the executor could drift into open-ended investigation instead of a scoped fix.
- [P3] Minor: The plan requires a worldenergydata follow-up issue when Cluster C uses skip-based deferral, but it does not define whether creating that issue is part of implementation scope, a manual owner action, or a precondition for merge. That governance dependency should be explicit.

### Suggestions
- Add a precondition for Cluster C: inspect `test_current_npv_implementation.py` and explicitly classify each test as legacy-only vs still valuable before allowing a module-level skip; if the file is mixed, use targeted skips instead of a whole-file skip.
- Make the Cluster B verification matrix fully conditional. If B1 is not triggered, remove or mark `verify_cashflow_no_duplicate_fixture` as not applicable so the test list matches the stated decision logic.
- Tighten A1b into a short deterministic branch: specify the exact files/env knobs to inspect, the evidence that confirms plugin-disablement, and the point where the executor must stop and open a follow-up instead of continuing diagnosis.
- State explicitly how the required worldenergydata follow-up issue is created and when: before merge, during implementation, or by the owner as a manual governance step.

### Questions for Author
- Have you verified that `test_current_npv_implementation.py` contains no non-legacy tests that would be lost by a module-level skip?
- For Cluster A1b, what exact signals will distinguish 'autoload/config bug confirmed' from 'investigation exceeded scope, open a follow-up and stop'?
