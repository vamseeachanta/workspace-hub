#!/usr/bin/env bash
# Guard: every JS workspace with a package.json that declares "workspaces"
# or has a pnpm-workspace.yaml must have a committed lockfile.
# Triggered from pre-commit hook. See #1513.

set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"

errors=0

# Find workspace-root package.json files (contain "workspaces" key or have pnpm-workspace.yaml sibling)
while IFS= read -r pkg; do
  dir="$(dirname "$pkg")"
  rel="$(realpath --relative-to="$REPO_ROOT" "$dir")"

  has_lockfile=false
  for lf in package-lock.json pnpm-lock.yaml yarn.lock; do
    if [[ -f "$dir/$lf" ]]; then
      has_lockfile=true
      break
    fi
  done

  if [[ "$has_lockfile" == false ]]; then
    echo "ERROR: JS workspace '$rel' has no committed lockfile (package-lock.json, pnpm-lock.yaml, or yarn.lock)" >&2
    errors=$((errors + 1))
  fi
done < <(git ls-files -- '*/package.json' 'package.json' | while IFS= read -r f; do
  dir="$(dirname "$REPO_ROOT/$f")"
  # Check if it's a workspace root (has workspaces field or pnpm-workspace.yaml)
  if grep -q '"workspaces"' "$REPO_ROOT/$f" 2>/dev/null || [[ -f "$dir/pnpm-workspace.yaml" ]]; then
    echo "$REPO_ROOT/$f"
  fi
done)

if [[ $errors -gt 0 ]]; then
  echo "Commit lockfiles to ensure reproducible installs. See issue #1513." >&2
  exit 1
fi

exit 0
