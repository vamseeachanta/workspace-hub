#!/usr/bin/env bash
# workstation-dispatch.sh — Route a command to the best-fit machine.
# Matches task requirements against the workstation registry capabilities
# and executes via SSH (or locally if this machine is the best fit).
#
# Usage:
#   # Dispatch a scheduled task by ID:
#   bash scripts/operations/workstation-dispatch.sh --task benchmark-regression
#
#   # Dispatch an ad-hoc command with capability requirements:
#   bash scripts/operations/workstation-dispatch.sh --requires claude,python3 --command "claude --print 'hello'"
#
#   # Dry-run — show which machine would be selected:
#   bash scripts/operations/workstation-dispatch.sh --task gsd-researcher --dry-run
#
#   # Force a specific machine:
#   bash scripts/operations/workstation-dispatch.sh --machine dev-secondary --command "uptime"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
REGISTRY="${WORKSPACE_HUB}/config/workstations/registry.yaml"
SCHEDULE="${WORKSPACE_HUB}/config/scheduled-tasks/schedule-tasks.yaml"

# ── Parse arguments ─────────────────────────────────────────────────────────
TASK_ID=""
REQUIRES=""
COMMAND=""
MACHINE=""
DRY_RUN=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)     TASK_ID="$2"; shift 2 ;;
    --requires) REQUIRES="$2"; shift 2 ;;
    --command)  COMMAND="$2"; shift 2 ;;
    --machine)  MACHINE="$2"; shift 2 ;;
    --dry-run)  DRY_RUN=true; shift ;;
    --verbose)  VERBOSE=true; shift ;;
    *)
      echo "ERROR: unknown arg: $1" >&2
      echo "Usage: $0 --task <id> | --requires <caps> --command <cmd> [--machine <name>] [--dry-run]" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$TASK_ID" && -z "$COMMAND" && -z "$MACHINE" ]]; then
  echo "ERROR: provide --task <id>, --command <cmd>, or --machine <name>" >&2
  exit 1
fi

log() { echo "[dispatch] $*"; }
vlog() { [[ "$VERBOSE" == "true" ]] && log "$*" || true; }

THIS_HOST=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
THIS_HOST=$(printf '%s' "$THIS_HOST" | tr '[:upper:]' '[:lower:]')

# ── Resolve task → requires + command ───────────────────────────────────────
if [[ -n "$TASK_ID" ]]; then
  TASK_INFO=$(uv run --no-project python -c "
import yaml, sys, json
with open('${SCHEDULE}') as f:
    data = yaml.safe_load(f)
for task in data.get('tasks', []):
    if task.get('id') == '${TASK_ID}':
        print(json.dumps({
            'requires': task.get('requires', []),
            'command': task.get('command', ''),
            'prefer': task.get('prefer', ''),
            'label': task.get('label', ''),
        }))
        sys.exit(0)
print('__NOT_FOUND__')
" 2>/dev/null)

  if [[ "$TASK_INFO" == "__NOT_FOUND__" ]]; then
    echo "ERROR: task '${TASK_ID}' not found in schedule-tasks.yaml" >&2
    exit 1
  fi

  # Extract fields from JSON
  REQUIRES=$(echo "$TASK_INFO" | uv run --no-project python -c "import sys,json; print(','.join(json.load(sys.stdin)['requires']))" 2>/dev/null)
  TASK_LABEL=$(echo "$TASK_INFO" | uv run --no-project python -c "import sys,json; print(json.load(sys.stdin)['label'])" 2>/dev/null)
  PREFER=$(echo "$TASK_INFO" | uv run --no-project python -c "import sys,json; print(json.load(sys.stdin)['prefer'])" 2>/dev/null)
  if [[ -z "$COMMAND" ]]; then
    COMMAND=$(echo "$TASK_INFO" | uv run --no-project python -c "import sys,json; print(json.load(sys.stdin)['command'])" 2>/dev/null)
  fi

  log "Task: ${TASK_ID} — ${TASK_LABEL}"
fi

vlog "Requires: ${REQUIRES:-<none>}"
vlog "Command: ${COMMAND}"

# ── Find best-fit machine ──────────────────────────────────────────────────
if [[ -z "$MACHINE" ]]; then
  MACHINE=$(uv run --no-project python -c "
import yaml, sys
with open('${REGISTRY}') as f:
    reg = yaml.safe_load(f)

required = set('${REQUIRES}'.split(',')) if '${REQUIRES}' else set()
prefer = '${PREFER:-}'
this_host = '${THIS_HOST}'

# Flatten each machine's capabilities into a single set
def get_caps(m):
    caps = set()
    c = m.get('capabilities', {})
    for key in ('agent_clis', 'languages', 'tools'):
        caps.update(c.get(key, []))
    gpu = c.get('gpu')
    if gpu and gpu is not True:
        caps.add(gpu)
    if gpu:
        caps.add('gpu')
    return caps

candidates = []
for name, m in reg.get('machines', {}).items():
    # Must have SSH or be local
    ssh = m.get('ssh')
    hostnames = [m['hostname']] + m.get('hostname_aliases', [])
    is_local = this_host in [h.lower() for h in hostnames]
    if not ssh and not is_local:
        continue
    # Must satisfy all requirements
    caps = get_caps(m)
    if not required.issubset(caps):
        continue
    # Score: prefer hint = +100, local = +10, fewer excess caps = tighter fit
    score = 0
    if name == prefer:
        score += 100
    if is_local:
        score += 10
    score -= len(caps - required)  # tighter fit is better
    candidates.append((score, name, is_local, ssh))

if not candidates:
    print('__NO_MATCH__')
else:
    candidates.sort(key=lambda x: -x[0])
    best = candidates[0]
    # Output: name|is_local|ssh_target
    print(f'{best[1]}|{best[2]}|{best[3] or \"\"}')
" 2>/dev/null)

  if [[ "$MACHINE" == "__NO_MATCH__" ]]; then
    echo "ERROR: no machine satisfies requires=[${REQUIRES}]" >&2
    echo "  Available machines and their capabilities:" >&2
    bash "${SCRIPT_DIR}/workstation-status.sh" --quick 2>&1 | sed 's/^/    /' >&2
    exit 1
  fi

  # Parse the result
  MACHINE_NAME=$(echo "$MACHINE" | cut -d'|' -f1)
  IS_LOCAL=$(echo "$MACHINE" | cut -d'|' -f2)
  SSH_TARGET=$(echo "$MACHINE" | cut -d'|' -f3)
else
  # Explicit --machine: resolve from registry
  MACHINE_NAME="$MACHINE"
  RESOLVE=$(uv run --no-project python -c "
import yaml
with open('${REGISTRY}') as f:
    reg = yaml.safe_load(f)
this_host = '${THIS_HOST}'
for name, m in reg.get('machines', {}).items():
    if name == '${MACHINE}' or m['hostname'] == '${MACHINE}':
        hostnames = [m['hostname']] + m.get('hostname_aliases', [])
        is_local = this_host in [h.lower() for h in hostnames]
        print(f'{name}|{is_local}|{m.get(\"ssh\") or \"\"}')
        break
else:
    print('__NOT_FOUND__')
" 2>/dev/null)
  if [[ "$RESOLVE" == "__NOT_FOUND__" ]]; then
    echo "ERROR: machine '${MACHINE}' not in registry" >&2
    exit 1
  fi
  MACHINE_NAME=$(echo "$RESOLVE" | cut -d'|' -f1)
  IS_LOCAL=$(echo "$RESOLVE" | cut -d'|' -f2)
  SSH_TARGET=$(echo "$RESOLVE" | cut -d'|' -f3)
fi

log "Target: ${MACHINE_NAME} (local=${IS_LOCAL})"

# ── Dry-run: stop here ─────────────────────────────────────────────────────
if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "DRY RUN — would execute on ${MACHINE_NAME}:"
  echo "  ${COMMAND}"
  exit 0
fi

# ── Execute ─────────────────────────────────────────────────────────────────
if [[ -z "$COMMAND" ]]; then
  echo "ERROR: no command to execute (provide --command or --task)" >&2
  exit 1
fi

# Expand $WORKSPACE_HUB in command
WS_ROOT=$(uv run --no-project python -c "
import yaml
with open('${REGISTRY}') as f:
    reg = yaml.safe_load(f)
for name, m in reg.get('machines', {}).items():
    if name == '${MACHINE_NAME}':
        print(m.get('workspace_root') or '')
        break
" 2>/dev/null)
EXPANDED_CMD="${COMMAND//\$WORKSPACE_HUB/$WS_ROOT}"

if [[ "$IS_LOCAL" == "True" ]]; then
  log "Executing locally..."
  eval "$EXPANDED_CMD"
  EXIT_CODE=$?
else
  if [[ -z "$SSH_TARGET" ]]; then
    echo "ERROR: ${MACHINE_NAME} has no SSH target and is not local" >&2
    exit 1
  fi
  # Verify reachability
  if ! ssh -n -o ConnectTimeout=5 -o BatchMode=yes "$SSH_TARGET" true 2>/dev/null; then
    echo "ERROR: ${MACHINE_NAME} (${SSH_TARGET}) is unreachable" >&2
    exit 1
  fi
  log "Executing on ${MACHINE_NAME} via ssh ${SSH_TARGET}..."
  ssh -n -o ConnectTimeout=10 -o BatchMode=yes "$SSH_TARGET" \
    "export WORKSPACE_HUB='${WS_ROOT}'; ${EXPANDED_CMD}"
  EXIT_CODE=$?
fi

if [[ "$EXIT_CODE" -eq 0 ]]; then
  log "Done (exit 0)"
else
  log "FAILED (exit ${EXIT_CODE})"
fi
exit "$EXIT_CODE"
