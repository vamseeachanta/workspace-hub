---
name: agentic-horizon
description: Weekly scan of all active WRK items to reassess agentic AI horizon notes as the landscape evolves; also mines archived items for newly-relevant follow-up work
version: 1.0.0
category: workspace-hub
type: skill
trigger: scheduled
cadence: weekly
auto_execute: true
capabilities:
  - horizon_reassessment
  - disposition_change_detection
  - archive_followup_mining
  - wrk_item_editing
tools: [Read, Write, Edit, Grep, Glob, Task]
related_skills: [work-queue, session-analysis, skill-learner]
see_also:
  - .claude/work-queue/working/WRK-228.md
  - .claude/docs/archive-horizon-followups.md
---

# Agentic Horizon Skill

> Weekly reassessment of all active WRK items against the current agentic AI landscape. Surfaces items whose disposition has changed — "wait" items that are now ready, "do now" items that should be parked, and archived work that warrants follow-up.

## When This Runs

- **Trigger**: weekly (Monday morning cron, same window as `claude-reflect`)
- **Auto-execute**: agent runs the scan autonomously; surfaces changes for user review before editing files
- **Also**: run manually at any time via `/agentic-horizon` or when a significant model release occurs

## What It Does

### Pass 1 — Active item reassessment (pending + working)

For every active WRK item with an `## Agentic AI Horizon` section:

1. Read the current disposition and rationale
2. Reassess against the current date and known model trajectory
3. Flag if disposition has changed:
   - `wait` / `park N months` → time has elapsed or landscape shifted → may be `do now`
   - `do now` → new model capability makes it premature → should be `park` or `invest differently`
   - `invest now` → delivering value as expected → no change needed
4. Collect flagged items; present to user as a batch before applying edits

**Change criteria** (flag if any apply):
- Disposition includes a month/timeframe that has now passed
- A model release or capability announcement directly affects the item's rationale
- The item has been in `pending` for >60 days with `park` disposition — may be worth revisiting
- Related WRK items were completed in a way that changes this item's horizon

### Pass 2 — Archive follow-up mining

Read `.claude/docs/archive-horizon-followups.md` (produced by WRK-228 step 4, updated each run):

- Check whether any previously-identified follow-up candidates now have a WRK item (if so, mark as actioned)
- Scan any newly-archived items (since last run) for follow-up signals
- Append new candidates to the document

### Pass 3 — Disposition drift detection

Across all active items, compute:
- Items with `do now` disposition but no activity in 30+ days → flag for re-evaluation or deprioritisation
- Items with `park` disposition whose park date has elapsed → surface for user decision
- Items with no `## Agentic AI Horizon` section → add to backfill queue

## Output

After each run, produce a summary at `.claude/state/horizon-scan/YYYY-MM-DD.md`:

```
## Agentic Horizon Scan — YYYY-MM-DD

### Disposition Changes Detected
[list of items where disposition should change, with before/after]

### Park Dates Elapsed
[list of items whose park window has passed — user decision needed]

### Stale "Do Now" Items
[items marked do-now but not touched in 30+ days]

### Archive Follow-ups Added
[new candidates from newly-archived items]

### No-Change Items
[count only]
```

Present the summary to the user. Apply edits to WRK item files **only after user reviews the changes**.

## Execution Pattern

```
1. Glob all pending/ and working/ WRK-*.md files
2. Read each; extract ## Agentic AI Horizon section
3. Reassess disposition against current date + landscape
4. Collect changes → present as summary
5. User approves → apply edits (one file at a time)
6. Read archive-horizon-followups.md
7. Scan newly-archived items (since last run date)
8. Append new candidates
9. Write scan summary to state/horizon-scan/
```

## Disposition Reference

| Disposition | Meaning | Reassess when |
|-------------|---------|---------------|
| `do now` | Time-sensitive, clear value today | Capability arrives that supersedes it |
| `invest now` | Builds infrastructure agents leverage | Delivering expected value → no change |
| `do now, shape for leverage` | Necessary now, shape for reuse | Value delivered; may need follow-up |
| `park 2-3 months` | Better with improved models | Park window elapsed |
| `park N months` | Timeframe-gated | Park date reached |
| `wait` | Likely superseded | Model capability milestone confirmed |
| `deprioritise` | Low agentic and strategic value | New strategic context changes priority |
| `groundwork now, park rest` | Foundation now, execution later | Foundation delivered; rest may be ready |

## Landscape Signals to Watch

The reassessment should consider:
- Claude model releases (capability jumps in code, reasoning, autonomy)
- Claude Code agentic feature releases (background agents, longer context, MCP ecosystem)
- OpenAI / Gemini parity signals (affects multi-provider strategy in WRK-235)
- Items in WRK-235 (roadmap) — strategic reprioritisation cascades to horizon assessments

## User Interaction

- Agent runs the scan **fully autonomously**
- Presents a concise diff of proposed changes before touching any files
- User can approve all / approve selectively / defer
- If no changes needed, reports "No disposition changes this week" and exits silently
