---
name: crossprovider codex use-python-for-yaml-frontmatter-mutation-never-s
description: Use Python for YAML/frontmatter mutation, never sed
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [yaml-safety, sed-antipattern, frontmatter]
---

Sed corrupts malformed YAML/frontmatter. Use `uv run --no-project python` with a proper YAML parser to handle edge cases: missing keys, duplicate keys, malformed structure. This avoids silent corruption and makes file updates idempotent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
