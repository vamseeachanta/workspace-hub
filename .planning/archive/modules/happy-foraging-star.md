# WRK-1143 Plan: Centralized WRK Status Index

## Context
`whats-next.sh` and related tools derive WRK state by scanning file locations
(`pending/`, `working/`) and re-parsing frontmatter on every call. When a parallel
session updates a WRK file's `status:` field without moving it (or vice versa), the
display diverges from reality. A single machine-readable index written at-source by
workflow scripts eliminates this class of inconsistency.

## Approach

### New scripts (2)

**`scripts/work-queue/update-wrk-index.sh <WRK-ID> <status> [caller]`**
- Reads priority/category/title/machine from the WRK `.md` file
- Atomically upserts one entry into `.claude/work-queue/wrk-status-index.json`
  via a Python heredoc (temp-file + `os.replace`) — avoids partial-write corruption
- Records `machine` (hostname), `last_updated` (ISO UTC), `updated_by` (caller)
- Idempotent: repeat calls with same status overwrite cleanly
- Exit 0 on success; exit 1 with stderr on missing WRK-ID

**`scripts/work-queue/rebuild-wrk-index.sh`**
- Scans `pending/`, `working/`, `blocked/`, `archive/YYYY-MM/` for `WRK-*.md`
- Calls `update-wrk-index.sh` for each file using its frontmatter `status:` field
- Full rebuild: safe to re-run at any time (idempotent)

### Wire into source scripts (3 insertion points)

All three scripts already call `generate-index.py` before exit. Add
`update-wrk-index.sh` call immediately **before** `generate-index.py` in each:

| Script | Line (approx) | New status | Insert before |
|--------|--------------|------------|---------------|
| `claim-item.sh` | 373 | `working` | `uv run ... generate-index.py` |
| `close-item.sh` | 335 | `done` | `uv run ... generate-index.py` |
| `archive-item.sh` | 117 | `archived` | `uv run ... generate-index.py` |

Pattern (same in all three):
```bash
# Update centralized status index
INDEX_UPDATER="${REPO_ROOT}/scripts/work-queue/update-wrk-index.sh"
if [[ -x "$INDEX_UPDATER" ]]; then
  bash "$INDEX_UPDATER" "$WRK_ID" "<status>" "$(basename "$0")" || true
fi
```

### Update `whats-next.sh`

Add `read_index_status()` helper near top:
```bash
read_index_status() {
  # Returns status from index, or empty string if absent
  local id="$1"
  local idx="$QUEUE_DIR/wrk-status-index.json"
  [[ -f "$idx" ]] || return
  python3 -c "
import json,sys
d=json.load(open('$idx'))
e=d.get('$id',{})
print(e.get('status',''))
" 2>/dev/null
}
```

In `process_file()`, after `id` is extracted, add:
```bash
  _idx_status=$(read_index_status "$id")
  _idx_source="scan"
  if [[ -n "$_idx_status" ]]; then _idx_source="index"; fi
  # --debug: annotate display with source
  [[ "${_DEBUG:-false}" == "true" ]] && title="$title (${_idx_source})"
```

Also add `--debug` flag to arg parser:
```bash
--debug) _DEBUG=true; shift ;;
```

### Update `generate-index.py`

At end of `main()`, after `validate-queue-state.sh` succeeds, add:
```python
rebuild_script = REPO_ROOT / "scripts" / "work-queue" / "rebuild-wrk-index.sh"
if rebuild_script.exists():
    subprocess.run(["bash", str(rebuild_script)], capture_output=True)
```

### Tests: `scripts/work-queue/tests/test_wrk_index.py`

Follow existing pattern: `REPO_ROOT = Path(__file__).resolve().parents[3]`, use `tmp_path`.

| ID | Test | Type |
|----|------|------|
| T60 | `rebuild-wrk-index.sh` on temp queue dir → valid JSON, correct status values | happy |
| T61 | `update-wrk-index.sh` upserts new entry; repeat call overwrites cleanly | idempotent |
| T62 | `update-wrk-index.sh` creates index file when none exists | edge |
| T63 | `update-wrk-index.sh` with missing WRK-ID exits 1 with message | error |
| T64 | `claim-item.sh` output includes `wrk-status-index.json` update line | integration |
| T65 | `whats-next.sh --debug` shows `(index)` annotation for indexed item | integration |

## Files Modified

- **New**: `scripts/work-queue/update-wrk-index.sh`
- **New**: `scripts/work-queue/rebuild-wrk-index.sh`
- **New**: `scripts/work-queue/tests/test_wrk_index.py`
- **Modified**: `scripts/work-queue/claim-item.sh` (~line 373)
- **Modified**: `scripts/work-queue/close-item.sh` (~line 335)
- **Modified**: `scripts/work-queue/archive-item.sh` (~line 117)
- **Modified**: `scripts/work-queue/whats-next.sh` (add helper + `--debug`)
- **Modified**: `scripts/work-queue/generate-index.py` (add rebuild call in main)

## Scripts to Create (25% rule)

`update-wrk-index.sh` and `rebuild-wrk-index.sh` are the deliverables — no further
helper scripts needed.

## Verification

```bash
# Build index from current queue state
bash scripts/work-queue/rebuild-wrk-index.sh
cat .claude/work-queue/wrk-status-index.json | python3 -m json.tool | head -20

# Confirm wiring in claim (dry observation — claim a real item or use test)
uv run --no-project python -m pytest scripts/work-queue/tests/test_wrk_index.py -v

# Debug mode
bash scripts/work-queue/whats-next.sh --debug | head -20
```
