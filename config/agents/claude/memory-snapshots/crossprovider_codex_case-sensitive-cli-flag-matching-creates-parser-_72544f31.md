---
name: crossprovider codex case-sensitive-cli-flag-matching-creates-parser-
description: Case-sensitive CLI flag matching creates parser gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator-design, flag-parsing]
---

Validators checking for `grep -R` miss `grep -r` or `grep --recursive`. Each flag variant is a separate bypass. Use case-insensitive matching or enumerate all flag variants (lowercase, combined forms, long form) in denylist patterns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
