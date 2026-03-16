---
name: comprehensive-learning
description: 'Single fire-and-forget command that runs the full session learning pipeline:
  insights → reflect → knowledge → improve → action-candidates → report. All machines
  run local Phases 1–9 against logs/orchestrator/ and commit derived state. ace-linux-1
  additionally runs Phase 10a (cross-machine compilation) and Phase 10 (report). Safe
  for cron scheduling. Use when session ends, nightly cron fires, or you want to harvest
  learnings from recent sessions. Replaces running 4 skills manually.

  '
version: 2.5.0
updated: 2026-03-09
category: workspace-hub
type: skill
invoke: comprehensive-learning
auto_execute: false
tools:
- Read
- Write
- Edit
- Bash
- Grep
- Glob
- Task
related_skills:
- improve
- claude-reflect
- knowledge-management
- session-end
- workstations
capabilities:
- session-learning
- ecosystem-improvement
- candidate-actioning
- cron-safe
- continual-learning
- cross-machine-analysis
tags:
- learning
- meta
- session-exit
- cron
- continual-learning
platforms:
- linux
wrk_ref: WRK-299
---
# comprehensive-learning — Session Learning Pipeline

Single fire-and-forget skill running Phases 1–9 on **all machines** and Phases 10a+10
(cross-machine compilation + report) on **ace-linux-1 only**.

> **Full phase specs**: `references/pipeline-detail.md` — read it when you need
> signal sources, extraction rules, candidate formats, or state file details.

## Mode-Based Routing

```bash
MACHINE=$(hostname -s 2>/dev/null || hostname | cut -d. -f1 | tr '[:upper:]' '[:lower:]')
case "$MACHINE" in
  ace-linux-1) CL_MODE="full" ;;
  ace-linux-2) CL_MODE="contribute" ;;
  acma-ansys05|acma-ws014) CL_MODE="contribute" ;;
  *) CL_MODE="contribute" ;;
esac
# All modes run Phases 1–9. Only 'full' runs Phase 10a (compilation) + Phase 10 (report).
```

## Cross-Machine Data Flow

| Machine | Commits | Notes |
|---------|---------|-------|
| ace-linux-2 | `candidates/`, `corrections/`, `patterns/`, `session-signals/` | Open-source CFD/dev |
| acma-ansys05 | `candidates/`, `corrections/`, `session-signals/`, `patterns/` | OrcaFlex/ANSYS |
| acma-ws014 | `candidates/` | Windows; no AI CLIs |

ace-linux-1 `git pull` in Phase 10a picks up all machines' committed derived state.

## Pipeline Summary

Run phases sequentially. Non-mandatory phases log failure and continue. Fatal failures
in Phases 1 or 4 set `_PIPELINE_EXIT=1`. Phase 10 always runs via `trap EXIT`.

| Phase | Name | Mandatory | Short description |
|-------|------|:---------:|-------------------|
| 1 | Insights | ✓ | Extract skill usage, tool patterns, session-quality signals from all log sources |
| 1b | Drift Detection | ace-linux-1 | Detect python_runtime/file_placement/git_workflow violations in yesterday's log |
| 2 | Reflect | — | Invoke /reflect against reflect-history/ and trends/ |
| 3 | Knowledge | — | Invoke /knowledge; update patterns/ |
| 3b | Memory Compaction | — | Compact MEMORY.md + topic files |
| 3c | Memory Curation | — | Promote stable patterns, expire stale entries |
| 4 | Improve | ✓ | Invoke /improve; update skills + rules from candidates/ |
| 5 | Correction Trends | — | Analyze corrections/ for recurring failure patterns |
| 6 | WRK Feedback + Ecosystem | — | WRK quality review + skill usage frequency + ecosystem health |
| 7 | Action Candidates | — | Convert candidates/ entries to WRK items |
| 8 | Report Review | — | Review learning report for coherence |
| 9 | Skill Coverage Audit | weekly | Audit skill coverage via `identify-script-candidates.sh` + `skill-coverage-audit.sh` |
| 10a | Cross-Machine Compile | full only | git pull + aggregate from all machines |
| 10 | Report | always | Write report (trap EXIT) |

**For phase details** (signal sources, extraction rules, YAML formats):
→ read `references/pipeline-detail.md`

## Session Design: Lean by Default

Sessions are pure **multi-agent execution engines** — all brain directed at the task.
Analysis, maintenance, and learning are deferred to the nightly run.

| In-session | Nightly pipeline |
|------------|-----------------|
| WRK gate check + active-wrk set | All insight/reflect/knowledge/improve runs |
| Multi-agent implementation | Correction trend analysis |
| Fast signal capture (hooks write raw signals) | Candidate → WRK auto-creation |
| /session-start context load | Memory and skill file updates |
| Cross-review (Codex gate) | Ecosystem health checks |
| Commit + push | Session archive rsync |

**Must NOT run standalone during sessions:** `/insights`, `/reflect`, `/knowledge`,
`/improve`, `consume-signals.sh` heavy analysis, `ecosystem-health-check.sh`,
`session-end-evaluate.sh` scoring.

**Stop hooks:** one hook only, raw write, < 1 second. See WRK-304.

## Scheduling

Crontab entry (ace-linux-1, 22:00 nightly):
```bash
0 22 * * * cd /mnt/local-analysis/workspace-hub && \
  bash scripts/cron/comprehensive-learning-nightly.sh \
  >> .claude/state/learning-reports/cron.log 2>&1
```
Script: `scripts/cron/comprehensive-learning-nightly.sh`
— `git pull` is a hard gate; each `rsync` is independently `|| true`.

## Related

- workstations skill: machine registry and `cron_variant` fields
- WRK-299: implementation tracking | WRK-304: Stop hook cleanup | WRK-305: signal emitters
- WRK-303: Ensemble planning → Planning Quality Loop (in references/pipeline-detail.md)
- `/insights`, `/reflect`, `/knowledge`, `/improve`: individual pipeline stages
- `scripts/planning/` — ensemble planning outputs harvested by Planning Quality Loop
