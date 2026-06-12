---
name: crossprovider hermes approval-gate-requires-marker-file-not-github-la
description: Approval gate requires marker file, not GitHub labels
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, approval-gate, workflow]
---

Formal implementation approval in this repo enforces `.planning/plan-approved/NNNN.md` marker files (checked by `.claude/hooks/plan-approval-gate.sh`), not GitHub labels (status:plan-approved). Label assignment alone does not satisfy the runtime gate; marker file must exist.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
