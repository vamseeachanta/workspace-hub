---
name: crossprovider codex bash-append-atomicity-with-flock
description: Bash append atomicity with flock
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash-concurrency, script-patterns, locking]
---

When implementing duplicate detection + append in shell scripts, keep both operations inside the same flock section to guarantee atomicity and avoid TOCTOU races. Separate calls lose the atomicity guarantee even if each is individually flocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
