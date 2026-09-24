---
name: crossprovider codex ci-scan-modes-with-clean-checkouts-must-use-full
description: CI scan modes with clean checkouts must use full-tree or PR-diff
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-cd, scanning, git-modes]
---

GitHub Actions `checkout` produces a clean working tree with no staged, unstaged, or untracked files. Scanning strategies that rely on `git diff --staged` or `--diff-only` will find nothing in CI. For CI, use full-tree scans or explicit PR base-diff scanning (e.g., `git diff origin/main HEAD` after a fetch).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
