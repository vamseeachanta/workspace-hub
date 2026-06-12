---
name: crossprovider codex github-connector-as-read-only-fallback-for-files
description: GitHub connector as read-only fallback for filesystem-blocked scouts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [scout-pattern, fallback-strategy, tooling]
---

When local filesystem inspection is blocked, GitHub connector provides code search and issue metadata as a fallback (e.g., committed marker inventory, issue labels, brief context). Does not access uncommitted files, real-time git state, or local logs; document access gaps explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
