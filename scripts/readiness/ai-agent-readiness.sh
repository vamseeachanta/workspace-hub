#!/usr/bin/env bash
# ai-agent-readiness.sh — Check CLI presence, version, and quota for all AI agents.
# Standalone; called by nightly-readiness.sh (R-AI-CLI + R-AI-QUOTA).
# Emits JSONL to .claude/state/session-signals/ai-readiness.jsonl (appended).
# Returns 0 always — failures are logged, never fatal.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
VERSIONS_FILE="${SCRIPT_DIR}/ai-agent-versions.yaml"
QUOTA_FILE="${WORKSPACE_HUB}/config/ai-tools/agent-quota-latest.json"
SIGNALS_DIR="${WORKSPACE_HUB}/.claude/state/session-signals"
JSONL_OUT="${SIGNALS_DIR}/ai-readiness.jsonl"
RUN_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
HOSTNAME_SHORT=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)

mkdir -p "$SIGNALS_DIR"

# Safe JSON string escaping (no external deps): escape backslash, double-quote, control chars
_json_str() {
  printf '%s' "$1" \
    | sed 's/\\/\\\\/g; s/"/\\"/g; s/'"$(printf '\t')"'/\\t/g' \
    | tr -d '\000-\037'
}

# Read a scalar value for a given key under an agent block in versions yaml.
# Uses grep to find "^<agent>:" then finds "  <key>:" in the next 5 lines.
# More targeted than -AN: anchors to the agent section header first.
_yaml_get() {
  local agent="$1" key="$2"
  # Find line number of agent block header
  local header_line
  header_line=$(grep -n "^${agent}:" "$VERSIONS_FILE" 2>/dev/null | head -1 | cut -d: -f1)
  [[ -z "$header_line" ]] && return 0
  # Read up to 5 lines after the header; stop at next top-level key
  sed -n "$((header_line + 1)),$((header_line + 5))p" "$VERSIONS_FILE" 2>/dev/null \
    | grep -E "^[[:space:]]+${key}:" | head -1 \
    | sed "s/.*${key}:[[:space:]]*//" | tr -d '"' | tr -d "'"
}

# Semver comparison: returns 0 if actual >= minimum
_version_ok() {
  local actual="$1" minimum="$2"
  [[ -z "$actual" || -z "$minimum" ]] && return 1
  local a m
  a=$(printf '%s' "$actual"  | sed 's/[^0-9.].*$//' | sed 's/^[^0-9]*//')
  m=$(printf '%s' "$minimum" | sed 's/[^0-9.].*$//' | sed 's/^[^0-9]*//')
  [[ -z "$a" || -z "$m" ]] && return 1
  local lo
  lo=$(printf '%s\n%s\n' "$a" "$m" | sort -V | head -1)
  [[ "$lo" == "$m" ]]
}

# Emit one JSONL record — uses _json_str to ensure no unescaped values
_emit() {
  local agent status version message
  agent=$(_json_str "$1")
  status=$(_json_str "$2")
  version=$(_json_str "${3:-}")
  message=$(_json_str "${4:-}")
  local host_esc
  host_esc=$(_json_str "$HOSTNAME_SHORT")
  printf '{"ts":"%s","host":"%s","agent":"%s","status":"%s","version":"%s","message":"%s"}\n' \
    "$RUN_TS" "$host_esc" "$agent" "$status" "$version" "$message" >> "$JSONL_OUT"
  echo "  ${2^^}  R-AI-CLI[${1}]: ${4:-version=${3:-}}"
}

echo "--- AI agent readiness: ${RUN_TS} ---"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Per-agent: presence + version check
# ─────────────────────────────────────────────────────────────────────────────
AGENTS=(claude codex gemini)

for agent in "${AGENTS[@]}"; do
  cli_min=$(_yaml_get "$agent" "cli_min")
  default_model=$(_yaml_get "$agent" "default_model")

  if ! command -v "$agent" &>/dev/null; then
    _emit "$agent" "warn" "" "CLI not found in PATH"
    continue
  fi

  raw_version=""
  case "$agent" in
    claude)  raw_version=$(claude --version 2>/dev/null | head -1 || true) ;;
    codex)   raw_version=$( codex --version 2>/dev/null | head -1 || true) ;;
    gemini)  raw_version=$(gemini --version 2>/dev/null | head -1 || true) ;;
  esac

  parsed_version=$(printf '%s' "$raw_version" \
    | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || true)

  if [[ -z "$parsed_version" ]]; then
    _emit "$agent" "warn" "" "installed but version unreadable"
    continue
  fi

  if [[ -n "$cli_min" ]] && ! _version_ok "$parsed_version" "$cli_min"; then
    _emit "$agent" "warn" "$parsed_version" \
      "version ${parsed_version} below minimum ${cli_min} — run update"
  else
    _emit "$agent" "ok" "$parsed_version" \
      "version ${parsed_version} ok; expected model ${default_model}"
  fi
done

# ─────────────────────────────────────────────────────────────────────────────
# 2. Quota check: flag providers ≥ 80% weekly usage
# ─────────────────────────────────────────────────────────────────────────────
echo "--- AI quota check ---"

if [[ ! -f "$QUOTA_FILE" ]]; then
  echo "  SKIP  R-AI-QUOTA: ${QUOTA_FILE} absent"
elif ! command -v jq &>/dev/null; then
  echo "  SKIP  R-AI-QUOTA: jq not installed"
else
  # Parse provider + week_pct in one jq call per entry
  while IFS=$'\t' read -r provider week_pct; do
    [[ "$week_pct" == "null" ]] && week_pct=0
    is_high=$(awk -v p="$week_pct" 'BEGIN { print (p >= 80) ? "yes" : "no" }')
    if [[ "$is_high" == "yes" ]]; then
      quota_msg="week_pct=${week_pct}% — quota >=80% weekly; plan accordingly"
      quota_provider_esc=$(_json_str "${provider}-quota")
      quota_msg_esc=$(_json_str "$quota_msg")
      quota_host_esc=$(_json_str "$HOSTNAME_SHORT")
      printf '{"ts":"%s","host":"%s","agent":"%s","status":"warn","version":"","message":"%s"}\n' \
        "$RUN_TS" "$quota_host_esc" "$quota_provider_esc" "$quota_msg_esc" >> "$JSONL_OUT"
      echo "  WARN  R-AI-QUOTA[${provider}]: ${quota_msg}"
    else
      echo "  OK    R-AI-QUOTA[${provider}]: week_pct=${week_pct}%"
    fi
  done < <(jq -r '.agents[] | [.provider // "unknown", (.week_pct // 0 | tostring)] | @tsv' \
             "$QUOTA_FILE" 2>/dev/null || true)
fi

echo "--- AI agent readiness done ---"
exit 0
