---
name: skills-curation-phase-5-session-input-health-check
description: "Sub-skill of skills-curation: Phase 5 \u2014 Session-Input Health Check."
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Phase 5 — Session-Input Health Check

## Phase 5 — Session-Input Health Check


**Purpose**: verify that sessions are actually producing skill signals and that the pipeline is live.

**Checks:**

| Check | Pass condition | Failure action |
|-------|---------------|----------------|
| skill-learner hook fired | At least once in last 7 days (check `.claude/state/session-signals/`) | Warn: "skill-learner hook has gone quiet" |
| candidates populated | `skill-candidates.md` has at least one entry since last curation run | Warn: "no skill candidates in N days" |
| skills committed recently | At least one skill file changed in last 7 days (git log) | Warn: "no skill updates committed in N days" |
| session-signals directory non-empty | Files exist in `.claude/state/session-signals/` | Warn: "session signals not being captured" |

**Health check output:**

```
Skills pipeline health: OK | DEGRADED | SILENT

[OK]    skill-learner hook: last fired 2026-02-19
[OK]    skill candidates: 3 entries since last run
[WARN]  recent skill commits: none in 7 days
[OK]    session signals: 12 files captured
```

If any check fails → append a `health_warning` entry to `curation-log.yaml`.

---
