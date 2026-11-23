# Work Queue Index Generator

## Summary

Create a Python script that parses all work item frontmatter and generates a structured `INDEX.md` with multiple lookup views (by repo, status, priority, complexity, dependencies). The script is re-runnable so the index stays current as items are added, processed, or archived.

## Files to Create

### 1. `.claude/work-queue/scripts/generate-index.py`

Python script that:
- Scans all queue directories: `pending/`, `working/`, `blocked/`, `archive/*/`
- Parses YAML frontmatter from each `WRK-*.md` file
- Generates `INDEX.md` with these sections:

**Sections in INDEX.md:**

| Section | Content |
|---------|---------|
| Summary | Total counts by status, priority, complexity, repo |
| Master Table | All items sorted by ID — columns: ID, Title, Status, Priority, Complexity, Repo, Blocked By |
| By Status | Separate tables for: done (unarchived), pending, working, blocked, archived |
| By Repository | One table per repo with its items |
| By Priority | High / Medium / Low groupings |
| By Complexity | Simple / Medium / Complex groupings |
| Dependencies | Items with `blocked_by` or `children` fields — shows chains |

**Frontmatter fields to extract:**
`id`, `title`, `status`, `priority`, `complexity`, `target_repos`, `blocked_by`, `related`, `children`, `compound`, `route`, `created_at`, `completed_at`

### 2. `.claude/work-queue/INDEX.md`

Generated output file (never hand-edited). Header includes generation timestamp and a note that it's auto-generated.

### 3. Update `.claude/skills/coordination/workspace/work-queue/SKILL.md`

Add `generate-index.py` to the Scripts table and document the `/work list` enhancement.

### 4. Update `.claude/skills/coordination/workspace/work-queue/actions/capture.md`

Add a step to regenerate the index after capturing new items.

## Implementation Details

- Use Python standard library only (`pathlib`, `yaml` via simple regex parsing, `datetime`)
- Parse frontmatter with a simple `---` delimiter split + `yaml.safe_load` (PyYAML is available in most Python environments; fallback to regex if not)
- Sort items by numeric ID extracted from `WRK-NNN`
- Mark the file as auto-generated with timestamp
- Script is idempotent — safe to re-run anytime

## Housekeeping (bundled)

While building the index, also:
- Move the 12 `status: done` items from `pending/` to `archive/2026-01/` (they should have been archived)
- Update `state.yaml` counters to reflect actual counts

## Verification

1. Run `python .claude/work-queue/scripts/generate-index.py` from workspace-hub root
2. Verify `.claude/work-queue/INDEX.md` is generated with all 65 items
3. Verify each section has correct groupings by spot-checking a few items
4. Re-run the script — output should be identical (idempotent)
