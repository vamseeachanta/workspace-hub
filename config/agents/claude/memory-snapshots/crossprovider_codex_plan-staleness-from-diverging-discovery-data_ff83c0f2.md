---
name: crossprovider codex plan-staleness-from-diverging-discovery-data
description: Plan staleness from diverging discovery data
metadata:
  type: reference
  source: codex
  bridged: 2026-06-25
  tags: [planning, maintenance, discovery]
---

Stale plans (e.g., workspace-hub #1579) drift from live filesystem state over time. When refreshing a plan, re-run discovery before declaring defects or constraints. Example: a plan based on 61 root entries was stale; live check found 63. Consider dating plans or including discovery-refresh gates in plan structure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
