---
name: crossprovider codex large-repos-need-bounded-probes-avoid-full-workt
description: Large repos need bounded probes; avoid full worktree scans in code review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, git, large-repos, tools]
---

Broad `git status --short`, `find` without path limits, and unbounded grep repeatedly timed out on llm-wiki. Alternatives that worked: `git status --untracked-files=no`, `git diff --cached`, `git ls-files`, path-scoped find/grep. In code reviews of large repos, use narrower commands even if slightly more verbose; timeout recovery is expensive.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
