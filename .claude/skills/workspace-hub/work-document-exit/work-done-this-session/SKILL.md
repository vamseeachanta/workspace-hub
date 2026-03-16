---
name: work-document-exit-work-done-this-session
description: 'Sub-skill of work-document-exit: Work Done This Session (+5).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Work Done This Session (+5)

## Work Done This Session

- <bullet: what was completed, tested, or decided>
- <bullet: ...>


## Files Modified

<list each file on its own line>


## What Remains

- <next step 1 — be specific enough to act without re-reading context>
- <next step 2>
- <next step 3>


## Commit Command

```bash
git add <files>
git commit -m "<conventional commit message>"
```


## Resume Notes

<Any gotchas, in-progress decisions, or context that would otherwise be lost>
```

Rules for writing the section:
- "Work Done" must reference the WRK acceptance criteria checkboxes when they exist
- "Files Modified" is the raw list from Step 2 (do not abbreviate)
- "What Remains" must be actionable enough to resume without re-reading the WRK body
- "Commit Command" must be a valid, pasteable shell command
- "Resume Notes" is optional; omit the heading if there is nothing to note


## Appending to the WRK File


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
