---
name: crossprovider hermes registry-and-standards-ledger-track-different-sc
description: Registry and standards ledger track different scopes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-modeling, architecture, registry]
---

registry.yaml tracks document-index records (e.g., 'other: 44,705'), while standards-transfer-ledger.yaml tracks standards by domain (e.g., 'other: 0'). Both are correct — different organizational axes. Don't conflate them in reports.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
