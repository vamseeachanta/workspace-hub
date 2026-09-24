---
name: crossprovider codex multi-item-follow-ups-must-require-all-items-to-
description: Multi-item follow-ups must require ALL items to clear parent state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-phase-work, parent-tracking, state-management]
---

When a parent issue (e.g., #725) is blocked by multiple child work items (#746 and #747), the clearance logic must check that BOTH are implemented, not just the first. A partial implementation that clears on #746 alone creates false-ready state in parent systems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
