---
name: session-analysis
description: First-class session mining — analyses every session's signals at 3AM to surface skill gaps, candidates, anti-patterns, and knowledge gaps; the foundation of the self-improving agent loop
version: 1.0.0
category: workspace-hub
type: skill
trigger: scheduled
cadence: per-session  # signal capture at session end; analysis at 3AM
auto_execute: true
capabilities:
  - signal_capture
  - skill_scoring
  - candidate_routing
  - gap_detection
  - wrk_item_creation
tools: [Read, Write, Edit, Bash, Grep, Glob]
related_skills: [agentic-horizon, work-queue, skill-learner, claude-reflect]
scripts:
  - scripts/analysis/session-analysis.sh
  - .claude/hooks/session-signals.sh
see_also:
  - .claude/work-queue/working/WRK-231.md
  - .claude/state/skill-scores.yaml
  - .claude/state/candidates/
  - .claude/state/session-signals/
---

# Session Analysis Skill

> The self-improving loop engine. Every session end captures raw signals; every 3AM those signals are analysed to improve skills, surface gaps, and identify automation candidates.

## Architecture

**Two-stage design** — hooks stay fast, analysis runs when time permits:

```
SESSION END (hook — <2s)
  └── .claude/hooks/session-signals.sh
        → writes .claude/state/session-signals/YYYY-MM-DD-HHMMSS.jsonl

3AM CRON (heavy analysis)
  └── scripts/analysis/session-analysis.sh
        → reads previous day's signals
        → updates skill-scores.yaml
        → populates state/candidates/
        → writes state/session-analysis/YYYY-MM-DD.md
        → creates WRK items for deep gaps
```

## Signal Format

Each session-end hook writes one JSONL line:
```json
{"ts":"...","event":"session_end","signals":{"skill_invocations":[],"tool_calls":[],"correction_events":[],"wrk_items_touched":[],"uncommitted_changes":false}}
```

## Candidate Routing

| Candidate type | File | Action |
|---------------|------|--------|
| Script | `state/candidates/script-candidates.md` | Bash sequences → scripts |
| Skill | `state/candidates/skill-candidates.md` | Patterns → skills |
| Hook | `state/candidates/hook-candidates.md` | Triggers → hooks |
| Agent | `state/candidates/agent-candidates.md` | Tasks → agent defs |
| MCP | `state/candidates/mcp-candidates.md` | Tools → MCP servers |

## Cron Schedule

| Time | Job | Machine |
|------|-----|---------|
| Session end | `session-signals.sh` | All machines |
| 3:00 AM | `session-analysis.sh` | `ace-linux-1` (primary aggregator) |
| 5:00 AM | `claude-reflect` | All machines |

## Cross-Machine

`ace-linux-1` is the primary aggregator. At 3AM it pulls signal files from other machines (git pull). If nothing arrived, analyses local sessions only.

## Quality Metric

Target: >80% of sessions produce at least one actionable output (gap WRK, skill target, or candidate). Tracked in `session-analysis/YYYY-MM-DD.md`.

## Usage

This skill is invoked automatically:
- `session-signals.sh` fires at every session Stop event (configured in Claude Code hooks)
- `session-analysis.sh` runs at 3AM via cron on ace-linux-1

Manual run for a specific date:
```bash
bash scripts/analysis/session-analysis.sh --date 2026-02-19
```

Force re-run (override idempotency guard):
```bash
FORCE_RERUN=true bash scripts/analysis/session-analysis.sh
```
