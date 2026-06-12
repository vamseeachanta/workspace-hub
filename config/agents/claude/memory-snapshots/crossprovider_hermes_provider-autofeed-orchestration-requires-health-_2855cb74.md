---
name: crossprovider hermes provider-autofeed-orchestration-requires-health-
description: Provider autofeed orchestration requires health-check gate before resume
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orchestration, provider-autofeed, multi-agent, saturation]
---

Spawning many parallel provider lanes (Claude/Codex/Gemini/Hermes) in rapid 15-minute autofeed cycles saturates the machine and produces overlapping/duplicate work. Reconcile current lane outputs (classify as useful/stalled/failed/duplicate), patch autofeed monitor logic, run one controlled live tick, inspect health, then decide whether to resume automation or keep paused.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
