---
name: crossprovider codex slow-git-status-in-large-repos-use-bounded-git-p
description: Slow `git status` in large repos — use bounded Git plumbing and issue queries instead of broad traversal
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [tooling-performance, large-repos, git-plumbing]
---

In repos with large working trees, `git status` and untracked-file scans can timeout. Substitute with `git ls-files` for tracked artifacts, `gh issue view` for metadata, and targeted `git diff -- <path>` for specific changes. Avoid broad `find` or `git status` in review/discovery phases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
