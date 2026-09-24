---
name: crossprovider gemini explicit-exit-codes-for-timeout-vs-other-failure
description: Explicit exit codes for timeout vs. other failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [exit-codes, error-handling, reliability]
---

Distinguish timeout (124), success (0), and other errors (1) with explicit `exit` statements instead of falling through to implicit 0. Upstream error handlers rely on this distinction to route different failure modes correctly.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
