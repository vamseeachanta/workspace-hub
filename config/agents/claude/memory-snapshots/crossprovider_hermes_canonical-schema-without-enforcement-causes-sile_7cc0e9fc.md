---
name: crossprovider hermes canonical-schema-without-enforcement-causes-sile
description: Canonical schema without enforcement causes silent contract drift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema, canonical-contracts, drift-detection]
---

Multiple 'canonical' examples (fixtures, reference configs, templates) with no shared schema or test enforcement diverge in naming (e.g., transit_speed_kt vs transit_speed_knots). Establish canonical schema in code or explicitly sync all instances via tests; passive examples drift.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
