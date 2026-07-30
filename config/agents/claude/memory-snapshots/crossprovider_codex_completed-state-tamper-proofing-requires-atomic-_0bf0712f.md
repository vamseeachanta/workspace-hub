---
name: crossprovider codex completed-state-tamper-proofing-requires-atomic-
description: Completed state tamper-proofing requires atomic ledger re-verification inside transaction
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [sqlite-transactions, state-tamper-proofing, atomic-operations]
---

After independent operations (e.g., row counting), re-verify ledger state inside BEGIN IMMEDIATE and hold that transaction through final output emission. Perform verify→derive→emit→commit as one atomic unit. Add deletion/replacement regressions to the suite.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
