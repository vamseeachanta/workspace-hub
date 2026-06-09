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
#
#   # Show provider routing for the selected machine (informational; F3 wiring):
#   bash scripts/operations/workstation-dispatch.sh --task gsd-researcher --route review --dry-run
#
#   # Role-aware selection (honor task roles ∩ machine harness_profile.roles, F3):
#   bash scripts/operations/workstation-dispatch.sh --task equality-report --role-aware --dry-run
#
#   # Acquire an atomic git-ref lease before dispatching so two dispatchers
#   # can't double-run the same task (F3 headline capability):
#   bash scripts/operations/workstation-dispatch.sh --task benchmark-regression --lease
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
ROUTE_TASK_TYPE=""   # F3: --route <task_type> → print provider routing for selected machine
ROLE_AWARE=false     # F3: --role-aware → honor task roles ∩ machine harness_profile.roles
USE_LEASE=false      # F3: --lease → acquire an atomic git-ref lease before dispatching

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)       TASK_ID="$2"; shift 2 ;;
    --requires)   REQUIRES="$2"; shift 2 ;;
    --command)    COMMAND="$2"; shift 2 ;;
    --machine)    MACHINE="$2"; shift 2 ;;
    --route)      ROUTE_TASK_TYPE="$2"; shift 2 ;;
    --role-aware) ROLE_AWARE=true; shift ;;
    --lease)      USE_LEASE=true; shift ;;
    --dry-run)    DRY_RUN=true; shift ;;
    --verbose)    VERBOSE=true; shift ;;
    *)
      echo "ERROR: unknown arg: $1" >&2
      echo "Usage: $0 --task <id> | --requires <caps> --command <cmd> [--machine <name>]" >&2
      echo "          [--route <task_type>] [--role-aware] [--lease] [--dry-run] [--verbose]" >&2
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
            'roles': task.get('roles', []),
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
  TASK_ROLES=$(echo "$TASK_INFO" | uv run --no-project python -c "import sys,json; print(','.join(json.load(sys.stdin).get('roles', [])))" 2>/dev/null)
  TASK_LABEL=$(echo "$TASK_INFO" | uv run --no-project python -c "import sys,json; print(json.load(sys.stdin)['label'])" 2>/dev/null)
  PREFER=$(echo "$TASK_INFO" | uv run --no-project python -c "import sys,json; print(json.load(sys.stdin)['prefer'])" 2>/dev/null)
  if [[ -z "$COMMAND" ]]; then
    COMMAND=$(echo "$TASK_INFO" | uv run --no-project python -c "import sys,json; print(json.load(sys.stdin)['command'])" 2>/dev/null)
  fi

  log "Task: ${TASK_ID} — ${TASK_LABEL}"
fi

vlog "Requires: ${REQUIRES:-<none>}"
vlog "Command: ${COMMAND}"

# ── F3 --role-aware: compute role-aware eligible set via dispatch_select.py ───
# Default OFF. When ON (and a task is being selected), the task's roles ∩ each
# machine's harness_profile.roles is honored IN ADDITION to the requires match,
# via the merged dispatch_select.select() core. The eligible machine ids become
# an allowlist that further constrains the existing requires-based scorer below;
# when the allowlist is empty the scorer behaves exactly as before (additive).
ROLE_ELIGIBLE=""
if [[ "$ROLE_AWARE" == "true" && -z "$MACHINE" ]]; then
  ROLE_ELIGIBLE=$(uv run --no-project --with pyyaml python -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}')
import yaml
from dispatch_select import select
with open('${REGISTRY}') as f:
    reg = yaml.safe_load(f)
machines = reg.get('machines', {}) or {}
task = {
    'requires': '${REQUIRES}'.split(',') if '${REQUIRES}' else [],
    'roles': '${TASK_ROLES:-}'.split(',') if '${TASK_ROLES:-}' else [],
}
# probe_fn=None -> ready == eligible (declared, JIT-probe deferred to dispatch).
result = select(task, machines)
print(','.join(result['eligible']))
" 2>/dev/null)
  vlog "Role-aware eligible: ${ROLE_ELIGIBLE:-<none>}"
fi

# ── Find best-fit machine ──────────────────────────────────────────────────
if [[ -z "$MACHINE" ]]; then
  MACHINE=$(uv run --no-project python -c "
import yaml, sys
with open('${REGISTRY}') as f:
    reg = yaml.safe_load(f)

required = set('${REQUIRES}'.split(',')) if '${REQUIRES}' else set()
prefer = '${PREFER:-}'
this_host = '${THIS_HOST}'
role_eligible = set('${ROLE_ELIGIBLE}'.split(',')) if '${ROLE_ELIGIBLE}' else set()

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
    # F3 --role-aware: when an eligibility allowlist was computed, the machine
    # must also be role-eligible (roles ∩ task roles, or cap-eligible) per the
    # dispatch_select core. Empty allowlist (default) = no extra constraint.
    if role_eligible and name not in role_eligible:
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

# ── F3 --route: informational provider routing for the selected machine ──────
# Prints which AI provider(s) should do <task_type> on the selected machine, via
# the single provider_route.py policy resolver. Informational ONLY — it does not
# change which machine is selected nor what command runs. The routing machine id
# is the registry hostname (matches policy machine_overrides keys, e.g.
# ace-linux-1); unknown machines fall back to the policy seed order.
if [[ -n "$ROUTE_TASK_TYPE" ]]; then
  ROUTE_MACHINE=$(uv run --no-project python -c "
import yaml
with open('${REGISTRY}') as f:
    reg = yaml.safe_load(f)
for name, m in reg.get('machines', {}).items():
    if name == '${MACHINE_NAME}':
        print(m.get('hostname') or name)
        break
else:
    print('${MACHINE_NAME}')
" 2>/dev/null)
  ROUTE_MACHINE="${ROUTE_MACHINE:-$MACHINE_NAME}"
  if PROVIDERS=$(uv run --script "${SCRIPT_DIR}/../ai/provider_route.py" "$ROUTE_TASK_TYPE" "$ROUTE_MACHINE" 2>/dev/null) \
       && [[ -n "$PROVIDERS" ]]; then
    log "Provider routing (${ROUTE_TASK_TYPE} on ${ROUTE_MACHINE}): ${PROVIDERS}"
  else
    log "Provider routing (${ROUTE_TASK_TYPE} on ${ROUTE_MACHINE}): <none — task_type unknown or all providers pruned>"
  fi
fi

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

# ── F3 --lease: acquire an atomic git-ref lease before dispatching ────────────
# Default OFF. When ON, acquire a versioned-CAS + fencing lease (dispatch_lease.py
# over the GitRefLease real-git adapter) named for the task BEFORE executing, so
# two dispatchers can never double-run the same task. If the lease is held, abort
# with a clear message. The lease is released (ref deleted, fenced by token) after
# execution. Reached only post-dry-run, so --dry-run never mutates a lease.
LEASE_NAME=""
LEASE_TOKEN=""
LEASE_REPO=""
if [[ "$USE_LEASE" == "true" ]]; then
  # Lease name = task id when dispatching a task, else a hash of the command.
  if [[ -n "$TASK_ID" ]]; then
    LEASE_NAME="$TASK_ID"
  else
    LEASE_NAME="cmd-$(printf '%s' "$COMMAND" | cksum | cut -d' ' -f1)"
  fi
  # Lease arbitration repo: defaults to the WORKSPACE_HUB git toplevel; overridable
  # via WS_DISPATCH_LEASE_REPO (e.g. a dedicated coordination repo, or a temp repo
  # for hermetic testing).
  LEASE_REPO="${WS_DISPATCH_LEASE_REPO:-$(git -C "${WORKSPACE_HUB}" rev-parse --show-toplevel 2>/dev/null || true)}"
  if [[ -z "$LEASE_REPO" ]] || ! git -C "$LEASE_REPO" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: --lease requires a git repo (set WS_DISPATCH_LEASE_REPO or run with a git WORKSPACE_HUB)" >&2
    exit 1
  fi
  # Fresh fencing token (caller-generated nondeterminism, per dispatch_lease contract).
  LEASE_TOKEN="${THIS_HOST}-$$-$(date +%s)-${RANDOM}"
  log "Acquiring dispatch lease '${LEASE_NAME}' (holder=${THIS_HOST})..."
  LEASE_RESULT=$(WS_LEASE_REPO="$LEASE_REPO" WS_LEASE_NAME="$LEASE_NAME" \
    WS_LEASE_HOLDER="$THIS_HOST" WS_LEASE_TOKEN="$LEASE_TOKEN" \
    uv run --no-project python -c "
import os, sys, time
sys.path.insert(0, '${SCRIPT_DIR}')
from git_ref_lease import GitRefLease
import dispatch_lease as dl
git = GitRefLease(os.environ['WS_LEASE_REPO'])
blob = dl.acquire(
    git, os.environ['WS_LEASE_NAME'], os.environ['WS_LEASE_HOLDER'],
    ttl_s=3600, now=time.time(), new_token=os.environ['WS_LEASE_TOKEN'],
)
print('ACQUIRED' if blob is not None else 'HELD')
" 2>/dev/null)
  if [[ "$LEASE_RESULT" != "ACQUIRED" ]]; then
    echo "ERROR: dispatch lease '${LEASE_NAME}' is held by another dispatcher; aborting (no double-run)" >&2
    exit 1
  fi
  log "Lease acquired."
fi

# Release the lease (token-fenced) on any exit once it has been acquired.
release_lease() {
  [[ "$USE_LEASE" == "true" && -n "$LEASE_TOKEN" ]] || return 0
  WS_LEASE_REPO="$LEASE_REPO" WS_LEASE_NAME="$LEASE_NAME" WS_LEASE_TOKEN="$LEASE_TOKEN" \
    uv run --no-project python -c "
import os, sys
sys.path.insert(0, '${SCRIPT_DIR}')
from git_ref_lease import GitRefLease, lease_ref
import dispatch_lease as dl, subprocess
git = GitRefLease(os.environ['WS_LEASE_REPO'])
# Fence: only delete the ref if WE still hold it (token unchanged). If another
# machine validly reclaimed it, leave it alone.
if dl.verify_token(git, os.environ['WS_LEASE_NAME'], os.environ['WS_LEASE_TOKEN']):
    ref = lease_ref(os.environ['WS_LEASE_NAME'])
    subprocess.run(['git', '-C', os.environ['WS_LEASE_REPO'], 'update-ref', '-d', ref],
                   capture_output=True)
" 2>/dev/null || true
  log "Lease '${LEASE_NAME}' released."
}
trap release_lease EXIT

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
