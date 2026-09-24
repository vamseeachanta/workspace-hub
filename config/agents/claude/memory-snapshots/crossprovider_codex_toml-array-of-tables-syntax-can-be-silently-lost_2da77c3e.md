---
name: crossprovider codex toml-array-of-tables-syntax-can-be-silently-lost
description: TOML array-of-tables syntax can be silently lost in incomplete parsers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [toml, data-loss, parser, testing]
---

If a TOML merger recognizes `[normal_table]` but not `[[array_of_tables]]`, subsequent array tables are silently deleted while the staged result still validates. After processing legacy `[status_line]`, a skip-mode flag can remain active and discard unrelated valid TOML. Fixtures must cover both syntax forms explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
