#!/usr/bin/env bash
# ABOUTME: Collect tool versions from all workstations and write env-parity snapshot.
# ABOUTME: Reads scripts/readiness/harness-config.yaml for machine connection details.
# Exit 0 = audit ran (drift in YAML); Exit 1 = operational failure (YAML write, local crash).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
CONFIG="$REPO_ROOT/scripts/readiness/harness-config.yaml"
OUTPUT="$REPO_ROOT/config/ai_agents/ai-tools-status.yaml"
NPM_PATH="\$HOME/.npm-global/bin:\$HOME/.local/bin:\$PATH"

TOOLS=(uv python3 claude codex gemini gh git node hermes gsd)

# ── helpers ─────────────────────────────────────────────────────────────────

die() { echo "ERROR: $*" >&2; exit 1; }

# Get a per-machine field from harness-config.yaml
machine_field() {
  local machine="$1" field="$2"
  # Extract the block for this machine, then find the field
  awk "/^  ${machine}:/{found=1; next} found && /^  [a-z]/{found=0} found && /^ *${field}:/{print; exit}" "$CONFIG" \
    | sed 's/.*:[[:space:]]*//' | tr -d '"' | tr -d "'" | tr -d ' '
}

# Collect tool versions from a remote host via SSH (explicit PATH)
collect_remote() {
  local target="$1"
  local cmd="export PATH=${NPM_PATH}; "
  for tool in "${TOOLS[@]}"; do
    cmd+="echo \"${tool}=\$(${tool} --version 2>/dev/null | head -1 || echo MISSING)\"; "
  done
  ssh -o ConnectTimeout=5 -o BatchMode=yes "$target" "$cmd" 2>/dev/null || true
}

# Collect tool versions locally
collect_local() {
  local epath
  epath="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
  for tool in "${TOOLS[@]}"; do
    local ver
    ver=$(PATH="$epath" "$tool" --version 2>/dev/null | head -1 || echo "MISSING")
    echo "${tool}=${ver}"
  done
}

# Extract semver X.Y.Z from a raw version string
extract_semver() {
  local raw="$1"
  echo "$raw" | grep -oP '\d+\.\d+\.\d+' | head -1 || true
}

major_ver() { echo "$1" | cut -d. -f1; }
minor_ver() { echo "$1" | cut -d. -f2; }
patch_ver()  { echo "$1" | cut -d. -f3; }

# ── parse workstation list ───────────────────────────────────────────────────

MACHINES=()
while IFS= read -r line; do
  if [[ "$line" =~ ^[[:space:]]{2}([a-z][a-z0-9_-]+):$ ]]; then
    MACHINES+=("${BASH_REMATCH[1]}")
  fi
done < <(sed -n '/^workstations:/,/^[a-zA-Z]/p' "$CONFIG")

[[ ${#MACHINES[@]} -eq 0 ]] && die "No workstations found in $CONFIG"

# ── collect versions per machine ────────────────────────────────────────────

declare -A MACHINE_REACHABLE
declare -A MACHINE_VERSIONS

for machine in "${MACHINES[@]}"; do
  linux_reachable=$(machine_field "$machine" "linux_reachable")
  ssh_tgt=$(machine_field "$machine" "ssh_target")
  tailscale_ip=$(machine_field "$machine" "tailscale_ip")

  if [[ "$linux_reachable" == "false" ]]; then
    MACHINE_REACHABLE["$machine"]="false"
    for tool in "${TOOLS[@]}"; do MACHINE_VERSIONS["${machine}:${tool}"]="UNREACHABLE"; done
    continue
  fi

  if [[ "$ssh_tgt" == "null" || -z "$ssh_tgt" ]]; then
    # Local machine
    MACHINE_REACHABLE["$machine"]="true"
    while IFS='=' read -r tool ver; do
      [[ -n "$tool" ]] && MACHINE_VERSIONS["${machine}:${tool}"]="$ver"
    done < <(collect_local)
  else
    # Remote via SSH — try alias then tailscale
    raw_out=$(collect_remote "$ssh_tgt")
    if [[ -z "$raw_out" && -n "$tailscale_ip" && "$tailscale_ip" != "null" ]]; then
      raw_out=$(collect_remote "$tailscale_ip")
    fi
    if [[ -z "$raw_out" ]]; then
      MACHINE_REACHABLE["$machine"]="false"
      for tool in "${TOOLS[@]}"; do MACHINE_VERSIONS["${machine}:${tool}"]="UNREACHABLE"; done
    else
      MACHINE_REACHABLE["$machine"]="true"
      while IFS='=' read -r tool ver; do
        [[ -n "$tool" ]] && MACHINE_VERSIONS["${machine}:${tool}"]="$ver"
      done <<< "$raw_out"
    fi
  fi
done

# ── compute drift ────────────────────────────────────────────────────────────

declare -A DRIFT_SEVERITY
declare -A DRIFT_NOTE

for tool in "${TOOLS[@]}"; do
  reachable_versions=()
  for machine in "${MACHINES[@]}"; do
    [[ "${MACHINE_REACHABLE[$machine]:-false}" == "true" ]] || continue
    reachable_versions+=("${MACHINE_VERSIONS[${machine}:${tool}]:-MISSING}")
  done

  if [[ ${#reachable_versions[@]} -lt 2 ]]; then
    DRIFT_SEVERITY["$tool"]="info"; DRIFT_NOTE["$tool"]="only 1 reachable machine"; continue
  fi

  has_missing=false
  for v in "${reachable_versions[@]}"; do
    [[ "$v" == "MISSING" || -z "$v" ]] && has_missing=true && break
  done
  if $has_missing; then
    DRIFT_SEVERITY["$tool"]="block"; DRIFT_NOTE["$tool"]="missing on at least one reachable machine"; continue
  fi

  max_sev="info"
  note="versions aligned"
  ref_sv=$(extract_semver "${reachable_versions[0]}")
  for v in "${reachable_versions[@]:1}"; do
    sv=$(extract_semver "$v")
    if [[ -z "$sv" || -z "$ref_sv" ]]; then
      max_sev="warn"; note="unparsable version string"; continue
    fi
    rm=$(major_ver "$ref_sv"); vm=$(major_ver "$sv")
    rn=$(minor_ver "$ref_sv"); vn=$(minor_ver "$sv")
    rp=$(patch_ver "$ref_sv"); vp=$(patch_ver "$sv")
    if [[ "$rm" != "$vm" ]]; then
      max_sev="block"; note="major version diff (${ref_sv} vs ${sv})"
    elif [[ "$rn" != "$vn" && "$max_sev" != "block" ]]; then
      max_sev="warn"; note="minor version diff (${ref_sv} vs ${sv})"
    elif [[ "$rp" != "$vp" && "$max_sev" == "info" ]]; then
      note="patch diff (${ref_sv} vs ${sv})"
    fi
  done
  DRIFT_SEVERITY["$tool"]="$max_sev"
  DRIFT_NOTE["$tool"]="$note"
done

# ── write YAML ───────────────────────────────────────────────────────────────

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
REACHABLE_COUNT=0
UNREACHABLE_MACHINES=()
for machine in "${MACHINES[@]}"; do
  if [[ "${MACHINE_REACHABLE[$machine]:-false}" == "true" ]]; then
    ((REACHABLE_COUNT++)) || true
  else
    UNREACHABLE_MACHINES+=("$machine")
  fi
done

UNREACHABLE_LIST=""
if [[ ${#UNREACHABLE_MACHINES[@]} -gt 0 ]]; then
  UNREACHABLE_LIST=$(printf '"%s",' "${UNREACHABLE_MACHINES[@]}" | sed 's/,$//')
fi

{
  echo "# Auto-generated by scripts/maintenance/ai-tools-status.sh"
  echo "last_updated: \"${TIMESTAMP}\""
  echo ""
  echo "collection_summary:"
  echo "  total_machines: ${#MACHINES[@]}"
  echo "  reachable: ${REACHABLE_COUNT}"
  echo "  unreachable: $(( ${#MACHINES[@]} - REACHABLE_COUNT ))"
  echo "  unreachable_machines: [${UNREACHABLE_LIST}]"
  echo ""
  echo "machines:"
  for machine in "${MACHINES[@]}"; do
    echo "  ${machine}:"
    echo "    reachable: ${MACHINE_REACHABLE[$machine]:-false}"
    echo "    tools:"
    for tool in "${TOOLS[@]}"; do
      raw="${MACHINE_VERSIONS[${machine}:${tool}]:-}"
      if [[ "$raw" == "UNREACHABLE" || -z "$raw" ]]; then
        echo "      ${tool}: {raw: null, semver: null, status: unreachable}"
      elif [[ "$raw" == "MISSING" ]]; then
        echo "      ${tool}: {raw: null, semver: null, status: missing}"
      else
        sv=$(extract_semver "$raw")
        echo "      ${tool}: {raw: \"${raw}\", semver: \"${sv:-null}\", status: ok}"
      fi
    done
  done
  echo ""
  echo "drift:"
  for tool in "${TOOLS[@]}"; do
    sev="${DRIFT_SEVERITY[$tool]:-info}"
    note="${DRIFT_NOTE[$tool]:-}"
    echo "  ${tool}:"
    echo "    severity: ${sev}"
    echo "    note: \"${note}\""
    echo "    machines:"
    for machine in "${MACHINES[@]}"; do
      [[ "${MACHINE_REACHABLE[$machine]:-false}" == "true" ]] || continue
      raw="${MACHINE_VERSIONS[${machine}:${tool}]:-}"
      [[ "$raw" == "UNREACHABLE" || "$raw" == "MISSING" || -z "$raw" ]] && raw=""
      sv=$(extract_semver "$raw" || true)
      echo "      ${machine}: \"${sv:-null}\""
    done
  done

  # ── working-tree drift for git-based tools (#1668 Phase 3) ───────────────
  echo ""
  echo "working_tree_drift:"
  echo "  description: \"Dirty file counts in git-based AI tools\""
  GIT_TOOL_DIRS=("hermes:~/.hermes/hermes-agent" "gstack:~/.claude/skills/gstack")
  for entry in "${GIT_TOOL_DIRS[@]}"; do
    local_tool="${entry%%:*}"
    local_dir="${entry##*:}"
    echo "  ${local_tool}:"
    echo "    tool_dir: \"${local_dir}\""
    echo "    machines:"
    for machine in "${MACHINES[@]}"; do
      [[ "${MACHINE_REACHABLE[$machine]:-false}" == "true" ]] || continue
      local_ssh=$(machine_field "$machine" "ssh_target")
      if [[ "$local_ssh" == "null" || -z "$local_ssh" ]]; then
        real_dir="${local_dir/#~/$HOME}"
        if [[ -d "$real_dir/.git" ]]; then
          dirty_count=$(git -C "$real_dir" status --porcelain 2>/dev/null | wc -l)
          echo "      ${machine}: {dirty_files: ${dirty_count}, reachable: true}"
        else
          echo "      ${machine}: {dirty_files: null, reachable: true, note: \"not installed\"}"
        fi
      else
        # Remote: check .git exists first, THEN count dirty files
        remote_count=$(ssh -o ConnectTimeout=5 -o BatchMode=yes "$local_ssh" \
          "dir=\"${local_dir/#~/'\$HOME'}\"; dir=\$(eval echo \"\$dir\"); [ -d \"\$dir/.git\" ] && git -C \"\$dir\" status --porcelain 2>/dev/null | wc -l || echo -1" 2>/dev/null || echo "-1")
        if [[ "$remote_count" == "-1" ]]; then
          echo "      ${machine}: {dirty_files: null, reachable: true, note: \"not installed\"}"
        else
          echo "      ${machine}: {dirty_files: ${remote_count}, reachable: true}"
        fi
      fi
    done
  done
} > "$OUTPUT" || die "Failed to write $OUTPUT"

echo "✔ ai-tools-status.yaml written: $OUTPUT"
echo "  Machines: ${#MACHINES[@]} total, ${REACHABLE_COUNT} reachable"
echo "  Drift summary:"
for tool in "${TOOLS[@]}"; do
  sev="${DRIFT_SEVERITY[$tool]:-info}"
  [[ "$sev" != "info" ]] && echo "    ${sev^^}: ${tool} — ${DRIFT_NOTE[$tool]:-}"
done
echo "  Done."
