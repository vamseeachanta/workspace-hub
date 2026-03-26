#!/usr/bin/env bash
# workstation-remote-agent.sh — Transfer a handoff bundle to a remote machine
# and launch a Claude agent session to execute the handoff instructions.
#
# Usage:
#   # Send handoff to best-fit machine (auto-selected):
#   bash scripts/operations/workstation-remote-agent.sh --bundle /tmp/handoff-3-20260326.tar.gz
#
#   # Send to specific machine:
#   bash scripts/operations/workstation-remote-agent.sh --bundle /tmp/handoff-3-20260326.tar.gz --machine dev-primary
#
#   # With timeout (default 30m):
#   bash scripts/operations/workstation-remote-agent.sh --bundle /tmp/handoff-3-20260326.tar.gz --timeout 1800
#
#   # Dry-run:
#   bash scripts/operations/workstation-remote-agent.sh --bundle /tmp/handoff-3-20260326.tar.gz --dry-run
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
REGISTRY="${WORKSPACE_HUB}/config/workstations/registry.yaml"

source "${WORKSPACE_HUB}/scripts/lib/workstation-lib.sh"

# ── Parse arguments ─────────────────────────────────────────────────────────
BUNDLE=""
MACHINE=""
TIMEOUT=1800
DRY_RUN=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bundle)   BUNDLE="$2"; shift 2 ;;
    --machine)  MACHINE="$2"; shift 2 ;;
    --timeout)  TIMEOUT="$2"; shift 2 ;;
    --dry-run)  DRY_RUN=true; shift ;;
    --verbose)  VERBOSE=true; shift ;;
    -h|--help)
      sed -n '2,/^set /{ /^#/s/^# \?//p }' "$0"
      exit 0
      ;;
    *)
      echo "ERROR: unknown arg: $1" >&2
      echo "Usage: $0 --bundle <path> [--machine <name>] [--timeout <secs>] [--dry-run]" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$BUNDLE" ]]; then
  echo "ERROR: --bundle is required" >&2
  exit 1
fi

if [[ ! -f "$BUNDLE" ]]; then
  echo "ERROR: bundle not found: ${BUNDLE}" >&2
  exit 1
fi

log() { echo "[remote-agent] $*"; }
vlog() { [[ "$VERBOSE" == "true" ]] && log "$*" || true; }

THIS_HOST=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
THIS_HOST=$(printf '%s' "$THIS_HOST" | tr '[:upper:]' '[:lower:]')

BUNDLE_BASENAME=$(basename "$BUNDLE")

# ── Read HANDOFF.json from the bundle ───────────────────────────────────────
log "Reading handoff metadata from ${BUNDLE_BASENAME}..."
HANDOFF_JSON=$(tar xzf "$BUNDLE" --to-stdout "handoff/HANDOFF.json" 2>/dev/null \
  || tar xzf "$BUNDLE" --to-stdout "HANDOFF.json" 2>/dev/null \
  || true)

if [[ -z "$HANDOFF_JSON" ]]; then
  echo "ERROR: could not extract HANDOFF.json from bundle" >&2
  exit 1
fi

PHASE=$(echo "$HANDOFF_JSON" | uv run --no-project python -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('phase', 'unknown'))
" 2>/dev/null)

RESULT_BRANCH=$(echo "$HANDOFF_JSON" | uv run --no-project python -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('result_branch', ''))
" 2>/dev/null)

REQUIRES=$(echo "$HANDOFF_JSON" | uv run --no-project python -c "
import sys, json
data = json.load(sys.stdin)
reqs = data.get('requires', [])
if isinstance(reqs, list):
    print(','.join(reqs))
else:
    print(reqs)
" 2>/dev/null)

if [[ -z "$RESULT_BRANCH" ]]; then
  RESULT_BRANCH="handoff/phase-${PHASE}/$(date +%Y%m%d-%H%M%S)"
  log "No result_branch in metadata; using ${RESULT_BRANCH}"
fi

vlog "Phase: ${PHASE}"
vlog "Result branch: ${RESULT_BRANCH}"
vlog "Requires: ${REQUIRES:-claude}"

# Ensure claude is always in the requirements
if [[ -z "$REQUIRES" ]]; then
  REQUIRES="claude"
elif [[ ! "$REQUIRES" =~ claude ]]; then
  REQUIRES="claude,${REQUIRES}"
fi

# ── Select target machine ──────────────────────────────────────────────────
if [[ -z "$MACHINE" ]]; then
  MACHINE_RESULT=$(uv run --no-project python -c "
import yaml, sys

with open('${REGISTRY}') as f:
    reg = yaml.safe_load(f)

required = set('${REQUIRES}'.split(',')) if '${REQUIRES}' else {'claude'}
this_host = '${THIS_HOST}'

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
    ssh = m.get('ssh')
    hostnames = [m['hostname']] + m.get('hostname_aliases', [])
    is_local = this_host in [h.lower() for h in hostnames]
    if not ssh and not is_local:
        continue
    caps = get_caps(m)
    if not required.issubset(caps):
        continue
    # Score: prefer remote machines (not local) for offloading work
    score = 0
    if not is_local:
        score += 10  # prefer remote — whole point is distributing work
    score -= len(caps - required)  # tighter fit is better
    candidates.append((score, name, is_local, ssh, m.get('workspace_root', '')))

if not candidates:
    print('__NO_MATCH__')
else:
    candidates.sort(key=lambda x: -x[0])
    best = candidates[0]
    print(f'{best[1]}|{best[2]}|{best[3] or \"\"}|{best[4] or \"\"}')
" 2>/dev/null)

  if [[ "$MACHINE_RESULT" == "__NO_MATCH__" ]]; then
    echo "ERROR: no machine with capabilities [${REQUIRES}] is SSH-reachable" >&2
    exit 1
  fi

  MACHINE_NAME=$(echo "$MACHINE_RESULT" | cut -d'|' -f1)
  IS_LOCAL=$(echo "$MACHINE_RESULT" | cut -d'|' -f2)
  SSH_TARGET=$(echo "$MACHINE_RESULT" | cut -d'|' -f3)
  REMOTE_WS_ROOT=$(echo "$MACHINE_RESULT" | cut -d'|' -f4)
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
        print(f'{name}|{is_local}|{m.get(\"ssh\") or \"\"}|{m.get(\"workspace_root\") or \"\"}')
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
  REMOTE_WS_ROOT=$(echo "$RESOLVE" | cut -d'|' -f4)
fi

if [[ -z "$SSH_TARGET" && "$IS_LOCAL" != "True" ]]; then
  echo "ERROR: ${MACHINE_NAME} has no SSH target and is not this machine" >&2
  exit 1
fi

log "Target: ${MACHINE_NAME} (ssh=${SSH_TARGET:-local})"
log "Bundle: ${BUNDLE_BASENAME}"
log "Result branch: ${RESULT_BRANCH}"
log "Timeout: ${TIMEOUT}s"

# ── Dry-run: stop here ─────────────────────────────────────────────────────
if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "DRY RUN — would execute:"
  echo "  Target machine:  ${MACHINE_NAME}"
  echo "  SSH target:      ${SSH_TARGET:-<local>}"
  echo "  Workspace root:  ${REMOTE_WS_ROOT}"
  echo "  Bundle:          ${BUNDLE}"
  echo "  Result branch:   ${RESULT_BRANCH}"
  echo "  Phase:           ${PHASE}"
  echo "  Timeout:         ${TIMEOUT}s"
  exit 0
fi

# ── Verify SSH reachability ────────────────────────────────────────────────
if [[ "$IS_LOCAL" != "True" ]]; then
  log "Verifying SSH connectivity to ${SSH_TARGET}..."
  if ! ssh -n -o ConnectTimeout=10 -o BatchMode=yes "$SSH_TARGET" true 2>/dev/null; then
    echo "ERROR: ${MACHINE_NAME} (${SSH_TARGET}) is unreachable via SSH" >&2
    exit 1
  fi
fi

# ── Transfer bundle ────────────────────────────────────────────────────────
if [[ "$IS_LOCAL" == "True" ]]; then
  log "Local execution — skipping transfer"
  REMOTE_BUNDLE="$BUNDLE"
else
  log "Transferring bundle to ${MACHINE_NAME}..."
  if ! scp -o ConnectTimeout=10 -o BatchMode=yes "$BUNDLE" "${SSH_TARGET}:/tmp/${BUNDLE_BASENAME}"; then
    echo "ERROR: failed to transfer bundle to ${MACHINE_NAME}" >&2
    exit 1
  fi
  REMOTE_BUNDLE="/tmp/${BUNDLE_BASENAME}"
fi

# ── Build remote execution script ──────────────────────────────────────────
REMOTE_SCRIPT=$(cat <<'REMOTE_EOF'
set -euo pipefail

WORKSPACE_HUB="__REMOTE_WS_ROOT__"
BUNDLE_PATH="__REMOTE_BUNDLE__"
RESULT_BRANCH="__RESULT_BRANCH__"
PHASE="__PHASE__"
TIMEOUT="__TIMEOUT__"

log() { echo "[remote-agent@$(hostname -s)] $*"; }

# Unpack the handoff bundle
WORK_DIR=$(mktemp -d /tmp/handoff-work-XXXXXX)
log "Unpacking bundle to ${WORK_DIR}..."
tar xzf "$BUNDLE_PATH" -C "$WORK_DIR"

# Find the HANDOFF.md — it may be inside a subdirectory
HANDOFF_MD=$(find "$WORK_DIR" -name "HANDOFF.md" -type f | head -1)
if [[ -z "$HANDOFF_MD" ]]; then
  log "ERROR: HANDOFF.md not found in bundle"
  rm -rf "$WORK_DIR"
  exit 1
fi

log "Found handoff instructions: ${HANDOFF_MD}"

# Set up the result branch in workspace-hub
cd "$WORKSPACE_HUB"
log "Checking out result branch: ${RESULT_BRANCH}"
git fetch origin 2>/dev/null || true
if git rev-parse --verify "$RESULT_BRANCH" >/dev/null 2>&1; then
  git checkout "$RESULT_BRANCH"
else
  git checkout -b "$RESULT_BRANCH"
fi

# Run Claude with the handoff prompt
HANDOFF_CONTENT=$(cat "$HANDOFF_MD")
log "Starting Claude agent (timeout=${TIMEOUT}s)..."
CLAUDE_EXIT=0
timeout "$TIMEOUT" claude -p "$HANDOFF_CONTENT" >"$WORK_DIR/claude.log" 2>&1 || CLAUDE_EXIT=$?

if [[ "$CLAUDE_EXIT" -eq 124 ]]; then
  log "WARNING: Claude agent timed out after ${TIMEOUT}s"
elif [[ "$CLAUDE_EXIT" -ne 0 ]]; then
  log "WARNING: Claude agent exited with code ${CLAUDE_EXIT}"
  cat "$WORK_DIR/claude.log" >&2 || true
fi

# Commit any changes Claude made
cd "$WORKSPACE_HUB"
git add -A
if ! git diff --staged --quiet; then
  git commit -m "handoff: phase ${PHASE} results from $(hostname -s)"
  log "Changes committed on branch ${RESULT_BRANCH}"
else
  log "No changes to commit"
fi

# Cleanup
rm -rf "$WORK_DIR"
if [[ "$BUNDLE_PATH" == /tmp/* ]]; then
  rm -f "$BUNDLE_PATH"
fi

log "Done. Result branch: ${RESULT_BRANCH}"
REMOTE_EOF
)

# Substitute placeholders
REMOTE_SCRIPT="${REMOTE_SCRIPT//__REMOTE_WS_ROOT__/$REMOTE_WS_ROOT}"
REMOTE_SCRIPT="${REMOTE_SCRIPT//__REMOTE_BUNDLE__/$REMOTE_BUNDLE}"
REMOTE_SCRIPT="${REMOTE_SCRIPT//__RESULT_BRANCH__/$RESULT_BRANCH}"
REMOTE_SCRIPT="${REMOTE_SCRIPT//__PHASE__/$PHASE}"
REMOTE_SCRIPT="${REMOTE_SCRIPT//__TIMEOUT__/$TIMEOUT}"

# ── Execute ────────────────────────────────────────────────────────────────
if [[ "$IS_LOCAL" == "True" ]]; then
  log "Executing locally..."
  bash -c "$REMOTE_SCRIPT"
  EXIT_CODE=$?
else
  log "Executing on ${MACHINE_NAME} via SSH..."
  ssh -n -o ConnectTimeout=10 -o BatchMode=yes "$SSH_TARGET" bash -c "'$(echo "$REMOTE_SCRIPT" | sed "s/'/'\\\\''/g")'"
  EXIT_CODE=$?
fi

# ── Report ─────────────────────────────────────────────────────────────────
echo ""
if [[ "$EXIT_CODE" -eq 0 ]]; then
  log "Remote agent completed successfully"
  echo "  Machine:       ${MACHINE_NAME}"
  echo "  Result branch: ${RESULT_BRANCH}"
  echo ""
  echo "To retrieve results:"
  echo "  git fetch ${SSH_TARGET}:${REMOTE_WS_ROOT} ${RESULT_BRANCH}"
else
  log "Remote agent FAILED (exit ${EXIT_CODE})"
  echo "  Machine: ${MACHINE_NAME}"
  echo "  Check logs on ${MACHINE_NAME} for details"
fi

exit "$EXIT_CODE"
