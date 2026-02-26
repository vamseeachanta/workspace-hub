---
title: Predictive Session Planning
description: >
  Heuristic model that recommends which WRK items to tackle each session,
  based on task complexity, agent speed estimates, and available quota.
  Surfaces as "Today's recommended plan" via a readiness hook at session start.
version: "1.0"
module: platform
status: parked
progress: 60
phase: 3
blocked_by: []
created: "2026-02-24"
updated: "2026-02-24"
target_completion: "2026-05-01"
wrk_ref: WRK-182
related:
  - WRK-172
  - WRK-173
tags:
  - session-lifecycle
  - prediction
  - optimization
  - quota
review:
  status: pending
  required_iterations: 3
  current_iteration: 0
  reviewers:
    openai_codex: {status: pending}
    google_gemini: {status: pending}
    legal_sanity: {status: pending}
---

# Predictive Session Planning

> **Module**: platform | **Status**: parked (revisit May 2026) | **WRK**: WRK-182

## Executive Summary

Session planning today is reactive: the engineer scans the work queue manually,
picks items, and hopes quota holds. This spec defines a lightweight readiness
hook (`hooks/readiness/session-planner.sh`) that reads the work queue, the live
quota snapshot, and a per-complexity agent-speed table to output a ranked
"Today's recommended plan" at session start.

The heuristic is deliberately simple: no ML, no persistent model storage.
The core formula is `estimated_effort = complexity_weight * agent_speed_factor`.
Available quota is divided by total estimated effort to derive a completion
probability, which drives item selection.

**Disposition**: parked until May 2026. Session-awareness in Claude Code is
maturing rapidly; a platform-level capability may supersede this work.
The Phase 3 hook is implemented now as a useful, low-risk session aid.

---

## Problem Statement

| Symptom | Root Cause |
|---------|------------|
| Sessions exhaust quota mid-task | No pre-session effort estimation |
| Wrong provider chosen for task | No complexity-to-provider mapping |
| High-value items skipped | No daily prioritisation surface |
| WRK context rebuilt every session | No persistent "today's plan" artefact |

---

## Technical Context

| Aspect | Details |
|--------|---------|
| Language | Bash (hook), Python optional for data collection |
| Quota source | `config/ai-tools/agent-quota-latest.json` (WRK-172) |
| WRK data source | `.claude/work-queue/pending/*.md` YAML frontmatter |
| Session data | `.claude/state/session-reports/*.md` |
| Hook entry point | `.claude/hooks/readiness/session-planner.sh` |
| Invocation | PreToolUse (first call) via `readiness.sh` dispatcher |

### Dependencies

- [x] WRK-172 done — quota JSON at `config/ai-tools/agent-quota-latest.json`
- [x] WRK-173 done — session lifecycle documented; hook slot confirmed
- [ ] Phase 4 — session outcome feedback loop (future)

---

## Heuristic Model

### Complexity Weights

```
simple   → 1 unit   (~15 min effective agent time)
medium   → 3 units  (~45 min effective agent time)
complex  → 8 units  (~2 h effective agent time)
```

These weights are derived from observation of completed WRK items in
`.claude/work-queue/archive/2026-02/*.md`. They are constants in Phase 3 and
will be tunable via config in Phase 4.

### Agent Speed Factors

```
provider = claude  → 1.0  (baseline)
provider = codex   → 1.2  (faster on code-only tasks, lower context)
provider = gemini  → 0.9  (slightly slower due to manual quota management)
```

### Quota-to-Effort Mapping

```
quota_remaining_pct  = 100 - max(week_pct, sonnet_pct)
quota_units          = quota_remaining_pct * QUOTA_SCALE_FACTOR
QUOTA_SCALE_FACTOR   = 0.5  (empirical: 1% quota ≈ 0.5 effort units on average)

completion_probability(item) = min(100, quota_units / estimated_effort * 100)
```

### Provider Selection

Prefer the provider with the most remaining quota that matches the task tag:
- Tags `code`, `refactor`, `test` → prefer codex
- Tags `docs`, `research`, `spec` → prefer gemini
- Default → claude

If preferred provider is >80% consumed, downgrade to next available.

---

## Phases

### Phase 1: Collect Session Data (COMPLETE — latent in existing reports)

Session reports in `.claude/state/session-reports/*.md` record tool calls,
commits, and corrections per session. The complexity distribution of archived
WRK items provides baseline effort data.

**Deliverables**:
- [x] Session reports exist (1,417 reports as of 2026-02-24)
- [x] Archived WRK items have complexity + status fields
- [ ] `scripts/session-planning/extract-session-durations.sh` (Phase 4 prerequisite)

**Exit Criteria**:
- [x] At least 100 completed WRK items available for baseline (148 done items confirmed)

---

### Phase 2: Heuristic Model (COMPLETE — embedded in Phase 3 script)

The heuristic constants above were derived from the archive data. No separate
model artefact is stored at this phase; constants live directly in the hook.

**Exit Criteria**:
- [x] Complexity weights defined
- [x] Agent speed factors defined
- [x] Quota-to-effort formula specified

---

### Phase 3: session-planner.sh Hook (IMPLEMENTED)

**Objective**: Display "Today's recommended plan" at session start.

**Script**: `.claude/hooks/readiness/session-planner.sh`

**Behaviour**:
1. Read quota from `config/ai-tools/agent-quota-latest.json`
2. Read pending WRK items from `.claude/work-queue/pending/*.md`
3. Apply heuristic model to score each item
4. Output top-N items ranked by: priority weight × completion probability
5. Exit 0 always (non-blocking)

**Output format** (printed to stdout, consumed by readiness.sh context):
```
Session Plan (quota: claude 54% remaining):
  1. WRK-XXX  [simple/claude] ~15m  — Title here
  2. WRK-XXX  [medium/codex]  ~45m  — Title here
  3. WRK-XXX  [simple/gemini] ~15m  — Title here
  Total estimated: ~75m | Completion probability: 87%
```

**Exit Criteria**:
- [x] Script exists and is executable
- [x] Output is non-blocking (exits 0 even if quota file missing)
- [x] Respects existing readiness.sh lock (runs once per session)
- [ ] Output validated against real quota + queue data

---

### Phase 4: Feedback Loop (FUTURE — May 2026)

After each session, record which planned items were actually completed and
compare against predictions. Use delta to tune complexity weights.

**Deliverables** (not started):
- [ ] `scripts/session-planning/extract-session-durations.sh`
- [ ] `config/session-planning/complexity-weights.yaml` — tunable constants
- [ ] Stop hook to log session outcome vs plan
- [ ] Weekly calibration report

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Quota file stale | Medium | Low | Graceful degradation — skip prediction, show raw queue |
| Complexity weights wrong | High | Low | Weights are visible constants; easy to tune |
| WRK YAML parse failure | Low | Low | Skip malformed files, continue with valid ones |
| Platform supersedes (Claude native) | High | Positive | Park hook if native planning appears; remove cleanly |

---

## File Map

```
.claude/hooks/readiness/
  session-planner.sh         # NEW — Phase 3 hook

scripts/session-planning/    # FUTURE — Phase 4 data collection
  extract-session-durations.sh

config/session-planning/     # FUTURE — Phase 4 tunable config
  complexity-weights.yaml

specs/modules/
  predictive-session-planning.md  # THIS FILE
```

---

## Cross-Review Process

| Gate | Status |
|------|--------|
| Minimum iterations (3) | Pending |
| Legal sanity | Pending |
| OpenAI Codex | Pending |
| Google Gemini | Pending |
| Ready for next step | BLOCKED — parked until May 2026 |

---

## Agentic AI Horizon

Session planning AI will improve substantially. Models with better planning
and quota-awareness will handle this natively in 3-4 months.

**Disposition: park 3 months** — revisit May 2026 when session-awareness in
Claude Code has matured. The Phase 3 hook is a useful interim aid that can be
removed cleanly if native planning appears.

---

*Spec generated 2026-02-24 for WRK-182*
