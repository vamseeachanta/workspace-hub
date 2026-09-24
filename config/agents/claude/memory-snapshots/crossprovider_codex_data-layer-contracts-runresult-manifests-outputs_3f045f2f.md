---
name: crossprovider codex data-layer-contracts-runresult-manifests-outputs
description: Data-layer contracts (RunResult, manifests, outputs) must be defined and tested before consumers are planned
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-contract, schema-design, integration-testing]
---

Sessions #611 and #612 found RunResult missing expected fields (warnings), and manifest-to-hydrodynamic-arrays mappings undefined. Downstream plans that consume these contracts must validate the schema exists and covers all required fields before writing acceptance tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
