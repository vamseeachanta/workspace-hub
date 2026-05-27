#!/usr/bin/env bash
# setup-kanban-loader-timer.sh — install a per-machine, time-based trigger that
# keeps THIS machine's local Hermes kanban (~/.hermes/kanban.db) in sync with the
# git-tracked board YAML source-of-truth (.claude/memory/kanban/boards/*.yaml).
# Issue: vamseeachanta/workspace-hub#2827 (Part 3).
#
# The periodic job, each time it fires:
#   1. captures the pre-pull SHA      (git -C <repo> rev-parse HEAD)
#   2. git -C <repo> pull --ff-only
#   3. captures the post-pull SHA
#   4. runs the loader ONLY if board YAML changed between the two SHAs
#   5. PROPAGATES loader failure (nonzero exit + log) — does NOT swallow it.
# It captures the SHAs itself rather than relying on kanban-autoload.sh's
# ORIG_HEAD..HEAD comparison, which is unreliable under a timer (no merge ⇒ no
# fresh ORIG_HEAD). kanban-autoload.sh also ends its loader call with `|| true`,
# masking failures; this wrapper deliberately does not.
#
# OPT-IN: installs nothing unless the marker ~/.hermes/kanban-autoload.enabled
# exists (reuses the same marker kanban-autoload.sh gates on). This is the
# Manual-orchestration safety gate — see .claude/memory/kanban/README.md.
#
# DEFAULT MODE IS --check (no mutation). Installs a systemd --user timer when
# systemd is available, else a crontab entry. Idempotent: re-running install
# overwrites the managed unit / replaces the managed crontab line in place.
#
# Usage:
#   setup-kanban-loader-timer.sh                 # --check (report state, no changes)
#   setup-kanban-loader-timer.sh --dry-run       # print exact actions, no changes
#   setup-kanban-loader-timer.sh --install [--interval 30m]
#   setup-kanban-loader-timer.sh --uninstall
#   setup-kanban-loader-timer.sh --run-job       # run one sync cycle now (what the timer fires)
#   setup-kanban-loader-timer.sh --help
set -uo pipefail

# ── Config (overridable via env for tests / non-standard layouts) ───────────
REPO_ROOT="${KANBAN_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
KANBAN_AUTOLOAD_MARKER="${KANBAN_AUTOLOAD_MARKER:-${HERMES_HOME}/kanban-autoload.enabled}"
LOADER="${KANBAN_LOADER:-${REPO_ROOT}/.claude/memory/kanban/scripts/load.py}"
BOARDS_REL=".claude/memory/kanban/boards"
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

UNIT_NAME="kanban-loader-sync"
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_PATH="${SYSTEMD_USER_DIR}/${UNIT_NAME}.service"
TIMER_PATH="${SYSTEMD_USER_DIR}/${UNIT_NAME}.timer"
CRON_SENTINEL="# MANAGED-BY: workspace-hub scripts/install/setup-kanban-loader-timer.sh (${UNIT_NAME})"

MODE="check"               # check | dry-run | install | uninstall | run-job
INTERVAL="${KANBAN_TIMER_INTERVAL:-30m}"

log()  { printf '%s\n' "$*" >&2; }
fail() { log "FAIL: $*"; exit 1; }

# ── Side-effecting wrappers (tests redefine these to log-only) ──────────────
run_systemctl() { systemctl --user "$@"; }
run_crontab()   { crontab "$@"; }
run_git()       { git -C "$REPO_ROOT" "$@"; }
run_loader() {
  # Run the YAML→Hermes loader. Prefer uv; fall back to python3. Return its rc.
  if command -v uv >/dev/null 2>&1; then
    uv run python "$LOADER"
  else
    python3 "$LOADER"
  fi
}

write_unit() {
  # $1 = path, content on stdin. Real install writes the file.
  local path="$1"; mkdir -p "$(dirname "$path")"; cat > "$path"
}
remove_unit() { rm -f "$1"; }

# ── Capability probes (tests redefine these for determinism) ────────────────
has_systemd() { command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; }
marker_present() { [ -f "$KANBAN_AUTOLOAD_MARKER" ]; }

# ── The periodic job: SHA-capture + change-detect + loader + fail-propagate ─
run_periodic_job() {
  local pre post rc=0
  pre="$(run_git rev-parse HEAD 2>/dev/null || echo NONE)"
  if ! run_git pull --ff-only >/dev/null 2>&1; then
    log "[kanban-timer] git pull --ff-only failed (non-fast-forward or no remote) — aborting cycle"
    return 1
  fi
  post="$(run_git rev-parse HEAD 2>/dev/null || echo NONE)"

  if [ "$pre" = "$post" ]; then
    log "[kanban-timer] HEAD unchanged ($pre) — board YAML cannot have changed; skipping loader"
    return 0
  fi
  # HEAD moved — did the board YAML change between pre and post?
  if run_git diff --quiet "$pre" "$post" -- "$BOARDS_REL" 2>/dev/null; then
    log "[kanban-timer] HEAD moved ${pre}->${post} but no board-YAML change; skipping loader"
    return 0
  fi

  log "[kanban-timer] board YAML changed ${pre}->${post} — running loader"
  run_loader; rc=$?
  if [ "$rc" -ne 0 ]; then
    log "[kanban-timer] LOADER FAILED (exit ${rc}) — NOT swallowing; cycle reports failure"
    return "$rc"
  fi
  log "[kanban-timer] loader ok"
  return 0
}

# ── Unit content generators ─────────────────────────────────────────────────
service_body() {
  cat <<EOF
[Unit]
Description=Sync git-tracked kanban YAML into local Hermes (workspace-hub #2827)
Documentation=file://${REPO_ROOT}/.claude/memory/kanban/README.md

[Service]
Type=oneshot
ExecStart=${SELF} --run-job
EOF
}

timer_body() {
  cat <<EOF
[Unit]
Description=Periodic kanban YAML -> local Hermes sync (workspace-hub #2827)

[Timer]
OnBootSec=2min
OnUnitActiveSec=${INTERVAL}
Persistent=true

[Install]
WantedBy=timers.target
EOF
}

# Convert a systemd-style interval (Nm | Nh | Nd) into the 5-field cron
# schedule prefix on stdout. systemd's OnUnitActiveSec accepts 30m/2h/90m
# natively, but cron has no interval syntax — only field globbing. The old
# `*/${INTERVAL%m}` only worked for minute intervals: `2h` produced the invalid
# `*/2h`, and `90m` produced `*/90` (cron minute field caps at 59). This maps
# each supported unit to a VALID cron schedule and rejects anything else.
#   Nm (1..59)  -> "*/N * * * *"     every N minutes
#   Nh (1..23)  -> "0 */N * * *"     every N hours, on the hour
#   Nd (1..31)  -> "0 0 */N * *"     every N days, at midnight
# A bare integer is treated as minutes (back-compat with the old `30` form).
interval_to_cron_schedule() {
  local iv="$1" num unit
  if [[ "$iv" =~ ^([0-9]+)([mhd]?)$ ]]; then
    num="${BASH_REMATCH[1]}"; unit="${BASH_REMATCH[2]:-m}"
  else
    fail "invalid --interval '$iv' (expected Nm, Nh, or Nd, e.g. 30m, 2h, 1d)"
  fi
  case "$unit" in
    m)
      [ "$num" -ge 1 ] && [ "$num" -le 59 ] || fail "--interval minutes must be 1..59 (got '${iv}'); use Nh for >=60m (e.g. 90m -> 1h30m has no cron form; pick 1h or use systemd)"
      printf '*/%s * * * *' "$num" ;;
    h)
      [ "$num" -ge 1 ] && [ "$num" -le 23 ] || fail "--interval hours must be 1..23 (got '${iv}'); use Nd for >=24h"
      printf '0 */%s * * *' "$num" ;;
    d)
      [ "$num" -ge 1 ] && [ "$num" -le 31 ] || fail "--interval days must be 1..31 (got '${iv}')"
      printf '0 0 */%s * *' "$num" ;;
    *) fail "invalid --interval unit in '$iv' (use m, h, or d)" ;;
  esac
}

cron_line() {
  # crontab runs the job; redirect its output to the journal-ish log file.
  # interval_to_cron_schedule runs in a command-substitution subshell, so its
  # `fail`/exit cannot terminate this process — capture rc and propagate.
  local sched rc
  sched="$(interval_to_cron_schedule "$INTERVAL")"; rc=$?   # error msg already on stderr
  [ "$rc" -eq 0 ] || exit "$rc"
  printf '%s %s --run-job >> %s/kanban-loader-timer.log 2>&1 %s\n' \
    "$sched" "$SELF" "$HERMES_HOME" "$CRON_SENTINEL"
}

# ── Reporting / preview ──────────────────────────────────────────────────────
report_state() {
  log "── kanban-loader-timer state ──"
  log "repo root:        $REPO_ROOT"
  log "loader:           $LOADER $( [ -f "$LOADER" ] && echo '(present)' || echo '(MISSING)')"
  log "opt-in marker:    $KANBAN_AUTOLOAD_MARKER $(marker_present && echo '(present)' || echo '(absent — installer is a no-op)')"
  if has_systemd; then
    log "scheduler:        systemd --user"
    log "timer installed:  $( [ -f "$TIMER_PATH" ] && echo yes || echo no ) ($TIMER_PATH)"
  else
    log "scheduler:        crontab (no systemd)"
    log "cron installed:   $(run_crontab -l 2>/dev/null | grep -qF "$CRON_SENTINEL" && echo yes || echo no)"
  fi
  log "interval:         $INTERVAL"
}

actions_preview() {
  log "Would perform (install):"
  if has_systemd; then
    log "  write_unit $SERVICE_PATH"
    log "  write_unit $TIMER_PATH"
    log "  systemctl --user daemon-reload"
    log "  systemctl --user enable --now ${UNIT_NAME}.timer"
  else
    log "  crontab: add managed line -> $(cron_line | sed "s| ${CRON_SENTINEL}||")"
  fi
}

# ── Install / uninstall ──────────────────────────────────────────────────────
do_install() {
  if has_systemd; then
    service_body | write_unit "$SERVICE_PATH"
    timer_body   | write_unit "$TIMER_PATH"
    run_systemctl daemon-reload || log "WARN: daemon-reload failed"
    run_systemctl enable --now "${UNIT_NAME}.timer" \
      && log "Installed + started ${UNIT_NAME}.timer (interval ${INTERVAL})." \
      || fail "systemctl enable --now ${UNIT_NAME}.timer failed"
  else
    # Idempotent: drop any prior managed line, append the fresh one.
    local existing fresh
    existing="$(run_crontab -l 2>/dev/null | grep -vF "$CRON_SENTINEL" || true)"
    fresh="$(printf '%s\n%s\n' "$existing" "$(cron_line)" | sed '/^$/d')"
    printf '%s\n' "$fresh" | run_crontab - \
      && log "Installed managed crontab entry (interval ${INTERVAL})." \
      || fail "crontab install failed"
  fi
}

do_uninstall() {
  if has_systemd; then
    run_systemctl disable --now "${UNIT_NAME}.timer" 2>/dev/null || true
    remove_unit "$TIMER_PATH"
    remove_unit "$SERVICE_PATH"
    run_systemctl daemon-reload 2>/dev/null || true
    log "Removed ${UNIT_NAME}.timer/.service."
  else
    local existing
    existing="$(run_crontab -l 2>/dev/null | grep -vF "$CRON_SENTINEL" || true)"
    printf '%s\n' "$existing" | sed '/^$/d' | run_crontab - 2>/dev/null || true
    log "Removed managed crontab entry."
  fi
}

# ── main ─────────────────────────────────────────────────────────────────────
parse_args() {
  while (( $# > 0 )); do
    case "$1" in
      --check) MODE="check" ;;
      --dry-run) MODE="dry-run" ;;
      --install) MODE="install" ;;
      --uninstall) MODE="uninstall" ;;
      --run-job) MODE="run-job" ;;
      --interval) shift; INTERVAL="${1:?--interval needs a value}" ;;
      --help|-h) sed -n '2,40p' "$SELF"; exit 0 ;;
      *) echo "ERROR: unknown arg: $1" >&2; exit 2 ;;
    esac
    shift
  done
}

main() {
  case "$MODE" in
    run-job)
      # The timer fires this. Gate on the opt-in marker too, so a stale unit on a
      # machine that opted out becomes a no-op.
      marker_present || { log "[kanban-timer] opt-in marker absent — skipping."; exit 0; }
      run_periodic_job; exit $? ;;
    check)
      report_state
      marker_present || { log "NEXT: create $KANBAN_AUTOLOAD_MARKER then re-run with --install (Manual-orchestration machines only)."; exit 0; }
      log "NEXT: run with --install to schedule the periodic sync."
      exit 0 ;;
    dry-run)
      report_state; actions_preview; exit 0 ;;
    install)
      marker_present || fail "opt-in marker $KANBAN_AUTOLOAD_MARKER absent — refusing to install (create it first; Manual-orchestration machines only)."
      [ -f "$LOADER" ] || fail "loader not found at $LOADER"
      do_install ;;
    uninstall)
      do_uninstall ;;
  esac
}

# Library mode: source for tests without executing (define funcs only).
if [ "${KANBAN_TIMER_LIB:-0}" != "1" ]; then
  parse_args "$@"
  main
fi
