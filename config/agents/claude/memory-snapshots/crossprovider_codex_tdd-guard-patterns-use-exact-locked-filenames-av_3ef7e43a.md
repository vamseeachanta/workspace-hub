---
name: crossprovider codex tdd-guard-patterns-use-exact-locked-filenames-av
description: TDD guard patterns: use exact locked filenames, avoid broad regexes, prevent stale evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, testing-patterns, regression-guards]
---

When testing for missing config/docs, use exact locked filenames in guards (e.g., `git grep -F "-"` is too broad in markdown). Prevent stale evidence by using count-free wording instead of embedding fixed test counts. Derive module structure from git tree (`git ls-tree -d --name-only`) rather than hardcoding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
