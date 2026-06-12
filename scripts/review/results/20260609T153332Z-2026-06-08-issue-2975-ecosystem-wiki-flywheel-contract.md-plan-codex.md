### Verdict: MAJOR

### Summary
REQUEST_CHANGES. The plan is substantially improved and covers most prior schema, routing, enum, legal-scan, and validator-scope concerns, but it is not approval-ready because its evidence integrity and TDD/acceptance boundaries still contain contradictions.

### Issues Found
- [P1] Critical: The plan’s embedded attestation hash contradicts the authoritative attested evidence in this prompt. The prompt’s live attestation payload is `sha256:f067f63c...`, while the plan claims `5580cda8...` for the same plan/commit family. That makes the review-evidence section stale or copied from a prior run and needs correction before approval.
- [P2] Important: The implementation sequencing still conflicts with the repo’s TDD gate. The plan says Phase A will create the standard, governance decision, config, and templates before Phase B validator tests. Since templates/config are validator inputs and part of the enforced contract, tests should be written first or Phase A should be explicitly limited to non-implementation drafting.
- [P2] Important: The acceptance criteria and blocking-test floor do not fully align. The plan says stale-pointer and scheduler-clean-run requirements are future hardening, but the test inventory includes stale-pointer and two-clean-run tests, while only `test_stale_pointer_uses_reference_time` is in the blocking subset. This leaves unclear which behaviors must pass before #2975 can close.
- [P3] Minor: The plan still carries extensive historical review narrative including prior FAIL/MAJOR state. That is useful provenance, but for an approval-stage artifact it increases stale-review drift risk; the actionable current state should be separated from historical review logs.

### Suggestions
- Regenerate or update the plan’s embedded attestation section so the hash, timestamp, and commit exactly match the current dispatch evidence, or remove the embedded hash and rely on the external `## Attested Evidence` block.
- Revise phase ordering to make tests/fixtures for config, templates, schema composition, projection allowlist, and legal attestation precede validator/config/template implementation, or explicitly mark any pre-test work as draft documentation only.
- Split the test list into `blocking for #2975`, `documented but deferred`, and `follow-up issue required`, then ensure every acceptance criterion maps to one of those buckets without ambiguity.
- Move historical review-wave detail to a referenced artifact and keep the plan body focused on the current approval candidate.

### Questions for Author
- Should `test_broken_wiki_target_fails`, `test_stale_pointer_existing_target_fails`, `test_two_clean_manual_runs_required_before_scheduling`, and `test_clean_run_requires_reviewed_generated_diff` be blocking for #2975, or should they be explicitly assigned to named follow-up issues?
- Was the attestation hash mismatch caused by re-running `attest-plan-claims.sh` after the plan text was embedded in the prompt?
