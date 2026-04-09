---
name: GSD migration complete
description: Old 20-stage WRK pipeline removed 2026-03-25, GSD is sole workflow — now at v1.34.1, Node.js 24+ required
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

**Version history:**
- v1.30.0 — installed as of 2026-03-25
- v1.34.1 — updated 2026-04-07 (session 3ea978b9). 124 locally modified files backed up to `gsd-local-patches/`, mostly Windows→Linux path diffs from cross-machine sync. Patches reapplied; most were mechanical (path normalization, `/gsd:xxx` → `/gsd-xxx` format migration).

**Node.js requirement:** GSD v1.34.1 requires Node.js 24+. Currently on v22.22.2 — may cause issues with newer features. Upgrade pending.

**How to apply:** No more WRK-NNN references. Tasks tracked as GitHub issues. Use `/gsd:*` commands for workflow. After updates, run `/gsd:reapply-patches` to restore local customizations.
