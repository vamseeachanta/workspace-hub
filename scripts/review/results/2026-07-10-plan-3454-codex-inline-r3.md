# Codex inline r3 — issue #3454 plan

**Reviewed commit:** `2426a59d1311b2546258bc8ca6821181ced15031`
**Verdict:** MAJOR

Three parallel reviews agreed that v3 still allowed unsafe or unverifiable paths:

1. partial/unknown mutation failures could escape rollback;
2. predictable runtime paths allowed stale/concurrent snapshot contamination;
3. the synthetic fuse root and target-value byte grammar were underconstrained;
4. iterative branches could not satisfy the immediate-parent base gate;
5. D1 REJECT/defer could be mistaken for issue completion.

The v4 draft will quarantine rollback failures, use locked random run roots and nonce-bound results, compare a hostile-tested synthetic child with a settings metadata FD, hash exact opaque scalar bytes, attest merge-base/behind/overlap state, and keep #3454 open until removal verifies. This verdict is not approval; fresh review must target the pushed v4 pair.
