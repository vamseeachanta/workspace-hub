#!/usr/bin/env bash
# require-stage-prompt-drift.sh — Pre-push drift guard for deleted stage prompt assets.
# Blocks only when the current diff introduces new stage-prompt drift relative to base ref.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DRIFT_SCRIPT_DEFAULT="${REPO_ROOT}/scripts/analysis/stage_prompt_drift_check.py"
DRIFT_SCRIPT="${STAGE_PROMPT_DRIFT_SCRIPT:-$DRIFT_SCRIPT_DEFAULT}"
BASE_REF="${STAGE_PROMPT_DRIFT_BASE_REF:-origin/main}"
HEAD_REF="${STAGE_PROMPT_DRIFT_HEAD_REF:-HEAD}"
STRICT_MODE="${STAGE_PROMPT_DRIFT_STRICT:-1}"
WRITE_STUBS="${STAGE_PROMPT_DRIFT_WRITE_STUBS:-1}"
LOG_FILE="${STAGE_PROMPT_DRIFT_LOG:-${REPO_ROOT}/logs/hooks/stage-prompt-drift-events.jsonl}"

log_event() {
  local verdict="$1"
  local detail="$2"
  mkdir -p "$(dirname "$LOG_FILE")"
  local timestamp branch detail_json
  timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
  detail_json="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$detail")"
  printf '{"timestamp":"%s","branch":"%s","base_ref":"%s","head_ref":"%s","strict_mode":"%s","verdict":"%s","detail":%s}\n' \
    "$timestamp" "$branch" "$BASE_REF" "$HEAD_REF" "$STRICT_MODE" "$verdict" "$detail_json" >> "$LOG_FILE"
}

if [[ "${DISABLE_ENFORCEMENT:-0}" == "1" ]]; then
  echo "[stage-prompt-drift] SKIP: enforcement disabled (DISABLE_ENFORCEMENT=1)" >&2
  log_event "skip" "enforcement disabled"
  exit 0
fi

if [[ ! -f "$DRIFT_SCRIPT" ]]; then
  echo "[stage-prompt-drift] SKIP: drift checker not found at $DRIFT_SCRIPT" >&2
  log_event "skip" "drift checker missing at $DRIFT_SCRIPT"
  exit 0
fi

if ! git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
  echo "[stage-prompt-drift] SKIP: base ref not found: $BASE_REF" >&2
  log_event "skip" "base ref not found: $BASE_REF"
  exit 0
fi

echo "[stage-prompt-drift] Checking newly introduced stage prompt drift against ${BASE_REF}...${HEAD_REF}" >&2
report_file="$(mktemp)"
stub_args=()
if [[ "$WRITE_STUBS" == "1" ]]; then
  stub_args+=(--write-evidence-stubs)
fi
set +e
uv run python "$DRIFT_SCRIPT" \
  --base-ref "$BASE_REF" \
  --head-ref "$HEAD_REF" \
  --output-md "$report_file" \
  "${stub_args[@]}" \
  --fail-on-issues
exit_code=$?
set -e
cat "$report_file"

if [[ $exit_code -eq 0 ]]; then
  echo "[stage-prompt-drift] PASS: no newly introduced stage prompt drift." >&2
  log_event "pass" "no newly introduced stage prompt drift"
  rm -f "$report_file"
  exit 0
fi

if [[ "$STRICT_MODE" == "1" ]]; then
  echo "[stage-prompt-drift] FAIL: newly introduced stage prompt drift detected." >&2
  echo "[stage-prompt-drift] Remediation: review any auto-generated evidence stub under .claude/work-queue/assets/<work-item>/evidence/ and replace it with a real summary before deleting a stage-N-prompt.md artifact." >&2
  log_event "fail" "newly introduced stage prompt drift detected"
  rm -f "$report_file"
  exit 1
fi

echo "[stage-prompt-drift] WARNING: drift detected (advisory mode — set STAGE_PROMPT_DRIFT_STRICT=1 to enforce)." >&2
echo "[stage-prompt-drift] Remediation: review any auto-generated evidence stub under .claude/work-queue/assets/<work-item>/evidence/ and replace it with a real summary before deleting a stage-N-prompt.md artifact." >&2
log_event "warning" "newly introduced stage prompt drift detected"
rm -f "$report_file"
exit 0
