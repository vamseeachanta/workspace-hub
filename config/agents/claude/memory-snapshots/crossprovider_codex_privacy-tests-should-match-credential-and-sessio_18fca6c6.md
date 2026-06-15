---
name: crossprovider codex privacy-tests-should-match-credential-and-sessio
description: Privacy tests should match credential and session patterns explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, testing, privacy]
---

Generic PII tests (email, phone, handle) miss credential/session leakage. Add explicit pattern matching for `api[_-]?key`, `access token`, `authorization`, `bearer`, `password`, `secret`, `token`. Ensure the test does not block legitimate prohibition text (e.g., 'do not share your API key').

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
