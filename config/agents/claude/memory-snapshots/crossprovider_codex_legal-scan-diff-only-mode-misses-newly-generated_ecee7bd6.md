---
name: crossprovider codex legal-scan-diff-only-mode-misses-newly-generated
description: Legal scan --diff-only mode misses newly generated tracked artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [legal-scan, ci-cd, artifact-handling, testing]
---

`git diff --name-only HEAD` (used by scan's diff mode) only sees staged/tracked changes, missing newly generated files like HTML/JSON reports created during plan execution. For generated artifacts, require full-repo scan, explicit artifact paths, or staged-before-scan checkpoint.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
