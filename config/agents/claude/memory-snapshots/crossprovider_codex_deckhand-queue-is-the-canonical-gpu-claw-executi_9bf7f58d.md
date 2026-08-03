---
name: crossprovider codex deckhand-queue-is-the-canonical-gpu-claw-executi
description: Deckhand queue is the canonical GPU-claw execution method
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [deployment, gpu-claw, queue-contract]
---

GPU-claw jobs are submitted via private Deckhand git queue (openfoam-run-batch), not direct SSH or local execution. Queue provides request/retry/artifact contracts that must be verified and documented in implementation plans before dispatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
