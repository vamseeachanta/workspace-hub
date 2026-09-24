---
name: crossprovider codex yaml-scalar-parsing-without-full-parser
description: YAML scalar parsing without full parser
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, yaml, parsing, no-dependencies]
---

Anchor grep to section header (`grep -n "^${key}:"`) to find line number, then use sed to read next N lines and grep for the target key. More robust than line-based parsing and avoids loading full YAML libraries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
