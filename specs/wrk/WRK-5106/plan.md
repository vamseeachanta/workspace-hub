---
confirmed_by: vamsee
confirmed_at: 2026-03-21T12:00:00Z
decision: passed
reviewed: true
approved: true
---
# WRK-5106 Plan — Merged

## Deliverable
One new script: `scripts/work-queue/backfill-issues.sh` (~150 lines bash)

## Approach

### Phase 0: Preflight
1. Check `gh auth status` and `uv` availability — fail fast if missing
2. Create temp file with `mktemp`; register `trap 'rm -f "$TMPFILE"' EXIT`

### Phase 1: Fetch & Match
1. `gh issue list --repo vamseeachanta/workspace-hub --state all --limit 5000 --json number,title` → `$TMPFILE`
2. Truncation check: if `jq length` equals 5000, warn and abort (use `--paginate` if needed)
3. All title processing stays in `jq` pipeline — never interpolate titles into shell variables
4. Extract WRK ID via `jq -r` regex: `.title | capture("(?<id>WRK-[0-9]+)")`
   - Zero matches → skip (SKIPPED_NO_WRK++)
   - One match → continue
   - Multiple matches → log warning, skip (SKIPPED_AMBIGUOUS++)
5. Find local WRK file using `find_wrk_file()` pattern from `backfill-domain-labels.sh`
   - Not found → skip (SKIPPED_NO_FILE++)
6. Process in ascending issue number order for deterministic behavior

### Phase 2: Backfill github_issue_ref
6. Use `uv run --no-project python` inline script to safely read/update YAML frontmatter
   - If `github_issue_ref` missing → inject with correct URL
   - If already correct → skip (no rewrite)
   - If malformed frontmatter → log and skip
7. In `--dry-run` mode: log "would update" but write nothing

### Phase 3: Update GitHub Issues
8. Call `uv run --no-project python scripts/knowledge/update-github-issue.py WRK-NNN --update`
9. Rate limit: `sleep 1` between calls; retry up to 3x on failure
10. On error: log issue number + WRK ID, continue (ERRORS++)

### Phase 4: Report
11. Print summary: total / matched / updated / skipped (by reason) / errors

## CLI Interface
```bash
backfill-issues.sh [--dry-run] [--limit N] [--resume-from ISSUE_NUMBER] [--verbose]
```

## Test Strategy
1. `--dry-run --limit 5` — verify output, zero writes
2. Live run on 3 known issues, spot-check in browser
3. Verify `github_issue_ref` backfilled via `git diff`
