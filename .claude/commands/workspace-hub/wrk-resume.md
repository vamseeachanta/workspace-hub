---
name: wrk-resume
description: Resume a WRK item from its last checkpoint — reads checkpoint.yaml and loads entry_reads files into context
version: 1.0.1
category: workspace-hub
argument-hint: WRK-NNN
---

> **DEPRECATED as primary resume path**: `/work run WRK-NNN` now auto-loads checkpoint.yaml.
> Use `/wrk-resume WRK-NNN` only for diagnostic inspection of checkpoint state.

# /wrk-resume $ARGUMENTS

Resume a WRK work item from its last checkpoint.

## Steps

**If no WRK ID was given**, list files in `.claude/work-queue/working/` and ask which to resume.

**1. Locate the checkpoint**

Check whether `.claude/work-queue/assets/$ARGUMENTS/checkpoint.yaml` exists.
If not, tell the user: "No checkpoint found for $ARGUMENTS. Run first: `bash scripts/work-queue/checkpoint.sh $ARGUMENTS`"

**2. Read the checkpoint file**

Use the Read tool on `.claude/work-queue/assets/$ARGUMENTS/checkpoint.yaml` and extract:

- `title` — WRK title
- `current_stage` + `stage_name` — where work left off
- `checkpointed_at` — timestamp
- `next_action` — what to do first in this session (warn if empty)
- `context_summary` — list of context bullets (warn if stored as a plain string, which indicates a checkpoint.yaml bug)
- `decisions_this_session` — decisions made in the last session
- `artifacts_written` — artifacts produced last session
- `entry_reads` — files to load into context

**3. Present the summary** in this format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Resuming WRK-NNN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Title     : <title>
Stage     : <current_stage> — <stage_name>
Checkpointed: <checkpointed_at>

▶ Next action: <next_action>

Context summary:
  • <item>

Decisions from last session:
  • <decision>

Artifacts written last session:
  • <artifact>

Entry reads:
  • <path>  ← read these files now
```

**4. Read all entry_reads files** using the Read tool so their content is in context.

**5. Confirm to the user** which files were loaded and that you are ready to continue from the `next_action`.

---

**Note — `/wrk-resume` vs `/work run`:**
`/wrk-resume WRK-NNN` is **session-level context restore** — reads checkpoint.yaml, presents state, loads entry_reads. Does not advance any stage or write artifacts.
`/work run` is **stage-level pipeline execution** — runs the next stage, invokes scripts, produces exit artifacts.
Always `/wrk-resume` first in a fresh session, then `/work run` to continue.
