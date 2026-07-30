# Adversarial plan review: issue #3544 — custom_ansys_runners R3

- Date: 2026-07-14
- Reviewer lane: `custom_ansys_runners`
- Reviewed commit: `8d1b347776dfc6fc241980b145425e2547bbb154`
- Verdict: **MAJOR**

## Findings

1. The cap and frozen-CLI supersession references named the wrong #3522
   sections/locations and all four clauses needed exact source references.
2. Retained proof/audit could age before the first environment write; full CAS
   was required immediately after proof and before that PUT.
3. Variant A omitted authority paths from its canonical CODEOWNERS matrix and did
   not freeze EOF order or test last-match shadowing in both author directions.

The R4 draft incorporates these findings but remains blocked on both owner
decisions and independent re-review. No implementation or external mutation was
reviewed or authorized.
