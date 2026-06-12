---
name: crossprovider hermes overnight-issue-loops-need-pre-validated-depende
description: Overnight issue loops need pre-validated dependency chains
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow, github-issues, automation]
---

All 6 plan-approved issues blocked by unresolved dependencies; overnight loop discovered this after queuing. Filter overnight candidates upfront to remove blocked issues; validate full dependency DAG before execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
