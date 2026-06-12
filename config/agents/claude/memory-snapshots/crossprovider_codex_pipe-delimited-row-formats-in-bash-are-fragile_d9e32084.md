---
name: crossprovider codex pipe-delimited-row-formats-in-bash-are-fragile
description: Pipe-delimited row formats in bash are fragile
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, data-structures, parsing]
---

Using `|` as a delimiter for extensible row formats in bash is brittle—user content containing `|` silently corrupts column parsing. Use parallel associative arrays (keyed by ID) or safer encoding instead. WRK-1125 showed how pipe-extension caused silent column shifts in reparses.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
