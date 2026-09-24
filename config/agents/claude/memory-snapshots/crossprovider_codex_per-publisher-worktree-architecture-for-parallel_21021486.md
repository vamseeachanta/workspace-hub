---
name: crossprovider codex per-publisher-worktree-architecture-for-parallel
description: Per-Publisher Worktree Architecture for Parallel Ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parallel-ingest, worktree-isolation, sequencing]
---

Parallelize ingest ACROSS publishers (concurrency cap ≤3), not across chunks. Each publisher gets a dedicated git worktree (git worktree add -b ingest/<slug>-corpus); chunks within that publisher run SEQUENTIALLY and commit their own changes (git add -A, then git commit). This avoids conflicts on shared per-domain index.md/log.md/_verification-queue.csv and lets chunk output accumulate correctly for the next chunk.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
