# Plan: WRK-1143 — Centralized WRK Status Index

## Context

WRK-1143 targets a single source of truth (`wrk-status-index.json`) for WRK status across
parallel sessions. Investigation reveals most infrastructure is **already implemented**:

| Component | Status |
|-----------|--------|
| `scripts/work-queue/update-wrk-index.sh` | ✅ exists, 72 lines, atomic JSON upsert |
| `scripts/work-queue/rebuild-wrk-index.sh` | ✅ exists, 46 lines, scans all dirs |
| `.claude/work-queue/wrk-status-index.json` | ✅ exists, 450+ entries |
| `claim-item.sh` → index hook | ✅ wired (line 376) |
| `close-item.sh` → index hook | ✅ wired (line 338) |
| `archive-item.sh` → index hook | ✅ wired (line 119) |
| `generate-index.py` → rebuild hook | ✅ wired (line 988) |
| `whats-next.sh` reads index | ✅ `read_index_status()` present |

**Two items remain**: (1) `whats-next.sh` reads index for debug only — not as primary source; (2) no TDD test file.

## What Needs Doing

### 1. Update `whats-next.sh` — promote index to primary status source

**File**: `scripts/work-queue/whats-next.sh`

In `process_file()` (line ~137), `_idx_status` is read but never used for routing.
After reading `_idx_status`, override `status` when the index has an entry:

```bash
# Current:
_idx_status=$(read_index_status "$id")
_idx_source="scan"
[[ -n "$_idx_status" ]] && _idx_source="index"
[[ "$_DEBUG" == "true" ]] && title="${title} (${_idx_source})"

# Add after:
if [[ -n "$_idx_status" ]]; then
  status="$_idx_status"   # index is primary source
fi
```

This means the existing routing logic (UNCLAIMED_ACTIVE detection, coordinating checks)
automatically uses ground-truth status from the index instead of the potentially-stale
frontmatter `status:` field.

### 2. Write TDD tests — `tests/work-queue/test_wrk_index.py`

6 tests covering all ACs:

| Test | AC |
|------|----|
| `test_update_creates_entry` | update-wrk-index.sh writes to JSON |
| `test_update_upserts_idempotent` | repeat calls same result |
| `test_update_fields_populated` | machine, priority, category, updated_by set |
| `test_update_status_overwrite` | status changes on second call |
| `test_rebuild_produces_valid_json` | rebuild-wrk-index.sh → parseable JSON |
| `test_rebuild_clears_stale_entries` | rebuild re-scans from scratch |

Pattern: `subprocess.run()` against shell scripts in a `tmp_path`-based fake queue dir.
Set `WORK_QUEUE_ROOT` env var to redirect to tmp dir (supported by both scripts).

## Files Changed

| File | Change |
|------|--------|
| `scripts/work-queue/whats-next.sh` | +3 lines in `process_file()` — promote `_idx_status` to `status` |
| `tests/work-queue/test_wrk_index.py` | New file — 6+ TDD tests |

## Verification

```bash
# TDD first — all 6 tests pass before touching whats-next.sh:
uv run --no-project python -m pytest tests/work-queue/test_wrk_index.py -v

# Smoke test whats-next.sh with --debug to confirm (index) label:
bash scripts/work-queue/whats-next.sh --debug | head -20

# Full test suite still green:
uv run --no-project python -m pytest tests/work-queue/ -v
```
