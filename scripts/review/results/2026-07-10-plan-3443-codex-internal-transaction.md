# Adversarial plan review — #3443 transaction/coverage

> Reviewer: Codex internal parallel reviewer (Ohm)
> Stage: plan, revision 1
> Verdict: MAJOR
> Provider-diverse gate credit: none; same-provider review only

## Defects found

1. Public rollout artifacts would disclose private identities and URLs.
2. Caller-controlled surface selection could downgrade outward work.
3. Staged evidence did not define deletion-only, rename/copy, type-change, unmerged, symlink/gitlink, binary, oversize, or index-mutation semantics.
4. CI range and rendered-output evidence were not bound to authoritative objects and metadata.
5. Cross-repository rollout had no exact state machine, lease, retry, recovery, target-governance, or final verification protocol.
6. Downstream repos had no immutable engine resolution contract.
7. Activation ordering and rollback were absent.
8. Inventory did not bind pagination, node IDs, default-branch OIDs, archive drift, or pre-write rechecks.
9. Verification commands were not executable enough for implementation review.

## Required disposition

Revision 2 will keep private details in a private governance store, define exact index/range/artifact evidence, use a journaled idempotent leased rollout with target issue/plan/approval gates, pin both local and CI engine distributions, require strict-first activation and strict-first rollback, re-enumerate live state before writes, and specify proposed verification commands.
