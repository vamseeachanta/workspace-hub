---
name: crossprovider gemini machine-aware-skill-routing-prevents-duplicate-w
description: Machine-aware skill routing prevents duplicate work in multi-machine setups
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [multi-machine, skill-routing, cron-safety]
---

comprehensive-learning skill determines execution mode (full/skip-candidates/lightweight) at runtime based on hostname. Secondary machines like ace-linux-2 skip Phase 5 (candidate actioning) to avoid duplicate WRK item creation when ace-linux-1 runs concurrently. Prevents redundant work-queue pollution in multi-machine environments.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
