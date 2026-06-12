---
name: crossprovider codex substring-based-pattern-exemption-misses-violati
description: Substring-based pattern exemption misses violations due to term order
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pattern-detection, false-negatives, shell-parsing]
---

Exempting patterns via substring presence (e.g., checking if 'uv run' appears in a command to exempt 'python3' violations) fails when the terms appear out of sequence or in unintended contexts. Example: 'echo uv run && python3 script.py' contains both substrings but not in the exempted relationship. Use tokenization or ordered pattern matching instead of substring search.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
