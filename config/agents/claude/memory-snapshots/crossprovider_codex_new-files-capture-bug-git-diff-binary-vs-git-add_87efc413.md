---
name: crossprovider codex new-files-capture-bug-git-diff-binary-vs-git-add
description: New Files Capture Bug: git diff --binary vs git add -A
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-correctness, file-capture, ingest-architecture]
---

git diff --binary captures only tracked modifications and drops untracked new files. Ingest output is mostly new pages + dataset CSVs (untracked), so this silently loses correctness. Fix: use git add -A from the worktree after chunk execution, then git commit to capture both new and modified files. Critical for correctness on large ingests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
