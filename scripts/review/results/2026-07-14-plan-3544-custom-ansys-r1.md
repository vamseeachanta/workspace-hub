# Adversarial plan review: issue #3544 — custom_ansys_runners R1

- Date: 2026-07-14
- Reviewer lane: `custom_ansys_runners`
- Reviewed commit: `9296f13bbf7bbd619718e19d1e1ebe67ddb71fe8`
- Verdict: **MAJOR**

## Findings

1. Variant A did not require the second collaborator in relevant base-branch
   CODEOWNERS rows or define an exact author/reviewer matrix.
2. The proof PR omitted the draft-to-ready transition.
3. The caller was absent from Files to Change and the two-commit A/B topology,
   caller pin, and immutable anchor identity were not explicit.
4. Key and synthetic-map creation, exact base64-plus-LF encoding, output
   withholding, and ledger `key_id` schema binding were incomplete.
5. A single initial CAS did not protect CURRENT, disabled-ruleset creation, and
   active-ruleset activation boundaries.
6. Public contract-bound blobs and private 0600 generated inputs were conflated.
7. Ambiguous forward/rollback response reconciliation was unspecified.
8. Retention was incorrectly described as necessary for rollback even though the
   baseline contains no CURRENT secret.

The revised plan incorporates these findings but remains blocked on both owner
decisions and independent re-review. No implementation or external mutation was
reviewed or authorized.
