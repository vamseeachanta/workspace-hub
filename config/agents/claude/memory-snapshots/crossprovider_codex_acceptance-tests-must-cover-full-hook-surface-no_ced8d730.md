---
name: crossprovider codex acceptance-tests-must-cover-full-hook-surface-no
description: Acceptance tests must cover full hook surface, not just per-repo loop
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [testing, hooks]
---

Hooks with multiple invocation paths (e.g., per-repo loop and coverage-mode outside the loop) need test coverage for all paths. Testing only the main loop misses bootstrap failures in secondary paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
