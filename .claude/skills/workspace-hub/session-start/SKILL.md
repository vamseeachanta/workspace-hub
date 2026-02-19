---
name: session-start
description: >
  Session startup briefing — surfaces readiness warnings, last session snapshot,
  top 3 unblocked pending work items, and quota status. Run at the beginning of
  every session before starting work.
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
  - workspace-hub/save
  - workspace-hub/work
  - workspace-hub/improve
capabilities:
  - readiness-surface
  - snapshot-surface
  - queue-briefing
  - quota-check
requires: []
invoke: session-start
---
# Session Start Skill

Run at the start of every session. Surfaces state from the previous session
and orients the orchestrator before any work begins.

## When to Use

- First action in every new session (before responding to any work request)
- After `/clear` (context was wiped — re-orient)
- When returning from a multi-day break

## Steps Claude Follows

### 1. Readiness Report (from last session's stop hook)

Read `.claude/state/readiness-report.md`. If it contains `## Warnings`, surface each
warning to the user with the suggested fix. If "All Clear", note it briefly.

### 2. Session Snapshot (from /save before last /clear)

Read `.claude/state/session-snapshot.md`. If the snapshot is less than 48 hours old
(check the timestamp in the file), surface the `## Ideas / Notes` section and the
WRK summary. If older than 48h, skip.

### 3. Quota Status

Read `config/ai-tools/agent-quota-latest.json`. Surface the weekly utilization for
each provider:
- >=90%: warn (route tasks to alternative provider)
- 70-89%: note (approaching limit)
- <70%: no comment needed

If the cache file is older than 4 hours, note that quota data may be stale.

### 4. Top 3 Unblocked Items

Scan `.claude/work-queue/pending/` for items where `blocked_by: []` (or no blocked_by
field). Show the top 3 by priority (high > medium > low), then by ID (lowest first).
For each item show: ID, title, complexity, tags (first 2).

### 5. Computer Context

If a `computer:` field exists in recent working/ items or in `.claude/state/`,
note which machine was last active. Prompt user to confirm if working on a different
machine today (multi-machine handoff check).

## Output Format

```
## Session Briefing — 2026-02-19

**Readiness:** [All Clear | N warnings listed]
**Snapshot:** [Summary of Ideas/Notes if fresh | None]
**Quota:** Claude 11% | Codex 43% | Gemini 0%

**Top 3 unblocked items:**
1. WRK-XXX — Title (complexity, tags)
2. WRK-YYY — Title (complexity, tags)
3. WRK-ZZZ — Title (complexity, tags)
```

## Hook Integration

This skill is also invocable as a startup context. Add to CLAUDE.md:
> At the start of every new session, run `/session-start` to orient before responding.
