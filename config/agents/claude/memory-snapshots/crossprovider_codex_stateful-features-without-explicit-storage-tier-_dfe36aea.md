---
name: crossprovider codex stateful-features-without-explicit-storage-tier-
description: Stateful features without explicit storage tier assignment are unverifiable
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, storage-tiers, state-management]
---

Plans proposing features like checkpointing, resumption, logging, or caching must explicitly assign storage paths, tier classification (git-tracked, shared-mount, local-cache), and schema/format. Vague references ('audit logs', 'checkpoint state') without concrete file paths and schemas fail the tier-compliance check.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
