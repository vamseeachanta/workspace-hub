---
name: crossprovider hermes validator-checks-structure-not-consistency
description: Validator checks structure not consistency
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, testing-gap, data-consistency]
---

Separating validation into 'does report have required headings?' (structural) vs 'do report counts match manifests?' (consistency) creates gaps. Heading-only validation passes even when report/manifest data drifts. Both checks needed for weekly data refreshes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
