---
name: crossprovider codex coordination-ledger-entries-must-match-plan-asse
description: Coordination ledger entries must match plan assertions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [coordination, registry-consistency]
---

Keep registry/coordination ledgers (validation commands, test lists, file paths) in sync with plan text. If a plan says 'this issue creates no implementation scripts,' the ledger must not list validation scripts for it—mismatches block approval gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
