---
name: save
description: Capture a session snapshot before /clear — saves active WRK state and conversational context
version: 1.0.0
category: workspace-hub
author: workspace-hub
type: skill
trigger: manual
auto_execute: false
tools: [Bash, Edit]
related_skills: [improve, knowledge]
tags: [session-lifecycle, context-engineering, pre-clear]
platforms: [all]
---

# /save — Pre-Clear Session Snapshot

Captures full session state before the user runs the built-in `/clear` command.
Use this as muscle memory: **`/save` → `/clear`**.

## Why

`/clear` destroys all in-session context. This skill preserves:
- Active WRK items and their step-level progress (via filesystem scan)
- Ideas, decisions, and tasks discussed but not yet in a WRK item (via Claude)

## Workflow

### Step 1 — Run the snapshot script

```bash
bash .claude/hooks/session-memory/save-snapshot.sh
```

This writes `.claude/state/session-snapshot.md` with:
- Active WRK items (from `work-queue/working/`) with last-done and next steps
- Recently modified WRK items (`git diff --name-only HEAD`)

### Step 2 — Write the Ideas / Notes section

Read the snapshot file. Then replace the `## Ideas / Notes` placeholder with a
concise summary of conversational context from this session that is NOT already
captured in a WRK item. Include:

- Ideas discussed but not yet turned into WRK items
- Decisions made (architectural, process, tooling)
- Follow-up tasks mentioned conversationally
- Any "important to remember next session" observations

Keep it brief — bullet points, 3–10 items max. Use this format:

```markdown
## Ideas / Notes
- [idea/decision/task description]
- [idea/decision/task description]
```

Use the Edit tool to replace the placeholder in the snapshot file.

### Step 3 — Confirm

Output to the user:

```
Snapshot saved to .claude/state/session-snapshot.md
Safe to run /clear — context will be available next session via readiness report.
```

## Output Location

`.claude/state/session-snapshot.md` — gitignored, human-readable Markdown.
Surfaced automatically in the next session's readiness report if <48h old.
