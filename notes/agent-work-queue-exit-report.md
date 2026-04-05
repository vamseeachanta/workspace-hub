# Agent Work Queue System (#1857) — Session Exit Report

**Date:** 2026-04-04 to 2026-04-05
**Duration:** ~8 hrs active + 4 hrs overnight scheduling

## What Was Built

### 1. Deterministic Agent Routing via GitHub Labels
- 4 labels: agent:gemini (30 open), agent:claude (30 open), agent:codex (30 open)
- 145 total issues labeled across 3 agents
- Labels are the queue — visible in GitHub UI, queryable via gh CLI

### 2. Research Output: 25+ Documents Created

standards-mapping/ (5): hydrodynamics-standards-map.csv, structural/pipeline/materials/remaining-gaps
prep/ (9): subseaiq, geotech-textbooks, OSS-tools, hydro-refs, ship-plan, semantic-scholar, research-pipeline, chart-library
analysis/ (1): research-charts.py (working Plotaly code)
doc-intel/ (10): mount-drive-audit, taxonomy-all-domains, marine-subdomain, cross-ref, standards-ledger, OCR-index, dedup-audit, DDE-migration, conference-index, GTM-scan, Phase-B-plan, TDD-fixtures, SNAME-extraction, holistic-resource, OCR-registry, repo-roadmap, DDE-unique-file-index, marine-Excel, large-workbook, promotion-feedback

### 3. Queue Infrastructure
- notes/agent-work-queue.md (auto-generated from label queries)
- docs/plans/overnight-prompts-2026-04-07.md (nightly template)
- scripts/refresh-agent-work-queue.sh (weekly regeneration)

## Issues Closed Today

| Issue | Agent | What |
|-------|-------|------|
| #140 | voice | Use /voice in Claude Code instead of Whisper-flow |
| #1823 | Gemini | 20 hydro function-to-standard mappings |
| #1821 | Gemini | Structural gaps analysis (24 gaps) |
| #1822 | Gemini | Pipeline gaps analysis (13 gaps) |
| #1819 | Gemini | Materials gaps plan (93 gaps, 3 phases) |
| #1860 | Gemini | SubseaIQ data acquisition strategy |
| #1864 | Gemini | Geotech textbooks acquisition plan |
| #1397 | Gemini | OSS engineering tools 2026 update |
| #1624 | Gemini | Marine hydro refs (Faltinsen Newman Pinkster) |
| #152 | Gemini | Ship plan extraction strategy |
| #182 | Gemini | Semantic Scholar MCP setup guide |
| #120 | Gemini | Research-to-action pipeline design |
| #55 | Gemini | Anthropic-style chart library + code |
| #1875 | Gemini | Remaining domains gap analysis |
| #1896-1899 | system | Future sprint issues created |
| +107 | Gemini | 10 standards mapping docs created |

**Total: 14 + 107 (docs) = 121 items completed**

## Future Issues Created

| Issue | Agent | Purpose |
|-------|-------|---------|
| #1911 | Gemini | Cron batch failure — 20 tasks need manual execution |
| #1912 | Claude | 4-domain implementation sprint (25 sub-issues) |
| #1913 | Codex | 4-batch test coverage sprint (30 sub-issues) |

## Overnight Result

**Cron batches 1-4 did NOT execute.** All 4 show `last_run_at: null`. All 20 research tasks remain. The cronjob tool creates scheduled agents that run via the Gemini model, but the environment may not have the right credentials for the cron session to execute.

## How to Resume

### Option 1: Live Gemini session (recommended)
```bash
h-router-gemini -t terminal,file -q "<batch prompt for 5 tasks>"
```

### Option 2: Re-run cron with env fix
```bash
# Need to ensure OPENROUTER_API_KEY available in cron env
hermes cron list
hermes cron update <job-id> --env KEY=VALUE
```

### Option 3: Claude/Codex sprints for implementation work
```bash
# Field development
h-opus -q "Work on field development sprint #1897/#1912"
# Naval architecture
h-opus -q "Work on naval architecture sprint #1898/#1912"
# Test coverage
h-codex -q "Work on codex sprint #1908/#1913"
```

## Key Decisions

1. agent: labels live on issues themselves — no drift between queue and reality
2. Batched research (5 tasks/session) over individual calls — maximizes Gemini quota
3. Sprint issues group related tasks for focused Claude/Codex execution
4. Research/planning BEFORE implementation — Gemini does the heavy analysis, Claude codes
