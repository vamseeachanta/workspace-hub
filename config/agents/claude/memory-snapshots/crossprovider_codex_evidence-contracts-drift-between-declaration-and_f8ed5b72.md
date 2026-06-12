---
name: crossprovider codex evidence-contracts-drift-between-declaration-and
description: Evidence contracts drift between declaration and emission
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cron, contracts, monitoring]
---

Scheduled tasks may declare one log path in config but emit artifacts to a different valid path (e.g., markdown to a secondary dir instead of the configured log glob). Cron-health monitors must validate this drift explicitly, not assume artifact patterns match config declarations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
