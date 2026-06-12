---
name: crossprovider codex multi-gate-approval-for-complex-migrations
description: Multi-gate approval for complex migrations
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [migration, approval-gates, safety]
---

Large file migrations benefit from tiered approval gates (APPROVED_FOR_DRYRUN → APPROVED_FOR_SIMULATION → APPROVED) rather than single approval; allows phased risk reduction. Prevents accidentally skipping dry-run validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
