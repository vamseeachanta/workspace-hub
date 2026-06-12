---
name: crossprovider hermes tdd-with-pre-committed-code-from-prior-sessions
description: TDD with pre-committed code from prior sessions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd-pattern, overnight-planning]
---

Overnight plans ask for TDD (tests first) but code may already be committed from prior sessions. Pattern: read existing code, write new test file, attempt implementation—git will show no diff if already done. Verify via line count, not just grep. Check HEAD commit messages for prior work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
