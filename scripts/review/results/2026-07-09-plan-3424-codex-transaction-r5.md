# Adversarial plan review — #3424 privacy/transaction r5

Provider: Codex parallel reviewer

Verdict: MAJOR

## Findings

1. Bootstrap trusted a mutable local journal/marker and live label presence without canonical authorized-human actor, bot exclusion, freshness, or remote pushed-plan binding proof; its `assert` checks were optimization-strippable.
2. Approval evidence was not hash-bound through final staging and commit despite the acceptance claim.
3. `git commit` with pathspecs could reread working-tree files instead of committing only the already-scanned index tree; the plan detected a mismatch only after advancing HEAD and specified no CAS rollback.
4. Step 12 said to update the hash-frozen manifest even though the final paths were already predeclared.
5. Cleanup and completeness review needed explicit transaction-residue disposition and the same two-distinct-provider degradation floor.

## Required disposition

- Replace local marker trust with direct canonical remote authority/binding evaluation and frozen local artifact hashes.
- Create and verify a detached commit directly from `scanned_tree`, then install with `update-ref` compare-and-swap under an owned lock and rollback on post-install failure.
- Keep the manifest immutable and apply the two-provider floor to completeness review.

No files were edited by the reviewer.
