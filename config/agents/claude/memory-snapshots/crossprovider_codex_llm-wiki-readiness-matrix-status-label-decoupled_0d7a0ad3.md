---
name: crossprovider codex llm-wiki-readiness-matrix-status-label-decoupled
description: llm-wiki readiness matrix: status label decoupled from gate resolution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, state-semantics, lifecycle-management]
---

Issues marked `current_gate: implemented` can still carry unresolved human-disposition blockers in `next_issue_ref` (e.g., #719 implemented but #647 still open). Status labels alone are misleading; always verify next_issue_ref points to the actual blocker, not an outdated issue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
