# Session-to-Summary Report Pipeline

**Version:** 1.0.0
**Module:** workspace-hub/session-reports
**Session ID:** snappy-purring-sunset
**Agent:** claude-opus-4-5

---

## Overview

Integrate claude-reflect, daily-reflect (same system), and insights into a **session-end hook** that produces individual session reports. These reports roll up into daily summaries, which roll up into weekly summaries.

```
Session Report (after each session)
    ↓ aggregates into
Daily Summary (end of day / on-demand)
    ↓ aggregates into
Weekly Summary (existing from claude-reflect)
```

---

## Current State

| Component | Status | Location |
|-----------|--------|----------|
| `session-end-evaluate.sh` | Exists | `.claude/hooks/session-memory/` |
| `capture-corrections.sh` | Exists | `.claude/hooks/` |
| `daily-reflect.sh` | Exists | `.claude/skills/coordination/workspace/claude-reflect/scripts/` |
| `reflect-state.yaml` | Exists | `.claude/state/` |
| Weekly reports | Exists | Generated on Sundays by `generate-report.sh` |

**Gap:** No structured session reports or daily summary aggregation.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SESSION END HOOK                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ session-end-    │    │ capture-        │                    │
│  │ evaluate.sh     │    │ corrections.sh  │                    │
│  │ (existing)      │    │ (existing)      │                    │
│  └────────┬────────┘    └────────┬────────┘                    │
│           │                      │                              │
│           └──────────┬───────────┘                              │
│                      ▼                                          │
│           ┌─────────────────────┐                               │
│           │ generate-session-   │  ← NEW                        │
│           │ report.sh           │                               │
│           └──────────┬──────────┘                               │
│                      │                                          │
│                      ▼                                          │
│           ┌─────────────────────┐                               │
│           │ session_YYYYMMDD_   │                               │
│           │ HHMMSS.md           │                               │
│           └─────────────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DAILY AGGREGATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                                           │
│  │ aggregate-      │  ← NEW (called by daily-reflect.sh)       │
│  │ daily-summary.sh│                                           │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ daily_summary_  │                                           │
│  │ YYYY-MM-DD.md   │                                           │
│  └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     WEEKLY AGGREGATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                                           │
│  │ generate-       │  EXISTING (modify to include daily)       │
│  │ report.sh       │                                           │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ weekly_digest_  │                                           │
│  │ YYYY-MM-DD.md   │                                           │
│  └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Session Report Generator

**New file:** `.claude/hooks/session-memory/generate-session-report.sh`

**Trigger:** Called at end of `session-end-evaluate.sh`

**Inputs:**
- Session transcript data (from hook stdin)
- Corrections from `corrections/session_YYYYMMDD.jsonl`
- Session patterns from `sessions/<session_id>.json`
- CC insights from `cc-insights/` (if available)

**Output:** `.claude/state/session-reports/session_YYYYMMDD_HHMMSS.md`

**Report sections:**
1. Session metadata (duration, start/end times)
2. Quick stats (tool calls, files modified, corrections)
3. Activity timeline (key milestones)
4. Work items touched (from commit messages, task tool)
5. Repositories modified
6. Correction patterns (from capture-corrections)
7. Insights & recommendations

### Phase 2: Daily Summary Aggregator

**New file:** `.claude/skills/coordination/workspace/claude-reflect/scripts/aggregate-daily-summary.sh`

**Trigger:**
- Called by `daily-reflect.sh` at 5 AM
- On-demand via `/daily-summary` command

**Inputs:**
- All session reports from `session-reports/session_YYYYMMDD_*.md`
- Corrections summary from `corrections/session_YYYYMMDD.jsonl`
- Git commits from that day

**Output:** `.claude/state/daily-summaries/daily_summary_YYYY-MM-DD.md`

**Report sections:**
1. Day overview (total sessions, duration, activity level)
2. Aggregated stats across all sessions
3. Timeline of all sessions
4. Work items completed (de-duped)
5. Repositories touched (merged)
6. Correction analysis (combined patterns)
7. Key insights (prioritized)
8. Tomorrow's focus (recommendations)

### Phase 3: Weekly Report Integration

**Modify:** `.claude/skills/coordination/workspace/claude-reflect/scripts/generate-report.sh`

**Changes:**
- Add section: "Daily Summary Roll-up"
- Include links to each day's summary
- Aggregate weekly metrics from daily summaries
- Trend analysis across the week

### Phase 4: Hook Wiring

**Modify:** `session-end-evaluate.sh` (lines 107-115)

Add call to generate session report:
```bash
# Generate session report (NEW)
REPORT_SCRIPT="${WORKSPACE_ROOT}/.claude/hooks/session-memory/generate-session-report.sh"
if [[ -x "$REPORT_SCRIPT" ]]; then
    echo "${HOOK_INPUT}" | "$REPORT_SCRIPT" "$SESSION_ID"
fi
```

**Modify:** `daily-reflect.sh` (before PHASE 1: REFLECT)

Add call to aggregate daily summary:
```bash
# Generate daily summary from session reports
if [[ -x "$SCRIPT_DIR/aggregate-daily-summary.sh" ]]; then
    "$SCRIPT_DIR/aggregate-daily-summary.sh" "$(date -d yesterday +%Y-%m-%d)"
fi
```

---

## File Structure

```
.claude/
├── hooks/
│   └── session-memory/
│       ├── session-end-evaluate.sh    # MODIFY
│       └── generate-session-report.sh # NEW
│
├── state/
│   ├── session-reports/               # NEW directory
│   │   ├── session_20260205_143025.md
│   │   └── session_20260205_091530.md
│   ├── daily-summaries/               # NEW directory
│   │   ├── daily_summary_2026-02-05.md
│   │   └── daily_summary_2026-02-04.md
│   ├── sessions/                      # EXISTING
│   ├── corrections/                   # EXISTING
│   └── reflect-state.yaml             # MODIFY (add new metrics)
│
└── skills/
    └── coordination/
        └── workspace/
            └── claude-reflect/
                └── scripts/
                    ├── daily-reflect.sh           # MODIFY
                    ├── aggregate-daily-summary.sh # NEW
                    └── generate-report.sh         # MODIFY
```

---

## Session Report Format

```markdown
# Session Report: YYYY-MM-DD HH:MM

**Session ID:** abc123
**Duration:** 45 minutes
**Activity Level:** High

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Tool Calls | 87 |
| Files Modified | 12 |
| Corrections | 2 |
| Commits | 1 |
| Delegation Score | 65% |

---

## Activity Timeline

- **14:30** - Session started
- **14:35** - Explored codebase (Task/Explore)
- **14:45** - Modified `.claude/hooks/session-end-evaluate.sh`
- **15:00** - Correction: Fixed syntax error in hook
- **15:10** - Committed changes
- **15:15** - Session ended

---

## Work Items

- [x] Implement session report generator

---

## Repositories Touched

| Repository | Files | Actions |
|------------|-------|---------|
| workspace-hub | 3 | 45 |

---

## Corrections

**2 corrections** (avg gap: 30s)

| File | Gap | Type |
|------|-----|------|
| session-end-evaluate.sh | 25s | syntax fix |
| SKILL.md | 35s | typo |

---

## Insights

- High delegation score (65%) - good orchestrator compliance
- Quick correction turnaround suggests active iteration

---

*Generated by session-report hook*
```

---

## Daily Summary Format

```markdown
# Daily Summary: YYYY-MM-DD

**Sessions:** 3
**Total Duration:** 4h 15m
**Activity Level:** High

---

## Day Overview

| Metric | Total | Avg/Session |
|--------|-------|-------------|
| Tool Calls | 234 | 78 |
| Files Modified | 28 | 9 |
| Corrections | 6 | 2 |
| Commits | 4 | 1.3 |

---

## Sessions

1. **09:15 - 10:30** (1h 15m) - Codebase exploration
2. **14:30 - 15:15** (45m) - Hook implementation
3. **19:00 - 21:30** (2h 30m) - Documentation

---

## Work Items Completed

- [x] Implement session report generator
- [x] Update daily-reflect integration
- [ ] Weekly report modifications (in progress)

---

## Repositories Touched

| Repository | Sessions | Files | Commits |
|------------|----------|-------|---------|
| workspace-hub | 3 | 18 | 3 |
| aceengineer-admin | 1 | 4 | 1 |

---

## Correction Patterns

**6 total corrections** across 3 sessions

- Most corrected: `.sh` files (4)
- Avg correction gap: 42s
- Pattern: Syntax errors in bash scripts

---

## Key Insights

1. High activity in `.claude/hooks/` - 15 modifications
2. Consistent delegation pattern (avg 62%)
3. Bash syntax errors suggest adding shellcheck

---

## Tomorrow's Focus

- Complete weekly report integration
- Add shellcheck to pre-commit hooks
- Review pending cross-reviews

---

*Generated by aggregate-daily-summary.sh*
```

---

## State Updates

Add to `reflect-state.yaml`:

```yaml
session_reports:
  enabled: true
  today_count: 3
  today_duration_minutes: 255
  last_report: session_20260205_193000.md

daily_summaries:
  enabled: true
  last_summary: daily_summary_2026-02-05.md
  summaries_this_week: 5
```

---

## Verification

1. **Session report generation:**
   - Start a Claude session, do some work, exit
   - Check `.claude/state/session-reports/` for new report
   - Verify report contains correct metrics

2. **Daily aggregation:**
   - Run `aggregate-daily-summary.sh` manually
   - Check `.claude/state/daily-summaries/` for output
   - Verify all sessions are included

3. **Weekly integration:**
   - Wait for Sunday or run `generate-report.sh` manually
   - Verify weekly report includes daily summary section
   - Check links to daily summaries work

4. **End-to-end:**
   - Run `/reflect` command
   - Verify `reflect-state.yaml` includes new metrics
   - Check all three report levels are generated

---

## Critical Files

| File | Action | Purpose |
|------|--------|---------|
| `.claude/hooks/session-memory/session-end-evaluate.sh` | Modify | Add report generation call |
| `.claude/hooks/session-memory/generate-session-report.sh` | Create | Generate session reports |
| `.claude/skills/.../aggregate-daily-summary.sh` | Create | Aggregate session→daily |
| `.claude/skills/.../generate-report.sh` | Modify | Include daily in weekly |
| `.claude/skills/.../daily-reflect.sh` | Modify | Call daily aggregator |
| `.claude/state/reflect-state.yaml` | Modify | Add new metrics |

---

## Review

- [ ] Cross-review required (3 iterations)
- [ ] Gemini review pending
- [ ] Codex review pending
- [ ] Claude review pending
