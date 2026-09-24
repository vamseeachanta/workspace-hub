---
name: crossprovider codex validate-empty-stdout-from-helper-functions-imme
description: Validate empty stdout from helper functions immediately
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, error-handling, defensive-coding]
---

Functions returning status via stdout must be validated with [[ -n "$RESULT" ]] before use. Do not rely on || true to hide failures; callers must fail clearly if resolution is empty.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
