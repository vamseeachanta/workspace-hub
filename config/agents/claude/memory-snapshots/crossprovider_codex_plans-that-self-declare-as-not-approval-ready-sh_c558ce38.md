---
name: crossprovider codex plans-that-self-declare-as-not-approval-ready-sh
description: Plans that self-declare as not-approval-ready should not request approval
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-gates, self-reference-hazard]
---

When a plan header says "NOT APPROVAL-READY after Codex MAJOR" or explicitly lists requirements before approval is OK, that's evidence the plan contradicts its own approval request. Approval review should flag self-defeating claims and ask the user to either resolve blockers or formally waive the stated requirement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
