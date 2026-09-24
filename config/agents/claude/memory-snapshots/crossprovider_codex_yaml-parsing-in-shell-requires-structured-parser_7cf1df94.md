---
name: crossprovider codex yaml-parsing-in-shell-requires-structured-parser
description: YAML parsing in shell requires structured parser, not regex
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [yaml, validation, shell-scripting, work-queue]
---

Multi-line YAML lists and type coercion (string "1" vs int 1) in gate validators fail silently with regex extraction. Work-queue metadata (blocked_by lists, version fields) must use python/yaml or native parsers to avoid false-pass gates on malformed data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
