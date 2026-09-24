---
name: crossprovider gemini email-processing-extract-and-queue-state-machine
description: Email processing: extract-and-queue state machine with deferred deletion
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, email-handling, state-machines, queue-systems]
---

Design email ingestion as extract → structured data with state tracking (labels + local state file) → action → delete on completion. Enables reply detection and re-activation. Avoids lossy archive-raw-then-delete pattern that destroys actionability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
