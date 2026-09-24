---
name: crossprovider codex broad-repository-operations-are-unreliable-on-la
description: Broad repository operations are unreliable on large checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, large-repos, git, bounded-operations]
---

Full `git status`, `find /`, and unbounded `rg`/`grep` commands hang or time out on large repos. Use targeted operations: `git diff <range>` to get changed files, then operate on that fileset; use `git status --short --branch` with bounded untracked probes; prefer `--paths` limits in scanners. Diff-file lists are more reliable than full-tree discovery.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
