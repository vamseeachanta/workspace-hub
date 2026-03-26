#!/usr/bin/env bash
# workstation-status.sh — Fleet health check for all registered workstations.
# Reads machine definitions from config/workstations/registry.yaml.
# Reports: reachability (SSH ping), workspace-hub presence, agent CLI versions.
#
# Usage:
#   bash scripts/operations/workstation-status.sh           # check all SSH-reachable machines
#   bash scripts/operations/workstation-status.sh --json    # machine-readable output
#   bash scripts/operations/workstation-status.sh --quick   # reachability only (no version checks)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
REGISTRY="${WORKSPACE_HUB}/config/workstations/registry.yaml"

JSON_MODE=false
QUICK_MODE=false
for arg in "$@"; do
  case "$arg" in
    --json)  JSON_MODE=true ;;
    --quick) QUICK_MODE=true ;;
  esac
done

if [[ ! -f "$REGISTRY" ]]; then
  echo "ERROR: registry not found at ${REGISTRY}" >&2
  exit 1
fi

THIS_HOST=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
THIS_HOST=$(printf '%s' "$THIS_HOST" | tr '[:upper:]' '[:lower:]')

# ── Parse registry with Python ────────────────────────────────────────────────
# Emits tab-separated lines: name\thostname\tssh\tos\trole\tworkspace_root\tagent_clis
MACHINES=$(uv run --no-project python -c "
import yaml, sys
with open('${REGISTRY}') as f:
    data = yaml.safe_load(f)
for name, m in data.get('machines', {}).items():
    ssh = m.get('ssh') or '_NONE_'
    ws = m.get('workspace_root') or '_NONE_'
    clis = ','.join(m.get('capabilities', {}).get('agent_clis', [])) or '_NONE_'
    print(f\"{name}\t{m['hostname']}\t{ssh}\t{m['os']}\t{m.get('role','_NONE_')}\t{ws}\t{clis}\")
" 2>/dev/null)

if [[ -z "$MACHINES" ]]; then
  echo "ERROR: failed to parse registry" >&2
  exit 1
fi

# ── Check each machine ────────────────────────────────────────────────────────
RESULTS=()
TOTAL=0
REACHABLE=0
UNREACHABLE=0
LOCAL=0
NO_SSH=0

check_machine() {
  local name="$1" hostname="$2" ssh_target="$3" os="$4" role="$5" ws_root="$6" agent_clis="$7"
  # _NONE_ sentinel used because bash read collapses adjacent tab delimiters
  [[ "$ssh_target" == "_NONE_" ]] && ssh_target=""
  [[ "$ws_root" == "_NONE_" ]] && ws_root=""
  [[ "$role" == "_NONE_" ]] && role=""
  local status="unknown" claude_ver="-" gemini_ver="-" ws_exists="-"

  TOTAL=$((TOTAL + 1))

  # Is this the local machine?
  local is_local=false
  if [[ "$hostname" == "$THIS_HOST" ]]; then
    is_local=true
  fi

  if [[ -z "$ssh_target" ]]; then
    status="no-ssh"
    NO_SSH=$((NO_SSH + 1))
  elif [[ "$is_local" == "true" ]]; then
    status="local"
    LOCAL=$((LOCAL + 1))
    if [[ -n "$ws_root" && -d "$ws_root/.git" ]]; then
      ws_exists="yes"
    elif [[ -n "$ws_root" ]]; then
      ws_exists="no"
    fi
    if [[ "$QUICK_MODE" == "false" ]]; then
      claude_ver=$(claude --version 2>/dev/null | head -1 || echo "not found")
      gemini_ver=$(gemini --version 2>/dev/null | head -1 || echo "not found")
    fi
  else
    # Remote SSH check with 5s timeout
    if ssh -n -o ConnectTimeout=5 -o BatchMode=yes "$ssh_target" true 2>/dev/null; then
      status="online"
      REACHABLE=$((REACHABLE + 1))
      if [[ -n "$ws_root" ]]; then
        if ssh -n -o ConnectTimeout=5 -o BatchMode=yes "$ssh_target" \
            "test -d '${ws_root}/.git'" 2>/dev/null; then
          ws_exists="yes"
        else
          ws_exists="no"
        fi
      fi
      if [[ "$QUICK_MODE" == "false" ]]; then
        claude_ver=$(ssh -n -o ConnectTimeout=5 -o BatchMode=yes "$ssh_target" \
          "claude --version 2>/dev/null | head -1" 2>/dev/null || echo "not found")
        gemini_ver=$(ssh -n -o ConnectTimeout=5 -o BatchMode=yes "$ssh_target" \
          "gemini --version 2>/dev/null | head -1" 2>/dev/null || echo "not found")
      fi
    else
      status="offline"
      UNREACHABLE=$((UNREACHABLE + 1))
    fi
  fi

  if [[ "$JSON_MODE" == "true" ]]; then
    RESULTS+=("{\"name\":\"${name}\",\"hostname\":\"${hostname}\",\"os\":\"${os}\",\"role\":\"${role}\",\"status\":\"${status}\",\"workspace\":\"${ws_exists}\",\"claude\":\"${claude_ver}\",\"gemini\":\"${gemini_ver}\"}")
  else
    local status_icon
    case "$status" in
      local)   status_icon="*" ;;
      online)  status_icon="+" ;;
      offline) status_icon="x" ;;
      no-ssh)  status_icon="-" ;;
      *)       status_icon="?" ;;
    esac
    printf "  [%s] %-22s %-14s %-18s ws=%-3s" \
      "$status_icon" "$name" "$hostname" "$role" "$ws_exists"
    if [[ "$QUICK_MODE" == "false" && "$status" != "no-ssh" && "$status" != "offline" ]]; then
      printf "  claude=%s" "$claude_ver"
    fi
    printf "\n"
  fi
}

if [[ "$JSON_MODE" != "true" ]]; then
  echo "Workstation Fleet Status (from ${THIS_HOST})"
  echo "──────────────────────────────────────────────────────────────────────"
  echo "  Legend: [*] local  [+] online  [x] offline  [-] no SSH"
  echo ""
fi

while IFS=$'\t' read -r name hostname ssh_target os role ws_root agent_clis; do
  check_machine "$name" "$hostname" "$ssh_target" "$os" "$role" "$ws_root" "$agent_clis"
done <<< "$MACHINES"

if [[ "$JSON_MODE" == "true" ]]; then
  echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"from\":\"${THIS_HOST}\",\"machines\":[$(IFS=,; echo "${RESULTS[*]}")]}"
else
  echo ""
  echo "Summary: ${TOTAL} machines — ${LOCAL} local, ${REACHABLE} online, ${UNREACHABLE} offline, ${NO_SSH} no-ssh"
fi
