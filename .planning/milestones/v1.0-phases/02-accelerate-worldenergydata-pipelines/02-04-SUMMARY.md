---
phase: 02-accelerate-worldenergydata-pipelines
plan: 04
subsystem: monitoring
tags: [staleness, alerting, smtp, scheduler, email]

requires:
  - phase: 02-01
    provides: "Scheduler monitoring (StatusReporter, RetryManager, JobLogger)"
  - phase: 02-02
    provides: "EIA adapter with JobResult pattern"
  - phase: 02-03
    provides: "BSEE/SODIR adapters with JobResult pattern"
provides:
  - "Staleness detection with per-source cadence thresholds (SODIR 36h, BSEE 10d, EIA 45d)"
  - "Email alerting via SMTP for job failures and staleness breaches"
  - "StatusReporter.check_and_alert integration method"
affects: [02-05, 02-06]

tech-stack:
  added: [smtplib, email.mime]
  patterns: [staleness-threshold-dict, alert-sender-pattern, graceful-smtp-fallback]

key-files:
  created:
    - worldenergydata/src/worldenergydata/scheduler/staleness.py
    - worldenergydata/src/worldenergydata/scheduler/alerting.py
    - worldenergydata/tests/unit/scheduler/test_staleness.py
    - worldenergydata/tests/unit/scheduler/test_alerts.py
  modified:
    - worldenergydata/src/worldenergydata/scheduler/monitor.py
    - worldenergydata/config/scheduler/scheduler_config.yml

key-decisions:
  - "Used MIMEMultipart/MIMEText for email construction (stdlib, no deps)"
  - "AlertSender returns graceful no-op when SMTP not configured (log-only fallback)"
  - "check_staleness treats missing jobs as stale (never-run = always stale)"
  - "Staleness check reads persisted status.json via _read_status for accurate timestamps"

patterns-established:
  - "Staleness threshold dict: STALENESS_THRESHOLDS maps job name to timedelta"
  - "Alert sender pattern: enabled property + send_alert with graceful exception handling"
  - "check_and_alert pattern: write status, check failures, check staleness, send alerts"

requirements-completed: [D-13, D-14, D-15, D-16]

duration: 18min
completed: 2026-03-26
---

# Phase 02 Plan 04: Staleness & Alerting Summary

**Staleness detection with per-source cadence thresholds and SMTP email alerting for failures and stale data**

## Performance

- **Duration:** 18 min
- **Started:** 2026-03-26T10:37:22Z
- **Completed:** 2026-03-26T10:55:25Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Staleness checker with SODIR 36h, BSEE 10d, EIA 45d thresholds matching D-13 cadences
- Email alerting via SMTP with graceful log-only fallback when not configured
- StatusReporter.check_and_alert integration wiring failures and staleness to alerts
- 17 tests covering staleness detection, alert sending, and integration scenarios

## Task Commits

Each task was committed atomically:

1. **Task 1: Staleness checker with per-source cadence thresholds** - `63e9935` (feat)
2. **Task 2: Email alerting and StatusReporter integration** - `9a8b6b9` (feat)

_Note: TDD tasks — tests written first, then implementation._

## Files Created/Modified
- `worldenergydata/src/worldenergydata/scheduler/staleness.py` - Staleness detection with STALENESS_THRESHOLDS dict and check_staleness/get_staleness_details functions
- `worldenergydata/src/worldenergydata/scheduler/alerting.py` - AlertSender class with SMTP delivery and graceful no-op fallback
- `worldenergydata/src/worldenergydata/scheduler/monitor.py` - Added check_and_alert and _read_status methods to StatusReporter
- `worldenergydata/config/scheduler/scheduler_config.yml` - Added smtp_host/user/pass/port/alert_recipients config fields
- `worldenergydata/tests/unit/scheduler/test_staleness.py` - 10 tests for staleness detection
- `worldenergydata/tests/unit/scheduler/test_alerts.py` - 7 tests for alerting with mocked SMTP

## Decisions Made
- Used MIMEMultipart/MIMEText for email construction (stdlib only, no external dependencies)
- AlertSender._enabled = bool(smtp_host and smtp_user and smtp_pass) for clean no-op check
- check_staleness treats jobs missing from status dict as stale (never-run = always stale)
- _read_status reads persisted status.json rather than in-memory report for accurate historical timestamps

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed staleness.py to handle missing jobs as stale**
- **Found during:** Task 1
- **Issue:** Pre-existing staleness.py (from parallel agent) skipped jobs not present in status dict instead of treating them as stale
- **Fix:** Changed to use `jobs.get(job_name, {})` and treat missing/None as stale
- **Files modified:** worldenergydata/src/worldenergydata/scheduler/staleness.py
- **Verification:** test_none_last_run_is_stale passes
- **Committed in:** 63e9935 (Task 1 commit)

**2. [Rule 1 - Bug] Fixed alerting.py to match plan spec (MIMEMultipart, enabled property)**
- **Found during:** Task 2
- **Issue:** Pre-existing alerting.py (from parallel agent) used EmailMessage instead of MIMEMultipart, lacked enabled property, had different fallback logic
- **Fix:** Rewrote to use MIMEMultipart/MIMEText, added enabled property and _enabled check
- **Files modified:** worldenergydata/src/worldenergydata/scheduler/alerting.py
- **Committed in:** 9a8b6b9 (Task 2 commit)

**3. [Rule 1 - Bug] Fixed monitor.py check_and_alert to include staleness checking**
- **Found during:** Task 2
- **Issue:** Pre-existing check_and_alert (from parallel agent) only checked failures, missing staleness integration
- **Fix:** Added staleness import, _read_status method, and staleness alert loop
- **Files modified:** worldenergydata/src/worldenergydata/scheduler/monitor.py
- **Committed in:** 9a8b6b9 (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (3 bugs from parallel agent partial implementations)
**Impact on plan:** All fixes necessary for correctness. No scope creep.

## Issues Encountered
- Parallel agent had created partial implementations of staleness.py, alerting.py, and modified monitor.py. These needed correction to match plan specifications and pass all required tests.

## User Setup Required

SMTP configuration required for email alerting. Environment variables needed:
- `SMTP_HOST` - SMTP server (e.g., smtp.gmail.com)
- `SMTP_USER` - SMTP login email
- `SMTP_PASS` - SMTP password or app-specific password

Without these, alerting degrades gracefully to log-only mode.

## Known Stubs

None - all data paths are fully wired.

## Next Phase Readiness
- Monitoring and alerting layer complete
- StatusReporter.check_and_alert ready for scheduler integration in 02-05/02-06
- SMTP config documented in scheduler_config.yml

## Self-Check: PASSED

- All 6 source/test files: FOUND
- Commit 63e9935 (Task 1): FOUND
- Commit 9a8b6b9 (Task 2): FOUND
- 17/17 tests passing

---
*Phase: 02-accelerate-worldenergydata-pipelines*
*Completed: 2026-03-26*
