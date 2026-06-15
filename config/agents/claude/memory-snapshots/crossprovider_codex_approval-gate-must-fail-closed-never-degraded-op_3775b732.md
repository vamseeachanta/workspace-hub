---
name: crossprovider codex approval-gate-must-fail-closed-never-degraded-op
description: Approval gate must fail-closed, never degraded-open
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, approval-gate, git-workflow]
---

Security gates must block (exit non-zero) when config/owners/ruleset cannot be verified. A fallback that 'warns instead of blocks' before config is in place violates acceptance criteria and creates a trust gap. Degraded-open behavior is unacceptable for approval gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
