---
name: crossprovider codex yaml-grep-misses-indented-keys-without-context
description: YAML grep misses indented keys without context
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [yaml, grep, verification]
---

Simple grep patterns for YAML keys like `^floating_marine_mooring_screen:` fail when the key is indented under a parent (e.g., under `workflows:`). Use context-aware search (grep with surrounding lines) or structural parsers to verify YAML claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
