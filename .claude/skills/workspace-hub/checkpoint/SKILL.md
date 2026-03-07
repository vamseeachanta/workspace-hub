---
name: checkpoint
description: >
  Save or restore WRK session state for zero-context-loss stage handoff across compactions.
  /checkpoint WRK-NNN snapshots current stage; /resume WRK-NNN reloads it in a fresh session.
version: 1.0.0
updated: 2026-03-07
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities:
  - session_checkpoint
  - context_handoff
  - stage_resume
related_skills:
  - workspace-hub/session-start
  - workspace-hub/work-queue-workflow
tools: [Read, Write, Bash]
see_also:
  - scripts/work-queue/checkpoint.sh
---

# Checkpoint Skill

> Two modes: `checkpoint WRK-NNN` (save before compaction) and `resume WRK-NNN` (load in new session).

---

## Save Mode — `/checkpoint WRK-NNN`

1. Run: `bash scripts/work-queue/checkpoint.sh WRK-NNN`
2. Read the written `.claude/work-queue/assets/WRK-NNN/checkpoint.yaml`.
3. Fill in agent-only stubs (script leaves these empty):
   - `decisions_this_session` — key decisions this session, one string each
   - `artifacts_written` — every file path written or modified
   - `next_action` — single imperative: what the next session must do first
   - `context_summary` — 3-5 bullets summarising current state
4. Write the updated yaml back.
5. Commit:
   ```bash
   REPO=$(git rev-parse --show-toplevel)
   git -C "$REPO" add .claude/work-queue/assets/WRK-NNN/checkpoint.yaml
   git -C "$REPO" commit -m "chore(WRK-NNN): checkpoint — stage N"
   ```
6. Print: `Checkpoint saved at Stage N. New session: /resume WRK-NNN`

---

## Load Mode — `/resume WRK-NNN`

Run as the FIRST action in a new session — before any other work.

1. Read `.claude/work-queue/assets/WRK-NNN/checkpoint.yaml` — nothing else yet.
2. Read ONLY the files in `entry_reads[]` (max 3). Stop there.
3. Print a 10-line summary (WRK, Stage, Checkpointed, Decisions, Artifacts, Next action, Context).
4. Do NOT load any other skill or file. Context is fresh — preserve it until user confirms direction.

---

## checkpoint.yaml Schema

```yaml
wrk_id: WRK-NNN
title: "..."
checkpointed_at: "ISO8601"
current_stage: 2
stage_name: "Resource Intelligence"
entry_reads:
  - .claude/work-queue/assets/WRK-NNN/evidence/stage-evidence.yaml
  - .claude/work-queue/pending/WRK-NNN.md
decisions_this_session: []   # agent fills
artifacts_written: []        # agent fills
next_action: ""              # agent fills
context_summary: []          # agent fills
```
