# Codex inline adversarial plan review — #3454 r1

## Verdict

MAJOR

## Retrieval

- Public plan v1, approved design HTML, issue #3454, private issue #37.
- Live `origin/main`, cleanup skill, legal/PII scripts, Pages flow, and fuseblk/runtime mount evidence.
- Linked private plan v1 and official provider UNAVAILABLE artifacts.

## Findings

1. The plan branch was stale and not remotely reviewable.
2. Manual delete/archive/relocate execution was promised without an executor or an explicit manual-only boundary.
3. Public/private schema and mutation ownership overlapped.
4. “Compare-and-swap” overstated digest-check plus atomic-replace guarantees.
5. Runtime rollback durability and same-fuse fsync behavior were undefined.
6. Permission authority did not bind target commitments, approval, and fresh absent/unregistered checks.
7. Private/public commits formed a self-referential publication cycle.
8. Exact-token scanning would self-block on common/public names.
9. Verification used a shell placeholder and allowed vacuous scan evidence.
10. Destructive actions lacked a pushed write-ahead checkpoint.
11. Historical 124→128 observations were incorrectly described as reconstructable deltas.
12. The public script was an oversized security-critical responsibility bundle.

## Blockers

All findings above required revision. V2 splits ownership/modules, freezes schema v1, uses optimistic guarded replacement wording, adds same-fuse probes, defines A→B→C receipts, classifies tokens, adds executable manifests, and requires private pushed WAL before mutation.

This artifact records r1 defects only. It is not a v2 approval or cross-provider consensus.
