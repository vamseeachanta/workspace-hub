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

# ── Snapshot agent memories ───────────────────────────────────────────
log "Snapshotting agent memories..."

# Hermes memories (#1777)
if [[ -f "${HOME}/.hermes/memories/MEMORY.md" ]]; then
  mkdir -p config/agents/hermes/memories
  cp "${HOME}/.hermes/memories/MEMORY.md" config/agents/hermes/memories/MEMORY.md.snapshot
  cp "${HOME}/.hermes/memories/USER.md" config/agents/hermes/memories/USER.md.snapshot 2>/dev/null || true
fi

# Claude Code project memory (#1779)
CLAUDE_MEM="${HOME}/.claude/projects/-mnt-local-analysis-workspace-hub/memory"
if [[ -d "$CLAUDE_MEM" ]]; then
  mkdir -p config/agents/claude/memory-snapshots
  cp "$CLAUDE_MEM"/*.md config/agents/claude/memory-snapshots/ 2>/dev/null || true
fi
CLAUDE_MEM_WED="${HOME}/.claude/projects/-mnt-local-analysis-workspace-hub-worldenergydata/memory"
if [[ -d "$CLAUDE_MEM_WED" ]]; then
  cp "$CLAUDE_MEM_WED/MEMORY.md" config/agents/claude/memory-snapshots/worldenergydata-MEMORY.md 2>/dev/null || true
fi

# Codex state (#1781)
if [[ -d "${HOME}/.codex" ]]; then
  mkdir -p config/agents/codex/state-snapshots
  cp "${HOME}/.codex/rules/default.rules" config/agents/codex/state-snapshots/ 2>/dev/null || true
  cp "${HOME}/.codex/history.jsonl" config/agents/codex/state-snapshots/ 2>/dev/null || true
  cp "${HOME}/.codex/session_index.jsonl" config/agents/codex/state-snapshots/ 2>/dev/null || true
fi

# Gemini state (#1781)
if [[ -d "${HOME}/.gemini" ]]; then
  mkdir -p config/agents/gemini/state-snapshots
  cp "${HOME}/.gemini/state.json" config/agents/gemini/state-snapshots/ 2>/dev/null || true
  cp "${HOME}/.gemini/projects.json" config/agents/gemini/state-snapshots/ 2>/dev/null || true
fi

# ── Redact session-signals before staging ─────────────────────────────
REDACT_SCRIPT="${WORKSPACE_HUB}/scripts/cron/redact-session-signals.sh"
if [[ -x "$REDACT_SCRIPT" ]]; then
  log "Redacting session-signals..."
  bash "$REDACT_SCRIPT" 2>&1 || log "WARNING: session-signal redaction had errors"
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
