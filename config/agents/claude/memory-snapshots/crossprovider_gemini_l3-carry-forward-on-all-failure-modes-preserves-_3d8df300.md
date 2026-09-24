---
name: crossprovider gemini l3-carry-forward-on-all-failure-modes-preserves-
description: L3 carry-forward on all failure modes preserves partial state
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [fault-tolerance, state-preservation, nightly-resilience]
---

When gemini CLI missing, subprocess fails, timeout, parse fails, or yields zero results: preserve existing capability_signals block. Stale signals beat no signals in best-effort nightly jobs.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
