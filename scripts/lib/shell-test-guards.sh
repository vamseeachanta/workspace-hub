# shell-test-guards.sh — runtime guards against false greens in shell test harnesses (#3876).
#
# Incident: a snapshot helper was defined only inside a selector branch. A
# targeted run skipped the definition, the later `before="$(snapshot ...)"`
# failed inside a command substitution whose status nobody checked, and two
# empty snapshots compared equal. The harness reported PASS without checking
# a single identity. Rule: .claude/rules/shell-test-helper-guards.md.
# Static companion: scripts/enforcement/check-shell-conditional-helpers.py.
#
# Every function returns non-zero and explains on stderr; the harness decides
# how to count it, e.g. `require_helpers snap || { fail snap_defined; exit 1; }`.
#
# require_helpers <fn>...              rc 1 if any name is not a shell FUNCTION
# require_nonempty <label> <value>     rc 1 if value is empty or whitespace-only
# assert_snapshot_unchanged <label> <after> <before>
#                                      rc 1 if either side is blank or they differ
# guard_init / guard_cleanup           create/remove the executed-marker directory
# guard_mark <fn>                      record that <fn> ran (works inside $(...))
# require_executed <fn>...             rc 1 if any <fn> never called guard_mark
# run_step <label> <cmd>...            run cmd, keep its rc in GUARD_LAST_RC, report
#                                      a failure on stderr and append every outcome
#                                      to $GUARD_RECEIPT when set (never truncated);
#                                      rc 3 if the receipt cannot be written.
#                                      It records the status the command RETURNS: a
#                                      helper function must propagate its own internal
#                                      failures, because errexit is not in force inside
#                                      a command run from an && / || list.
#
# Snapshot records with a fixed frame (e.g. 'A <path> <payload>') are never blank;
# check the payload itself with require_nonempty before framing it.

require_helpers() {
  [ "$#" -gt 0 ] || { echo "require_helpers: no helper names given" >&2; return 2; }
  local fn missing=0
  for fn in "$@"; do
    [[ "$fn" != -* ]] && declare -F "$fn" >/dev/null 2>&1 && continue
    echo "require_helpers: helper '$fn' is not defined in this mode" >&2
    missing=1
  done
  return "$missing"
}

require_nonempty() {
  local label="$1" value="${2-}"
  if [[ -z "${value//[[:space:]]/}" ]]; then
    echo "require_nonempty: '$label' record is empty" >&2
    return 1
  fi
}

assert_snapshot_unchanged() {
  local label="$1" after="${2-}" before="${3-}" rc=0
  require_nonempty "$label (before)" "$before" || rc=1
  require_nonempty "$label (after)" "$after" || rc=1
  [[ "$rc" == 0 ]] || return 1
  if [[ "$after" != "$before" ]]; then
    echo "assert_snapshot_unchanged: '$label' changed" >&2
    return 1
  fi
}

guard_init() {
  guard_cleanup
  GUARD_MARK_DIR="$(mktemp -d)" || { echo "guard_init: mktemp failed" >&2; return 1; }
  export GUARD_MARK_DIR
}

guard_cleanup() {
  [[ -n "${GUARD_MARK_DIR:-}" && -d "$GUARD_MARK_DIR" ]] && rm -rf -- "$GUARD_MARK_DIR"
  unset GUARD_MARK_DIR
  return 0
}

guard_mark() {
  [ "$#" -eq 1 ] || { echo "guard_mark: usage: guard_mark <fn>" >&2; return 2; }
  if [[ -z "${GUARD_MARK_DIR:-}" || ! -d "$GUARD_MARK_DIR" ]]; then
    echo "guard_mark: call guard_init in the parent shell first" >&2
    return 1
  fi
  : > "$GUARD_MARK_DIR/$1"
}

require_executed() {
  [ "$#" -gt 0 ] || { echo "require_executed: no helper names given" >&2; return 2; }
  local fn missing=0
  for fn in "$@"; do
    [[ -n "${GUARD_MARK_DIR:-}" && -e "$GUARD_MARK_DIR/$fn" ]] && continue
    echo "require_executed: helper '$fn' never ran" >&2
    missing=1
  done
  return "$missing"
}

run_step() {
  [ "$#" -gt 1 ] || { echo "run_step: usage: run_step <label> <cmd>..." >&2; return 2; }
  local label="$1"; shift
  # The && / || list keeps `set -e` from exiting before the code is recorded.
  "$@" && GUARD_LAST_RC=0 || GUARD_LAST_RC=$?
  if [[ "$GUARD_LAST_RC" != 0 ]]; then
    echo "run_step: '$label' failed rc=$GUARD_LAST_RC" >&2
  fi
  if [[ -n "${GUARD_RECEIPT:-}" ]]; then
    printf '%s step=%s rc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$label" "$GUARD_LAST_RC" \
      >> "$GUARD_RECEIPT" || { echo "run_step: receipt write failed: $GUARD_RECEIPT" >&2; return 3; }
  fi
  return "$GUARD_LAST_RC"
}
