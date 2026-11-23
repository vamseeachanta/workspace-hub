#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-}"
cad_state_file=""
document_state_file=""
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CONFIG="${DRIVE_INDEX_CONFIG:-$REPO_ROOT/scripts/data/drive-index/drive-index-config.yaml}"
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
    ace|dde) state_file="$document_state_file" ;;
    cad) state_file="$cad_state_file" ;;
    *) return 0 ;;
  esac
  [[ -n "$state_file" ]] || return 0
  local dir
  dir="$(dirname "$state_file")"
  if [[ -d "$dir" && -w "$dir" ]]; then
    "$PY" - "$state_file" "$target" "$message" <<'PY' || true
import json
import sys
from pathlib import Path

path, target, message = sys.argv[1:]
path = Path(path)
try:
    previous = json.loads(path.read_text())
except (OSError, ValueError):
    previous = {}
# The builder owns detailed scan state; the wrapper must retain that evidence.
previous.update(index_id=target, status="failed", wrapper_error=message)
if target == "cad" or not previous.get("error"):
    previous["error"] = message
temporary = path.with_suffix(path.suffix + ".tmp")
temporary.write_text(json.dumps(previous, indent=2) + "\n")
temporary.replace(path)
PY
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

run_python() {
  if [[ -x "$UV" ]]; then
    "$UV" run --with pyyaml "$PY" "$@"
  else
    "$PY" "$@"
  fi
}

trap 'fail "$TARGET" "line $LINENO: $BASH_COMMAND"' ERR

if [[ "$TARGET" == "cad" ]]; then
  cad_root="${DRIVE_INDEX_CAD_ROOT:-}"
  if [[ -z "$cad_root" ]]; then
    cad_root="$(run_python -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["drives"]["ace"]["canonical_prefix"])' \
      "$CONFIG")"
  fi
  cad_dir="$cad_root/_cad-index"
  cad_state_file="$cad_dir/refresh-state.json"
fi

if [[ "$TARGET" != "cad" ]]; then
  document_db="$(run_python -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["drives"][sys.argv[2]]["db"])' "$CONFIG" "$TARGET")"
  document_state_file="$(dirname "$document_db")/refresh-state.json"
fi

LOCK_FILE="${TMPDIR:-/tmp}/workspace-hub-drive-index-${TARGET}.lock"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  fail "$TARGET" "another refresh is already running"
fi
run_builder() {
  local drive="$1"
  run_python "$REPO_ROOT/scripts/data/drive-index/build_drive_index.py" \
    --config "$CONFIG" --drive "$drive" --incremental --prune
}

case "$TARGET" in
  ace)
    [[ -f "$document_db" ]] || fail ace "index.db missing"
    output="$(run_builder ace)"
    ;;
  dde)
    [[ -f "$document_db" ]] || fail dde "index.db missing"
    output="$(run_builder dde)"
    ;;
  cad)
    mkdir -p "$cad_dir"
    "$PY" "$REPO_ROOT/scripts/data/drive-index/cad/scan_cad_raw.py" \
      --root "$cad_root" --out "$cad_dir/cad-raw.tsv"
    "$PY" "$REPO_ROOT/scripts/data/drive-index/cad/build_cad_index.py" \
      --raw "$cad_dir/cad-raw.tsv" \
      --dedup "$cad_dir/dedup" \
      --out "$cad_dir/cad-readability-index.tsv"
    printf '{"index_id":"cad_readability","status":"ok"}\n' > "${cad_state_file}.tmp"
    mv "${cad_state_file}.tmp" "$cad_state_file"
    output="cad refresh complete"
    ;;
esac

notify cron "drive-index-refresh-$TARGET" pass "$output"
