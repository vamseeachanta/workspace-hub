# WRK-1078 Cross-Review — Plan Phase

**WRK:** WRK-1078
**Title:** Audit and fix WRK pipeline Windows/Git Bash compatibility gaps
**Route:** B (Medium)
**Review type:** Plan review

## Context

The WRK pipeline has 5 compatibility gaps that prevent scripts from running
cleanly on Windows MINGW64 (Git Bash). Resource intelligence (Stage 2) audited
all affected scripts. Triage confirmed sed -i is NOT a problem on MINGW64
(GNU sed handles it correctly). 4 actionable fixes + 1 doc update remain.

## Plan Summary

### Phase 1 — Cross-platform browser opener
**File:** `scripts/work-queue/log-user-review-browser-open.sh` (line 58)

Replace bare `xdg-open "$HTML_PATH"` with an `_open_browser()` helper:
```bash
_open_browser() {
  local path="$1"
  case "$(uname -s)" in
    Linux*)  xdg-open "$path" >/dev/null 2>&1 ;;
    Darwin*) open "$path" >/dev/null 2>&1 ;;
    MINGW*|MSYS*|CYGWIN*) start "" "$path" >/dev/null 2>&1 ;;
    *) return 1 ;;
  esac
}
```
Then call `_open_browser "$HTML_PATH"` in place of `xdg-open`.

### Phase 2 — archive-item.sh python3 → uv
**File:** `.claude/work-queue/scripts/archive-item.sh` (lines ~59, ~79)

Replace `python3 <<EOF` with `uv run --no-project python <<EOF` and
`python3 "${QUEUE_DIR}/scripts/generate-index.py"` with the uv equivalent.

### Phase 3 — verify-setup.sh Windows uv hint
**File:** `scripts/setup/verify-setup.sh` (line ~234)

Extend the `_fail "python not found"` message to include Windows-specific
uv install instructions (curl installer + PATH hint).

### Phase 4 — Python Unicode encoding (bonus fix)
**Files:** `scripts/work-queue/start_stage.py`, `scripts/work-queue/exit_stage.py`

Add at top of `_main()`:
```python
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
```
This prevents UnicodeEncodeError when printing box-drawing characters
(╔═╗) from `checkpoint_writer.py` on Windows cp1252 consoles.

### Phase 5 — Crontab documentation
**File:** `.claude/docs/new-machine-setup.md` §5

Add blockquote noting cron automation is Linux (ace-linux-1) only; Windows
machines use Task Scheduler for contribute-minimal tasks only.

## Review Questions

1. Is the `uname -s` approach the right cross-platform detection strategy, or
   should we use `$OSTYPE` instead?
2. Are there any other pipeline scripts (beyond archive-item.sh) that need
   python3→uv migration for Windows compatibility?
3. Is `sys.stdout.reconfigure` safe for Python 3.7+? (It's available from 3.7)
4. Any concerns with the `start "" "$path"` Windows approach for HTML opening?
