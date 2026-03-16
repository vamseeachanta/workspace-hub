---
name: session-start
description: "Session startup briefing \u2014 surfaces readiness warnings, last session\
  \ snapshot, top 3 unblocked pending work items, and quota status. Run at the beginning\
  \ of every session before starting work.\n"
version: 1.0.0
updated: 2026-02-19
category: workspace-hub
triggers:
- session start
- start session
- morning briefing
- what should I work on
- session briefing
- startup check
related_skills:
- save
- work-queue
- workflow-gatepass
- improve
capabilities:
- readiness-surface
- snapshot-surface
- queue-briefing
- quota-check
requires: []
invoke: session-start
tags: []
see_also:
- session-start-0-auto-load-drift-risk-rules-non-interactive-2s
- session-start-output-format
- session-start-session-briefing-2026-02-19
- session-start-path-discipline-reminder
- session-start-hook-integration
---

# Session Start

## When to Use

- First action in every new session (before responding to any work request)
- After `/clear` (context was wiped — re-orient)
- When returning from a multi-day break

## Sub-Skills

- [0. Auto-Load Drift-Risk Rules (non-interactive, < 2s) (+12)](0-auto-load-drift-risk-rules-non-interactive-2s/SKILL.md)
- [Output Format](output-format/SKILL.md)
- [Session Briefing — 2026-02-19](session-briefing-2026-02-19/SKILL.md)
- [Path Discipline Reminder](path-discipline-reminder/SKILL.md)
- [Hook Integration](hook-integration/SKILL.md)
