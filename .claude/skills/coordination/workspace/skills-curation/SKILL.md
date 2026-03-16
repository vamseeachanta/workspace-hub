---
name: skills-curation
description: "Periodic skills library maintenance \u2014 online research for new/stale\
  \ skills, knowledge graph review against active WRK items, session-input health\
  \ check, and autonomous skill creation or WRK spin-off for deep gaps."
version: 1.0.0
category: coordination
type: skill
trigger: scheduled
cadence: dynamic
auto_execute: true
standing: true
capabilities:
- online_research
- knowledge_graph_review
- gap_triage
- skill_stub_creation
- wrk_item_creation
- session_input_health_check
- yield_tracking
- cadence_adjustment
tools:
- Read
- Write
- Edit
- Bash
- Grep
- Glob
- WebSearch
- Task
related_skills:
- session-analysis
- skill-learner
- knowledge-manager
- agentic-horizon
- work-queue
scripts:
- scripts/analysis/session-analysis.sh
- .claude/hooks/session-signals.sh
see_also:
- skills-curation-when-this-runs
- skills-curation-architecture
- skills-curation-phase-1-session-candidate-intake
- skills-curation-candidates
- skills-curation-phase-2-knowledge-graph-review
- skills-curation-phase-3-online-research
- skills-curation-shallow-gap
- skills-curation-skill-stub-creation-shallow-gaps
- skills-curation-what-this-skill-does
- skills-curation-status
- skills-curation-source-signal
- skills-curation-steps
- skills-curation-phase-5-session-input-health-check
- skills-curation-phase-6-yield-tracking-and-cadence-adjustment
- skills-curation-curation-log-format
- skills-curation-cron-schedule
- skills-curation-execution-checklist
- skills-curation-session-analysis
- skills-curation-error-handling
requires: []
tags: []
---

# Skills Curation

## Quick Start

```bash
# Manual trigger
/skills-curation

# Force a run regardless of cadence schedule
/skills-curation --force

# Run only graph review (no web search)
/skills-curation --graph-only

# Run only health check
/skills-curation --health-check
```

## Related Skills

- [session-analysis](../session-analysis/SKILL.md) — populates skill-candidates.md
- [skill-learner](../skill-learner/SKILL.md) — post-commit skill extraction
- [knowledge-manager](../knowledge-manager/SKILL.md) — broader knowledge capture
- [agentic-horizon](../agentic-horizon/SKILL.md) — WRK item disposition management
- [work-queue](../work-queue/SKILL.md) — WRK item lifecycle

---

## Version History

- **1.0.0** (2026-02-20): Initial release — three-pipeline curation (session candidates, graph review, online research), gap triage (shallow auto-create / deep WRK spin-off), session-input health check, yield tracking, dynamic cadence adjustment.

## Sub-Skills

- [When This Runs](when-this-runs/SKILL.md)
- [Architecture](architecture/SKILL.md)
- [Phase 1 — Session Candidate Intake](phase-1-session-candidate-intake/SKILL.md)
- [Candidates](candidates/SKILL.md)
- [Phase 2 — Knowledge Graph Review](phase-2-knowledge-graph-review/SKILL.md)
- [Phase 3 — Online Research](phase-3-online-research/SKILL.md)
- [Shallow Gap (+1)](shallow-gap/SKILL.md)
- [Skill Stub Creation (Shallow Gaps)](skill-stub-creation-shallow-gaps/SKILL.md)
- [What This Skill Does](what-this-skill-does/SKILL.md)
- [Status](status/SKILL.md)
- [Source Signal](source-signal/SKILL.md)
- [Steps (+1)](steps/SKILL.md)
- [Phase 5 — Session-Input Health Check](phase-5-session-input-health-check/SKILL.md)
- [Phase 6 — Yield Tracking and Cadence Adjustment](phase-6-yield-tracking-and-cadence-adjustment/SKILL.md)
- [Curation Log Format](curation-log-format/SKILL.md)
- [Cron Schedule](cron-schedule/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [session-analysis (+3)](session-analysis/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
