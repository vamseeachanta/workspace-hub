---
name: crossprovider gemini stop-hooks-are-ideal-for-automated-cleanup-at-ev
description: Stop hooks are ideal for automated cleanup at every stage gate
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [hooks, automation, maintenance]
---

Stop hooks fire at the end of each stage (1-20) and provide a clean checkpoint for maintenance: tidy-agent-teams.sh runs after Stage 20 complete to delete archived WRK teams and purge orphaned >7d task dirs. No separate scheduler needed; hook lifecycle is automatic.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
