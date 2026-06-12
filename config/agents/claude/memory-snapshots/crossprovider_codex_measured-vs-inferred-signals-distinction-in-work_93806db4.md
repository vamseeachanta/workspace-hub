---
name: crossprovider codex measured-vs-inferred-signals-distinction-in-work
description: Measured vs inferred signals distinction in workflow gates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [workflow, compliance, orchestration]
---

Workflow compliance gates count only explicit stage signals emitted by scripts (logging, artifact generation), not inferred signals detected from logs/behavior. Document this distinction in skill specs and gate validators to prevent false-positive compliance claims. WRK-624 codified: 'inferred signals are diagnostic only and are NOT counted as measured signal compliance.'

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
