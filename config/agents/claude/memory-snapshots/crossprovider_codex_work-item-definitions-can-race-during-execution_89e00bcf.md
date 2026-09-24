---
name: crossprovider codex work-item-definitions-can-race-during-execution
description: Work item definitions can race during execution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [work-queue, concurrency, state-sync, operational-risk]
---

WRK items can be modified concurrently (title, fields, frontmatter) during orchestration execution. Validator may find different copies than the one being edited. Requires synchronization check and validator re-run if state diverges.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
