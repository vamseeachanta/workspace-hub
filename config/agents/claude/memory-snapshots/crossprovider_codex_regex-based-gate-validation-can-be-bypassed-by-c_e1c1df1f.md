---
name: crossprovider codex regex-based-gate-validation-can-be-bypassed-by-c
description: Regex-based gate validation can be bypassed by code examples
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [validation, defect-class, gate-design]
---

When gate checks use regex to scan entire file contents (e.g., `check_plan_confirmation()`), code-fenced examples and documentation snippets can unintentionally satisfy validation conditions. A file containing only a markdown-fenced code block with `confirmed_by`, `confirmed_at`, `decision: passed` will pass the gate. Use structured YAML/JSON parsing or anchor regex to specific sections, not whole-file scanning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
