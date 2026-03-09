# WRK-1076 Acceptance Criteria Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| AC-1 | `notify.sh` appends structured JSONL | test-session-start-notify.sh: notify-writes-jsonl | PASS |
| AC-2 | `session-start-notify.sh` reads last 24h, prints failure banner | test-session-start-notify.sh: one-fail-banner | PASS |
| AC-3 | Banner suppressed when all jobs pass | test-session-start-notify.sh: all-pass-silent | PASS |
| AC-4 | No dir → silent (handles missing log dir) | test-session-start-notify.sh: no-dir-silent | PASS |
| AC-5 | Mixed PASS/FAIL → only FAILs in banner | test-session-start-notify.sh: mixed-only-fails | PASS |
| AC-6 | Nightly cron wired to notify.sh | comprehensive-learning-nightly.sh: manual inspection | PASS |
| AC-7 | 7-day retention purge in crontab-template.sh | crontab-template.sh: manual inspection | PASS |

Test run: `bash scripts/hooks/tests/test-session-start-notify.sh`
Result: 5 pass, 0 fail
