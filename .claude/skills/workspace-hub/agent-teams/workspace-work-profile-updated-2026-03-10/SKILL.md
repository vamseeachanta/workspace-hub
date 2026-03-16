---
name: agent-teams-workspace-work-profile-updated-2026-03-10
description: 'Sub-skill of agent-teams: Workspace Work Profile (Updated 2026-03-10).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Workspace Work Profile (Updated 2026-03-10)

## Workspace Work Profile (Updated 2026-03-10)


This workspace is **engineering-heavy with sequential solver pipelines**. Most
work does NOT benefit from teams. Use this table before spawning:

| Work Type | Team Useful? | Notes |
|-----------|-------------|-------|
| OrcaWave/AQWA solver runs | **No** | Sequential: mesh → solve → validate → report |
| WRK item staged pipeline | **No** | Each stage depends on previous stage output |
| Cross-review (Claude/Codex/Gemini) | **No** | Already scripted via `cross-review.sh` |
| L01–L06 validation cases | **Maybe** | Cases are independent — 2-3 agents viable |
| Multi-repo exploration | **Maybe** | Parallel file reads across submodules |
| Documentation/reporting | **No** | Single-pass generation |
| Bulk transforms (50+ files) | **Yes** | One agent per batch |

**Key insight**: The biggest efficiency gain in this workspace comes from
**better WRK scoping** (1-2 goals per session), not from parallelising with
teams. Use teams only when tasks are genuinely independent AND > 20 min each.
