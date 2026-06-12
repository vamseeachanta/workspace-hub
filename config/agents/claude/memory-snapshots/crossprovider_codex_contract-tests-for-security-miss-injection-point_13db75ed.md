---
name: crossprovider codex contract-tests-for-security-miss-injection-point
description: Contract tests for security miss injection points
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [security, testing, credentials]
---

A test that only checks 'token absent after line X' misses injections before that line (git config, git remote set-url, gh auth setup-git). Test actual credential binding (what cred is used, what scope), not just final state. Least-privilege scopes matter even for temporary tokens.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
