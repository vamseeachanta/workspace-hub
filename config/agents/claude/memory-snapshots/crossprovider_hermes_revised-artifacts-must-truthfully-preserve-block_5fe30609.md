---
name: crossprovider hermes revised-artifacts-must-truthfully-preserve-block
description: Revised artifacts must truthfully preserve blocked/provisional status, not overclaim completion
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-honesty, data-quality, status-preservation]
---

The #2112 field-development dataset was resubmitted with PASS verdict by preserving status:needs-data and explicitly disclosing that num_manifolds, tieback_distance_km, and cost_usd_bn remain proxy-coded/unseeded. Honesty about limitations is load-bearing; overclaiming 'correlation-ready' while data is mixed-sourced breaks downstream use.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
