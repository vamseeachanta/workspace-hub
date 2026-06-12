---
name: crossprovider gemini dry-run-mode-tests-don-t-exercise-real-file-oper
description: Dry-run mode tests don't exercise real file operations — coverage gap
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, coverage, cli-patterns]
---

Tests for `--dry-run` leave file creation, state persistence, and ID generation untouched. Both dry-run AND apply paths must be tested to catch real-world bugs.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
