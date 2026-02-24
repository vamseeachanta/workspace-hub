---
name: work-document-exit
description: >
  Documents the active WRK item's session state — work done, files changed, next steps —
  writes a Session Handoff section to the WRK file, stages files, and exits cleanly.
version: "1.0.0"
updated: 2026-02-24
category: workspace-hub
triggers:
  - work document exit
  - document and exit
  - handoff
  - exit session
  - prepare handoff
  - wrap this WRK
  - document work
related_skills:
  - workspace-hub/session-end
  - workspace-hub/save
  - workspace-hub/session-start
capabilities:
  - wrk-state-capture
  - session-handoff
  - staged-commit-prep
  - active-wrk-resolution
requires:
  - .claude/work-queue/
  - git
see_also:
  - workspace-hub/session-end
  - workspace-hub/save
invoke: work-document-exit
---

# /work-document-exit — WRK State Capture + Session Handoff

Documents the active in-progress WRK item before exiting. Writes a structured
`## Session Handoff` section into the WRK file and prepares a ready-to-paste
commit command. Use this as the "prepare to leave" skill when stopping mid-task.

## When to Use

- Before `/clear` when a WRK item is still in progress
- When handing off to another session or machine
- Before an unexpected exit with work partially done
- When `/session-end` is run while a WRK item is active

## What It Does

1. Identifies the active WRK item
2. Collects session context: files changed, progress summary, next steps
3. Writes `## Session Handoff — <date>` to the WRK item file
4. Stages changed files (or prints the `git add` command)
5. Outputs a ready-to-run commit command
6. Clears `.claude/state/active-wrk` if it exists

---

## Step 1 — Identify the Active WRK Item

Check these sources in order, use the first that resolves:

```bash
# Source A: explicit active-wrk state file
ACTIVE_WRK_FILE=".claude/state/active-wrk"
if [[ -f "$ACTIVE_WRK_FILE" ]]; then
  WRK_ID=$(cat "$ACTIVE_WRK_FILE" | tr -d '[:space:]')
fi

# Source B: most recently modified working/ item
if [[ -z "$WRK_ID" ]]; then
  WRK_ID=$(ls -t .claude/work-queue/working/*.md 2>/dev/null \
    | head -1 \
    | xargs basename 2>/dev/null \
    | sed 's/\.md$//')
fi

# Source C: git status — infer from branch name
if [[ -z "$WRK_ID" ]]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
  WRK_ID=$(echo "$BRANCH" | grep -oE 'WRK-[0-9]+' | head -1)
fi

# Source D: no active WRK — document general session state
if [[ -z "$WRK_ID" ]]; then
  echo "No active WRK item found. Documenting general session state."
  WRK_ID="general"
fi
```

If `WRK_ID` is a real ID (not "general"), locate the WRK file:

```bash
WRK_FILE=$(find .claude/work-queue/ -name "${WRK_ID}.md" 2>/dev/null | head -1)
if [[ -z "$WRK_FILE" ]]; then
  WRK_FILE=$(find .claude/work-queue/ -name "${WRK_ID}-*.md" 2>/dev/null | head -1)
fi
```

## Step 2 — Collect Session Context

Gather the raw material for the handoff note. Run these commands and store results:

```bash
# Files changed since last commit (staged + unstaged)
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null)
STAGED_FILES=$(git diff --name-only --cached 2>/dev/null)

# Combined unique list
ALL_CHANGED=$(printf '%s\n%s\n' "$CHANGED_FILES" "$STAGED_FILES" \
  | sort -u | grep -v '^$')

# Last 5 commits on this branch for context
RECENT_COMMITS=$(git log --oneline -5 2>/dev/null)

# Current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

# Session date
SESSION_DATE=$(date -u +"%Y-%m-%d")
SESSION_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```

## Step 3 — Write Session Handoff Section

Ask Claude to synthesize the handoff note using the session context and the
WRK item's acceptance criteria. Claude writes the section; the script appends it.

The handoff section format (Claude fills in `<...>` placeholders):

```markdown
## Session Handoff — <SESSION_DATE>

**Status at exit:** <one-line summary — e.g., "Step 3 complete, Step 4 in progress">
**Percent complete:** <estimated %>

### Work Done This Session
- <bullet: what was completed, tested, or decided>
- <bullet: ...>

### Files Modified
<list each file on its own line>

### What Remains
- <next step 1 — be specific enough to act without re-reading context>
- <next step 2>
- <next step 3>

### Commit Command
```bash
git add <files>
git commit -m "<conventional commit message>"
```

### Resume Notes
<Any gotchas, in-progress decisions, or context that would otherwise be lost>
```

Rules for writing the section:
- "Work Done" must reference the WRK acceptance criteria checkboxes when they exist
- "Files Modified" is the raw list from Step 2 (do not abbreviate)
- "What Remains" must be actionable enough to resume without re-reading the WRK body
- "Commit Command" must be a valid, pasteable shell command
- "Resume Notes" is optional; omit the heading if there is nothing to note

### Appending to the WRK File

If `WRK_FILE` was found, append the section using the Edit tool:

```bash
# Check if a handoff section already exists for today
if grep -q "## Session Handoff — ${SESSION_DATE}" "$WRK_FILE" 2>/dev/null; then
  echo "Handoff section for today already exists — updating in place."
  # Use Edit tool to replace existing section for today
else
  # Append new section at end of file
  echo "" >> "$WRK_FILE"
  cat <<HANDOFF >> "$WRK_FILE"
<generated handoff section>
HANDOFF
fi
```

If no WRK file was found (general session), write to
`.claude/state/session-handoff.md` instead:

```bash
HANDOFF_FILE=".claude/state/session-handoff.md"
# Write full handoff with date header
```

## Step 4 — Stage Files

Show the user what will be staged and print the git add command:

```
Files to stage:
  .claude/skills/workspace-hub/work-document-exit/SKILL.md
  .claude/skills/workspace-hub/work-document-exit/README.md
  .claude/work-queue/pending/WRK-392.md

Ready to stage:
  git add <file1> <file2> ...

To commit:
  git commit -m "feat(wrk-392): ..."
```

Do NOT run `git add` or `git commit` automatically. Print the commands only.
The user must paste and run them to preserve the WRK gate.

Exception: if the user explicitly says "stage for me" or "run git add", then
run `git add` for the listed files only (no `-A`, no wildcard).

## Step 5 — Clear Active WRK State

```bash
ACTIVE_WRK_FILE=".claude/state/active-wrk"
if [[ -f "$ACTIVE_WRK_FILE" ]]; then
  rm "$ACTIVE_WRK_FILE"
  echo "Cleared .claude/state/active-wrk"
fi
```

## Step 6 — Output Summary

Print a clean exit summary to the user:

```
=== Work Document Exit — <SESSION_DATE> ===

Active WRK: <WRK_ID> — <title if available>
Handoff written to: <WRK_FILE or session-handoff.md>
Files changed: <count>
Branch: <BRANCH>

Next session: run /session-start to reload this handoff.

To commit now:
  git add <files>
  git commit -m "<commit message>"
==========================================
```

## No-Active-WRK Fallback

When `WRK_ID` is "general" (no active WRK found):

1. Still collect changed files from git diff
2. Write a general session summary to `.claude/state/session-handoff.md`
3. Skip the WRK file append step
4. Print the same commit command output

The handoff note is still useful even without an active WRK item.

## Integration with /session-end

This skill is designed to run as a sub-step of `/session-end` when a
WRK item is active. Call it before Step 5 (snapshot + clear) in the
`session-end` workflow.

Manual invocation: `/work-document-exit`
Auto-trigger: When `/session-end` detects a working/ item with `percent_complete < 100`

---

*Counterpart to `/session-start` context loading. Use together for clean multi-session WRK handoffs.*
