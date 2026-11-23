# WRK-5105: Index-First whats-next with Enriched Columns

## Context

`whats-next.sh` takes **2m36s** for `--all` because it scans 419 WRK files individually and calls `uv run urgency_score.py` (21s alone). The user wants ≤2s with richer columns (category, subcategory, urgency, GH#, age). The fix: pre-compute everything in `wrk-status-index.json` at write time, make whats-next a pure read-and-render script.

## Plan

### Step 1: Enrich `update-wrk-index.sh` (the write path)

**File:** `scripts/work-queue/update-wrk-index.sh`

Currently extracts 3 frontmatter fields (title, priority, category). Add extraction for:

| Field | Source | grep pattern |
|---|---|---|
| `subcategory` | frontmatter | `^subcategory:` |
| `created_at` | frontmatter | `^created_at:` |
| `blocked_by` | frontmatter | `^blocked_by:` |
| `github_issue_ref` | frontmatter | `^github_issue_ref:` |
| `type` | frontmatter | `^type:` |
| `note` | frontmatter | `^note:` |
| `not_before` | frontmatter | `^not_before:` |
| `standing` | frontmatter | `^standing:` |
| `cadence` | frontmatter | `^cadence:` |
| `computer` | frontmatter | `^computer:` |

Also compute and store:
- `checkpoint_stage` — read from `assets/WRK-NNN/checkpoint.yaml` if it exists
- `session_pid` — read from `assets/WRK-NNN/evidence/session-lock.yaml` if it exists
- `urgency_score` — inline Python computation (port the core formula from urgency_score.py, no `uv run`)

Update the Python upsert block to include all new fields in the JSON entry.

### Step 2: Enrich `rebuild-wrk-index.sh`

**File:** `scripts/work-queue/rebuild-wrk-index.sh`

No structural change needed — it already calls `update-wrk-index.sh` per file. The enriched update script automatically enriches the index during rebuild.

Add: after all files are processed, run a single-pass urgency score computation (blocking_count requires knowing all items). This is a post-pass Python snippet that:
1. Reads the just-built index
2. For each non-archived entry, computes `blocking_count` (how many other items list this WRK in their `blocked_by`)
3. Computes final `urgency_score` using the same formula as `urgency_score.py`
4. Writes scores back into the index atomically

### Step 3: Rewrite `whats-next.sh` data path (index-first)

**File:** `scripts/work-queue/whats-next.sh`

Replace the current approach:
- ~~`process_file()` scanning each .md file with grep~~
- ~~`uv run urgency_score.py --all --json`~~
- ~~`is_archived()` with find calls~~

With:
1. Single `python3 -c` call that reads `wrk-status-index.json` and outputs pre-filtered, pre-sorted rows as TSV
2. The Python snippet handles: category/subcategory filtering, blocker resolution (index has `blocked_by` + archived status), urgency sorting, section classification (working/parked/unclaimed/high/newly-unblocked/medium/blocked/deferred)
3. Bash reads TSV output and feeds directly into existing `draw_table()` functions

Keep `draw_table()` and all render functions unchanged — only the data source changes.

### Step 4: Add new columns to render functions

**File:** `scripts/work-queue/whats-next.sh`

Update `render_ready_section()`:
- New columns: `ICON | WRK | PRI | URG | CAT | SUB | GH# | AGE | TITLE`
- Column widths: `4|10|5|4|10|12|6|5|60` (≈120 chars)

Update `render_working_section()`:
- New columns: `ICON | WRK | PRI | URG | STG | PID | GH# | AGE | TITLE`

Add `--compact` flag that uses the current minimal columns (backward compat).

### Step 5: Add AGE and GH# formatting

In the Python data-prep snippet (Step 3):
- `age`: compute `(today - created_at)` → format as `Xd` (<30), `Xw` (<90), `Xmo` (≥90)
- `gh_num`: extract issue number from `github_issue_ref` URL → `#1253` or `—`

### Step 6: Update tests

**File:** `scripts/work-queue/tests/test_wrk_index.py`

- Add test for enriched index fields (subcategory, urgency_score, github_issue_ref, etc.)
- Add test that rebuild produces urgency scores
- Update T65 (whats-next wiring) to verify index-first path

## Files Modified

| File | Change |
|---|---|
| `scripts/work-queue/update-wrk-index.sh` | Extract 10 new frontmatter fields + checkpoint/pid |
| `scripts/work-queue/rebuild-wrk-index.sh` | Add urgency score post-pass |
| `scripts/work-queue/whats-next.sh` | Index-first data path + new column layout |
| `scripts/work-queue/tests/test_wrk_index.py` | Tests for enriched fields |

## Reuse

- `urgency_score.py` formula (lines 103-115) — port to inline Python in rebuild script
- `draw_table()` function (lines 287-351) — keep as-is
- `render_blocked()`, `render_coordinating()` — keep as-is, just add columns
- Existing `get_field()` pattern in update-wrk-index.sh — extend for new fields

## Verification

1. `bash scripts/work-queue/rebuild-wrk-index.sh` — verify enriched JSON has all new fields
2. `python3 -c "import json; d=json.load(open('.claude/work-queue/wrk-status-index.json')); print(json.dumps(list(d.values())[0], indent=2))"` — spot-check one entry
3. `time bash scripts/work-queue/whats-next.sh --all` — must complete in ≤2s
4. `bash scripts/work-queue/whats-next.sh --compact` — backward compat (old column layout)
5. `uv run --no-project python -m pytest scripts/work-queue/tests/test_wrk_index.py -v` — all tests pass
6. Visual: verify new columns render correctly in terminal at 120+ chars width
