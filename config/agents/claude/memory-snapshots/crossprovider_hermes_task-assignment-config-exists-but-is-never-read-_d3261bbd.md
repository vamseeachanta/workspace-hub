---
name: crossprovider hermes task-assignment-config-exists-but-is-never-read-
description: Task assignment config exists but is never read by live code
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [task-assignment, routing, automation-gap]
---

routing-config.yaml defines tier-based routing rules (simple/standard/complex/reasoning) with provider signals and cross-review policies, but no live router script reads or enforces it. Overnight batch terminal assignment is 100% manual; review-routing-gate.py is the only automated dispatcher (and only for review, not work items). The specification sits dormant while actual routing happens by human decision each night.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
