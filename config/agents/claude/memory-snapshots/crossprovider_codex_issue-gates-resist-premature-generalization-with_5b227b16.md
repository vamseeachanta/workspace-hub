---
name: crossprovider codex issue-gates-resist-premature-generalization-with
description: Issue gates resist premature generalization without explicit approval
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [contracts, issue-gating, dependencies]
---

Selectors and snapshot modes (e.g., #68's review artifact selectors) are intentionally pinned to a specific issue/gate. Do not mutate them for cross-gate use or assume they're generic until an explicit generalization gate (#72) approves. Each gate owns its selectors until handoff is formalized.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
