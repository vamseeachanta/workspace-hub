# Adversarial plan review: issue #3544 — prepare_fer_extraction R2

- Date: 2026-07-14
- Reviewer lane: `prepare_fer_extraction`
- Reviewed commit: `547bf3ce763af35797f3be19a5b4fb09a7368c49`
- Verdict: **MAJOR**

## Findings

1. All four superseded #3522 clauses and the obsolete preview required explicit
   cross-links, deprecation, Files-to-Change coverage, and rejection tests.
2. Variant A needed exact CODEOWNERS rows including the frozen proof path.
3. Argv/stdout secrecy language incorrectly included required public path flags.
4. The 0600-input test was stale after public inputs became commit-A Git blobs.
5. CSPRNG failures/collisions, proof identity, and A/B merge preservation needed
   explicit RED tests and acceptance gates.
6. Encrypted-at-rest evidence was undefined and had to be defined or removed.

The revised draft incorporates these findings but remains blocked on owner
decisions and independent re-review. No implementation or external mutation was
reviewed or authorized.
