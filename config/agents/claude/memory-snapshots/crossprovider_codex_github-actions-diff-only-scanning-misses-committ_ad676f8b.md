---
name: crossprovider codex github-actions-diff-only-scanning-misses-committ
description: GitHub Actions --diff-only scanning misses committed content in clean checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [ci-scanning, security-gates, validation]
---

A clean `actions/checkout` contains only unstaged changes and untracked files, not committed content. Scanners using `git diff` alone will never see malicious commits in a PR. Require explicit CI mode for commit-range or full-tracked-tree scanning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
