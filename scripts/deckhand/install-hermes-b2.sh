#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/deckhand/install-hermes-b2.sh [--apply]

Dry-run by default:
  - checks Hermes B2 patch hunks against ~/.hermes/hermes-agent
  - prints the shim install actions it would take

With --apply:
  - symlinks Deckhand shims into ~/.hermes/deckhand/shims
  - chmods shims executable
  - applies patches to ~/.hermes/hermes-agent after drift checks pass
EOF
}

apply=0
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
elif [[ "${1:-}" == "--apply" ]]; then
  apply=1
elif [[ $# -gt 0 ]]; then
  usage >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "$script_dir/../.." && pwd -P)"
shim_src="$repo_root/scripts/deckhand/shims"
shim_dst="${HOME}/.hermes/deckhand/shims"
hermes_tree="${HERMES_AGENT_TREE:-${HOME}/.hermes/hermes-agent}"
patch_dir="$repo_root/patches/hermes"

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "missing required file: $path" >&2
    exit 1
  fi
}

check_patch() {
  local patch_file="$1"
  local patch_name
  patch_name="$(basename "$patch_file")"
  if [[ ! -d "$hermes_tree" ]]; then
    echo "DRIFT-CHECK FAIL $patch_name: Hermes tree not found at $hermes_tree" >&2
    return 1
  fi
  if git -C "$hermes_tree" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$hermes_tree" apply --check "$patch_file"
  else
    patch -d "$hermes_tree" -p1 --dry-run --silent < "$patch_file"
  fi
}

apply_patch_file() {
  local patch_file="$1"
  if git -C "$hermes_tree" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$hermes_tree" apply "$patch_file"
  else
    patch -d "$hermes_tree" -p1 < "$patch_file"
  fi
}

for tool in git gh hub; do
  require_file "$shim_src/$tool"
done
for patch_file in "$patch_dir"/*.patch; do
  require_file "$patch_file"
done

echo "Deckhand B2 install mode: $([[ "$apply" == 1 ]] && echo apply || echo dry-run)"
echo "Workspace: $repo_root"
echo "Hermes tree: $hermes_tree"
echo "Shim destination: $shim_dst"

echo
echo "Checking Hermes patch drift..."
for patch_file in "$patch_dir"/*.patch; do
  echo "  check $(basename "$patch_file")"
  check_patch "$patch_file"
done

echo
if [[ "$apply" == 1 ]]; then
  mkdir -p "$shim_dst"
  for tool in git gh hub; do
    ln -sfn "$shim_src/$tool" "$shim_dst/$tool"
    chmod +x "$shim_src/$tool"
    chmod +x "$shim_dst/$tool"
    echo "installed shim: $shim_dst/$tool -> $shim_src/$tool"
  done

  for patch_file in "$patch_dir"/*.patch; do
    echo "applying $(basename "$patch_file")"
    apply_patch_file "$patch_file"
  done
else
  echo "Dry-run only. Would symlink:"
  for tool in git gh hub; do
    echo "  $shim_dst/$tool -> $shim_src/$tool"
  done
  echo "Dry-run only. Would apply:"
  for patch_file in "$patch_dir"/*.patch; do
    echo "  $(basename "$patch_file")"
  done
fi

cat <<EOF

Post-install validation steps:
  1. Restart Hermes gateway so tools/environments/local.py is reloaded.
  2. From a scoped Hermes DM, run: /scope
  3. In a Hermes terminal, run: command -v git && command -v gh
     Expected: both resolve under ${HOME}/.hermes/deckhand/shims.
  4. In the same scoped terminal, run: gh api user -q .login
     Expected: the scoped PAT identity, not the ambient owner.
  5. Run an allowed read: gh repo view vamseeachanta/llm-wiki-acma --json nameWithOwner
  6. Run an outside-scope negative read and confirm access is denied.
  7. Only after those pass, run a throwaway branch push smoke in the scoped repo.
EOF
