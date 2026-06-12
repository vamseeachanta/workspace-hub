---
name: crossprovider hermes live-state-acceptance-criteria-are-brittle-for-a
description: Live-state acceptance criteria are brittle for approval gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, approval-gates, determinism]
---

Approval gates tied to 'repo currently contains example X' fail as repo evolves. Use fixture-backed deterministic tests instead; document live examples separately as validation aid only.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
