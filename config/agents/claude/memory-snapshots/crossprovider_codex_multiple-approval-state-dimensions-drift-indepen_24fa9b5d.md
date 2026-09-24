---
name: crossprovider codex multiple-approval-state-dimensions-drift-indepen
description: Multiple approval state dimensions drift independently and require aligned verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-freshness, approval-consistency, multi-dimension-drift]
---

Local plan file version, approval marker SHA, branch HEAD, and GitHub label can diverge independently. Gate verification requires checking all four; if any misalign (e.g., stale v1 plan while approval binds to v2, or missing marker file despite label), implementation is unsafe and requires evidence-based blocking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
