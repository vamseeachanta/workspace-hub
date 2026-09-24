---
name: crossprovider codex storage-tier-authority-must-be-explicit-when-git
description: Storage tier authority must be explicit when git and mounted copies coexist
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [storage-design, tier-governance, cross-machine-coordination]
---

Plans with dual data copies (e.g., git-tracked registry + `/mnt/ace/` raw store) that don't declare authority, sync direction, or tier classification violate cross-machine rules and receive defect flags. If both copies exist, one must be authoritative and the other a cache or mirror with explicit sync semantics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
