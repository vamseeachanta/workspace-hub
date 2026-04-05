# Plan Review — WRK-309

## Work Item

**ID**: WRK-309
**Title**: chore: portable Python invocation — consistent cross-machine execution, zero error noise
**Complexity**: medium (Route B)
**Target**: workspace-hub

## Problem Statement

Two related friction issues on Windows MINGW64:

1. **`python3` not found** — Windows exposes Python as `python`, not `python3`. Scripts that call `python3` fail with exit code 49. The workaround (`python`) works but is inconsistent — agents waste turns on the fallback.

2. **`uv run python` per-file in `check-encoding.sh`** — The hook's `check_file()` function is called once per staged/tracked file (line 52 of `.claude/hooks/check-encoding.sh`). Each call spawns a fresh `uv run` process. On Windows, uv startup overhead × 200 files = noticeable commit-loop delay.

## Proposed Plan

### Step 1: Create `scripts/lib/python-resolver.sh`

New file. Sets `PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)` with hard exit if neither found. All scripts source this file to get a portable `$PYTHON` variable.

### Step 2: Fix 7 scripts with bare `python3` calls

Source the resolver, replace `python3` with `${PYTHON}`. Files:
- `scripts/cron/comprehensive-learning-nightly.sh:11`
- `scripts/operations/compliance/normalize_work_queue_metadata.sh:28`
- `scripts/operations/compliance/validate_work_queue_schema.sh:45`
- `scripts/test/lib/invoke-pytest.sh:51`
- `scripts/development/ai-workflow/auto-fix-loop.sh:228`
- `scripts/ai/assessment/auto-sync-usage.sh:115,190,202,209`
- `scripts/utilities/doc-to-context/doc2context.sh:60,97`

### Step 3: Refactor `check-encoding.sh` — batch mode

Replace the per-file `check_file()` loop with a single `uv run python` invocation that receives all file paths via stdin and returns all bad files at once. 200 files → 1 uv process.

### Test Plan

- `bash .claude/hooks/check-encoding.sh` — no exit 49, completes in <5s on 200+ files
- `scripts/operations/compliance/validate_work_queue_schema.sh` — exits cleanly on Windows
- Zero `python3: command not found` output on Windows MINGW64

## Review Questions

1. Are there any other `python3` call sites that should be included (e.g. in `.claude/skills/`)?
2. Is `scripts/lib/` the right location for a shared resolver, or should it live in `scripts/utilities/`?
3. Any concerns about the batch stdin approach for `check-encoding.sh`? Is there a simpler refactor?
4. Should `scripts/data/batchtools/` (which already guards with `command -v python3`) also be updated for consistency?
