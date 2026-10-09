#!/usr/bin/env bash
# commit-learning-artifacts.sh — Git-add + commit all learning state that gitignore allows
#
# Called at the end of comprehensive-learning-nightly.sh to ensure
# corrections, patterns, insights, and cross-agent state survive machine loss.
#
# Usage: bash scripts/cron/commit-learning-artifacts.sh [--dry-run]
# Cron:  Called by comprehensive-learning-nightly.sh (last step)
#
# Snapshot redaction and normal commit hooks remain enabled.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$WORKSPACE_HUB"

DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
  esac
done

log() { echo "[commit-learning-artifacts] $*"; }

# Source git-safe if available (for coordinated git access)
GIT_SAFE_LOG_PREFIX="[commit-learning]"
if [[ -f "${WORKSPACE_HUB}/scripts/cron/lib/git-safe.sh" ]]; then
  source "${WORKSPACE_HUB}/scripts/cron/lib/git-safe.sh"
  git_safe_init "$WORKSPACE_HUB"
fi

# ── C20: every host copy into this PUBLIC tree goes through the redactor ──
# The snapshots below copy host agent state (codex history, memories) into a
# public repository. Each copy is redacted by the identifier gate's Redactor
# (scripts/legal/public_redaction.py); a file whose name carries an identifier
# is not copied at all. The private deny list (WORKSPACE_HUB_DENY_LIST) extends
# the redactor when this host has one; without it the public rules apply (S01).
# If the redactor cannot load -- a missing rules file, a named list or map that
# is absent -- nothing is snapshotted and nothing is committed.
if [[ -n "${WORKSPACE_HUB_PYTHON:-}" ]]; then
  PY_RUN=("$WORKSPACE_HUB_PYTHON")
else
  PY_RUN=(uv run python)
fi
PUBLIC_REDACTION="${WORKSPACE_HUB}/scripts/legal/public_redaction.py"
# The private client codename map, when this host has one, extends the redactor.
PII_MAP="${PII_CODENAME_MAP:-${WORKSPACE_HUB}/config/agents/.client-codename-map.local.yaml}"
if [[ -z "${LEGAL_CLIENT_MAP:-}" && -f "$PII_MAP" ]]; then
  export LEGAL_CLIENT_MAP="$PII_MAP"
fi
if ! "${PY_RUN[@]}" "$PUBLIC_REDACTION" self-check; then
  log "ERROR: the public redactor cannot load -- nothing snapshotted or committed (C20)"
  exit 1
fi

# Copy SRC to DEST through the redactor. Absent SRC is not an error (optional
# host state); a failed redaction is.
redact_copy() {
  local src="$1" dest="$2"
  [[ -f "$src" ]] || return 0
  mkdir -p "$(dirname "$dest")"
  "${PY_RUN[@]}" "$PUBLIC_REDACTION" copy "$src" "$dest"
}
pii_snapshot_copy() { redact_copy "$1" "$2"; }
fail_closed() { log "ERROR: redacting copy failed -- nothing committed (C20)"; exit 1; }

CLAUDE_MEMORY_SNAPSHOT_REPO="${CLAUDE_MEMORY_SNAPSHOT_REPO:-vamseeachanta/claude-memory-snapshots}"
CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE="${CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE:-${HOME}/.local/share/claude-memory-snapshots}"
CLAUDE_PRIVATE_SNAPSHOT_READY=false
CLAUDE_PRIVATE_SNAPSHOT_STAGED=false
CLAUDE_PRIVATE_SNAPSHOT_DRY_RUN_LOGGED=false
CLAUDE_PRIVATE_STAGE=""

cleanup_claude_private_stage() {
  if [[ -n "$CLAUDE_PRIVATE_STAGE" && -d "$CLAUDE_PRIVATE_STAGE" ]]; then
    rm -rf "$CLAUDE_PRIVATE_STAGE"
  fi
}
trap cleanup_claude_private_stage EXIT

normalize_github_repo_url() {
  local value="$1"
  value="${value#git@github.com:}"
  value="${value#https://github.com/}"
  value="${value#http://github.com/}"
  value="${value%.git}"
  printf '%s\n' "$value"
}

resolve_path_for_guard() {
  "${PY_RUN[@]}" -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve(strict=False))' "$1"
}

verify_claude_private_snapshot_visibility() {
  local visibility
  visibility="$(gh repo view "$CLAUDE_MEMORY_SNAPSHOT_REPO" --json isPrivate --jq .isPrivate)"
  if [[ "$visibility" != "true" ]]; then
    log "ERROR: Claude memory snapshot repo is not private: $CLAUDE_MEMORY_SNAPSHOT_REPO"
    return 1
  fi
}

verify_claude_private_snapshot_target_path() {
  local clone_real hub_real
  clone_real="$(readlink -f "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE" 2>/dev/null || true)"
  if [[ -z "$clone_real" ]]; then
    clone_real="$(resolve_path_for_guard "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE")"
  fi
  hub_real="$(readlink -f "$WORKSPACE_HUB" 2>/dev/null || true)"
  if [[ -z "$hub_real" ]]; then
    hub_real="$(resolve_path_for_guard "$WORKSPACE_HUB")"
  fi
  case "$clone_real" in
    "$hub_real"|"$hub_real"/*)
      log "ERROR: Claude memory snapshot clone must be outside the public checkout"
      return 1
      ;;
  esac
}

verify_claude_private_snapshot_repo() {
  local origin expected
  expected="$(normalize_github_repo_url "$CLAUDE_MEMORY_SNAPSHOT_REPO")"
  verify_claude_private_snapshot_visibility || return 1
  verify_claude_private_snapshot_target_path || return 1
  origin="$(git -C "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE" remote get-url origin 2>/dev/null || true)"
  if [[ "$(normalize_github_repo_url "$origin")" != "$expected" ]]; then
    log "ERROR: Claude memory snapshot clone has unexpected origin: ${origin:-<none>}"
    return 1
  fi
}

prepare_claude_private_snapshot_repo() {
  if [[ "$CLAUDE_PRIVATE_SNAPSHOT_READY" == "true" ]]; then
    return 0
  fi
  verify_claude_private_snapshot_visibility || return 1
  verify_claude_private_snapshot_target_path || return 1
  if [[ ! -d "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE/.git" ]]; then
    mkdir -p "$(dirname "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE")"
    gh repo clone "$CLAUDE_MEMORY_SNAPSHOT_REPO" "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE" -- --quiet
  fi
  verify_claude_private_snapshot_repo || return 1
  if ! $DRY_RUN && git -C "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE" remote get-url origin >/dev/null 2>&1; then
    git -C "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE" pull --ff-only --quiet
  fi
  mkdir -p "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE/config/agents/claude/memory-snapshots"
  CLAUDE_PRIVATE_SNAPSHOT_READY=true
}

stage_claude_private_snapshot_file() {
  local src="$1" name="$2"
  [[ -f "$src" ]] || return 0
  if $DRY_RUN; then
    if [[ "$CLAUDE_PRIVATE_SNAPSHOT_DRY_RUN_LOGGED" != "true" ]]; then
      log "[dry-run] Would update private Claude memory snapshots in $CLAUDE_MEMORY_SNAPSHOT_REPO"
      CLAUDE_PRIVATE_SNAPSHOT_DRY_RUN_LOGGED=true
    fi
    return 0
  fi
  if [[ -z "$CLAUDE_PRIVATE_STAGE" ]]; then
    CLAUDE_PRIVATE_STAGE="$(mktemp -d)"
  fi
  mkdir -p "$CLAUDE_PRIVATE_STAGE"
  cp "$src" "$CLAUDE_PRIVATE_STAGE/$name"
  CLAUDE_PRIVATE_SNAPSHOT_STAGED=true
}

copy_claude_private_memory_dir() {
  local src="$1" prefix="${2:-}"
  [[ -d "$src" ]] || return 0
  local f base
  for f in "$src"/*.md; do
    [[ -f "$f" ]] || continue
    base="$(basename "$f")"
    stage_claude_private_snapshot_file "$f" "${prefix}${base}" || return 1
  done
}

copy_claude_private_file() {
  local src="$1" name="$2"
  stage_claude_private_snapshot_file "$src" "$name"
}

finalize_claude_private_snapshot_repo() {
  [[ "$CLAUDE_PRIVATE_SNAPSHOT_STAGED" == "true" ]] || return 0
  prepare_claude_private_snapshot_repo || return 1
  (
    cd "$CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE"
    rsync -a --delete "$CLAUDE_PRIVATE_STAGE/" config/agents/claude/memory-snapshots/
    find config/agents/claude/memory-snapshots -type f -print0 | sort -z | xargs -0 -r sha256sum > SNAPSHOT_MANIFEST.sha256
    git add SNAPSHOT_MANIFEST.sha256 config/agents/claude/memory-snapshots
    if git diff --cached --quiet; then
      log "Claude private memory snapshots already up to date"
      return 0
    fi
    git commit -m "chore: refresh Claude memory snapshots" -- \
      SNAPSHOT_MANIFEST.sha256 config/agents/claude/memory-snapshots
    git push
  )
}

# ── Snapshot agent memories ───────────────────────────────────────────
log "Snapshotting agent memories..."

# Hermes memories (#1777)
if [[ -f "${HOME}/.hermes/memories/MEMORY.md" ]]; then
  redact_copy "${HOME}/.hermes/memories/MEMORY.md" config/agents/hermes/memories/MEMORY.md.snapshot || fail_closed
  redact_copy "${HOME}/.hermes/memories/USER.md" config/agents/hermes/memories/USER.md.snapshot || fail_closed
fi

# Claude Code project memory (#1779) — private snapshot repo only.
# Owner decision E07: Claude memory snapshots are not written to this public
# checkout. They are copied to the private snapshot repository above; the public
# repo keeps only the live .claude/memory bridge surface.
CLAUDE_MEM="${HOME}/.claude/projects/-mnt-local-analysis-workspace-hub/memory"
if [[ -d "$CLAUDE_MEM" ]]; then
  copy_claude_private_memory_dir "$CLAUDE_MEM" || fail_closed
fi
CLAUDE_MEM_WED="${HOME}/.claude/projects/-mnt-local-analysis-workspace-hub-worldenergydata/memory"
if [[ -d "$CLAUDE_MEM_WED" ]]; then
  copy_claude_private_file "$CLAUDE_MEM_WED/MEMORY.md" worldenergydata-MEMORY.md || fail_closed
fi
finalize_claude_private_snapshot_repo || fail_closed

# Codex state (#1781). history.jsonl is raw prompt history: it is published
# only in redacted form (C20).
if [[ -d "${HOME}/.codex" ]]; then
  redact_copy "${HOME}/.codex/rules/default.rules" config/agents/codex/state-snapshots/default.rules || fail_closed
  redact_copy "${HOME}/.codex/history.jsonl" config/agents/codex/state-snapshots/history.jsonl || fail_closed
  redact_copy "${HOME}/.codex/session_index.jsonl" config/agents/codex/state-snapshots/session_index.jsonl || fail_closed
fi

# Gemini state (#1781)
if [[ -d "${HOME}/.gemini" ]]; then
  redact_copy "${HOME}/.gemini/state.json" config/agents/gemini/state-snapshots/state.json || fail_closed
  redact_copy "${HOME}/.gemini/projects.json" config/agents/gemini/state-snapshots/projects.json || fail_closed
fi

# ── Redact session-signals before staging ─────────────────────────────
REDACT_SCRIPT="${WORKSPACE_HUB}/scripts/cron/redact-session-signals.sh"
if [[ -x "$REDACT_SCRIPT" ]]; then
  log "Redacting session-signals..."
  bash "$REDACT_SCRIPT" 2>&1 || log "WARNING: session-signal redaction had errors"
fi

# ── Codename-redact client identifiers from learning state (#3097) ─────
# Defense-in-depth: the learning pipeline emits client names into committed
# state. Codename-redact them using a PRIVATE local map (the real names live
# only in the private aceengineer-strategy archive — never in this public repo).
# Provision per cron host: copy
#   aceengineer-strategy/pii-remediation/3097-2026-06-14/client-codename-map.yaml
# to $PII_CODENAME_MAP (default below). If absent, warn and retain the
# existing public redactor; no identifier gate runs at commit time.
PII_REDACTOR="${WORKSPACE_HUB}/scripts/legal/redact-client-pii.py"
if [[ -f "$PII_MAP" && -f "$PII_REDACTOR" ]]; then
  log "Codename-redacting client identifiers from learning state..."
  uv run python "$PII_REDACTOR" --map "$PII_MAP" --root "$WORKSPACE_HUB" \
    .claude/state/corrections .claude/state/patterns .claude/state/reflect-history \
    .claude/state/cc-insights .claude/state/candidates .claude/state/graduation .claude/state/trends \
    .claude/state/session-signals .claude/state/skill-eval-results \
    config/agents/codex/state-snapshots \
    config/agents/gemini/state-snapshots 2>&1 || log "WARNING: client redaction had errors"
else
  log "WARNING: PII codename map not found ($PII_MAP) — skipping optional client codename redaction"
fi

# ── Stage learning artifacts ──────────────────────────────────────────
log "Staging learning artifacts..."

# .claude/state/ directories (already excepted in .gitignore)
STATE_DIRS=(
  .claude/state/corrections/
  .claude/state/patterns/
  .claude/state/reflect-history/
  .claude/state/cc-insights/
  .claude/state/candidates/
  .claude/state/graduation/
  .claude/state/trends/
  .claude/state/session-signals/
  .claude/state/skill-eval-results/
)

STATE_FILES=(
  .claude/state/learned-patterns.json
  .claude/state/skill-scores.yaml
  .claude/state/cc-user-insights.yaml
  .claude/state/hermes-insights.yaml
  .claude/state/cross-agent-memory.yaml
  .claude/state/drift-summary.yaml
  .claude/state/portfolio-signals.yaml
  .claude/state/readiness-issues.md
  .claude/state/session-health.yaml
  .claude/state/correction-trend-meta.json
  .claude/state/correction-confidence-threshold.json
  .claude/state/skill-scope-classification.json
)

staged=0

for dir in "${STATE_DIRS[@]}"; do
  if [[ -d "$dir" ]]; then
    git add "$dir" 2>/dev/null && ((staged++)) || true
  fi
done

for file in "${STATE_FILES[@]}"; do
  if [[ -f "$file" ]]; then
    git add "$file" 2>/dev/null && ((staged++)) || true
  fi
done

# logs/orchestrator/ exports are raw session dumps with client names in commands —
# NOT learning artifacts. Skip staging them; they trigger legal deny-list (client references)
# and serve no purpose in the repo. (#1985)

# Agent memory snapshots (#1777, #1779, #1781)
for snap_dir in config/agents/hermes/memories config/agents/codex/state-snapshots config/agents/gemini/state-snapshots; do
  if [[ -d "$snap_dir" ]]; then
    git add "$snap_dir/" 2>/dev/null && ((staged++)) || true
  fi
done

# .gitignore itself (in case we just added exceptions)
git add .gitignore 2>/dev/null || true

log "Staged $staged artifact sources"

# ── Preserve existing staged snapshot redaction ──────────────────────
# Re-stage redacted output. Redaction failures still stop snapshot publication;
# the retired identifier/scanner gate is not invoked.
mapfile -d '' STAGED_FILES < <(git diff --cached --name-only --diff-filter=ACMR -z 2>/dev/null || true)
if (( ${#STAGED_FILES[@]} > 0 )); then
  if ! "${PY_RUN[@]}" "$PUBLIC_REDACTION" inplace "${STAGED_FILES[@]}"; then
    git reset -q HEAD -- . >/dev/null 2>&1 || true
    fail_closed
  fi
  git add -- "${STAGED_FILES[@]}" 2>/dev/null || true
fi

# ── Check if anything changed ─────────────────────────────────────────
if git diff --cached --quiet 2>/dev/null; then
  log "No changes to commit"
  exit 0
fi

# Show what would be committed
CHANGED=$(git diff --cached --stat 2>/dev/null | tail -1)
log "Changes: $CHANGED"

if $DRY_RUN; then
  log "[dry-run] Would commit the above changes"
  git diff --cached --name-only
  git reset HEAD -- . >/dev/null 2>&1 || true
  exit 0
fi

# ── Commit and push ──────────────────────────────────────────────────
DATE_STAMP=$(date +%Y-%m-%d)

if type -t git_safe_commit >/dev/null 2>&1; then
  git_safe_commit "chore(nightly): commit learning artifacts ${DATE_STAMP}"
  git_safe_push
else
  git commit -m "chore(nightly): commit learning artifacts ${DATE_STAMP}"
  git push 2>/dev/null || log "WARNING: git push failed — changes committed locally"
fi

log "Learning artifacts committed and pushed (${DATE_STAMP})"
