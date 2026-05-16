#!/usr/bin/env bash
# install-pre-commit-hook-cross-repo.sh — propagate the conflict-marker hook
# across all tier-1 repos.
#
# Issue: workspace-hub#2722.
#
# Reads the manifest at $WS_ROOT/scripts/agents/tier1-repos.sh, then for each
# sibling repo:
#   1. Vendors a copy of scripts/enforcement/check-no-conflict-markers.sh.
#   2. Resolves the hooks directory via `git rev-parse --git-common-dir` so
#      git-worktree siblings (where `.git` is a file) work correctly.
#   3. Creates a minimal pre-commit stub if missing (with REPO_ROOT defined
#      in the prologue — required by the inserted wiring block).
#   4. Idempotently wires the check into pre-commit BEFORE the final `exit 0`.
#   5. Refuses to overwrite uncommitted local changes (dirty-sibling skip).
#
# Path resolution: $WS_ROOT/../$repo (single deterministic form per Claude r1
# finding #5). Skips repos that don't exist at that path with a notice.

set -uo pipefail

log() { echo "[install-pre-commit-hook-cross-repo] $*"; }

WS_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CANONICAL="$WS_ROOT/scripts/enforcement/check-no-conflict-markers.sh"
MANIFEST="$WS_ROOT/scripts/agents/tier1-repos.sh"

if [[ ! -f "$CANONICAL" ]]; then
  log "ERROR: canonical script not found at $CANONICAL"
  exit 2
fi
if [[ ! -f "$MANIFEST" ]]; then
  log "ERROR: manifest not found at $MANIFEST"
  exit 2
fi

# shellcheck disable=SC1090
source "$MANIFEST"

WIRING_SENTINEL="check-no-conflict-markers"
WIRING_BLOCK='
# ── Conflict-marker check (workspace-hub#2722) ──
CHECK="${REPO_ROOT:?REPO_ROOT must be set in pre-commit prologue}/scripts/enforcement/check-no-conflict-markers.sh"
if [[ -f "$CHECK" ]]; then
  bash "$CHECK" || exit 1
fi'

for repo in "${TIER1_REPOS[@]}"; do
  # Skip self — workspace-hub gets its own hook via scripts/enforcement/install-hooks.sh.
  if [[ "$repo" == "workspace-hub" ]]; then
    continue
  fi

  REPO_PATH="$WS_ROOT/../$repo"
  if [[ ! -e "$REPO_PATH/.git" ]]; then
    log "skip: $repo (not present at $REPO_PATH)"
    continue
  fi

  # Resolve hooks dir via git-common-dir (worktree-safe).
  GIT_COMMON_DIR="$(git -C "$REPO_PATH" rev-parse --git-common-dir 2>/dev/null)"
  if [[ -z "$GIT_COMMON_DIR" ]]; then
    log "skip: $repo (cannot resolve git-common-dir)"
    continue
  fi
  # git-common-dir may be relative to repo root
  if [[ "$GIT_COMMON_DIR" != /* ]]; then
    GIT_COMMON_DIR="$REPO_PATH/$GIT_COMMON_DIR"
  fi
  HOOKS_DIR="$GIT_COMMON_DIR/hooks"
  mkdir -p "$HOOKS_DIR"

  # Dirty-sibling check: refuse to overwrite uncommitted local changes
  # in either the enforcement scripts or the hooks dir staging area.
  # (Hooks-dir contents are not git-tracked, but staged scripts/enforcement/ is.)
  if ! git -C "$REPO_PATH" diff --quiet -- scripts/enforcement/ 2>/dev/null \
     || ! git -C "$REPO_PATH" diff --cached --quiet -- scripts/enforcement/ 2>/dev/null; then
    log "WARN: $repo has uncommitted/staged changes in scripts/enforcement/; skipping (dirty)"
    continue
  fi

  # Vendor the canonical script.
  VENDORED_DIR="$REPO_PATH/scripts/enforcement"
  mkdir -p "$VENDORED_DIR"
  VENDORED="$VENDORED_DIR/check-no-conflict-markers.sh"
  cp "$CANONICAL" "$VENDORED"
  chmod +x "$VENDORED"

  # Create or extend pre-commit hook.
  PRE_COMMIT="$HOOKS_DIR/pre-commit"
  if [[ ! -f "$PRE_COMMIT" ]]; then
    cat > "$PRE_COMMIT" <<'STUB'
#!/usr/bin/env bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
exit 0
STUB
    chmod +x "$PRE_COMMIT"
  fi

  if grep -qF "$WIRING_SENTINEL" "$PRE_COMMIT"; then
    log "OK: $repo already wired"
    continue
  fi

  # Linux-gated sed -i for in-place insertion before `exit 0`.
  # Non-Linux: emit manual-install instructions instead (per Claude r1 #6).
  if [[ "$(uname -s)" == "Linux" ]]; then
    # Use awk for clarity (sed -i with multiline insert is fragile across distros).
    tmpfile="$(mktemp)"
    awk -v block="$WIRING_BLOCK" '
      /^exit 0$/ && !done {
        print block
        print
        done = 1
        next
      }
      { print }
      END {
        if (!done) {
          # No `exit 0` found — append the block + a fresh exit 0.
          print block
          print "exit 0"
        }
      }
    ' "$PRE_COMMIT" > "$tmpfile"
    mv "$tmpfile" "$PRE_COMMIT"
    chmod +x "$PRE_COMMIT"
    log "OK: $repo wired (vendored + hook)"
  else
    log "WARN: non-Linux platform ($(uname -s)) — auto-wiring skipped for $repo"
    log "      Add the following block to $PRE_COMMIT before the final 'exit 0':"
    printf '%s\n' "$WIRING_BLOCK" | sed 's/^/        /'
  fi
done
