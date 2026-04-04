---
name: GSD migration complete
description: Old 20-stage WRK pipeline removed, GSD framework is now the sole workflow system
type: project
---

On 2026-03-25, the old 20-stage WRK pipeline was fully removed and replaced by GSD.

**Why:** 4% completion rate, 3100+ unused skill files, 35 hooks blocking work, 86 scripts overhead. GSD offloads workflow maintenance to a community-maintained framework.

**What was removed:**
- 268 work-queue scripts (scripts/work-queue/)
- 20 stage micro-skills + 100 files
- 7 enforcement hooks (enforce-active-stage, dispatch, human-gate, etc.)
- Agent wrapper scripts (scripts/agents/)
- Work-queue config (config/work-queue/ including reserved-wrk-ids.txt)
- 42MB of work-queue state (.claude/work-queue/)
- Old lifecycle docs, dispatch breadcrumbs, orchestrator skills

**What was kept:**
- Memory system, ecosystem terminology, domain skills
- Session signals (JSONL), corrections capture hook
- Essential hooks: check-encoding, session-logger, context-budget-monitor
- All GSD hooks and skills (57 skills, 5 hooks, 16 agents)

**How to apply:** No more WRK-NNN references. Tasks tracked as GitHub issues. Use `/gsd:*` commands for workflow. PROJECT.md still needs creation via `/gsd:new-project`.
