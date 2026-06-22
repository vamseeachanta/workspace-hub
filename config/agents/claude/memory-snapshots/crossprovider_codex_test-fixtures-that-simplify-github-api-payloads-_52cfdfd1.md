---
name: crossprovider codex test-fixtures-that-simplify-github-api-payloads-
description: Test fixtures that simplify GitHub API payloads hide integration gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [testing, api-mismatch, fail-closed-gates]
---

Plan specifies `gh issue view --json comments` author as an object `{login, ...}`, but tests inject owner-evidence as dict with string author. Real API payloads fail silently if parser expects string. Always validate test shape against live API responses before marking implementation ready.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
