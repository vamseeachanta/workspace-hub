---
name: crossprovider codex script-design-yaml-mutations-cli-checks-and-idem
description: Script design: YAML mutations, CLI checks, and idempotent updates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, error-handling, resume-recovery]
---

Use `uv run --no-project python` for YAML/frontmatter edits (not `sed`). Preflight-check CLI availability and GitHub auth with `gh auth status` before processing. Parse structured CLI output (e.g., `gh issue list --json`) with Python, not bash. Make file updates idempotent and use stable ordering for deterministic `--limit`/`--resume-from` behavior across reruns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
