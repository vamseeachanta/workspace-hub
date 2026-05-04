---
name: git-blob-size-filter-cleanup
description: Strip oversized blobs from unpushed commits using git filter-branch when GitHub's 100 MB limit blocks push
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["git", "github", "blob-management", "troubleshooting"]
---

# Git Blob Size Filter Cleanup

When a file (e.g., `cost-tracking.jsonl`) grows beyond 100 MB in unpushed commits and blocks GitHub push, use `git filter-branch` to strip the oversized blob. Add the file to `.gitignore`, then run `git filter-branch --tree-filter 'rm -f <filepath>' HEAD~N..HEAD` to rewrite commits. This is safe only for unpushed commits not yet in origin. After rewriting, commit the `.gitignore` change and push normally.