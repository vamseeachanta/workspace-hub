---
name: crossprovider codex multi-machine-learning-via-git-synced-state-file
description: Multi-machine learning via git-synced state files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, multi-machine, architecture]
---

Central orchestrator (ace-linux-1) runs learning pipeline while distributed machines contribute by committing state files (`candidates/`, `corrections/`, `patterns/`). Orchestrator `git pull` picks up all contributions before processing. Clean cross-machine data handoff.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
