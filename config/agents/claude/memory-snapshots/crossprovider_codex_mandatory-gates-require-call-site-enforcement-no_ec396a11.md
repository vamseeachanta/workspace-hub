---
name: crossprovider codex mandatory-gates-require-call-site-enforcement-no
description: Mandatory gates require call-site enforcement, not library export
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [gates-enforcement, call-site-coupling, mandatory-validation]
---

Extracting a validator into a library function makes it discoverable but not mandatory. If a gate must block invalid data from being written, it must be called unconditionally on every write path (e.g., inside `write_sanitized_corpus()`), not just exposed as a helper (e.g., `preflight()`). Test coverage of the helper doesn't guarantee enforcement. In #267, `preflight()` existed but the extraction write path never called it; malformed taxonomy rows still passed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
