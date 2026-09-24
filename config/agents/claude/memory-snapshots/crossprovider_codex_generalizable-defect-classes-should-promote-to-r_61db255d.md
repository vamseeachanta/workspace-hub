---
name: crossprovider codex generalizable-defect-classes-should-promote-to-r
description: Generalizable defect classes should promote to rules, not rot in reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-process, knowledge-transfer, rules]
---

When adversarial review surfaces a defect class that applies beyond the current scope (e.g., TOCTOU between working tree and staged blob, threat-model inversion in skip conditions), file a follow-on issue or add a rule to `.claude/rules/` or SHARED_SOUL.md so the next plan in that domain doesn't re-discover it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
