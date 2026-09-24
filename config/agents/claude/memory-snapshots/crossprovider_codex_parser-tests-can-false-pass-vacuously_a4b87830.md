---
name: crossprovider codex parser-tests-can-false-pass-vacuously
description: Parser tests can false-pass vacuously
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validation, fail-closed]
---

Parsing tests that check "every row has field X" pass if the parser returns zero rows (no data to test). Tests must explicitly fail when expected data is missing and require proof the parsed data actually exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
