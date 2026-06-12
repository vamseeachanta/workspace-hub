---
name: crossprovider hermes closeout-is-transactional-cannot-defer-any-phase
description: Closeout is transactional; cannot defer any phase
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [closeout, github-workflow, transaction]
---

Closeout requires validate → commit → push → issue comment → label cleanup/closure → branch disposition → clean-state proof in a single window. Closing first and cleaning later breaks the gate. For issues with substantial scope (assetutilities#78, digitalmodel#596), plan closeout transactionality upfront.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
