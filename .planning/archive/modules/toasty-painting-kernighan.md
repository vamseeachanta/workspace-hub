# Plan: Pre-Clear Session Snapshot

## Context

`/clear` is a Claude Code built-in CLI command processed at the shell level before messages
reach Claude. It cannot be intercepted by a skill, PreToolUse hook, or any other hook event.
The 4 supported hook events are: PreToolUse, PostToolUse, PreCompact, Stop — none fires on
`/clear`.

**Problem**: When the user runs `/clear`, all in-session context is lost:
- In-progress WRK items and their step-level progress
- Ideas and decisions discussed but not yet captured in a WRK item
- Pending follow-up tasks mentioned conversationally

**Solution**: Create a `/save` skill (user-invocable) that captures a full session snapshot
before the user runs the built-in `/clear`. Make it fast, automatic, and comprehensive so it
becomes muscle memory: `/save` → `/clear`.

---

## What to Build

### 1. Snapshot script: `.claude/hooks/session-memory/save-snapshot.sh`

Captures file-system-observable state (no conversational context):

- **Active WRK items**: list files in `.claude/work-queue/working/`, extract id + title + percent_complete
- **Recently modified WRK items**: `git diff --name-only HEAD` filtered to `work-queue/`, read id + title
- **In-progress step detection**: For each active WRK, find last `[x]` checked item (latest step done)
- **Next step detection**: For each active WRK, find first `[ ]` unchecked item (next step)
- **Timestamp + branch**: current git branch + timestamp

Output: `.claude/state/session-snapshot.md` (gitignored, human-readable Markdown)

Format:
```markdown
# Session Snapshot — 2026-02-19T14:30:00Z
Branch: feature/WRK-205-skills-knowledge-graph

## Active WRK Items
- WRK-205: Skills knowledge graph (60% complete)
  - Last done: Step 3 — canonical_ref to 115 _diverged/ SKILL.md
  - Next: Step 5 — 12 category INDEX.md files

## Recently Modified
- WRK-080: added Blog Post 5 candidate (LinkedIn post, Erik De Haas)

## Ideas / Notes (added by Claude during /save)
[Claude fills this section with conversational context]
```

### 2. Skill: `.claude/skills/workspace-hub/save/SKILL.md`

User-invocable via `/save`. Instructs Claude to:

1. Run `save-snapshot.sh` (captures file-based state)
2. Review the current conversation for ideas/decisions/tasks NOT yet in a WRK item
3. Append those to the `## Ideas / Notes` section of the snapshot file
4. Confirm to user: "Snapshot saved. Safe to run /clear."

Skill prompt must be concise (<100 tokens when invoked) since it runs at end-of-session
when context is often full.

### 3. Session-lifecycle doc update: `.claude/docs/session-lifecycle.md`

Add a "Pre-Clear Workflow" section documenting the `/save` → `/clear` pattern.

### 4. Snapshot auto-load on next session start

The existing readiness hook (`ensure-readiness.sh` Stop hook) already runs R5 (context
budget audit). Add a step: if `.claude/state/session-snapshot.md` exists and is <48h old,
surface it in the next-session readiness report so Claude notices it immediately.

---

## WRK Item

This task needs a WRK item for traceability. It will be created as Step 0 during
implementation.

**Proposed**: Route A (inline plan, no cross-review required — small-scope, single-file ops)

```yaml
id: WRK-218  # next available — verify before creating
title: "Pre-clear session snapshot — /save skill + save-snapshot.sh script"
status: pending
priority: medium
complexity: low
target_repos: [workspace-hub]
tags: [session-lifecycle, context-engineering, skills]
related: [WRK-205, WRK-187]
route: A
```

---

## Files to Create / Modify

| Action | File |
|--------|------|
| Create | `.claude/hooks/session-memory/save-snapshot.sh` |
| Create | `.claude/skills/workspace-hub/save/SKILL.md` |
| Modify | `.claude/hooks/readiness/ensure-readiness.sh` — add snapshot surfacing |
| Modify | `.claude/docs/session-lifecycle.md` — add pre-clear workflow section |

---

## Skill Prompt Design

The skill prompt in SKILL.md should:
1. Tell Claude to run `bash .claude/hooks/session-memory/save-snapshot.sh`
2. Then ask Claude to write the "Ideas / Notes" section (conversational context only Claude has)
3. Confirm saved

The Bash execution is what makes this durable — the ideas section is what makes it uniquely
valuable (scripts can't read conversation context; Claude can).

---

## Out of Scope

- Intercepting the built-in `/clear` — not possible with current Claude Code hook API
- Auto-running `/save` on `/clear` — same limitation; not achievable without CLI-level changes
- WRK item creation from snapshot — that's a separate session-start workflow

---

## Verification

1. Run `/save` — snapshot appears at `.claude/state/session-snapshot.md` with correct WRK state
2. Verify `## Ideas / Notes` section has conversational context Claude wrote
3. Run built-in `/clear` — conversation history cleared
4. In new session: readiness hook surfaces the snapshot file automatically
5. No WRK data lost; next session has full context to resume
