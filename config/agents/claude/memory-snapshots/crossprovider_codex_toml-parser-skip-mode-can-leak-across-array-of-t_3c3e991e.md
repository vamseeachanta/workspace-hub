---
name: crossprovider codex toml-parser-skip-mode-can-leak-across-array-of-t
description: TOML parser skip mode can leak across array-of-tables boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [toml, parsing, data-loss, test-coverage]
---

After entering skip mode to handle legacy `[status_line]`, the parser does not exit skip mode when encountering `[[array-of-tables]]`. Unrelated valid array tables that follow are silently deleted while staged TOML still validates and replaces the target. Current test fixtures mask this by omitting array-table cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
