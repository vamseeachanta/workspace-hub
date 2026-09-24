---
name: crossprovider codex fdas-output-contract-beyond-standard-columns
description: FDAS output contract: beyond STANDARD_COLUMNS
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [fdas-contract, conformance, testing]
---

Adapter output must pass to_fdas_production conformance checks, not just emit STANDARD_COLUMNS (region, field_name, year, month, oil_bbl, gas_mcf, water_bbl). Conformance tests verify downstream compatibility; adapters that emit columns but fail contract shape cause silent downstream failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
