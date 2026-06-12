---
name: crossprovider hermes plan-implementation-command-parity-verification
description: Plan-implementation command parity verification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-review, cli-contracts, correctness-verification]
---

Approved plans may document CLI flags (e.g., --output path) that are not implemented, with tests passing if they don't cover the CLI contract. Before closeout, verify that documented artifact-generation commands are actually executable, not just described.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
