---
name: crossprovider codex two-tier-legacy-discriminator-for-backward-compa
description: Two-tier legacy discriminator for backward-compatible gating
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gating, versioning, backward-compatibility, architectural-pattern]
---

When introducing new gate/logging requirements across work items with pre-existing data, use numeric ID as primary discriminator (legacy WRK id < 658 skip enforcement entirely) and created_at timestamp as secondary discriminator (items created before cutoff date also skip enforcement). This dual-tier approach enables gradual rollout without breaking work items that predate the requirement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
