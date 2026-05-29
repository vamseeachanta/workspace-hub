#!/usr/bin/env bash
# dispatch-leader-watch.sh — per-machine dispatch-leader health watcher (#2847 Phase 1).
#
# WHAT: on the leader, refresh the committed heartbeat (self-fenced on a confirmed
#   push); on a secondary, check the leader's heartbeat and ALERT if it is stale.
#   Phase 1 is alert-only — it never auto-promotes (that is Phase 2, behind a flag).
#
# WHERE: runs on every dispatch-capable machine via cron (see schedule-tasks.yaml).
#   Cadence should be <= STALE_THRESHOLD so a dead leader is surfaced within one cycle.
#
# EXIT: 0 = leader fresh / heartbeat ok; 2 = stale leader detected (alerted);
#       1 = undetermined (could not read state — never treated as a dead leader).
set -uo pipefail

REPO_ROOT="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
MACHINE="${DISPATCHER_MACHINE:-$(hostname 2>/dev/null)}"; MACHINE="${MACHINE:-${COMPUTERNAME:-unknown}}"
LEADER_HOST="${DISPATCH_LEADER_HOST:-ace-linux-1}"
PY="$REPO_ROOT/scripts/ai/dispatch_leader.py"

if [ ! -f "$PY" ]; then
  echo "[dispatch-leader-watch] missing $PY — skip" >&2
  exit 0
fi

# Prefer uv if available (repo convention); fall back to python3.
run_py() {
  if command -v uv >/dev/null 2>&1; then
    ( cd "$REPO_ROOT" && uv run --no-project python "$PY" "$@" )
  else
    ( cd "$REPO_ROOT" && python3 "$PY" "$@" )
  fi
}

if [ "$MACHINE" = "$LEADER_HOST" ]; then
  # Leader: refresh heartbeat. A failed push self-fences (rc=1) but is non-fatal
  # to the cron — the next dispatch loop's may_write_leases gate enforces it.
  run_py --machine "$MACHINE" --heartbeat
  rc=$?
  [ "$rc" -eq 0 ] && echo "[dispatch-leader-watch] heartbeat ok ($MACHINE)" \
                  || echo "[dispatch-leader-watch] heartbeat NOT confirmed (self-fenced) ($MACHINE)" >&2
  exit 0
fi

# Secondary: detect leader health (alert only).
status="$(run_py --machine "$MACHINE" --check)"; rc=$?
echo "[dispatch-leader-watch] leader status: ${status:-unknown} (rc=$rc)"
exit "$rc"
