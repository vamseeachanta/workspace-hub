#!/usr/bin/env bash
# workstation-collect.sh — Collect results from a remote agent handoff branch.
# Fetches the result branch, shows what changed, and optionally merges.
#
# Usage:
#   # Fetch and show results from a specific branch:
#   bash scripts/operations/workstation-collect.sh --branch handoff/3-ace-linux-1-20260326T050000
#
#   # Fetch from a specific machine's remote first:
#   bash scripts/operations/workstation-collect.sh --branch handoff/3-ace-linux-1-20260326T050000 --machine dev-primary
#
#   # Auto-detect latest handoff branch for a phase:
#   bash scripts/operations/workstation-collect.sh --phase 3
#
#   # Show diff only (don't offer merge hint):
#   bash scripts/operations/workstation-collect.sh --branch handoff/3-ace-linux-1-20260326T050000 --diff-only
#
#   # Merge into current branch:
#   bash scripts/operations/workstation-collect.sh --branch handoff/3-ace-linux-1-20260326T050000 --merge
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
REGISTRY="${WORKSPACE_HUB}/config/workstations/registry.yaml"

source "${WORKSPACE_HUB}/scripts/lib/workstation-lib.sh"

# ── Parse arguments ─────────────────────────────────────────────────────────
BRANCH=""
PHASE=""
MACHINE=""
DIFF_ONLY=false
MERGE=false
CLEANUP=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch)    BRANCH="$2"; shift 2 ;;
    --phase)     PHASE="$2"; shift 2 ;;
    --machine)   MACHINE="$2"; shift 2 ;;
    --diff-only) DIFF_ONLY=true; shift ;;
    --merge)     MERGE=true; shift ;;
    --cleanup)   CLEANUP=true; shift ;;
    -h|--help)
      sed -n '2,/^set /{ /^#/s/^# \?//p }' "$0"
      exit 0
      ;;
    *)
      echo "ERROR: unknown arg: $1" >&2
      echo "Usage: $0 --branch <name> | --phase <n> [--machine <name>] [--diff-only | --merge] [--cleanup]" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$BRANCH" && -z "$PHASE" ]]; then
  echo "ERROR: provide --branch <name> or --phase <n>" >&2
  exit 1
fi

log() { echo "[collect] $*"; }

BASE_BRANCH=$(git -C "${WORKSPACE_HUB}" rev-parse --abbrev-ref HEAD)

# ── Resolve machine SSH target from registry ────────────────────────────────
resolve_ssh_target() {
  local machine="$1"
  uv run --no-project python -c "
import yaml
with open('${REGISTRY}') as f:
    reg = yaml.safe_load(f)
for name, m in reg.get('machines', {}).items():
    if name == '${machine}' or m['hostname'] == '${machine}':
        ssh = m.get('ssh')
        ws = m.get('workspace_root') or ''
        print(f'{ssh or \"\"}|{ws}')
        break
else:
    print('__NOT_FOUND__')
" 2>/dev/null
}

# ── Resolve branch from --phase ─────────────────────────────────────────────
if [[ -z "$BRANCH" && -n "$PHASE" ]]; then
  log "Finding latest handoff branch for phase ${PHASE}..."

  # Fetch remote refs first so we see remote handoff branches
  git -C "${WORKSPACE_HUB}" fetch origin --quiet 2>/dev/null || true

  # Search local and remote branches for handoff/{phase}-*
  BRANCH=$(git -C "${WORKSPACE_HUB}" for-each-ref \
    --sort=-creatordate \
    --format='%(refname:short)' \
    "refs/heads/handoff/${PHASE}-*" \
    "refs/remotes/origin/handoff/${PHASE}-*" \
    | head -n 1)

  # Strip origin/ prefix if it came from a remote ref
  BRANCH="${BRANCH#origin/}"

  if [[ -z "$BRANCH" ]]; then
    echo "ERROR: no handoff branch found matching handoff/${PHASE}-*" >&2
    echo "  Checked local branches and origin remote." >&2
    exit 1
  fi

  log "Resolved to: ${BRANCH}"
fi

# ── Fetch from remote machine (if --machine given) ─────────────────────────
if [[ -n "$MACHINE" ]]; then
  RESOLVE=$(resolve_ssh_target "$MACHINE")
  if [[ "$RESOLVE" == "__NOT_FOUND__" ]]; then
    echo "ERROR: machine '${MACHINE}' not in registry" >&2
    exit 1
  fi

  SSH_TARGET=$(echo "$RESOLVE" | cut -d'|' -f1)
  REMOTE_WS=$(echo "$RESOLVE" | cut -d'|' -f2)

  if [[ -z "$SSH_TARGET" ]]; then
    echo "ERROR: machine '${MACHINE}' has no SSH target" >&2
    exit 1
  fi

  log "Pushing ${BRANCH} from ${MACHINE} (${SSH_TARGET}) to origin..."
  if ! ssh -n -o ConnectTimeout=10 -o BatchMode=yes "$SSH_TARGET" \
    "cd '${REMOTE_WS}' && git push origin '${BRANCH}'" 2>/dev/null; then
    echo "ERROR: failed to push ${BRANCH} from ${MACHINE}" >&2
    exit 1
  fi
fi

# ── Fetch the branch locally ───────────────────────────────────────────────
log "Fetching ${BRANCH} from origin..."
if ! git -C "${WORKSPACE_HUB}" fetch origin "${BRANCH}" 2>/dev/null; then
  echo "ERROR: failed to fetch ${BRANCH} from origin" >&2
  echo "  If the branch is only on a remote machine, use --machine <name> to push it first." >&2
  exit 1
fi

# Ensure we have a local tracking ref
if ! git -C "${WORKSPACE_HUB}" rev-parse --verify "${BRANCH}" >/dev/null 2>&1; then
  git -C "${WORKSPACE_HUB}" branch "${BRANCH}" "origin/${BRANCH}" 2>/dev/null || true
fi

# ── Show results ────────────────────────────────────────────────────────────
SEPARATOR="$(printf '%0.s─' {1..50})"

echo ""
echo "Handoff Results: ${BRANCH}"
echo "${SEPARATOR}"

echo "Commits:"
git -C "${WORKSPACE_HUB}" log --oneline "${BASE_BRANCH}..${BRANCH}" 2>/dev/null \
  | sed 's/^/  /' || echo "  (no commits)"

echo ""
echo "Files changed:"
git -C "${WORKSPACE_HUB}" diff --stat "${BASE_BRANCH}..${BRANCH}" 2>/dev/null \
  | sed 's/^/  /' || echo "  (no changes)"

# ── Diff-only: stop here ───────────────────────────────────────────────────
if [[ "$DIFF_ONLY" == "true" ]]; then
  echo ""
  echo "Full diff:"
  git -C "${WORKSPACE_HUB}" diff "${BASE_BRANCH}..${BRANCH}" 2>/dev/null
  exit 0
fi

# ── Merge ───────────────────────────────────────────────────────────────────
if [[ "$MERGE" == "true" ]]; then
  echo ""
  log "Merging ${BRANCH} into ${BASE_BRANCH}..."
  git -C "${WORKSPACE_HUB}" merge "${BRANCH}" --no-ff \
    -m "merge: handoff results from ${BRANCH}"

  if [[ $? -eq 0 ]]; then
    log "Merge successful."
  else
    echo "ERROR: merge failed — resolve conflicts and commit manually" >&2
    exit 1
  fi

  # Cleanup if requested
  if [[ "$CLEANUP" == "true" ]]; then
    log "Cleaning up handoff branch..."
    git -C "${WORKSPACE_HUB}" branch -d "${BRANCH}" 2>/dev/null && \
      log "Deleted local branch ${BRANCH}" || true
    git -C "${WORKSPACE_HUB}" push origin --delete "${BRANCH}" 2>/dev/null && \
      log "Deleted remote branch ${BRANCH}" || true
    log "Branch cleaned up."
  else
    log "Branch preserved. Use --cleanup to delete after merge."
  fi

  exit 0
fi

# ── Default: show hint ──────────────────────────────────────────────────────
echo ""
echo "To merge: bash scripts/operations/workstation-collect.sh --branch ${BRANCH} --merge"
