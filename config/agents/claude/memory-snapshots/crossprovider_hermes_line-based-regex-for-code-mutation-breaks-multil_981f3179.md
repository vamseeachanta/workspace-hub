---
name: crossprovider hermes line-based-regex-for-code-mutation-breaks-multil
description: Line-based regex for code mutation breaks multiline TOML strings
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [toml, shell-safety, correctness-bug]
---

Sanitizing managed keys with line-regex patterns like `/^\s*model\s*=/` corrupts valid TOML multiline strings containing those patterns. A TOML string like `text = """...model = literal..."""` gets silently modified. Use TOML-aware parsing (Python tomllib) and recursive dict mutation instead of line-based sed.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
