---
name: crossprovider codex isolated-worktrees-committed-head-authority-prev
description: Isolated worktrees + committed HEAD authority prevents silent contamination in parallel development
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [workflow, git-isolation, concurrent-development, quality-gate]
---

When multiple sessions work in parallel, supposedly 'isolated' implementation branches can receive unauthorized modifications during audit phases. Enforce separate worktrees per agent, treat only committed HEAD as authoritative for review decisions, and preserve contaminated worktrees as evidence rather than merging them forward.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
