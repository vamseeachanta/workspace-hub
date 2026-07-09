---
name: crossprovider codex section-level-recently-added-metadata-can-t-rely
description: Section-level 'recently added' metadata can't rely on file-level git history
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [spec-validation, git-metadata, section-tracking]
---

Sections and content live inside files; `git log` on a file doesn't capture in-file additions or modifications. When specs rely on 'recently added' metadata or naming-based identifiers (section-id, explorer-stem), use explicit section-level anchor tracking and add CI tests that validate bijection between spec sections and backend code/data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
