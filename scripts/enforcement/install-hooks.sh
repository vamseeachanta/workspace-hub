#!/usr/bin/env bash
# install-hooks.sh — Install enforcement environment and wire learning pipeline into git hooks
# Issue: #2027
#
# Idempotent: safe to run multiple times.
#
# What it does:
# 1. Copies enforcement-env.sh to .git/hooks/enforcement-env
# 2. Wires enforcement-env sourcing into pre-commit (if not already present)
# 3. Wires stage-prompt drift guard into pre-push (if not already present)
# 4. Wires post-commit-learnings.sh into post-commit (fixes dead code after exit 0)
#
# Usage:
#   bash scripts/enforcement/install-hooks.sh
#   bash scripts/enforcement/install-hooks.sh --dry-run

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
  esac
done

log() { echo "[install-hooks] $1"; }

# ── Step 1: Install enforcement-env ─────────────────────────────────────
ENFORCEMENT_SRC="${REPO_ROOT}/scripts/enforcement/enforcement-env.sh"
ENFORCEMENT_DST="${REPO_ROOT}/.git/hooks/enforcement-env"

if [[ -f "$ENFORCEMENT_SRC" ]]; then
  if [[ "$DRY_RUN" == "1" ]]; then
    log "DRY-RUN: Would copy enforcement-env.sh -> .git/hooks/enforcement-env"
  else
    cp "$ENFORCEMENT_SRC" "$ENFORCEMENT_DST"
    chmod 644 "$ENFORCEMENT_DST"
    log "OK: Installed enforcement-env to .git/hooks/"
  fi
else
  log "SKIP: enforcement-env.sh not found at ${ENFORCEMENT_SRC}"
fi

# ── Step 2: Wire enforcement-env into pre-commit ────────────────────────
PRE_COMMIT="${REPO_ROOT}/.git/hooks/pre-commit"

if [[ -f "$PRE_COMMIT" ]]; then
  if grep -q "enforcement-env" "$PRE_COMMIT" 2>/dev/null; then
    log "OK: enforcement-env already wired into pre-commit"
  else
    if [[ "$DRY_RUN" == "1" ]]; then
      log "DRY-RUN: Would add enforcement-env sourcing to pre-commit"
    else
      # Insert after the PATH export line
      sed -i '/^export PATH=/a\
\
# Source enforcement environment (#2027)\
ENFORCEMENT_ENV="${REPO_ROOT}/.git/hooks/enforcement-env"\
if [[ -f "${ENFORCEMENT_ENV}" ]]; then\
  source "${ENFORCEMENT_ENV}"\
fi' "$PRE_COMMIT"
      log "OK: Wired enforcement-env into pre-commit"
    fi
  fi
else
  log "SKIP: pre-commit hook not found"
fi

# ── Step 3: Wire stage prompt drift guard into pre-push ─────────────────
PRE_PUSH="${REPO_ROOT}/.git/hooks/pre-push"

if [[ -f "$PRE_PUSH" ]]; then
  if grep -q "require-stage-prompt-drift.sh" "$PRE_PUSH" 2>/dev/null; then
    log "OK: stage prompt drift guard already wired into pre-push"
  else
    if [[ "$DRY_RUN" == "1" ]]; then
      log "DRY-RUN: Would wire stage prompt drift guard into pre-push"
    else
      cat >> "$PRE_PUSH" <<'EOF'

# ── Stage prompt drift guard (installed by install-hooks.sh) ─────────────
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STAGE_PROMPT_DRIFT_GATE="${REPO_ROOT}/scripts/enforcement/require-stage-prompt-drift.sh"
if [[ -f "$STAGE_PROMPT_DRIFT_GATE" ]]; then
  bash "$STAGE_PROMPT_DRIFT_GATE" || exit $?
fi
EOF
      chmod +x "$PRE_PUSH"
      log "OK: Wired stage prompt drift guard into pre-push"
    fi
  fi
else
  log "SKIP: pre-push hook not found"
fi

# ── Step 4: Wire learning pipeline into post-commit ─────────────────────
POST_COMMIT="${REPO_ROOT}/.git/hooks/post-commit"

if [[ -f "$POST_COMMIT" ]]; then
  if grep -q "post-commit-learnings" "$POST_COMMIT" 2>/dev/null; then
    log "OK: learning pipeline already wired into post-commit"
  else
    if [[ "$DRY_RUN" == "1" ]]; then
      log "DRY-RUN: Would wire learning pipeline into post-commit (fix dead code)"
    else
      # Remove the dead code after exit 0 and replace with learning pipeline call
      # The post-commit has: exit 0 \n\n# Track skill...\nbash scripts/hooks/...
      # We need to replace that with: learning pipeline call \n exit 0

      # Create a temporary file with the fix
      tmpfile="$(mktemp)"

      # Process the file: find the "exit 0" that precedes dead code, replace it
      awk '
        /^exit 0$/ {
          # Check if next lines are dead code (track-skill-patches)
          if (!printed_learning) {
            print ""
            print "# ── Post-commit learning pipeline (#2027) ────────────────────────────"
            print "REPO_ROOT=\"$(git rev-parse --show-toplevel 2>/dev/null || pwd)\""
            print "bash \"${REPO_ROOT}/scripts/hooks/post-commit-learnings.sh\" || true"
            print ""
            print "exit 0"
            printed_learning = 1
            skip_dead_code = 1
            next
          }
          print
          next
        }
        skip_dead_code && /^$/ { next }
        skip_dead_code && /^#/ { next }
        skip_dead_code && /^bash/ { next }
        skip_dead_code { skip_dead_code = 0 }
        !skip_dead_code { print }
      ' "$POST_COMMIT" > "$tmpfile"

      cp "$tmpfile" "$POST_COMMIT"
      chmod +x "$POST_COMMIT"
      rm -f "$tmpfile"
      log "OK: Wired learning pipeline into post-commit (fixed dead code)"
    fi
  fi
else
  log "SKIP: post-commit hook not found"
fi

# ── Summary ─────────────────────────────────────────────────────────────
log ""
log "Enforcement hook chain:"
log "  pre-commit -> enforcement-env -> plan-approval-gate"
log "  pre-push -> review-gate -> stage-prompt-drift-gate -> repo/test gates"
log "  post-commit -> auto-push -> learning pipeline -> extract-learnings"
log ""
if [[ "$DRY_RUN" == "1" ]]; then
  log "DRY-RUN mode — no changes made. Remove --dry-run to apply."
fi
