#!/usr/bin/env bash
# scope-repo-memory.sh — scaffold repo-scoped agent memory (epic #3084)
#
# Gives a repo its own .claude/memory/ so an agent working there starts from
# clean, on-topic context instead of inheriting the whole workspace-hub blob.
# Idempotent + no-clobber: never overwrites an existing repo's memory.
#
# Usage:
#   scope-repo-memory.sh <repo_path> [--force] [--dry-run]
#
# What it does (each step idempotent):
#   1. Create <repo>/.claude/memory/MEMORY.md from the template (skip if present).
#   2. Patch <repo>/.gitignore so a blanket claude-flow-era `memory/` rule does
#      not also ignore `.claude/memory/` (add negation; skip if already present).
#   3. Add a memory-precedence line to <repo>/CLAUDE.md if one is not present and
#      doing so keeps the file within the 20-line harness cap (else warn).
#
# Exit: 0 = success/no-op, 2 = bad args, 3 = repo path invalid.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TEMPLATE="${SCOPE_TEMPLATE:-${HUB_ROOT}/.claude/memory/_template-repo-memory/MEMORY.md}"
PRECEDENCE_MARKER="Memory: read THIS repo"
PRECEDENCE_LINE="> Memory: read THIS repo's \`.claude/memory/\` first; consult workspace-hub memory only for cross-repo concerns"

DRY_RUN=false
FORCE=false
REPO=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --force)   FORCE=true ;;
    -*) echo "unknown flag: $arg" >&2; exit 2 ;;
    *)  REPO="$arg" ;;
  esac
done

[[ -n "$REPO" ]] || { echo "usage: scope-repo-memory.sh <repo_path> [--force] [--dry-run]" >&2; exit 2; }
# Accept both a normal checkout (.git dir) and a linked worktree (.git file).
[[ -d "$REPO/.git" || -f "$REPO/.git" ]] || { echo "not a git repo: $REPO" >&2; exit 3; }

# Derive the canonical repo name from the origin URL, NOT basename($REPO) — the
# latter yields the worktree dir name (e.g. "wt-digitalmodel") when run in a worktree.
repo_name="$(basename -s .git "$(git -C "$REPO" remote get-url origin 2>/dev/null || echo "$REPO")")"

say() { echo "[scope-memory] $*"; }
act() { if $DRY_RUN; then echo "[dry-run] would: $*"; else eval "$2"; say "$1"; fi; }

# ── 1. repo-scoped MEMORY.md ────────────────────────────────────────────────
MEM_DIR="$REPO/.claude/memory"
MEM_FILE="$MEM_DIR/MEMORY.md"
if [[ -f "$MEM_FILE" && "$FORCE" != true ]]; then
  say "MEMORY.md already exists — skip (no clobber): $MEM_FILE"
else
  if $DRY_RUN; then
    echo "[dry-run] would create: $MEM_FILE (from template, REPO=$repo_name)"
  else
    mkdir -p "$MEM_DIR"
    sed "s/{{REPO}}/${repo_name}/g" "$TEMPLATE" > "$MEM_FILE"
    say "created $MEM_FILE"
  fi
fi

# ── 2. .gitignore negation ──────────────────────────────────────────────────
GI="$REPO/.gitignore"
if [[ -f "$GI" ]] && grep -qE '^\s*memory/\s*$|^\s*\.claude/memory' "$GI" && ! grep -qF '!.claude/memory/' "$GI"; then
  if $DRY_RUN; then
    echo "[dry-run] would patch .gitignore: add '!.claude/memory/' negation"
  else
    printf '\n# epic #3084: keep repo-scoped agent memory tracked despite blanket memory/ rule\n!.claude/memory/\n!.claude/memory/**\n' >> "$GI"
    say "patched .gitignore negation"
  fi
else
  say ".gitignore: no blanket memory/ conflict (or negation already present) — skip"
fi

# ── 3. CLAUDE.md precedence line ────────────────────────────────────────────
CM="$REPO/CLAUDE.md"
if [[ -f "$CM" ]]; then
  if grep -qF "$PRECEDENCE_MARKER" "$CM"; then
    say "CLAUDE.md already has memory-precedence line — skip"
  else
    lines="$(wc -l < "$CM")"
    if (( lines < 20 )); then
      if $DRY_RUN; then
        echo "[dry-run] would append memory-precedence line to CLAUDE.md (currently ${lines} lines)"
      else
        printf '%s\n' "$PRECEDENCE_LINE" >> "$CM"
        say "appended memory-precedence line to CLAUDE.md"
      fi
    else
      say "WARN: CLAUDE.md at ${lines} lines — no headroom under 20-line cap; add memory line manually or trim"
    fi
  fi
else
  if $DRY_RUN; then
    echo "[dry-run] would create minimal CLAUDE.md (no existing one) to activate scoping"
  else
    {
      printf '# %s\n' "$repo_name"
      printf '> Inherits workspace-hub/CLAUDE.md\n'
      printf '%s\n' "$PRECEDENCE_LINE"
    } > "$CM"
    say "created minimal CLAUDE.md to activate scoping"
  fi
fi

say "done: $REPO"
