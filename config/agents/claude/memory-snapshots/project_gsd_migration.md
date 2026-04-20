---
name: GSD migration complete
description: Old 20-stage WRK pipeline removed 2026-03-25, GSD is sole workflow — now at v1.38.1, Node.js 24+ required
type: project
originSessionId: 57335aaf-c168-418e-9e12-dafe06cf553a
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
- v1.36.0 — confirmed installed as of 2026-04-17 via `/gsd:update` (no-op, already on latest). LOCAL scope under `./.claude/`.
- v1.38.1 — installed 2026-04-19 via `/gsd:update` (1.36.0 → 1.38.1, npm tagged patch newer than 1.38.0). LOCAL scope. 9 files from v1.34.1 era backed up to `gsd-local-patches/`; run `/gsd-reapply-patches` to merge.

**Node.js requirement:** GSD v1.38.1 requires Node.js 24+. On this machine: `/usr/bin/node` is v24.14.1 as of 2026-04-19, installed from NodeSource apt repo (`/etc/apt/sources.list.d/nodesource.sources`, tracks node_24.x). Upgrade path: `sudo apt update && sudo apt upgrade nodejs`. No version manager in use (no nvm/fnm/n/volta).

**How to apply:** No more WRK-NNN references. Tasks tracked as GitHub issues. Use `/gsd:*` commands for workflow. After updates, run `/gsd:reapply-patches` to restore local customizations.
