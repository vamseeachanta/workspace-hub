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

run_python() {
  if [[ -x "$UV" ]]; then
    "$UV" run --with pyyaml "$PY" "$@"
  else
    "$PY" "$@"
  fi
}

run_builder() {
  local drive="$1"
  run_python "$REPO_ROOT/scripts/data/drive-index/build_drive_index.py" \
    --drive "$drive" --incremental --prune
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
    cad_root="${DRIVE_INDEX_CAD_ROOT:-}"
    if [[ -z "$cad_root" ]]; then
      cad_root="$(run_python -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["drives"]["ace"]["canonical_prefix"])' \
        "$REPO_ROOT/scripts/data/drive-index/drive-index-config.yaml")"
    fi
    cad_dir="$cad_root/_cad-index"
    mkdir -p "$cad_dir"
    "$PY" "$REPO_ROOT/scripts/data/drive-index/cad/scan_cad_raw.py" \
      --root "$cad_root" --out "$cad_dir/cad-raw.tsv"
    "$PY" "$REPO_ROOT/scripts/data/drive-index/cad/build_cad_index.py" \
      --raw "$cad_dir/cad-raw.tsv" \
      --dedup "$cad_dir/dedup" \
      --out "$cad_dir/cad-readability-index.tsv"
    printf '{"index_id":"cad_readability","status":"ok"}\n' > "$cad_dir/refresh-state.json.tmp"
    mv "$cad_dir/refresh-state.json.tmp" "$cad_dir/refresh-state.json"
    output="cad refresh complete"
    ;;
esac

notify cron "drive-index-refresh-$TARGET" pass "$output"
