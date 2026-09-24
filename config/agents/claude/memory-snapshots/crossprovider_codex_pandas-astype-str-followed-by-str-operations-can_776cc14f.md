---
name: crossprovider codex pandas-astype-str-followed-by-str-operations-can
description: pandas astype(str) followed by .str operations can crash on non-string types
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pandas, type-handling, data-pipeline]
---

Type coercion with `astype(str)` does not guarantee subsequent `.str` accessor operations (e.g., `.str.strip()`) work on int64 or mixed-type columns — they raise AttributeError or produce NaN values. Explicit type checking and defensive handling are needed before applying string methods.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
