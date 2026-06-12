---
name: crossprovider hermes multi-machine-handoffs-need-concrete-script-path
description: Multi-machine handoffs need concrete script paths and verification commands
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-machine, handoff-artifacts, concrete-paths]
---

Multi-machine workflows must include exact script locations, remote SSH verification commands, and baseline collectors saved to git (not ephemeral chat). Downstream sessions need concrete artifacts to act without re-discovery. Handoffs referencing chat memory cause handoff failures.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
