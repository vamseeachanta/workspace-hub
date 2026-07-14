# Adversarial plan review: issue #3544 — custom_ansys_runners R2

- Date: 2026-07-14
- Reviewer lane: `custom_ansys_runners`
- Reviewed commit: `547bf3ce763af35797f3be19a5b4fb09a7368c49`
- Verdict: **MAJOR**

## Findings

1. Genesis needed a separately approved, genesis-only transaction before the
   activation preview; activation must retain and consume exact envelope bytes.
2. The merge strategy did not guarantee preservation/reachability of A/B OIDs.
3. Public pin evidence lacked a frozen path, schema, contents, and B ownership.
4. Proof branch/title/path/bytes/diff and post-creation PR/head/check identities
   were not frozen and CAS-bound.
5. Genesis execution needed verified detached/extracted A bytes and all imported
   module blobs verified before entropy.

The revised draft incorporates these findings but remains blocked on owner
decisions and independent re-review. No implementation or external mutation was
reviewed or authorized.
