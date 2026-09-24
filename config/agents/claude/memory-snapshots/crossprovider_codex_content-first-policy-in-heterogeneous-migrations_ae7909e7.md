---
name: crossprovider codex content-first-policy-in-heterogeneous-migrations
description: Content-first policy in heterogeneous migrations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migrations, data-integrity, pragmatism]
---

When migrating data across repos with varying metadata (timestamps, file modes), prioritize content integrity (sha256sum parity) over mode/timestamp parity. Non-blocking differences reduce friction while preserving correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
