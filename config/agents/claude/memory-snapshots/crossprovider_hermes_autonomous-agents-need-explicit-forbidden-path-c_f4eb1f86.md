---
name: crossprovider hermes autonomous-agents-need-explicit-forbidden-path-c
description: Autonomous agents need explicit forbidden-path constraints
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agent-safety, autonomous-execution, guardrails]
---

Claude repeatedly touched `scripts/testing/coverage-results.json` during unattended runs across multiple sessions; manual revert + redirect was the workaround each time. Suggests agents require hardened scope constraints or path guardrails, not just advisory documentation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
