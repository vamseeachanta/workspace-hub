---
name: crossprovider codex untracked-generated-artifacts-hide-wip-completen
description: Untracked generated artifacts hide WIP completeness from tracked commits
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [git, testing, deliverables]
---

Generated files (reports, configs, test fixtures) that exist locally but aren't tracked can pass local test runs while remaining entirely absent from `git commit`/PR. If plan deliverables include generated outputs, track them explicitly or acknowledge them as out-of-scope; untracked files mask incomplete implementations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
