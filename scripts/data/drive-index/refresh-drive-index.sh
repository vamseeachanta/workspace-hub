#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-}"
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PY="$(command -v python3 || true)"
if [[ -z "$PY" ]]; then
  PY="/usr/bin/python3"
fi
UV="$(command -v uv || true)"
if [[ -z "$UV" ]]; then
  UV="$HOME/.local/bin/uv"
fi

notify() {
  local source="$1"
  local job="$2"
  local status="$3"
  local details="${4:-}"
  if [[ -n "${DRIVE_INDEX_NOTIFY_LOG:-}" ]]; then
    printf '%s\t%s\t%s\t%s\n' "$source" "$job" "$status" "$details" >> "$DRIVE_INDEX_NOTIFY_LOG"
    return 0
  fi
  bash "$REPO_ROOT/scripts/notify.sh" "$source" "$job" "$status" "$details" || true
}

fail() {
  local target="${1:-unknown}"
  local message="${2:-refresh failed}"
  write_failure_state "$target" "$message"
  notify cron "drive-index-refresh-$target" fail "$message"
  exit 1
}

write_failure_state() {
  local target="${1:-unknown}"
  local message="${2:-refresh failed}"
  local state_file=""
  case "$target" in
    ace) state_file="/mnt/ace/.ace-knowledge/refresh-state.json" ;;  # abs-path-allowed
    dde) state_file="/mnt/dde/.dde-knowledge/refresh-state.json" ;;  # abs-path-allowed
    cad) state_file="/mnt/ace/_cad-index/refresh-state.json" ;;  # abs-path-allowed
    *) return 0 ;;
  esac
  local dir
  dir="$(dirname "$state_file")"
  if [[ -d "$dir" && -w "$dir" ]]; then
    printf '{"index_id":"%s","status":"failed","error":"%s"}\n' "$target" "${message//\"/\\\"}" > "${state_file}.tmp" || true
    mv "${state_file}.tmp" "$state_file" 2>/dev/null || true
  fi
}

usage() {
  echo "usage: refresh-drive-index.sh <ace|dde|cad>" >&2
}

if [[ "$TARGET" != "ace" && "$TARGET" != "dde" && "$TARGET" != "cad" ]]; then
  usage
  fail "${TARGET:-unknown}" "invalid target"
fi

if [[ "${DRIVE_INDEX_TEST_MODE:-}" == "1" ]]; then
  notify cron "drive-index-refresh-$TARGET" pass "test-mode"
  exit 0
fi

LOCK_FILE="${TMPDIR:-/tmp}/workspace-hub-drive-index-${TARGET}.lock"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  fail "$TARGET" "another refresh is already running"
fi
trap 'fail "$TARGET" "line $LINENO: $BASH_COMMAND"' ERR

run_builder() {
  local drive="$1"
  if [[ -x "$UV" ]]; then
    "$UV" run --with pyyaml "$PY" "$REPO_ROOT/scripts/data/drive-index/build_drive_index.py" \
      --drive "$drive" --incremental --prune
  else
    "$PY" "$REPO_ROOT/scripts/data/drive-index/build_drive_index.py" \
      --drive "$drive" --incremental --prune
  fi
}

case "$TARGET" in
  ace)
    [[ -f /mnt/ace/.ace-knowledge/index.db ]] || fail ace "index.db missing"  # abs-path-allowed
    output="$(run_builder ace)"
    ;;
  dde)
    [[ -f /mnt/dde/.dde-knowledge/index.db ]] || fail dde "index.db missing - #3334 production run not landed?"  # abs-path-allowed
    output="$(run_builder dde)"
    ;;
  cad)
    mkdir -p /mnt/ace/_cad-index  # abs-path-allowed
    "$PY" "$REPO_ROOT/scripts/data/drive-index/cad/scan_cad_raw.py" \
      --root /mnt/ace --out /mnt/ace/_cad-index/cad-raw.tsv  # abs-path-allowed
    "$PY" "$REPO_ROOT/scripts/data/drive-index/cad/build_cad_index.py" \
      --raw /mnt/ace/_cad-index/cad-raw.tsv \  # abs-path-allowed
      --dedup /mnt/ace/_cad-index/dedup \  # abs-path-allowed
      --out /mnt/ace/_cad-index/cad-readability-index.tsv  # abs-path-allowed
    printf '{"index_id":"cad_readability","status":"ok"}\n' > /mnt/ace/_cad-index/refresh-state.json.tmp  # abs-path-allowed
    mv /mnt/ace/_cad-index/refresh-state.json.tmp /mnt/ace/_cad-index/refresh-state.json  # abs-path-allowed
    output="cad refresh complete"
    ;;
esac

notify cron "drive-index-refresh-$TARGET" pass "$output"
