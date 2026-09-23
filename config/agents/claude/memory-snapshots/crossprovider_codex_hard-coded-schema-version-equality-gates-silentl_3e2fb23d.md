---
name: crossprovider codex hard-coded-schema-version-equality-gates-silentl
description: Hard-coded schema version equality gates silently reject upgraded formats
metadata:
  type: reference
  source: codex
  bridged: 2026-07-28
  tags: [schema-migration, data-pipeline, version-gates]
---

Version checks like `== schema_version: 4` in transform pipelines become silent rejection gates when producers upgrade to schema 5, turning valid new-format records into MISSING-EVIDENCE status. Use `>= min_version` or explicit allowlists instead of equality checks to prevent invisible data loss during schema migrations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
