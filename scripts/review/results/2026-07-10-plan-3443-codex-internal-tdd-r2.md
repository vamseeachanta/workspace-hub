# Adversarial plan re-review — #3443 TDD/enforcement

> Reviewer: Codex internal parallel reviewer (Fermat)
> Stage: plan, revision 2
> Verdict: MAJOR
> Provider-diverse gate credit: none; same-provider review only

## Defects found

1. Authorized `SKIP` reduction, review-resolution transition, and numeric exit codes were incomplete.
2. Signed artifacts lacked an external trust root and canonical parser/signature contract.
3. A repository-wide literal bypass ban would block its own implementation and 148 safe tracked references.
4. Secret/check activation did not prove exact remote workflow identity, ref scope, bypass closure, or current candidate binding.
5. Legacy migration covered patterns but not broad legacy exclusions.
6. Proposed commands omitted focused/full/security/distribution/runtime/report verification and missing-tool disposition.

## Required disposition

Revision 3 will add a complete reduction/exit contract, role-separated canonical signed artifacts, semantic executable-surface bypass analysis plus exact fixture allowances, exact ruleset/check identity tests, one-to-one exclusion migration, and executable local/CI verification commands.
