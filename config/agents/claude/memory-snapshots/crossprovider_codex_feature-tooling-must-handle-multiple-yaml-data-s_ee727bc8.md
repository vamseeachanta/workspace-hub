---
name: crossprovider codex feature-tooling-must-handle-multiple-yaml-data-s
description: Feature tooling must handle multiple YAML data shapes or declare migration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [yaml, data-migration, backwards-compatibility]
---

Existing queue data uses both inline-list (`children: [WRK-A, WRK-B]`) and block-list (`children:\n  - WRK-A`) YAML formats. New tooling supporting only one format will silently fail on real items; either parse both or perform a declared data migration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
