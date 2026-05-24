# Codex Re-Review — Issue #2747

Verdict: MINOR

MAJOR findings: None found from the supplied current diff. The prior blocker classes appear materially addressed: boolean gate/allowance validation, nonblank identity/provenance validation, public gate fail-closed behavior, score-vs-approval separation, and revision-lineage shape/version checks are all covered by targeted tests.

MINOR findings:
- `docs/reports/issue-2747-implementation-notes.html` is stale: it says `44 tests` / `44 passed`, while the current target reports `75 passed`. Not a closure blocker, but it is misleading closeout evidence.
- Add one direct regression for invalid allowance booleans through the readiness path: e.g. high score + true clearance gates + `private_wiki_allowed: "true"` should not classify `client-ready` unless callers always validate first. Existing tests validate rejection of bad allowance values, and test classifier rejection of truthy gate strings, but not truthy allowance strings.

Tests meaningfully cover the prior bypass paths. No client-private/public leakage issue is visible in the diff; examples use placeholders/ACME-style fake data, and public output gating requires reviewer, legal, sanitization, public release clearance, and rationale.

Review caveat: the supplied `promotion_ledger.py` diff is truncated and the local sandbox blocked file reads, so this re-review is based on the provided patch text and visible test coverage.
