---
name: crossprovider codex scope-containment-child-issues-must-not-absorb-p
description: Scope containment: child issues must not absorb parent-layer details
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [issue-decomposition, scope, planning]
---

Layered issue decomposition requires strict scope gates. Parent issue (#2726) defines cross-layer contract; child issues (#2727/#2728/#2729) refine their own layer only by consuming parent contract, not redefining upstream/downstream. Review catches scope creep via explicit parent/child declarations and "sequencing boundaries" sections.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
