#!/usr/bin/env bash
# dev-env-check.sh — Dev environment readiness check
# Reads per-machine manifest and validates agent CLIs, repos, and domain tools.
# Output: color-coded summary. Exit 0 always (informational).
# Log: ~/.dev-env-check.log
# Target: <2s execution via parallel version probes.

# Use a subshell wrapper so set -e doesn't abort the whole terminal session
# when sourced from .bashrc. We always exit 0.
(
set -uo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MANIFESTS_DIR="$WORKSPACE_HUB/specs/modules/hardware-inventory/manifests"
LOG_FILE="${HOME}/.dev-env-check.log"
CURRENT_HOSTNAME="$(hostname)"
MANIFEST_FILE="$MANIFESTS_DIR/${CURRENT_HOSTNAME}.yml"
VERSION_TIMEOUT=1   # seconds per CLI version probe

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG_FILE"; }

# ---------------------------------------------------------------------------
# Version comparison: returns 0 if actual >= minimum (numeric semver)
# ---------------------------------------------------------------------------
version_ge() {
    local actual minimum
    actual="$(printf '%s' "$1" | grep -oE '[0-9]+(\.[0-9]+)*' | head -1)"
    minimum="$(printf '%s' "$2" | grep -oE '[0-9]+(\.[0-9]+)*' | head -1)"
    [ -z "$actual" ] && return 1
    [ -z "$minimum" ] && return 0
    [ "$(printf '%s\n%s\n' "$minimum" "$actual" | sort -V | head -1)" = "$minimum" ]
}

# ---------------------------------------------------------------------------
# YAML helpers (simple line-oriented, no external deps)
# ---------------------------------------------------------------------------
yaml_get() {
    grep -E "^${2}:" "$1" | head -1 \
        | sed 's/^[^:]*:[[:space:]]*//' | tr -d '"'"'"
}

yaml_list_items() {
    awk "/^${2}:/{f=1;next} f && /^[a-zA-Z]/{exit} f && /^  - /{print}" "$1" \
        | sed 's/^[[:space:]]*-[[:space:]]*//'
}

yaml_map_items() {
    awk "/^${2}:/{f=1;next} f && /^[a-zA-Z]/{exit} f && /^  [a-zA-Z]/{print}" "$1" \
        | sed 's/^[[:space:]]*//' | tr -d '"'"'"
}

# ---------------------------------------------------------------------------
# Status printers
# ---------------------------------------------------------------------------
ok()   { printf "  ${GREEN}[OK]${RESET}    %s\n" "$*"; log "OK    $*"; }
warn() { printf "  ${YELLOW}[WARN]${RESET}  %s\n" "$*"; log "WARN  $*"; }
miss() { printf "  ${RED}[MISS]${RESET}  %s\n" "$*"; log "MISS  $*"; }

# ---------------------------------------------------------------------------
# Parallel version probe
# Writes result to a temp file: "<status>|<message>"
# Status: ok | warn | miss
# ---------------------------------------------------------------------------
probe_tool() {
    local tool="$1"
    local min_ver="$2"
    local out_file="$3"

    if ! cmd_path="$(command -v "$tool" 2>/dev/null)"; then
        printf 'miss|%s — not found (requires >=%s)\n' "$tool" "$min_ver" > "$out_file"
        return
    fi

    local raw_ver
    raw_ver="$(timeout "${VERSION_TIMEOUT}s" "$tool" --version 2>&1 \
               | grep -oE '[0-9]+(\.[0-9]+)*' | head -1 || true)"

    if [ -z "$raw_ver" ]; then
        printf 'warn|%s — found at %s but version unreadable (timeout or unsupported flag)\n' \
            "$tool" "$cmd_path" > "$out_file"
        return
    fi

    if version_ge "$raw_ver" "$min_ver"; then
        printf 'ok|%s %s (>=%s) — %s\n' "$tool" "$raw_ver" "$min_ver" "$cmd_path" > "$out_file"
    else
        printf 'warn|%s %s — OUTDATED (requires >=%s)\n' "$tool" "$raw_ver" "$min_ver" > "$out_file"
    fi
}

# Runs probes in parallel, collects and prints results in definition order.
check_tools_parallel() {
    local section="$1"
    local file="$2"
    local tmpdir
    tmpdir="$(mktemp -d)"
    local pids=()
    local tools_ordered=()
    local idx=0

    while IFS=': ' read -r tool min_spec; do
        [ -z "$tool" ] && continue
        local min_ver
        min_ver="$(printf '%s' "$min_spec" | grep -oE '[0-9]+(\.[0-9]+)*' | head -1)"
        probe_tool "$tool" "$min_ver" "$tmpdir/$idx" &
        pids+=($!)
        tools_ordered+=("$idx")
        (( idx++ )) || true
    done < <(yaml_map_items "$file" "$section")

    # Wait for all probes
    for pid in "${pids[@]+"${pids[@]}"}"; do
        wait "$pid" 2>/dev/null || true
    done

    # Print in order
    for i in "${tools_ordered[@]+"${tools_ordered[@]}"}"; do
        local result_file="$tmpdir/$i"
        [ -f "$result_file" ] || continue
        local status msg
        IFS='|' read -r status msg < "$result_file"
        case "$status" in
            ok)   ok   "$msg" ;;
            warn) warn "$msg" ;;
            *)    miss "$msg" ;;
        esac
    done

    rm -rf "$tmpdir"
}

# ---------------------------------------------------------------------------
# Guard: manifest must exist
# ---------------------------------------------------------------------------
if [ ! -f "$MANIFEST_FILE" ]; then
    printf 'No manifest found for %s — skipping dev env check\n' "$CURRENT_HOSTNAME"
    log "No manifest found for $CURRENT_HOSTNAME — skipping"
    exit 0
fi

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
ALIAS="$(yaml_get "$MANIFEST_FILE" "alias")"
ROLE="$(yaml_get "$MANIFEST_FILE" "role")"
WORKSPACE_ROOT="$(yaml_get "$MANIFEST_FILE" "workspace_root")"

printf '\n%bDev Environment Check%b — %s (%s | %s)\n' \
    "$BOLD" "$RESET" "$CURRENT_HOSTNAME" "${ALIAS:-n/a}" "${ROLE:-n/a}"
printf 'Manifest: %s\n' "$MANIFEST_FILE"
printf 'Log:      %s\n\n' "$LOG_FILE"
log "=== dev-env-check start: $CURRENT_HOSTNAME (alias=${ALIAS:-n/a}) ==="

# ---------------------------------------------------------------------------
# 1. Agent CLIs  (parallel probes)
# ---------------------------------------------------------------------------
printf '%bAgent CLIs%b\n' "$BOLD" "$RESET"
check_tools_parallel "agent_clis" "$MANIFEST_FILE"

# ---------------------------------------------------------------------------
# 2. Repos  (fast filesystem checks — no parallelism needed)
# ---------------------------------------------------------------------------
printf '\n%bRepos%b (workspace_root: %s)\n' "$BOLD" "$RESET" "$WORKSPACE_ROOT"
while IFS= read -r repo; do
    [ -z "$repo" ] && continue
    repo_path="$WORKSPACE_ROOT/$repo"
    if [ -d "$repo_path" ]; then
        ok "$repo — $repo_path"
    else
        miss "$repo — missing at $repo_path"
    fi
done < <(yaml_list_items "$MANIFEST_FILE" "repos")

# ---------------------------------------------------------------------------
# 3. Domain Tools  (parallel probes)
# ---------------------------------------------------------------------------
printf '\n%bDomain Tools%b\n' "$BOLD" "$RESET"
check_tools_parallel "domain_tools" "$MANIFEST_FILE"

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
printf '\n'
log "=== dev-env-check complete ==="

exit 0
)
# Outer subshell always exits 0 regardless of internal errors
exit 0
