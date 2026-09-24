---
name: crossprovider codex schema-drift-silently-corrupts-data-when-parsers
description: Schema drift silently corrupts data when parsers tolerate missing columns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-quality, schema-robustness, error-handling]
---

Parsers using `usecols` filtering followed by fallback to empty series for missing columns can produce null data silently instead of failing closed. If upstream schema changes, malformed data lands in curated outputs. Parsers must validate required columns after read and emit parser quality for missing/parse-failed fields; empty series indicates corruption, not valid absence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
