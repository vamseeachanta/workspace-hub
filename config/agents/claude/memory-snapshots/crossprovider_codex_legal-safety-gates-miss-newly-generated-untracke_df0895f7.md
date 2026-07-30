---
name: crossprovider codex legal-safety-gates-miss-newly-generated-untracke
description: Legal/safety gates miss newly generated untracked files when using --diff-only
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [gates, legal-scans, generated-artifacts, untracked-files]
---

Scanning `git diff --name-only HEAD` via `--diff-only` flags omits newly generated files unless they are staged first. Generated outputs from a plan (HTML, JSON, reports) may be untracked during execution, so gates need full-repo scans, explicit artifact-path scanning, or a staged-before-scan checkpoint to prove coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
