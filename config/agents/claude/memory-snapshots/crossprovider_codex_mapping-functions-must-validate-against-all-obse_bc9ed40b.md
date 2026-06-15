---
name: crossprovider codex mapping-functions-must-validate-against-all-obse
description: Mapping functions must validate against all observed data combinations
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-validation, testing, mappings]
---

When building mappings between data structures (e.g., scorecard fields → contract fields), validation must cover ALL real-world value combinations present in production data, not just hypothetical or common cases. Sessions found multiple instances where mapping tables omitted rows like (freshness_status=missing, catalog_status=runtime_fetched) that actually appeared in live scorecard data, leaving validator behavior ambiguous.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
