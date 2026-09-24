---
name: crossprovider codex weak-github-workflow-security-tests-miss-credent
description: Weak GitHub workflow security tests miss credential injection vectors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-security, test-coverage, token-scope]
---

Testing credential absence only at one point in the flow (e.g., first literal git push) misses earlier injection (git config, gh auth setup-git). Test the full credential source→use pathway. Repository dispatch triggers should be filtered by event_type; unfiltered dispatch allows any event to invoke the workflow. Token mint should request least-privilege scopes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
