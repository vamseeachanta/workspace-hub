---
name: crossprovider hermes verify-live-filesystem-state-before-asserting-ti
description: Verify live filesystem state before asserting tier-1 repo presence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [inventory, state-verification, assumptions-testing]
---

Contracts list expected tier-1 repos (digitalmodel, assetutilities, worldenergydata) but live inventories may lack them. Always run `find /mnt/local-analysis -maxdepth 1 -type d -name .git` before claiming a repo exists. Absence is valid data, not an error to fix ad-hoc; repo presence must be tracked as a separate decision.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
