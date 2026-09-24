---
name: crossprovider codex blind-regex-replacements-fail-in-shell-contexts
description: Blind regex replacements fail in shell contexts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [refactoring, shell, risk]
---

Global find-replace for tool names/paths (e.g., `python3 → uv run --no-project python`) breaks valid shell logic in shebangs, `command -v` checks, help text, heredocs, and fallback branches. Requires allowlisted file-by-file edits with explicit validation per file.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
