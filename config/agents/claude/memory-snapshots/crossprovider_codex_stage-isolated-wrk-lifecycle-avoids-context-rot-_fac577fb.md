---
name: crossprovider codex stage-isolated-wrk-lifecycle-avoids-context-rot-
description: Stage-isolated WRK lifecycle avoids context rot and enables per-stage quality scaling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-architecture, context-management, stage-isolation]
---

The 20-stage WRK model spawns fresh Task agents for autonomous stages (2–4, 8–9, 11–16, 18–20) and runs human gates (5, 7, 17) in-session. Each stage enters with zero context from prior noise, preventing hard-stop compaction mid-workflow and allowing stage-specific context budgets and review depth (light=4KB, medium=8KB, heavy=16KB).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
