---
name: crossprovider codex toml-merge-scope-must-reset-between-section-head
description: TOML merge scope must reset between section headers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [toml, parser, data-safety]
---

When merging TOML configs, parser scope set by `[table]` headers persists into subsequent `[[array-of-tables]]` sections if not explicitly reset. Unrelated valid TOML in array sections can be silently deleted while staged output still validates, causing data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
