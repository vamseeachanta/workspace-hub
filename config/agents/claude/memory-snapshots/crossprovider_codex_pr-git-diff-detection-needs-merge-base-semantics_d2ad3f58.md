---
name: crossprovider codex pr-git-diff-detection-needs-merge-base-semantics
description: PR git diff detection needs merge-base semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git, ci-cd, github-actions]
---

PR-based git diff detection should use merge-base (three-dot) semantics instead of simple base/head comparison. A PR branch behind main can include changes present only in base, causing false positive domain selection in CI routing systems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
