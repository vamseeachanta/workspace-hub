---
name: crossprovider codex review-cited-artifacts-must-exist-verify-paths-a
description: Review cited artifacts must exist; verify paths are current
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, traceability, artifact-management]
---

A plan that cites review artifacts like `scripts/review/results/2026-06-02-plan-264-claude.md` should have adversarial review verify those files exist at HEAD. Nonexistent paths break traceability and signal stale plan text. Use `git ls-files` or `ls` to verify before citing in plan headers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
