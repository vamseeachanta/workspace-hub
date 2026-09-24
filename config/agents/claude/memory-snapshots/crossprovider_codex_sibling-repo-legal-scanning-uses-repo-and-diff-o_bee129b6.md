---
name: crossprovider codex sibling-repo-legal-scanning-uses-repo-and-diff-o
description: Sibling-repo legal scanning uses --repo and --diff-only
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, legal-scanning, workspace-nav]
---

The `legal-sanity-scan.sh --repo=../sibling-repo --diff-only` form works for scanning sibling checkouts without full-tree traversal. `--diff-only` runs `git diff --name-only HEAD` inside the target repo, enabling focused compliance checks across related worktrees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
