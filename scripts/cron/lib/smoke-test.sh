#!/usr/bin/env bash
# Standalone shared-helper examples only; no cadence execution or repository setup.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/cron/lib/cadence-common.sh
source "${SCRIPT_DIR}/cadence-common.sh"

check() {
    local label="$1" expected="$2" actual
    shift 2
    actual="$("$@")"
    if [[ "$actual" != "$expected" ]]; then
        printf 'cadence helpers: FAIL (%s)\n' "$label" >&2
        exit 1
    fi
}

# Literal header example: test_emit_report_header_format in
# tests/cron/test_cadence_common.py (same period, status and Markdown layout).
check header $'# cadence-smoke — 2026-W16\n\n**Status:** GREEN — synthetic example' \
    emit_report_header cadence-smoke 2026-W16 GREEN 'synthetic example'

# Hand-picked integers from test_compute_status_band_basic and boundary tests
# in tests/cron/test_cadence_common.py. The helper's threshold comments specify:
# 3 <= 5 -> GREEN; 5 == warn -> GREEN; 5 < 7 <= 10 -> YELLOW;
# 10 == block -> YELLOW; 15 > 10 -> RED. Equality must never enter the next band.
check 'below warn' GREEN compute_status_band 3 5 10
check 'warn equality' GREEN compute_status_band 5 5 10
check 'between thresholds' YELLOW compute_status_band 7 5 10
check 'block equality' YELLOW compute_status_band 10 5 10
check 'above block' RED compute_status_band 15 5 10

# Stub the date command, not cadence_period: these examples cannot read the clock.
# Synthetic calendar basis: April 16, 2026 is Thursday, fifteen weeks after
# January 1 (also Thursday), hence ISO week 16. Month 4 gives quarter
# (4 - 1) / 3 + 1 = 2 using integer division. Weekly notation also matches the
# cited header fixture. No external date command is executed.
date() {
    case "$*" in
        +%Y-W%V) printf '%s\n' '2026-W16' ;;
        +%Y-%m) printf '%s\n' '2026-04' ;;
        +%Y) printf '%s\n' '2026' ;;
        +%-m) printf '%s\n' '4' ;;
        *) printf 'unexpected smoke date format\n' >&2; return 1 ;;
    esac
}

check weekly 2026-W16 cadence_period weekly
check monthly 2026-04 cadence_period monthly
check quarterly 2026-Q2 cadence_period quarterly
printf 'cadence helpers: PASS\n'
