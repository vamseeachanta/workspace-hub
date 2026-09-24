---
name: crossprovider codex rotation-archival-need-explicit-continuity-rules
description: Rotation + archival need explicit continuity rules in append-only systems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit, rotation, chain-integrity, append-only]
---

For append-only chained logs with file rotation (e.g., monthly), explicitly define chain continuity across boundaries: does a new file start with genesis or carry the prior file's terminal hash? Without this rule, verification becomes undefined across rotations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
