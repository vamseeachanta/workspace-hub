#!/usr/bin/env bash
# generate_provider_adapters.sh — Create .codex/ and .gemini/ provider adapters
# at workspace-hub root and propagate skills symlinks to all submodule repos.
# Usage: bash scripts/operations/compliance/generate_provider_adapters.sh [--dry-run]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PROVIDERS=("codex" "gemini")
DRY_RUN=false

[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

log() { printf "  %s\n" "$*"; }
log_ok()   { printf "  OK   %s\n" "$*"; }
log_add()  { printf "  ADD  %s\n" "$*"; }
log_skip() { printf "  SKIP %s\n" "$*"; }
log_fail() { printf "  FAIL %s\n" "$*"; }

# --- Hub-level adapter creation ---
create_hub_adapters() {
  for provider in "${PROVIDERS[@]}"; do
    local dir="$HUB_ROOT/.$provider"
    local link="$dir/skills"
    local target="../.claude/skills"

    if [[ "$DRY_RUN" == "true" ]]; then
      log_skip "DRY-RUN: would ensure $dir/skills -> $target"
      continue
    fi

    mkdir -p "$dir"

    if [[ -L "$link" ]]; then
      log_ok "$dir/skills (symlink exists)"
    else
      ln -sf "$target" "$link"
      log_add "$dir/skills -> $target"
    fi
  done
}

# --- Submodule adapter propagation ---
create_submodule_adapters() {
  local submodules
  submodules=$(git -C "$HUB_ROOT" submodule foreach --quiet 'echo $name' 2>/dev/null)

  local linked=0 skipped=0

  for repo in $submodules; do
    local repo_dir="$HUB_ROOT/$repo"
    [[ ! -d "$repo_dir" ]] && log_skip "$repo (dir absent)" && continue

    for provider in "${PROVIDERS[@]}"; do
      local adapter_dir="$repo_dir/.$provider"
      local link="$adapter_dir/skills"
      local target="../../.claude/skills"

      if [[ "$DRY_RUN" == "true" ]]; then
        if [[ -L "$link" ]]; then
          log_skip "DRY-RUN: $repo/.$provider/skills (exists)"
        else
          log_add "DRY-RUN: would create $repo/.$provider/skills -> $target"
        fi
        continue
      fi

      mkdir -p "$adapter_dir"
      if [[ -L "$link" ]]; then
        log_ok "$repo/.$provider/skills (exists)"
        skipped=$((skipped + 1))
      else
        ln -sf "$target" "$link"
        log_add "$repo/.$provider/skills -> $target"
        linked=$((linked + 1))
      fi
    done
  done

  if [[ "$DRY_RUN" == "false" ]]; then
    printf "\nSubmodule adapters: %d created, %d already present\n" "$linked" "$skipped"
  fi
}

main() {
  printf "Provider adapter generation (hub: %s)\n" "$HUB_ROOT"
  [[ "$DRY_RUN" == "true" ]] && printf "DRY-RUN — no changes will be made\n"
  echo ""

  printf "Hub adapters:\n"
  create_hub_adapters

  echo ""
  printf "Submodule adapters:\n"
  create_submodule_adapters

  echo ""
  printf "Done.\n"
}

main "$@"
