---
name: crossprovider codex pattern-validation-gap-regex-like-strings-can-sm
description: Pattern validation gap: regex-like strings can smuggle literal private values
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [validation, false-positive, input-safety]
---

Validators that check allow-contexts may pass strings like `regex_pattern: /some.*path/` even when they embed literal private values, because the string "looks like regex." Requires explicit classification (literal vs. regex) or mandatory escape-checking on all patterns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
