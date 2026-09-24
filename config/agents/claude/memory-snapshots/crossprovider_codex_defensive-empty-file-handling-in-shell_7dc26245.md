---
name: crossprovider codex defensive-empty-file-handling-in-shell
description: Defensive empty-file handling in shell
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell, unix, robustness]
---

Use `find ... | wc -l` with `pipefail` when counting files that may not exist or be empty. Bare arithmetic on missing variables/globs can error silently. Example: dry-run scripts counting Claude memory snapshot targets require defensiveness for zero-result cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
