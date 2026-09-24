---
name: crossprovider codex implementation-must-fail-closed-when-local-prere
description: Implementation must fail-closed when local prerequisites are missing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, prerequisites, implementation-planning]
---

Implementation depending on pre-built local artifacts (e.g., document indexes, mounted resources) should explicitly check prerequisites and fail early with clear error messages. Plans must note when local state is required and implementation must not proceed silently if it is absent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
