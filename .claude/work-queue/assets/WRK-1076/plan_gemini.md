# WRK-1076 Plan — Route A (Claude)

Route A (simple) — single inline plan. See `## Plan` in `pending/WRK-1076.md`.

## Summary
- `scripts/notify.sh` — writer shim, appends JSONL
- `scripts/hooks/session-start-notify.sh` — reader, silent on clean, banner on failures
- Wire into nightly cron + 7-day retention purge in crontab-template.sh
- 4 tests in `scripts/hooks/tests/test-session-start-notify.sh`
