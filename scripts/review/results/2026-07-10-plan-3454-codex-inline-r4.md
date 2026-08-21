# Codex inline r4 — issue #3454 plan

**Reviewed commit:** `c3de2afc2a70371e44a6d82c8b174edf62c29ee1`
**Plan SHA-256:** `1e989de34fdb0951aa3297ccc6b2bb95a20362c6e4501bbf438422660c9e96e7`
**Verdict:** MAJOR

Three parallel defect-hunting reviews found two public blockers:

1. the non-allow-subtree and retained-sequence digest payload/framing rules were not canonical enough for independent public/private implementations;
2. same-device/source checks plus path-based probe creation could accept a different mount or lose a symlink-swap race.

The v5 draft will freeze every digest payload byte grammar, retain independently opened directory FDs, compare Linux mount IDs, and perform all probe/replacement operations FD-relatively. Pair review also found private protocol blockers; those remain private and must clear before the dependency gate can advance. This verdict is not approval; fresh review must target the pushed v5 pair.
