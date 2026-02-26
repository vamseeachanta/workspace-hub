#!/usr/bin/env bash
# check-network-mounts.sh — Verify SSHFS network mounts are live; attempt remount if stale.
# Run daily via cron. Exit 0 = all mounts OK, 1 = one or more failed.
#
# Cron (ace-linux-1, as root):
#   0 7 * * * /mnt/local-analysis/workspace-hub/scripts/readiness/check-network-mounts.sh
#
# Cron (ace-linux-2, as root):
#   0 7 * * * /mnt/local-analysis/workspace-hub/scripts/readiness/check-network-mounts.sh
set -euo pipefail

HOSTNAME="$(hostname -s)"
LOG_DIR="/mnt/local-analysis/workspace-hub/.claude/state/session-signals"
LOG_FILE="$LOG_DIR/network-mounts.jsonl"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DATE="$(date +%Y-%m-%d)"

mkdir -p "$LOG_DIR"

# ── Mount definitions per host ────────────────────────────────────────────────
# Format: "mount_point|remote_host|probe_subpath"
declare -A HOST_MOUNTS
HOST_MOUNTS["ace-linux-1"]="
/mnt/remote/ace-linux-2/local-analysis|ace-linux-2|.
/mnt/remote/ace-linux-2/dde|ace-linux-2|.
"
HOST_MOUNTS["ace-linux-2"]="
/mnt/workspace-hub|ace-linux-1|.git/HEAD
/mnt/remote/ace-linux-1/local-analysis|ace-linux-1|.
/mnt/remote/ace-linux-1/ace|ace-linux-1|.
"

if [[ -z "${HOST_MOUNTS[$HOSTNAME]:-}" ]]; then
  echo "[$TIMESTAMP] SKIP: no mount definitions for host '$HOSTNAME'" >&2
  exit 0
fi

# ── Helpers ───────────────────────────────────────────────────────────────────
log_json() {
  local status="$1" mount="$2" detail="$3"
  printf '{"ts":"%s","host":"%s","mount":"%s","status":"%s","detail":"%s"}\n' \
    "$TIMESTAMP" "$HOSTNAME" "$mount" "$status" "$detail" >> "$LOG_FILE"
}

probe_mount() {
  local mount="$1" probe="$2"
  timeout 10 ls "${mount}/${probe}" &>/dev/null
}

# Convert systemd unit name from mount path: /mnt/foo-bar/baz → mnt-foo\x2dbar-baz.mount
mount_unit() {
  local path="$1"
  # Strip leading slash, replace - with \x2d, replace / with -
  local stripped="${path#/}"
  local dashes="${stripped//-/\\x2d}"
  local unit="${dashes//\//-}"
  echo "${unit}.mount"
}

trigger_remount() {
  local mount="$1"
  local unit
  unit="$(mount_unit "$mount")"
  # Unmount stale FUSE if needed, then start unit
  fusermount -u "$mount" 2>/dev/null || true
  systemctl start "$unit" 2>/dev/null || true
  sleep 3
}

# ── Check loop ────────────────────────────────────────────────────────────────
FAILED=0
RECOVERED=0
OK=0

while IFS='|' read -r mount remote probe; do
  [[ -z "$mount" ]] && continue

  # First probe
  if probe_mount "$mount" "$probe"; then
    log_json "ok" "$mount" "accessible"
    (( OK++ )) || true
    continue
  fi

  # Stale — check if remote is reachable before trying remount
  if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$remote" 'true' 2>/dev/null; then
    log_json "unreachable" "$mount" "remote $remote not reachable"
    echo "WARN: $mount — remote $remote unreachable, skipping remount" >&2
    (( FAILED++ )) || true
    continue
  fi

  echo "INFO: $mount stale, attempting remount..." >&2
  trigger_remount "$mount"

  # Second probe after remount
  if probe_mount "$mount" "$probe"; then
    log_json "recovered" "$mount" "remounted successfully"
    echo "OK: $mount recovered" >&2
    (( RECOVERED++ )) || true
  else
    log_json "failed" "$mount" "remount attempted but still inaccessible"
    echo "ERROR: $mount still inaccessible after remount attempt" >&2
    (( FAILED++ )) || true
  fi

done <<< "${HOST_MOUNTS[$HOSTNAME]}"

# ── Summary ───────────────────────────────────────────────────────────────────
TOTAL=$(( OK + RECOVERED + FAILED ))
SUMMARY="ok=$OK recovered=$RECOVERED failed=$FAILED total=$TOTAL"

printf '{"ts":"%s","host":"%s","event":"summary","%s"}\n' \
  "$TIMESTAMP" "$HOSTNAME" \
  "$(echo "$SUMMARY" | sed 's/=/":/g; s/ /,""/g; s/^/"/' | sed 's/$/"/')" \
  >> "$LOG_FILE" 2>/dev/null || \
printf '{"ts":"%s","host":"%s","event":"summary","ok":%d,"recovered":%d,"failed":%d}\n' \
  "$TIMESTAMP" "$HOSTNAME" "$OK" "$RECOVERED" "$FAILED" >> "$LOG_FILE"

echo "[$DATE] $HOSTNAME network-mounts: $SUMMARY"

[[ $FAILED -eq 0 ]]
