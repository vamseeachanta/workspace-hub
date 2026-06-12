---
name: crossprovider hermes boundary-enforcement-tests-must-cover-existing-a
description: Boundary enforcement tests must cover existing artifacts, not just metadata
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-governance, test-coverage, boundary-guards]
---

When reclassifying internal reference data, tests that only check metadata/README updates miss residual client-facing outputs (e.g., GTM PDF packs). Guardrails must assert absence/non-consumability of pre-existing artifacts in the reuse surface, or approval is blocked.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
