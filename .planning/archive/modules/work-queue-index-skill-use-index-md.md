# Fix: Work Queue List Should Read INDEX.md, Not Scan Files

## Context

`/work list` is painfully slow because Claude interprets the SKILL.md instructions and manually globs + reads 80+ individual work item files every time. Meanwhile, a pre-built `INDEX.md` already exists at `.claude/work-queue/INDEX.md` with all the same data in structured tables. The `generate-index.py` script (417 lines, works) rebuilds it from scratch. The fix is to make the skill instructions route `/work list` to read INDEX.md directly, and regenerate the index after every mutation.

## Changes

### 1. Update SKILL.md — `/work list` reads INDEX.md directly

**File**: `.claude/skills/coordination/workspace/work-queue/SKILL.md`

In the **Command Interface** table, change the `list` row description from "Show all pending/working/blocked items (regenerates INDEX.md)" to "Read and display `.claude/work-queue/INDEX.md`".

Add a new section **## Index Management** after the existing sections:

```markdown
## Index Management

**INDEX.md is the source of truth for listing.** Never scan individual work item files for a list operation.

### `/work list` Behavior
1. Read `.claude/work-queue/INDEX.md`
2. Display the relevant section (filter by repo/status/priority if args provided)
3. If INDEX.md is missing or empty, regenerate: `python3 .claude/work-queue/scripts/generate-index.py`

### Index Regeneration Triggers
After ANY mutation to work items, regenerate the index:
- `/work add` — after creating the new item file
- `/work archive` — after moving the item to archive/
- Status changes (pending → working, working → done, etc.)
- Priority or complexity changes

Regeneration command:
```
python3 .claude/work-queue/scripts/generate-index.py
```

This is fast (<2s for 100+ items) and ensures INDEX.md stays current.
```

### 2. Update SKILL.md — Add regeneration step to Phase 1 (Capture) and Phase 2 (Process)

In the **Phase 1: Capture** section, add as the last bullet:
- `Regenerate INDEX.md: run python3 .claude/work-queue/scripts/generate-index.py`

In the **Phase 2: Process** section, after "Auto-claim: move to working/, update frontmatter":
- `Regenerate INDEX.md after status change`

In the archive pipeline step:
- `Regenerate INDEX.md after archiving`

### 3. No new scripts needed

`generate-index.py` already exists and works. No wrapper script needed — just call it directly via `python3`.

## Files Modified

| File | Change |
|------|--------|
| `.claude/skills/coordination/workspace/work-queue/SKILL.md` | Add Index Management section, update list command, add regen triggers to capture/process flows |

## Verification

1. Run `/work list` — should read INDEX.md instantly (no file scanning)
2. Run `/work add test item` — should create item AND regenerate INDEX.md
3. Verify INDEX.md contains the new item
4. Run `python3 .claude/work-queue/scripts/generate-index.py` manually — should complete in <2s
