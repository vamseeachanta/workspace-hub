---
name: crossprovider hermes issue-executability-requires-both-agent-claude-a
description: Issue executability requires both agent:claude AND status:plan-approved labels; 7/10 currently meet gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github, issue-triage, execution-gates, labeling]
---

GitHub issues are directly executable in Claude Code only when they have both labels simultaneously. Without status:plan-approved, even agent:claude-tagged issues block on approval gate. Current workspace-hub has 7 directly executable, 3 near-ready but gated.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
