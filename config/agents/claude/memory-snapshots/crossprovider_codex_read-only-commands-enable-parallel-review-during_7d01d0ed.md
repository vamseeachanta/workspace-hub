---
name: crossprovider codex read-only-commands-enable-parallel-review-during
description: Read-only commands enable parallel review during active implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [workflow, git-coordination, concurrency]
---

Use git show, bounded file reads, and targeted inspection to review changes while active implementation work uses hooks and commits in the same repo. Avoid checkout/status operations that mutate state. This allows thorough review to coexist with mutable parallel work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
