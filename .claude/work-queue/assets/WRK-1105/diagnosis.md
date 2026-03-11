# WRK-1105: Diagnosis — Why WRK Summaries Land in MEMORY.md

## Confirmed Call-Site

WRK-NNN ARCHIVED summary lines are written to MEMORY.md by **Claude Code's auto-memory
system** — the orchestrator agent itself, not any script. The trigger is the agent noticing
a WRK has been archived and emitting a compact summary to its persistent memory file.

Exact write path:
1. Orchestrator runs `archive-item.sh WRK-NNN`
2. Orchestrator constructs a 1-line summary of the WRK
3. Orchestrator writes (or edits) the line into MEMORY.md via Claude Code's `Write`/`Edit`
   tool as part of the "save to memory" auto-memory hook
4. No script mediates this write — it is 100% orchestrator discretion

Evidence: `scripts/work-queue/archive-item.sh` contains zero references to MEMORY.md,
`auto-memory`, or `ARCHIVED`. The write happens entirely in the agent layer.

## Current Format (Confirmed)

Each ARCHIVED entry is a **single-line bullet**:

```
- **WRK-NNN ARCHIVED** (githash): title — key facts/artifacts/patterns; follow-ons
```

No multi-line blocks. Confirmed by reading the actual MEMORY.md (≈146 lines, ~25 entries).

## Trigger Mechanism

- Auto-memory rule: "save work-done summaries after archiving a WRK item"
- Orchestrator learns this from CLAUDE.md / skill instructions to "update MEMORY.md"
- The pattern is self-reinforcing: MEMORY.md already has ARCHIVED entries so the
  orchestrator continues the established format

## Current Fate of Evicted Entries

When MEMORY.md approaches the 200-line limit, `compact-memory.py` runs with rule 1:
**done-WRK eviction** — it deletes lines matching `WRK-NNN ARCHIVED` without saving
them to any other location. The knowledge is permanently lost.

`compact-memory.py` currently:
- Reads MEMORY.md only for line count (line 123 in compact-memory.py)
- Skips MEMORY.md in `_read_topic_files()` — operates on topic files only
- Rule 1 (`_evict_done_wrks`) deletes done-WRK bullets, no preservation

## Why This Diagnosis Matters

The root cause is **architectural** — no script captures WRK learnings at archive time.
The orchestrator fills this gap with MEMORY.md writes, but MEMORY.md is line-limited and
not queryable. The fix: add a `capture-wrk-summary.sh` hook to `archive-item.sh` so
knowledge is captured structurally, and update `compact-memory.py` to route before evicting.

## Audit of Comprehensive-Learning

`scripts/agents/comprehensive-learning.sh` Stage 16 updates `resource-intelligence` skills
but does not write to MEMORY.md or knowledge-base/. It is a separate learning path that
enriches docs/skills from session logs. No WRK ARCHIVED summaries are routed there.
