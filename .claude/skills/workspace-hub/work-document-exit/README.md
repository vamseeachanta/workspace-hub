# work-document-exit

Documents the active WRK item's state and prepares a clean session handoff
before exiting. Writes a `## Session Handoff` section to the WRK file with
work done, files changed, next steps, and a ready-to-paste commit command.

## Trigger

```
/work-document-exit
```

Also invoked automatically by `/session-end` when a working/ item has
`percent_complete < 100`.

## Quick Start

1. Run `/work-document-exit` before `/clear` or ending the session.
2. Review the generated `## Session Handoff` section in the WRK file.
3. Paste the printed `git add` and `git commit` commands to commit.
4. Run `/clear` — the handoff section persists in the WRK file.

## Active WRK Resolution

The skill looks for the active WRK item in this order:

| Priority | Source |
|----------|--------|
| 1 | `.claude/state/active-wrk` (explicit state file) |
| 2 | Most recently modified `work-queue/working/*.md` |
| 3 | Branch name (e.g., `feature/WRK-392-...`) |
| 4 | General session fallback (no WRK item) |

## What Gets Written

```markdown
## Session Handoff — YYYY-MM-DD

**Status at exit:** ...
**Percent complete:** ...

### Work Done This Session
- ...

### Files Modified
...

### What Remains
- ...

### Commit Command
git add ...
git commit -m "..."

### Resume Notes
...
```

## Safety

- Never auto-commits. Prints the commit command only.
- `git add` only runs when the user explicitly requests it.
- Appends to the WRK file; never overwrites existing content.

## Full Documentation

See `SKILL.md` for complete step-by-step logic, fallback behaviour,
and integration with `/session-end`.
