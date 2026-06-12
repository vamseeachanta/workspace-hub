---
name: crossprovider gemini schema-versioning-on-data-ledgers
description: Schema versioning on data ledgers
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [versioning, backward-compatibility, schema-design]
---

Include schema_version field in YAML ledgers (e.g., mounted-source-registry.yaml, resource-intelligence-maturity.yaml) to enable safe evolution—add fields without breaking old consumers. Measurement metadata should record owner and update process for auditability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
