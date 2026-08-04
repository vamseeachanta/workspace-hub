---
name: crossprovider codex toml-array-of-tables-don-t-reset-parse-context-i
description: TOML array-of-tables don't reset parse context in mergers
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [toml, parsing, data-loss]
---

When merging TOML with managed sections, parsers that only recognize `[table]` headers miss `[[array]]` headers; skip mode stays active afterward, silently deleting unrelated valid keys in the array scope or following sections. Sessions 7–8 show this causes data loss with passing validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
