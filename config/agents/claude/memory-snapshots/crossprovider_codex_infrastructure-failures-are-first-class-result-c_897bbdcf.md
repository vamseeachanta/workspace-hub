---
name: crossprovider codex infrastructure-failures-are-first-class-result-c
description: Infrastructure failures are first-class result categories, not parse shadows
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [error-handling, orchestration, exit-codes]
---

When wrapping external tools (pytest, mypy, ruff), classify process outcomes as explicit statuses: `success`, `infra_error` (uv resolution failed), `missing_repo`, `timeout`, `parse_error`. Do not hide infrastructure failures behind summary-line parsing (e.g. 'no summary → 0 errors'). Validator reported failures as 'FAIL (0 errors)' when underlying uv invocation broke, which is both incorrect and non-actionable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
