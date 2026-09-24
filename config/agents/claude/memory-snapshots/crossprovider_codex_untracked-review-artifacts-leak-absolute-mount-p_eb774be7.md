---
name: crossprovider codex untracked-review-artifacts-leak-absolute-mount-p
description: Untracked review artifacts leak absolute mount paths, triggering legal scan failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [legal-scanning, artifact-isolation, path-leakage]
---

Review scripts that write temporary results (e.g., `review-result*.md`) outside staged diff can contain absolute paths like `/mnt/ace/` or `/mnt/local-analysis/`. Legal scan fails on those artifacts independent of the staged target. Fix: write review artifacts to .gitignore paths or redirect legal scan to staged-only via `--diff-only` flag.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
