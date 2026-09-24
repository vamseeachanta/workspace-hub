---
name: crossprovider codex explicit-pathspec-lists-prevent-false-stale-mark
description: Explicit pathspec lists prevent false-stale-marking in git status checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, freshness-detection, pathspec]
---

Using broad patterns like `git status -- .claude scripts config` marks healthy reports as stale when unrelated tracked files change. Instead, use an explicit allowlist of specific measured paths (e.g., `.claude/skills`, `.claude/memory/context.md`, `.claude/rules`) to avoid noise and maintain accuracy in freshness detection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
