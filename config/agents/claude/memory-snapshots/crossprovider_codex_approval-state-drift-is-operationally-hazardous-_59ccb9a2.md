---
name: crossprovider codex approval-state-drift-is-operationally-hazardous-
description: Approval-state drift is operationally hazardous and must be explicit
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-gates, git-state, status-tracking]
---

Stale local `.planning/plan-approved/<issue>.md` markers and live GitHub `status:plan-approved` labels can reflect older approval revisions, not current draft. Plans must evidence this drift with timestamps (file mtime, git log) and operationally describe what gate corrections are needed (close stale marker, relabel issue).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
