#!/usr/bin/env bash
# install-all-hooks.sh — idempotent git hook installer (WRK-312)
# Copies all scripts/hooks/* to .git/hooks/ and makes them executable.
# Run once per machine to bootstrap; post-merge/post-rewrite keep hooks
# current on every subsequent git pull (merge or rebase).
#
# Usage:
#   bash scripts/setup/install-all-hooks.sh           # verbose
#   bash scripts/setup/install-all-hooks.sh --quiet   # silent (used by hooks)
#
# Platform: bash required (Linux, macOS, Git Bash / MINGW64 on Windows)
# PowerShell is NOT supported.
set -euo pipefail

QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "install-all-hooks: must be run inside a git repository" >&2
  exit 2
}

HOOKS_SRC="${REPO_ROOT}/scripts/hooks"
HOOKS_DST="${REPO_ROOT}/.git/hooks"

[[ -d "$HOOKS_SRC" ]] || { echo "install-all-hooks: $HOOKS_SRC not found" >&2; exit 2; }
mkdir -p "$HOOKS_DST"

installed=0
skipped=0

for src in "$HOOKS_SRC"/*; do
  [[ -f "$src" ]] || continue
  name="$(basename "$src")"
  dst="${HOOKS_DST}/${name}"

  # Skip if already identical regular file (avoid unnecessary mtime changes).
  # Use -L on cmp to read through symlinks for content comparison, but only
  # skip when dst is a plain file — symlinks must always be replaced.
  if [[ -f "$dst" ]] && [[ ! -L "$dst" ]] && cmp -s "$src" "$dst"; then
    skipped=$((skipped + 1))
    continue
  fi

  # Remove dst first so symlinks are replaced with regular files, not written through.
  rm -f "$dst"
  cp "$src" "$dst"
  chmod +x "$dst"
  installed=$((installed + 1))
  [[ "$QUIET" -eq 0 ]] && echo "  installed: $name"
done

[[ "$QUIET" -eq 0 ]] && echo "install-all-hooks: ${installed} installed, ${skipped} unchanged"
