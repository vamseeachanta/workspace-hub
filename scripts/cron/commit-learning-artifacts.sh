#!/usr/bin/env bash
# commit-learning-artifacts.sh — Git-add + commit all learning state that gitignore allows
#
# Called at the end of comprehensive-learning-nightly.sh to ensure
# corrections, patterns, insights, and cross-agent state survive machine loss.
#
# Usage: bash scripts/cron/commit-learning-artifacts.sh [--dry-run]
# Cron:  Called by comprehensive-learning-nightly.sh (last step)
#
# Safety: runs legal-sanity-scan --diff-only before committing.
# If legal scan finds violations, skips commit and logs warning.

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
# is not copied at all. If the redactor cannot load -- no private deny list
# (WORKSPACE_HUB_DENY_LIST), a missing rules file, a named map that is absent
# -- nothing is snapshotted and nothing is committed.
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

# ── Snapshot agent memories ───────────────────────────────────────────
log "Snapshotting agent memories..."

# Hermes memories (#1777)
if [[ -f "${HOME}/.hermes/memories/MEMORY.md" ]]; then
  redact_copy "${HOME}/.hermes/memories/MEMORY.md" config/agents/hermes/memories/MEMORY.md.snapshot || fail_closed
  redact_copy "${HOME}/.hermes/memories/USER.md" config/agents/hermes/memories/USER.md.snapshot || fail_closed
fi

# Claude Code project memory (#1779) — PII-filtered snapshot (#3073).
# project_*.md (engagement-specific) is NEVER copied to the public repo; the
# helper also self-heals any already-present project_*.md. See the helper header.
CLAUDE_MEM="${HOME}/.claude/projects/-mnt-local-analysis-workspace-hub/memory"
if [[ -d "$CLAUDE_MEM" ]]; then
  _wh_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  # shellcheck source=scripts/cron/lib/pii-safe-memory-snapshot.sh
  source "$_wh_root/scripts/cron/lib/pii-safe-memory-snapshot.sh"
  pii_safe_snapshot "$CLAUDE_MEM" config/agents/claude/memory-snapshots "$_wh_root/.legal-deny-list.yaml" || fail_closed
fi
CLAUDE_MEM_WED="${HOME}/.claude/projects/-mnt-local-analysis-workspace-hub-worldenergydata/memory"
if [[ -d "$CLAUDE_MEM_WED" ]]; then
  redact_copy "$CLAUDE_MEM_WED/MEMORY.md" config/agents/claude/memory-snapshots/worldenergydata-MEMORY.md || fail_closed
fi

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
# to $PII_CODENAME_MAP (default below). If absent, warn — the #3099 legal scan
# is the hard backstop gate.
PII_REDACTOR="${WORKSPACE_HUB}/scripts/legal/redact-client-pii.py"
if [[ -f "$PII_MAP" && -f "$PII_REDACTOR" ]]; then
  log "Codename-redacting client identifiers from learning state..."
  uv run python "$PII_REDACTOR" --map "$PII_MAP" --root "$WORKSPACE_HUB" \
    .claude/state/corrections .claude/state/patterns .claude/state/reflect-history \
    .claude/state/cc-insights .claude/state/candidates .claude/state/graduation .claude/state/trends \
    .claude/state/session-signals .claude/state/skill-eval-results \
    config/agents/claude/memory-snapshots config/agents/codex/state-snapshots \
    config/agents/gemini/state-snapshots 2>&1 || log "WARNING: client redaction had errors"
else
  log "WARNING: PII codename map not found ($PII_MAP) — skipping client redaction (#3099 legal scan is the backstop)"
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
for snap_dir in config/agents/hermes/memories config/agents/claude/memory-snapshots config/agents/codex/state-snapshots config/agents/gemini/state-snapshots; do
  if [[ -d "$snap_dir" ]]; then
    git add "$snap_dir/" 2>/dev/null && ((staged++)) || true
  fi
done

# .gitignore itself (in case we just added exceptions)
git add .gitignore 2>/dev/null || true

log "Staged $staged artifact sources"

# ── C20: redact everything staged, then gate it ───────────────────────
# The learning pipeline writes client names into state files too. Redact every
# staged file with the same Redactor, re-stage, and run the identifier gate on
# the staged content (names in file PATHS included). Any failure: unstage and
# stop -- a stale public snapshot is harmless, a published name is not.
mapfile -d '' STAGED_FILES < <(git diff --cached --name-only --diff-filter=ACMR -z 2>/dev/null || true)
if (( ${#STAGED_FILES[@]} > 0 )); then
  if ! "${PY_RUN[@]}" "$PUBLIC_REDACTION" inplace "${STAGED_FILES[@]}"; then
    git reset -q HEAD -- . >/dev/null 2>&1 || true
    fail_closed
  fi
  git add -- "${STAGED_FILES[@]}" 2>/dev/null || true
  if ! "${PY_RUN[@]}" "${WORKSPACE_HUB}/scripts/legal/check_identifiers.py"; then
    log "ERROR: the identifier gate failed on the staged learning artifacts -- nothing committed (C20)"
    git reset -q HEAD -- . >/dev/null 2>&1 || true
    exit 1
  fi
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

# ── Legal scan gate ───────────────────────────────────────────────────
LEGAL_SCAN="scripts/legal/legal-sanity-scan.sh"
if [[ -x "$LEGAL_SCAN" ]]; then
  log "Running legal scan on staged changes..."
  if ! bash "$LEGAL_SCAN" --diff-only 2>&1; then
    log "WARNING: Legal scan found violations — skipping commit"
    log "Run 'bash $LEGAL_SCAN --diff-only' manually to review"
    git reset HEAD -- . >/dev/null 2>&1 || true
    exit 1
  fi
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
