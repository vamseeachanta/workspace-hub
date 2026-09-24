---
name: crossprovider gemini schema-versioning-in-yaml-ledgers
description: Schema versioning in YAML ledgers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [yaml, schema, versioning, ledgers]
---

Include `schema_version` field in YAML ledgers (maturity tracking, registries, etc.) to support schema evolution without breaking existing readers. Readers can check version and handle migrations or compatibility.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
