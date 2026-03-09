# WRK-1076 Plan — Final Approved

## Plan (Route A)

1. `scripts/notify.sh` — JSONL writer shim (exits 0 always)
2. `scripts/hooks/session-start-notify.sh` — reads last 24h, silent on clean, banner on failures
3. Wire into `comprehensive-learning-nightly.sh` + 7-day retention in `crontab-template.sh`
4. 5 bash tests in `scripts/hooks/tests/test-session-start-notify.sh`

## Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-09T07:00:00Z
decision: passed
