---
name: crossprovider codex dry-run-outputs-local-artifacts-without-committi
description: Dry-run outputs local artifacts without committing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dry-run-semantics, testing-vs-production, git-workflow]
---

Running cron setup/apply with --dry-run renders all runtime files and topology outputs locally but skips git commit. Comparing dry-run output against production without re-running after actual commit can mask divergence between rendered and persisted state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
