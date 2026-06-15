---
name: crossprovider codex generated-reports-must-validate-their-manifest-s
description: Generated reports must validate their manifest source before claiming reconciliation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-validation, report-contracts, determinism]
---

Reports that claim 'existing page reconciliation' or similar must verify the referenced rows and fields exist in the manifest before emitting the report; hardcoded selections without validation silently emit false reconciliation claims if the manifest drifts. Regeneration tests must be deterministic (committed artifacts must byte-match fresh generation) and must enforce that contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
