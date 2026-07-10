# Adversarial plan re-review — #3443 transaction/coverage

> Reviewer: Codex internal parallel reviewer (Ohm)
> Stage: plan, revision 2
> Verdict: MAJOR
> Provider-diverse gate credit: none; same-provider review only

## Defects found

1. Artifact evidence still depended on a caller manifest rather than complete independent enumeration and transport of exact scanned bytes.
2. New branches could race because not every ref write used an expected-state lease.
3. Offline/cached attestations could survive revocation and public-visibility drift.
4. Mutable GitHub metadata lacked edit/delete triggers and a final watermark check.
5. The private authority journal lacked a durable path class, schema, locks, atomic writes, signing trust, backup, and recovery.
6. API pagination did not prove the token could see the owner's complete private set.
7. Verification omitted several focused/full/security/runtime/rollback/staged commands.

## Required disposition

Revision 3 will make public-egress publication gate-owned and content-addressed, lease every ref write, require live visibility/attestation and strict fallback, add metadata mutation invalidation, define a verified signed private Git journal, authenticate/reconcile enumeration coverage, and expand proposed verification commands.
