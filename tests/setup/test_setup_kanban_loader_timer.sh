#!/usr/bin/env bash
# test_setup_kanban_loader_timer.sh — TDD tests for
# scripts/install/setup-kanban-loader-timer.sh
# Issue: vamseeachanta/workspace-hub#2827 (Part 3 — per-machine time-based trigger)
#
# Strategy (mirrors tests/setup/test_install_provider_clis.sh): source the
# installer with KANBAN_TIMER_LIB=1 so it defines functions but does NOT run
# main(). Redefine the side-effecting wrappers (systemctl/crontab/git/loader)
# to log invocations into a file, then call the installer's functions and assert
# on the log + exit codes.
#
# Run: bash tests/setup/test_setup_kanban_loader_timer.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
INSTALLER="${REPO_ROOT}/scripts/install/setup-kanban-loader-timer.sh"

PASS=0
FAIL=0
FAILED_TESTS=()

_assert_contains() {
    local name="$1" needle="$2" haystack="$3"
    if grep -qF -- "$needle" <<<"$haystack"; then
        echo "  PASS  $name"; PASS=$((PASS + 1))
    else
        echo "  FAIL  $name"
        echo "        expected substring: $needle"
        echo "        actual:"; echo "$haystack" | sed 's/^/          /'
        FAIL=$((FAIL + 1)); FAILED_TESTS+=("$name")
    fi
}

_assert_not_contains() {
    local name="$1" needle="$2" haystack="$3"
    if grep -qF -- "$needle" <<<"$haystack"; then
        echo "  FAIL  $name"
        echo "        forbidden substring present: $needle"
        FAIL=$((FAIL + 1)); FAILED_TESTS+=("$name")
    else
        echo "  PASS  $name"; PASS=$((PASS + 1))
    fi
}

_assert_eq() {
    local name="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS  $name"; PASS=$((PASS + 1))
    else
        echo "  FAIL  $name (expected '$expected', got '$actual')"
        FAIL=$((FAIL + 1)); FAILED_TESTS+=("$name")
    fi
}

echo "=== test_setup_kanban_loader_timer.sh (issue #2827 Part 3) ==="
echo ""

if [[ ! -f "$INSTALLER" ]]; then
    echo "  FAIL  installer script missing: $INSTALLER"
    echo "        (expected in TDD RED phase before implementation)"
    echo ""
    echo "=== Summary: 0 PASS, 1 FAIL ==="
    exit 1
fi

# --- Test 1: --check makes NO mutations ------------------------------------
log="$(bash <<TESTEOF 2>&1
    set -u
    export KANBAN_TIMER_LIB=1
    export KANBAN_AUTOLOAD_MARKER="\$(mktemp)"   # marker present -> enabled
    source "$INSTALLER"
    # Override every mutator to log instead of acting.
    run_systemctl() { echo "FAKE systemctl \$*"; }
    run_crontab()   { echo "FAKE crontab \$*"; }
    write_unit()    { echo "FAKE write_unit \$1"; }
    remove_unit()   { echo "FAKE remove_unit \$1"; }
    MODE=check
    main
TESTEOF
)"
_assert_not_contains "check_no_systemctl"   "FAKE systemctl"   "$log"
_assert_not_contains "check_no_crontab"     "FAKE crontab"     "$log"
_assert_not_contains "check_no_write_unit"  "FAKE write_unit"  "$log"

# --- Test 2: --dry-run makes NO mutations (but previews) --------------------
log="$(bash <<TESTEOF 2>&1
    set -u
    export KANBAN_TIMER_LIB=1
    export KANBAN_AUTOLOAD_MARKER="\$(mktemp)"
    source "$INSTALLER"
    run_systemctl() { echo "FAKE systemctl \$*"; }
    run_crontab()   { echo "FAKE crontab \$*"; }
    write_unit()    { echo "FAKE write_unit \$1"; }
    remove_unit()   { echo "FAKE remove_unit \$1"; }
    MODE=dry-run
    main
TESTEOF
)"
_assert_not_contains "dryrun_no_systemctl"  "FAKE systemctl enable" "$log"
_assert_not_contains "dryrun_no_write_unit" "FAKE write_unit"       "$log"
_assert_contains     "dryrun_previews"      "Would"                 "$log"

# --- Test 3: install emits a timer/cron entry ------------------------------
log="$(bash <<TESTEOF 2>&1
    set -u
    export KANBAN_TIMER_LIB=1
    export KANBAN_AUTOLOAD_MARKER="\$(mktemp)"
    source "$INSTALLER"
    run_systemctl() { echo "FAKE systemctl \$*"; }
    run_crontab()   { echo "FAKE crontab \$*"; }
    write_unit()    { echo "FAKE write_unit \$1"; }
    remove_unit()   { echo "FAKE remove_unit \$1"; }
    # Force the systemd path deterministically for the assertion.
    has_systemd() { return 0; }
    MODE=install
    main
TESTEOF
)"
_assert_contains "install_writes_timer_unit"  "FAKE write_unit"        "$log"
_assert_contains "install_enables_timer"      "FAKE systemctl"         "$log"

# --- Test 4: install via crontab fallback when no systemd ------------------
log="$(bash <<TESTEOF 2>&1
    set -u
    export KANBAN_TIMER_LIB=1
    export KANBAN_AUTOLOAD_MARKER="\$(mktemp)"
    source "$INSTALLER"
    run_systemctl() { echo "FAKE systemctl \$*"; }
    run_crontab()   { echo "FAKE crontab \$*"; }
    write_unit()    { echo "FAKE write_unit \$1"; }
    remove_unit()   { echo "FAKE remove_unit \$1"; }
    has_systemd() { return 1; }   # no systemd -> crontab path
    MODE=install
    main
TESTEOF
)"
_assert_contains "install_crontab_fallback" "FAKE crontab" "$log"

# --- Test 5: teardown removes the timer/cron entry -------------------------
log="$(bash <<TESTEOF 2>&1
    set -u
    export KANBAN_TIMER_LIB=1
    export KANBAN_AUTOLOAD_MARKER="\$(mktemp)"
    source "$INSTALLER"
    run_systemctl() { echo "FAKE systemctl \$*"; }
    run_crontab()   { echo "FAKE crontab \$*"; }
    write_unit()    { echo "FAKE write_unit \$1"; }
    remove_unit()   { echo "FAKE remove_unit \$1"; }
    has_systemd() { return 0; }
    MODE=uninstall
    main
TESTEOF
)"
_assert_contains "teardown_removes_unit"     "FAKE remove_unit"        "$log"
_assert_contains "teardown_disables_timer"   "FAKE systemctl"          "$log"

# --- Test 6: SHA-capture + change-detection: loader runs only when YAML changed
# run_periodic_job is the function the timer fires. It must capture pre/post SHA
# itself, pull, and run the loader ONLY if board YAML changed. We stub git and
# the loader to drive both branches.
#   6a: YAML changed (pre SHA != post SHA) -> loader runs.
# pre/post rev-parse run in command-substitution subshells, so a counter var
# won't persist; use a temp file the pull "advances".
SHA_STATE="$(mktemp)"; echo "PRE_SHA" > "$SHA_STATE"
log="$(INSTALLER="$INSTALLER" SHA_STATE="$SHA_STATE" bash <<TESTEOF 2>&1
    set -u
    export KANBAN_TIMER_LIB=1
    source "$INSTALLER"
    run_git() {
        case "\$*" in
            *"rev-parse HEAD"*) cat "\$SHA_STATE" ;;
            *"pull --ff-only"*) echo "POST_SHA" > "\$SHA_STATE"; return 0 ;;  # advance HEAD
            *"diff"*) return 1 ;;   # nonzero = board YAML differs
            *) return 0 ;;
        esac
    }
    run_loader() { echo "FAKE run_loader"; return 0; }
    run_periodic_job
TESTEOF
)"
rm -f "$SHA_STATE"
_assert_contains "job_runs_loader_when_changed" "FAKE run_loader" "$log"

#   6b: YAML unchanged (pre==post SHA) -> loader does NOT run
log="$(INSTALLER="$INSTALLER" bash <<TESTEOF 2>&1
    set -u
    export KANBAN_TIMER_LIB=1
    source "$INSTALLER"
    run_git() {
        case "\$*" in
            *"rev-parse HEAD"*) echo "SAME_SHA" ;;   # pre == post
            *"pull --ff-only"*) echo "FAKE git pull"; return 0 ;;
            *) return 0 ;;
        esac
    }
    run_loader() { echo "FAKE run_loader"; return 0; }
    run_periodic_job
TESTEOF
)"
_assert_not_contains "job_skips_loader_when_unchanged" "FAKE run_loader" "$log"

# --- Test 7: failure propagation — loader nonzero -> job reports failure ----
SHA_STATE2="$(mktemp)"; echo "PRE_SHA" > "$SHA_STATE2"
out="$(INSTALLER="$INSTALLER" SHA_STATE="$SHA_STATE2" bash <<TESTEOF 2>&1
    set -u
    export KANBAN_TIMER_LIB=1
    source "$INSTALLER"
    run_git() {
        case "\$*" in
            *"rev-parse HEAD"*) cat "\$SHA_STATE" ;;
            *"pull --ff-only"*) echo "POST_SHA" > "\$SHA_STATE"; return 0 ;;
            *"diff"*) return 1 ;;   # board YAML differs -> loader should run
            *) return 0 ;;
        esac
    }
    run_loader() { echo "loader exploded" >&2; return 7; }
    run_periodic_job
    echo "JOB_EXIT=\$?"
TESTEOF
)"
rm -f "$SHA_STATE2"
job_exit="$(grep -oE 'JOB_EXIT=[0-9]+' <<<"$out" | head -1 | cut -d= -f2)"
_assert_contains "fail_prop_nonzero_logged" "loader" "$out"
if [[ -n "$job_exit" && "$job_exit" -ne 0 ]]; then
    _assert_eq "fail_prop_job_exit_nonzero" "nonzero" "nonzero"
else
    _assert_eq "fail_prop_job_exit_nonzero" "nonzero" "zero(${job_exit})"
fi

# --- Test 8: interval -> cron schedule conversion ---------------------------
# The old `*/${INTERVAL%m}` only handled minutes: `2h` -> invalid `*/2h`,
# `90m` -> invalid `*/90` (cron minute field caps at 59). The converter must
# emit a VALID 5-field cron schedule per unit and reject unconvertible inputs.
_cron_sched_for() {
    # Echo the cron schedule (first 5 fields of cron_line) for INTERVAL=$1.
    KANBAN_TIMER_INTERVAL="$1" bash <<TESTEOF 2>/dev/null
        set -u
        export KANBAN_TIMER_LIB=1
        export KANBAN_TIMER_INTERVAL="$1"
        source "$INSTALLER"
        INTERVAL="$1"
        # First 5 whitespace-separated fields == the cron schedule.
        line="\$(cron_line)" || exit 3
        read -r m h dom mon dow _rest <<<"\$line"
        echo "\$m \$h \$dom \$mon \$dow"
TESTEOF
}

_assert_eq "interval_30m_minutes"  "*/30 * * * *"  "$(_cron_sched_for 30m)"
_assert_eq "interval_bare_int_minutes" "*/15 * * * *" "$(_cron_sched_for 15)"
_assert_eq "interval_2h_hours"     "0 */2 * * *"   "$(_cron_sched_for 2h)"
_assert_eq "interval_1d_days"      "0 0 */1 * *"   "$(_cron_sched_for 1d)"

# Rejections: a nonzero exit means cron_line refused the interval (no output).
_reject_rc() {
    KANBAN_TIMER_INTERVAL="$1" bash <<TESTEOF >/dev/null 2>&1
        set -u
        export KANBAN_TIMER_LIB=1
        export KANBAN_TIMER_INTERVAL="$1"
        source "$INSTALLER"
        INTERVAL="$1"
        cron_line
TESTEOF
    echo $?
}
_assert_eq "interval_90m_rejected"  "nonzero" "$( [ "$(_reject_rc 90m)" -ne 0 ] && echo nonzero || echo zero )"
_assert_eq "interval_2x_rejected"   "nonzero" "$( [ "$(_reject_rc 2x)"  -ne 0 ] && echo nonzero || echo zero )"
_assert_eq "interval_0m_rejected"   "nonzero" "$( [ "$(_reject_rc 0m)"  -ne 0 ] && echo nonzero || echo zero )"
# And the rejected forms must NOT leak an invalid cron schedule.
_assert_not_contains "interval_2h_no_invalid_glob" "*/2h" "$(_cron_sched_for 2h)"

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then
    echo "    Failed: ${FAILED_TESTS[*]}"
    exit 1
fi
exit 0
