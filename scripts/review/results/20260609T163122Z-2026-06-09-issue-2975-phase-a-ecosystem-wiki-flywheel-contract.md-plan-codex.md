### Verdict: MINOR

### Summary
The Phase A plan is mostly approval-ready: it is bounded, uses attested file/issue evidence correctly, splits validator behavior into #3013, and has a focused TDD surface. I found no P1/P2 blockers, but one artifact-evidence gap should be tightened before treating this as a clean reviewed plan.

### Issues Found
- [P3] Minor: The plan header cites fresh r1 review artifact paths under `scripts/review/results/20260609T162507Z-...`, but the attested evidence only verifies the older `20260609T160108Z-...` artifacts. The plan also says “fresh r2 required after repair,” so this is not an approval blocker, but the artifact map/status should avoid implying those cited r1 files are verified unless they are attested or otherwise checked.

### Suggestions
- Add the exact final r2 artifact paths and verdicts only after the repaired plan is re-reviewed, or mark the current `20260609T162507Z-*` paths as pending/unverified in the header.
- Keep the Phase A/Phase B boundary explicit during implementation: no validator, generated-bundle fixture validation, legal attestation rehashing, wrapper gate, public projection enforcement, hook, or CI wiring in #2975 Phase A.

### Questions for Author
- Will the final r2 dispatch attestation include the repaired review artifact paths so the issue can move to `status:plan-review` without artifact-authority ambiguity?
