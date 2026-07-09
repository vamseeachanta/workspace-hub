---
name: crossprovider codex scanner-precondition-untracked-files-invisible-t
description: Scanner precondition: untracked files invisible to git diff --diff-only without git add -N
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [governance, security-scanning, git-workflow]
---

Public/private leak scans using git diff --diff-only skip untracked files silently. Any plan declaring --diff-only scanning must explicitly stage new files with git add -N first, or the scanner covers incomplete work. Discovered when a new test file was untracked but plan assumed it was scanned; the legal scanner passed despite the gap.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
