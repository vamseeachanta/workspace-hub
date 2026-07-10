# Adversarial plan review — #3443 TDD/enforcement

> Reviewer: Codex internal parallel reviewer (Fermat)
> Stage: plan, revision 1
> Verdict: MAJOR
> Provider-diverse gate credit: none; same-provider review only

## Defects found

1. Open-ended actions such as `block/review` lacked deterministic exit status, precedence, and protected minimums.
2. Private skip could succeed without installed, available, enforced staged and CI secret gates.
3. Public-egress was asserted rather than derived from a trusted boundary; commit and PR metadata were omitted.
4. Deletion-only behavior contradicted the zero-blob requirement.
5. The plan's file-level self-exemption conflicted with the required narrow sentinel model.
6. Existing bypasses and rollout dispositions lacked an executable checker/schema.
7. Legacy rules lacked one-to-one migration and public-profile parity tests; generated provider runtimes lacked regression checks.

## Required disposition

Revision 2 will define a closed action enum and precedence, make replacement gates activation prerequisites, derive operations from protected entrypoints and authoritative context, use tombstone manifest records for deletions, define a narrow expiring sentinel grammar, add bypass and rollout validators, prove legacy-rule bijection/public parity, and regenerate/test every provider runtime.
