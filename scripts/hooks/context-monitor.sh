#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel)}"
LOG_FILE="$REPO_ROOT/logs/context-monitor.log"

usage() {
  echo "Usage: $0 --usage-pct <0-100>" >&2
  exit 1
}

# Parse args
USAGE_PCT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --usage-pct)
      USAGE_PCT="${2:-}"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

# Validate --usage-pct
if [[ -z "$USAGE_PCT" ]]; then
  usage
fi
if ! [[ "$USAGE_PCT" =~ ^[0-9]+$ ]] || (( USAGE_PCT > 100 )); then
  echo "ERROR: --usage-pct must be an integer 0-100, got: '$USAGE_PCT'" >&2
  usage
fi

mkdir -p "$REPO_ROOT/logs"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Read active WRK
ACTIVE_WRK_FILE="$REPO_ROOT/.claude/state/active-wrk"
if [[ ! -f "$ACTIVE_WRK_FILE" ]] || [[ -z "$(cat "$ACTIVE_WRK_FILE" 2>/dev/null | tr -d '[:space:]')" ]]; then
  echo "LEVEL=SKIP ts=$NOW msg=no_active_wrk action=exit0" >> "$LOG_FILE"
  exit 0
fi
WRK_ID="$(cat "$ACTIVE_WRK_FILE" | tr -d '[:space:]')"

# Validate WRK ID format
if ! [[ "$WRK_ID" =~ ^WRK-[0-9]+$ ]]; then
  echo "LEVEL=SKIP ts=$NOW msg=invalid_wrk_id value=$WRK_ID action=exit0" >> "$LOG_FILE"
  exit 0
fi

# Threshold 70 warning
if (( USAGE_PCT >= 70 )); then
  echo "LEVEL=WARN ts=$NOW wrk_id=$WRK_ID usage_pct=$USAGE_PCT threshold=70" >> "$LOG_FILE"
fi

# Threshold 80 actions
if (( USAGE_PCT >= 80 )); then
  echo "LEVEL=WARN ts=$NOW wrk_id=$WRK_ID usage_pct=$USAGE_PCT threshold=80" >> "$LOG_FILE"

  ASSETS_DIR="$REPO_ROOT/.claude/work-queue/assets/$WRK_ID"
  WARNING_YAML="$ASSETS_DIR/context-warning.yaml"

  # Idempotency check
  if [[ -f "$WARNING_YAML" ]]; then
    existing_threshold="$(grep '^threshold:' "$WARNING_YAML" 2>/dev/null | awk '{print $2}' || echo "")"
    if [[ "$existing_threshold" == "80" ]]; then
      echo "LEVEL=SKIP ts=$NOW wrk_id=$WRK_ID msg=context-warning.yaml_already_exists threshold=80" >> "$LOG_FILE"
      exit 0
    fi
  fi

  # Call checkpoint.sh (non-fatal)
  if ! bash "$REPO_ROOT/scripts/work-queue/checkpoint.sh" "$WRK_ID" 2>>"$LOG_FILE"; then
    echo "LEVEL=ERROR ts=$NOW wrk_id=$WRK_ID msg=checkpoint.sh_failed action=continuing" >> "$LOG_FILE"
  fi

  # Write context-warning.yaml
  mkdir -p "$ASSETS_DIR"
  cat > "$WARNING_YAML" <<YAML
wrk_id: $WRK_ID
usage_pct: $USAGE_PCT
threshold: 80
action: checkpoint_triggered
triggered_at: $NOW
YAML
fi
