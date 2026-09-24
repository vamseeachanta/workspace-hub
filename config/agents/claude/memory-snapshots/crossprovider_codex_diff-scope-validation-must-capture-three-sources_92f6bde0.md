---
name: crossprovider codex diff-scope-validation-must-capture-three-sources
description: Diff-scope validation must capture three sources of file changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, scope-creep, git-patterns, governance]
---

When validating whether implementation stays within approved scope (e.g., checking forbidden paths), enumerate all three sources: committed diff (`git diff --name-only <base>...HEAD`), current staging (`git diff --name-only`), and untracked files (`git ls-files --others --exclude-standard`). Using only `git diff HEAD` allows scope creep into uncommitted/untracked surfaces.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
