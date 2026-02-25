#!/usr/bin/env bash

# ABOUTME: Audit contract, adapter, and spec locality drift
# ABOUTME: Produces JSON report under reports/compliance/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
REPORT_DIR="$WORKSPACE_ROOT/reports/compliance"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
REPORT_FILE="$REPORT_DIR/contract-drift-$(date -u +%Y-%m-%d).json"

mkdir -p "$REPORT_DIR"

CONTRACT_VERSION="unknown"
if [[ -f "$WORKSPACE_ROOT/AGENTS.md" ]]; then
  CONTRACT_VERSION="$(awk -F': ' '/^Contract-Version:/{print $2}' "$WORKSPACE_ROOT/AGENTS.md" | head -n1)"
  CONTRACT_VERSION="${CONTRACT_VERSION:-unknown}"
fi

json_escape() {
  sed 's/\\/\\\\/g; s/"/\\"/g'
}

repo_entries=()

collect_repo() {
  local repo_path="$1"
  local repo_name
  repo_name="$(basename "$repo_path")"

  local missing=()
  local severity="low"

  [[ -f "$repo_path/CLAUDE.md" ]] || missing+=("CLAUDE.md")
  [[ -f "$repo_path/AGENTS.md" || "$repo_path" == "$WORKSPACE_ROOT" ]] || missing+=("AGENTS.md")

  local outdated_adapter="false"
  if [[ -f "$repo_path/CLAUDE.md" ]]; then
    if ! grep -q "Generated from workspace-hub/AGENTS.md" "$repo_path/CLAUDE.md"; then
      outdated_adapter="true"
      severity="medium"
    elif ! grep -q "Contract-Version: $CONTRACT_VERSION" "$repo_path/CLAUDE.md"; then
      outdated_adapter="true"
      severity="medium"
    fi
  fi

  local spec_violation_count=0
  if [[ -d "$repo_path/specs" && "$repo_path" != "$WORKSPACE_ROOT" ]]; then
    spec_violation_count="$(find "$repo_path/specs" -type f | wc -l | tr -d ' ')"
    if [[ "$spec_violation_count" -gt 0 ]]; then
      severity="high"
    fi
  fi

  local missing_json="[]"
  if [[ ${#missing[@]} -gt 0 ]]; then
    local parts=()
    for m in "${missing[@]}"; do
      parts+=("\"$m\"")
    done
    missing_json="[${parts[*]}]"
    missing_json="${missing_json// /, }"
    severity="high"
  fi

  repo_entries+=("{\"repo\":\"$repo_name\",\"missing_files\":$missing_json,\"outdated_adapter\":$outdated_adapter,\"spec_location_violation\":$spec_violation_count,\"severity\":\"$severity\"}")
}

collect_repo "$WORKSPACE_ROOT"
while IFS= read -r -d '' dir; do
  if [[ -e "$dir/.git" ]]; then
    collect_repo "$dir"
  fi
done < <(find "$WORKSPACE_ROOT" -mindepth 1 -maxdepth 1 -type d -print0)

wrk_external_count="$(find "$WORKSPACE_ROOT" -type f -name 'WRK-*.md' \
  ! -path "$WORKSPACE_ROOT/.claude/work-queue/*" \
  ! -path "$WORKSPACE_ROOT/*/scripts/review/results/*" | wc -l | tr -d ' ')"

{
  echo "{"
  echo "  \"generated_at\": \"$TIMESTAMP\"," 
  echo "  \"contract_version\": \"$CONTRACT_VERSION\"," 
  echo "  \"wrk_outside_queue\": $wrk_external_count," 
  echo "  \"repos\": ["
  for i in "${!repo_entries[@]}"; do
    if [[ "$i" -gt 0 ]]; then
      echo "    ,${repo_entries[$i]}"
    else
      echo "    ${repo_entries[$i]}"
    fi
  done
  echo "  ]"
  echo "}"
} > "$REPORT_FILE"

echo "Drift report written: $REPORT_FILE"
