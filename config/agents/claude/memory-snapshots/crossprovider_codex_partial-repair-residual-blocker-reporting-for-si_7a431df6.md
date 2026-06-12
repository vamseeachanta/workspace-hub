---
name: crossprovider codex partial-repair-residual-blocker-reporting-for-si
description: Partial repair + residual blocker reporting for sibling SSoT sync
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [sso, repair, resilience]
---

Allow repairable sibling work to complete while reporting blocked repos (missing AGENTS.md, divergent contracts) instead of aborting on first blocker. Avoids cascading all-or-nothing failures and lets operators see progress on repairable repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
