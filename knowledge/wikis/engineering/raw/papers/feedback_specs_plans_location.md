> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_specs_plans_location.md

---
name: Specs and plans co-located with their workflow state
description: Convention — specs, plans, and research co-locate with their phase in .planning/
type: feedback
---

Specs and plans must co-locate with their workflow state, not scatter across docs directories.

**Why:** Disconnected specs and plans get lost. Co-location keeps everything for a unit of work in one place.

**How to apply (GSD era, post 2026-03-25):**
- Plans: `.planning/phases/<N>/PLAN.md`
- Research: `.planning/phases/<N>/RESEARCH.md`
- State: `.planning/STATE.md`, `.planning/ROADMAP.md`
- Previous convention (WRK pipeline, removed 2026-03-25) used `.claude/work-queue/assets/WRK-<ID>/` — no longer applicable
