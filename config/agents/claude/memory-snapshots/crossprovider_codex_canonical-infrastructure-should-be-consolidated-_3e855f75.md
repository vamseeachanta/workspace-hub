---
name: crossprovider codex canonical-infrastructure-should-be-consolidated-
description: Canonical infrastructure should be consolidated, not paralleled
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, code-reuse, technical-debt]
---

Inventory/catalog generation can accumulate multiple implementations (e.g., `generate_data_catalog.py` vs `generate_catalog.py` vs legacy inventory scripts). Identify the canonical implementation (structured YAML/JSON output, freshness tracking, domain inference) and consolidate work toward it rather than building parallel systems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
