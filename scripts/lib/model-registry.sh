#!/usr/bin/env bash
# Shared reader for config/agents/model-registry.yaml latest_models keys.
# Dependency-free (grep/sed only) so it works in hooks, cron, and minimal shells.
# Per behavior-contract.yaml > model_versioning: scripts MUST read model IDs from
# the registry instead of hardcoding them. (workspace-hub #3038)
#
# Usage:
#   source "$(git rev-parse --show-toplevel)/scripts/lib/model-registry.sh"
#   model="$(registry_model claude_primary)"          # -> claude-fable-5
#   model="$(registry_model openai_primary gpt-9.9)"  # with fallback default

_MODEL_REGISTRY_FILE="${MODEL_REGISTRY_FILE:-}"

_model_registry_path() {
  if [[ -n "$_MODEL_REGISTRY_FILE" && -f "$_MODEL_REGISTRY_FILE" ]]; then
    echo "$_MODEL_REGISTRY_FILE"; return 0
  fi
  local root
  root="$(git rev-parse --show-toplevel 2>/dev/null)" || root="${WORKSPACE_HUB:-/mnt/local-analysis/workspace-hub}"
  local candidate="${root}/config/agents/model-registry.yaml"
  [[ -f "$candidate" ]] || candidate="${WORKSPACE_HUB:-/mnt/local-analysis/workspace-hub}/config/agents/model-registry.yaml"
  echo "$candidate"
}

# registry_model <latest_models key> [fallback]
# Echoes the model id; falls back (and warns on stderr) if key/file missing.
registry_model() {
  local key="$1" fallback="${2:-}"
  local reg; reg="$(_model_registry_path)"
  local val=""
  if [[ -f "$reg" ]]; then
    # Match lines like:   claude_primary: "claude-fable-5"   # comment
    val="$(sed -n -E "s/^[[:space:]]+${key}:[[:space:]]*\"([^\"]+)\".*/\1/p" "$reg" | head -1)"
  fi
  if [[ -z "$val" ]]; then
    echo "[model-registry] WARN: key '${key}' not found in ${reg}; using fallback '${fallback}'" >&2
    val="$fallback"
  fi
  echo "$val"
}
