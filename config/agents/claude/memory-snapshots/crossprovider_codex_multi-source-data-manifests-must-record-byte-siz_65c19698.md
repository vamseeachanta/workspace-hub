---
name: crossprovider codex multi-source-data-manifests-must-record-byte-siz
description: Multi-source data manifests must record byte-size and SHA256 for all inputs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [provenance, reproducibility, data-integration]
---

When combining data from multiple sources (e.g., completion packets + Wellbore Query database), record provenance (input_paths, size, SHA256) for ALL sources, not just the primary. Incomplete provenance breaks reproducibility and makes it hard to audit which external data was used. Include all source artifacts in the `input_artifacts` manifest field.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
