---
name: crossprovider codex universal-gitattributes-adoption-in-chain-ingest
description: Universal .gitattributes adoption in chain ingest pipelines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, ingest-pipeline, merge-driver, worktree, chain-processing]
---

In multi-publisher ingest workflows where each publisher creates a worktree and merges from parent/main, .gitattributes adoption must run for every publisher (both chain heads and children) immediately after worktree creation and before any merges. Running adoption only for chain heads leaves children vulnerable to conflicts on append-only files because their merges run before .gitattributes is staged.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
