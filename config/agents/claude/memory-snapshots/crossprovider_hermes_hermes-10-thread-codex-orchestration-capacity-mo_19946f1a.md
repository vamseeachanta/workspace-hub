---
name: crossprovider hermes hermes-10-thread-codex-orchestration-capacity-mo
description: Hermes 10-thread Codex orchestration capacity model
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex-orchestration, capacity-planning, lane-management]
---

Maintain ~10 parallel Codex work threads in isolated worktrees. Directory root: `/mnt/local-analysis/codex-10thread-YYYYMMDD-existing/` with prompts/ and lanes.tsv. Classify lanes: RUNNING, READY_FOR_REVIEW, STALLED_NO_OUTPUT, BLOCKED. Top up on schedule until reset window; weekly quota typically 40%+ remaining for productive burn.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
