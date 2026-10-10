#!/usr/bin/env bash
# Disable the Mexico CNH source-watch systemd user timer without deleting it.
#
# Scheduler identity:
#   local-user-systemd-claude-routine-mx-720-cnh-source-watch
#
# The script is intentionally exact-identity only. It does not scan for similar
# unit names, does not delete unit files, and does not mutate a remote scheduler.

set -euo pipefail

UNIT_NAME="claude-routine-mx-720-cnh-source-watch.timer"
SERVICE_NAME="claude-routine-mx-720-cnh-source-watch.service"
STATE_ROOT="${XDG_STATE_HOME:-${HOME}/.local/state}/workspace-hub/scheduler-mutations"
LOCK_FILE="${STATE_ROOT}/${UNIT_NAME}.lock"
MODE="check"

log() { printf '[cnh-source-watch] %s\n' "$*"; }
warn() { printf '[cnh-source-watch] %s\n' "$*" >&2; }

run_systemctl() {
  systemctl --user "$@"
}

usage() {
  cat <<USAGE
Usage: $0 [--check|--apply]

--check   Capture and report the exact current user-timer state. No mutation.
--apply   Disable --now ${UNIT_NAME}; do not delete the unit.

Rollback after --apply:
  systemctl --user enable --now ${UNIT_NAME}
  systemctl --user status ${UNIT_NAME}
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check) MODE="check" ;;
    --apply) MODE="apply" ;;
    -h|--help) usage; exit 0 ;;
    *) warn "ERROR: unknown argument: $1"; usage >&2; exit 2 ;;
  esac
  shift
done

if ! command -v systemctl >/dev/null 2>&1; then
  warn "ERROR: systemctl is required for this mutator"
  exit 2
fi

mkdir -p "$STATE_ROOT"

timestamp() {
  date -u +%Y%m%dT%H%M%SZ
}

snapshot_state() {
  local dest="$1"
  mkdir -p "$dest"

  {
    printf 'unit=%s\n' "$UNIT_NAME"
    printf 'service=%s\n' "$SERVICE_NAME"
    printf 'mode=%s\n' "$MODE"
    printf 'timestamp_utc=%s\n' "$(timestamp)"
  } > "${dest}/metadata.env"

  run_systemctl show -p UnitFileState,ActiveState,NextElapseUSecRealtime "$UNIT_NAME" > "${dest}/timer.show" 2>&1 || true
  run_systemctl status "$UNIT_NAME" --no-pager > "${dest}/timer.status" 2>&1 || true
  run_systemctl is-enabled "$UNIT_NAME" > "${dest}/timer.is-enabled" 2>&1 || true
  run_systemctl is-active "$UNIT_NAME" > "${dest}/timer.is-active" 2>&1 || true

  local unit_dir="${HOME}/.config/systemd/user"
  for name in "$UNIT_NAME" "$SERVICE_NAME"; do
    if [ -f "${unit_dir}/${name}" ]; then
      cp -p "${unit_dir}/${name}" "${dest}/${name}.unit"
    fi
  done
}

read_timer_state() {
  run_systemctl show -p UnitFileState,ActiveState,NextElapseUSecRealtime "$UNIT_NAME"
}

state_value() {
  local key="$1"
  awk -F= -v key="$key" '$1 == key {print $2; found=1} END {if (!found) exit 1}'
}

state_summary() {
  local state="$1" unit_state active_state
  unit_state="$(printf '%s\n' "$state" | state_value UnitFileState || true)"
  active_state="$(printf '%s\n' "$state" | state_value ActiveState || true)"
  printf 'UnitFileState=%s ActiveState=%s' "${unit_state:-missing}" "${active_state:-missing}"
}

verify_disabled() {
  local state enabled active
  state="$(read_timer_state 2>/dev/null || true)"
  enabled="$(printf '%s\n' "$state" | state_value UnitFileState || true)"
  active="$(printf '%s\n' "$state" | state_value ActiveState || true)"
  [ "$enabled" = "disabled" ] || return 1
  [ "$active" = "inactive" ] || return 1
}

with_lock() {
  local stamp baseline verify before after
  stamp="$(timestamp)"
  baseline="${STATE_ROOT}/${UNIT_NAME}.${stamp}.baseline"
  verify="${STATE_ROOT}/${UNIT_NAME}.${stamp}.post"

  exec 9>"$LOCK_FILE"
  flock 9

  snapshot_state "$baseline"
  before="$(cat "${baseline}/timer.show")"
  log "baseline: $baseline"
  log "backup: $baseline"
  log "current-state: $(state_summary "$before")"

  if [ "$MODE" = "check" ]; then
    log "no mutation requested"
    log "rollback after a future apply: systemctl --user enable --now ${UNIT_NAME}"
    return 0
  fi

  local cas_snapshot
  cas_snapshot="${STATE_ROOT}/${UNIT_NAME}.${stamp}.cas"
  snapshot_state "$cas_snapshot"
  after="$(cat "${cas_snapshot}/timer.show")"
  if [ "$before" != "$after" ]; then
    warn "ERROR: timer state changed between baseline and apply; refusing mutation"
    warn "baseline: $baseline"
    warn "cas: $cas_snapshot"
    exit 3
  fi

  run_systemctl disable --now "$UNIT_NAME"
  snapshot_state "$verify"

  if ! verify_disabled; then
    local rollback_state
    rollback_state="$(read_timer_state 2>/dev/null || true)"
    warn "ERROR: post-state is not disabled/inactive; attempting rollback"
    warn "rollback pre-state: $(state_summary "$rollback_state")"
    run_systemctl enable --now "$UNIT_NAME" || true
    warn "rollback command: systemctl --user enable --now ${UNIT_NAME}"
    exit 4
  fi

  log "disabled: ${UNIT_NAME}"
  log "post-state: $verify"
  log "rollback: systemctl --user enable --now ${UNIT_NAME}"
}

with_lock
