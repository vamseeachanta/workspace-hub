# Focused adversarial re-review synthesis — #2760 OCIMF source/provenance patch

- **Date:** 2026-05-20
- **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2760
- **Plan:** `docs/plans/2026-05-20-issue-2760-b1528-sirocco-force-review-revision.md`
- **Scope:** Re-review after patching the plan to replace the unresolved `ocimf_coefficients_production.csv` blocker with the licensed off-repo workbook/provenance route and explicit SIROCCO generic/reference limitation.

## Reviewer results

| Reviewer lane | Verdict | Blocking findings |
|---|---:|---|
| Focused source/provenance reviewer | APPROVE | None |
| Licensing/provenance/calc-citation reviewer | APPROVE | None |
| Implementation-readiness/TDD reviewer | MINOR | None |

## Findings incorporated after review

The MINOR lane recommended strengthening non-blocking details. The plan was patched to add:

1. `test_issue_2760_ocimf_no_coefficient_corpus_leakage` to enforce that repo-bound artifacts do not serialize a reusable OCIMF coefficient corpus unless license approval is recorded.
2. `test_issue_2760_citation_sidecars_resolve` to verify successful OCIMF/rudder sidecar resolution, not only missing-source failure.
3. Generic OCIMF class-selection tie-break rule: prefer conservative larger-magnitude force/moment envelope and record rejected alternatives; stop if required geometry inputs are unavailable.
4. Rudder area/drag fallback criterion: allowed only when `rudder_normal_force` cannot represent the B1528 rudder geometry/input set or cannot provide a citation-compatible coefficient basis; record reason in manifest and issue thread before report generation.

## Synthesis verdict

**APPROVE for remaining in `status:plan-review` pending explicit user approval.**

No implementation may begin until the user explicitly approves the plan and the issue is moved to `status:plan-approved`.

The plan now adequately handles:

- Licensed off-repo OCIMF source route: `/mnt/ace/acma-codes/OCIMF/OCIMF Coef.xlsx`.
- No committed workbook/PDFs/extracted coefficient corpora by default.
- Citation target identity and fail-closed sidecar requirements.
- Generic/reference OCIMF tanker-current limitation for B1528 SIROCCO.
- TDD coverage for placeholder removal, source/citation gates, corpus-leakage prevention, sign/oracle checks, and output contract.

Residual implementation risk remains intentional: if the workbook, citation target, license-safe coefficient access path, or rudder citation cannot be verified during Phase 0, implementation stops and returns to the issue thread rather than producing report numbers.
