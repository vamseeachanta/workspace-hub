# WRK-1078 Plan — Claude Draft

**Title:** Audit and fix WRK pipeline Windows/Git Bash compatibility gaps
**Route:** B (Medium)
**Date:** 2026-03-10

## Executive Summary

Five compatibility gaps prevent the WRK pipeline from running cleanly on
Windows MINGW64 (acma-ansys05). This plan fixes the four actionable gaps
and documents the one non-issue (sed -i).

## Triage Findings

| Gap | Finding | Action |
|-----|---------|--------|
| xdg-open | Missing on Windows/macOS | Fix — cross-platform helper |
| sed -i | GNU sed on MINGW64 — works fine | No change needed |
| uv not available | verify-setup.sh lacks Windows hint | Fix — add hint text |
| python3 bare calls | archive-item.sh (2 lines) | Fix — uv run --no-project python |
| Python Unicode stdout | checkpoint_writer.py box chars crash cp1252 | Fix — stdout reconfigure |
| Crontab | Full cron is Linux-only | Doc — add callout to new-machine-setup.md |

## Phase 1 — Cross-platform browser opener

**File:** `scripts/work-queue/log-user-review-browser-open.sh`

Replace:
```bash
if ! xdg-open "$HTML_PATH" >/dev/null 2>&1; then
```

With a `_open_browser()` function that detects OS:
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

## Phase 2 — archive-item.sh python3 → uv

**File:** `.claude/work-queue/scripts/archive-item.sh`

- Line ~59: `python3 <<EOF` → `uv run --no-project python <<EOF`
- Line ~79: `python3 "${QUEUE_DIR}/scripts/generate-index.py"` → `uv run --no-project python ...`

## Phase 3 — verify-setup.sh Windows uv hint

**File:** `scripts/setup/verify-setup.sh`

In the `_fail "python not found"` branch, expand to:
```
_fail "python not found — install uv (https://docs.astral.sh/uv/getting-started/installation/) or Python 3.10+"
_warn "  Windows/MINGW64: curl -LsSf https://astral.sh/uv/install.sh | sh"
_warn "  Then add \$USERPROFILE/.local/bin to PATH"
```

## Phase 4 — Python Unicode encoding fix

**Files:** `scripts/work-queue/start_stage.py`, `scripts/work-queue/exit_stage.py`

Add near top of `_main()` in each file:
```python
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
```

This guards against cp1252 crash when printing box-drawing characters from
`checkpoint_writer.py`.

## Phase 5 — Crontab documentation

**File:** `.claude/docs/new-machine-setup.md` §5 Cron Jobs

Add callout after "Windows Task Scheduler (contribute-minimal)" heading:
```
> **Note:** Full nightly automation (comprehensive-learning, session-analysis,
> repository-sync) runs on ace-linux-1 only. Windows machines (ACMA-ANSYS05,
> acma-ws014) are contribute-minimal — no cron daemon; use Windows Task
> Scheduler for the two scheduled tasks only.
```

## Test Strategy

1. Run `start_stage.py` and `exit_stage.py` without `PYTHONIOENCODING` → no crash
2. Run `log-user-review-browser-open.sh WRK-TEST --stage plan_draft --html x.html --no-open`
3. Run `bash scripts/setup/verify-setup.sh` → all checks pass on Linux
4. Simulate archive with a dummy item to confirm `uv run` path works
