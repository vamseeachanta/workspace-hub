---
name: crossprovider codex dict-get-key-default-does-not-substitute-when-ke
description: dict.get(key, default) does not substitute when key exists with None
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [python-trap, data-handling]
---

`dict.get(k, default)` returns `None` if the dict has `{k: None}`, not the default. Normalize explicitly: `value if (value := dict.get(k)) is not None else default`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
