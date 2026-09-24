---
name: crossprovider codex tdd-false-pass-risk-substring-checks-miss-yaml-s
description: TDD false-pass risk: substring checks miss YAML structure violations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, tdd, yaml, false-positives]
---

Frontmatter tests using substring/regex matching can pass even when required YAML fields are missing or types are wrong. Must parse YAML with repo helpers, assert exact field values and types, hash canonical bytes, and include negative assertions for correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
