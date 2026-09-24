---
name: crossprovider codex terminal-hold-states-plus-orphaned-follow-up-ref
description: Terminal hold-states plus orphaned follow-up references create workflow/gate risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [disposition-ledgers, issue-tracking, semantic-correctness]
---

Assigning rows to 'hold for owner review' as a terminal disposition while referencing follow-up work via placeholder strings (e.g., 'required-extraction-plan-issue') orphans that follow-up and makes it invisible to lifecycle tracking. Follow-up actions must be concrete GitHub issue refs (#NNNN) or the disposition is incomplete. A terminal state that doesn't actually resolve pending work leaves the issue ready to close while follow-up gates remain undiscovered.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
