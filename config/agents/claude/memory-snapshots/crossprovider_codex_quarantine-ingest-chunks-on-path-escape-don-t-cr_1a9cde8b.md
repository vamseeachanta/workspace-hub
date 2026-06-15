---
name: crossprovider codex quarantine-ingest-chunks-on-path-escape-don-t-cr
description: Quarantine ingest chunks on path escape, don't crash dispatcher
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest, resilience, batch-processing]
---

When chunk output violates path constraints (e.g., creates scripts/), catch the error, quarantine via git reset/clean, log warning, and continue to next chunk. Only create PR if any chunks committed successfully. Prevents one bad chunk from losing all prior good work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
