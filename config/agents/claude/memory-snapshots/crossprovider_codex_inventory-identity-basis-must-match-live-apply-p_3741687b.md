---
name: crossprovider codex inventory-identity-basis-must-match-live-apply-p
description: Inventory identity basis must match live apply path
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [governance, architecture, identity, blocker]
---

Task inventory identity (workspace root, checkout basis) must be identical between generation and live apply/audit; misalignment is a blocker-level governance defect. Dry-run output diagnostically proves misalignment when registry lines are unexpectedly uncataloged.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
