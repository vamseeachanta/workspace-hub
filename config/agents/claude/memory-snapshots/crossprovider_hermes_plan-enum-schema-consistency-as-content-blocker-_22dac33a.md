---
name: crossprovider hermes plan-enum-schema-consistency-as-content-blocker-
description: Plan enum/schema consistency as content blocker in governance issues
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, adversarial-review, governance-issues, schema-consistency]
---

Enum mismatches (e.g., `reference_data` defined in derivation rules but missing from the manifest schema in #354) are MAJOR blockers when the enum is central to the issue's deliverable. This is not cosmetic: implementers and tests have no valid contract. Governance/documentation work should anchor enums to source-of-truth and freeze them before plan approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
