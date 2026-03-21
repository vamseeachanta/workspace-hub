# WRK-5106 Plan — Claude

## Deliverable
One new script: `scripts/work-queue/backfill-issues.sh` (~120 lines bash)

## Approach

### Phase 1: Fetch & Match
1. `gh issue list --repo vamseeachanta/workspace-hub --state all --limit 5000 --json number,title` → temp file
2. For each issue, extract `WRK-NNN` from title via regex
3. Find local WRK file using `find_wrk_file()` pattern from `backfill-domain-labels.sh`

### Phase 2: Backfill github_issue_ref
4. If WRK file lacks `github_issue_ref:` line, inject it into YAML frontmatter
5. Use `sed` to insert after `github_issue_ref:` or before closing `---`

### Phase 3: Update Issues
6. Call `uv run --no-project python scripts/knowledge/update-github-issue.py WRK-NNN --update` for each match
7. Rate limit: `sleep 0.5` between calls (~10 min for 1256 issues)
8. On error: log and continue (don't abort)

### Phase 4: Report
9. Print summary: total / updated / skipped (no WRK ID, no file, already current) / errors

## CLI Interface
```
backfill-issues.sh [--dry-run] [--limit N] [--resume-from N]
```
- `--dry-run`: log what would happen, no API writes
- `--limit N`: process only first N issues
- `--resume-from N`: skip first N issues (for failure recovery)

## Risks
- WRK files with minimal content may produce sparse issue bodies (acceptable — template is additive)
- Rate limiting: 2512 API calls at 0.5s spacing = ~21 min, well within 5000/hr

## Test Strategy
1. `--dry-run --limit 5` — verify output format, no API calls
2. Manual spot-check 3 updated issues in browser
3. Verify `github_issue_ref` backfilled correctly in WRK files
