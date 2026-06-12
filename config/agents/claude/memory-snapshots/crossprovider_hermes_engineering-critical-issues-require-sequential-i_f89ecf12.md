---
name: crossprovider hermes engineering-critical-issues-require-sequential-i
description: Engineering-critical issues require sequential implementation gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-workflow, gating, issue-management]
---

Issues labeled `cat:engineering-calculations` (e.g., SIROCCO #2760) block implementation until ALL gates complete in order: resource intelligence → revision plan → adversarial review → post for approval → explicit user approval. Jumping to implementation before approval is a violation, regardless of plan completeness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
