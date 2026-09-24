---
name: crossprovider gemini yaml-manipulation-from-shell-is-unsafe-use-yq-or
description: YAML manipulation from shell is unsafe; use yq or Python instead
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [yaml-handling, shell-scripting, data-formats]
---

Bash cannot safely parse or merge YAML—risk of schema corruption via string operations. When shell scripts extend YAML produced by other tools, delegate normalization to yq (simple edits) or embedded Python (complex merging). Example: a wrapper script that injects new fields into runner YAML should use Python, not string concatenation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
