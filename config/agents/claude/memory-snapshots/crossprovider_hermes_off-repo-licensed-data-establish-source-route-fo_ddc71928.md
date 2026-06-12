---
name: crossprovider hermes off-repo-licensed-data-establish-source-route-fo
description: Off-repo licensed data: establish source route, forbid corpus commit, fail-closed resolution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [licensing, external-source, boundary-control]
---

For licensed workbooks/PDFs (e.g., OCIMF Coef.xlsx at `/mnt/ace/acma-codes/...`), enforce: (1) document source route in plan, (2) forbid committing workbook/PDFs/extracted corpora by default, (3) require calc-time resolution from off-repo workbook or off-repo cache, (4) make missing source/citation a fail-closed blocker. Treat as generic reference data, not ship-specific coefficients.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
