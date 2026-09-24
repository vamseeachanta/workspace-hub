---
name: crossprovider codex context-budget-hard-stop-at-70-prevents-silent-m
description: Context budget hard-stop at 70% prevents silent mid-session compaction
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [context-management, checkpoint, stage-guard]
---

start-stage.sh must measure entry_reads total size against context_budget_kb; if ≥70%, HARD STOP and prompt /checkpoint before advancing. This prevents the hard-stop instruction set from being silently compressed away mid-workflow, which was a root cause of stage jumping in prior WRK cycles.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
