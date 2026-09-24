---
name: crossprovider codex checklist-based-stage-boundaries-require-explici
description: Checklist-based stage boundaries require explicit STOP guards to prevent stage bleeding
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [stage-design, boundary-enforcement, agent-scope]
---

Without structural boundaries between stages, Task agents can drift into next-stage work (e.g., writing planning artifacts when only Stage 2 resource-intelligence is requested). Explicit '⛔ STOP — Stage N exit point. Write [artifact] then halt.' guards are necessary; for Stage 2/16 resource-intelligence, guard must distinguish which artifact each stage produces (Stage 2→evidence/resource-intelligence.yaml vs. Stage 16→evidence/resource-intelligence-update.yaml).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
