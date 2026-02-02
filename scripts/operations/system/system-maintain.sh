#!/bin/bash
set -euo pipefail
# ABOUTME: System maintenance orchestrator (Linux). Runs hardware assessment, system updates, and re-assessment to track changes over time.

SCRIPT_VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Defaults ──────────────────────────────────────────────────────────
CONFIG_FILE=""
OUTPUT_DIR="."
SKIP_ASSESS=0
SKIP_UPDATE=0
QUIET=0
REBOOT=0

# ── Color Logging ─────────────────────────────────────────────────────
_CLR_BLUE='\033[0;34m'
_CLR_YELLOW='\033[0;33m'
_CLR_RED='\033[0;31m'
_CLR_GREEN='\033[0;32m'
_CLR_CYAN='\033[0;36m'
_CLR_RESET='\033[0m'

log_info()    { [[ "${QUIET}" -eq 1 ]] && return; printf "${_CLR_BLUE}[INFO]${_CLR_RESET} %s\n" "$*" >&2; }
log_warn()    { [[ "${QUIET}" -eq 1 ]] && return; printf "${_CLR_YELLOW}[WARN]${_CLR_RESET} %s\n" "$*" >&2; }
log_error()   { printf "${_CLR_RED}[ERROR]${_CLR_RESET} %s\n" "$*" >&2; }
log_success() { [[ "${QUIET}" -eq 1 ]] && return; printf "${_CLR_GREEN}[OK]${_CLR_RESET} %s\n" "$*" >&2; }
log_phase()   { [[ "${QUIET}" -eq 1 ]] && return; printf "\n${_CLR_CYAN}════════════════════════════════════════${_CLR_RESET}\n" >&2; printf "${_CLR_CYAN}  %s${_CLR_RESET}\n" "$*" >&2; printf "${_CLR_CYAN}════════════════════════════════════════${_CLR_RESET}\n\n" >&2; }

# ── Usage ─────────────────────────────────────────────────────────────
usage() {
    cat <<'HELPEOF'
Usage: system-maintain.sh [OPTIONS]

Orchestrate full system maintenance: assess → update → re-assess → changelog.

Options:
  -c, --config FILE     Custom software config for updates (JSON)
  -d, --output-dir DIR  Directory for all output files (default: .)
  --skip-assess         Skip hardware assessments (update only)
  --skip-update         Skip updates (assess only)
  --reboot              Reboot after updates if needed
  -q, --quiet           Suppress log messages
  -h, --help            Show this help message

Workflow:
  1. Pre-update hardware assessment  → hardware-assessment-<host>-<date>-pre.json
  2. System update                    → system-update-<host>-<date>.json
  3. Post-update hardware assessment → hardware-assessment-<host>-<date>-post.json
  4. Changelog generation            → system-changelog-<host>-<date>.json

Examples:
  sudo system-maintain.sh -d /var/log/maintenance
  sudo system-maintain.sh -c /etc/custom-packages.json --reboot
  system-maintain.sh --skip-update    # Assessment only
HELPEOF
}

# ── CLI Argument Parsing ──────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        -c|--config)     CONFIG_FILE="$2"; shift 2 ;;
        -d|--output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        --skip-assess)   SKIP_ASSESS=1; shift ;;
        --skip-update)   SKIP_UPDATE=1; shift ;;
        --reboot)        REBOOT=1; shift ;;
        -q|--quiet)      QUIET=1; shift ;;
        -h|--help)       usage; exit 0 ;;
        *)               log_error "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# ── JSON Helpers ──────────────────────────────────────────────────────
json_escape() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="$(printf '%s' "$s" | tr -d '\000-\011\013-\037')"
    printf '%s' "$s"
}

# ── Generate Changelog ────────────────────────────────────────────────
generate_changelog() {
    local pre_file="$1" post_file="$2" update_file="$3" changelog_file="$4"

    log_info "Generating changelog..."

    if command -v python3 &>/dev/null; then
        python3 - "$pre_file" "$post_file" "$update_file" "$changelog_file" <<'PYEOF'
import json, sys
from datetime import datetime

pre_file, post_file, update_file, changelog_file = sys.argv[1:5]

changelog = {
    "schema_version": "1.0",
    "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "hostname": "",
    "changes": {
        "hardware": [],
        "software": [],
        "os": []
    }
}

# Load files (each may not exist)
pre = post = updates = None
try:
    with open(pre_file) as f: pre = json.load(f)
except: pass
try:
    with open(post_file) as f: post = json.load(f)
except: pass
try:
    with open(update_file) as f: updates = json.load(f)
except: pass

if pre:
    changelog["hostname"] = pre.get("os", {}).get("hostname", "unknown")

# Compare hardware changes (pre vs post)
if pre and post:
    for section in ["cpu", "memory", "motherboard"]:
        pre_sec = pre.get(section, {})
        post_sec = post.get(section, {})
        for key in set(list(pre_sec.keys()) + list(post_sec.keys())):
            old_val = pre_sec.get(key)
            new_val = post_sec.get(key)
            if old_val != new_val:
                changelog["changes"]["hardware"].append({
                    "section": section,
                    "field": key,
                    "before": old_val,
                    "after": new_val
                })

    # OS changes
    pre_os = pre.get("os", {})
    post_os = post.get("os", {})
    for key in ["name", "kernel"]:
        old_val = pre_os.get(key)
        new_val = post_os.get(key)
        if old_val != new_val:
            changelog["changes"]["os"].append({
                "field": key,
                "before": old_val,
                "after": new_val
            })

# Software changes from update log
if updates:
    up = updates.get("updates", {})

    os_pkgs = up.get("os_packages", {})
    if os_pkgs.get("status") == "success" and os_pkgs.get("upgraded_count", 0) > 0:
        changelog["changes"]["software"].append({
            "category": "os_packages",
            "manager": os_pkgs.get("manager", "unknown"),
            "count": os_pkgs.get("upgraded_count", 0),
            "packages": os_pkgs.get("packages", [])
        })

    snap = up.get("snap_packages", {})
    if snap.get("status") == "success" and snap.get("upgraded_count", 0) > 0:
        changelog["changes"]["software"].append({
            "category": "snap_packages",
            "count": snap.get("upgraded_count", 0),
            "packages": snap.get("packages", [])
        })

    tools = up.get("tools", {})
    for tool_name, tool_data in tools.items():
        if isinstance(tool_data, dict):
            st = tool_data.get("status", "")
            if st == "updated":
                changelog["changes"]["software"].append({
                    "category": "tool",
                    "name": tool_name,
                    "from_version": tool_data.get("from_version", ""),
                    "to_version": tool_data.get("to_version", "")
                })

    custom = up.get("custom", {})
    items = custom.get("items", [])
    for item in items:
        if item.get("action") in ("install", "upgrade"):
            changelog["changes"]["software"].append({
                "category": "custom",
                "name": item.get("name", ""),
                "action": item.get("action", ""),
                "result": item.get("result", "")
            })

changelog["summary"] = {
    "hardware_changes": len(changelog["changes"]["hardware"]),
    "software_changes": len(changelog["changes"]["software"]),
    "os_changes": len(changelog["changes"]["os"]),
    "total_changes": len(changelog["changes"]["hardware"]) + len(changelog["changes"]["software"]) + len(changelog["changes"]["os"])
}

with open(changelog_file, "w") as f:
    json.dump(changelog, f, indent=2)

print(f"Changelog: {changelog['summary']['total_changes']} changes detected")
PYEOF
    else
        # Fallback: basic changelog without diffing
        local hn
        hn="$(hostname 2>/dev/null || printf 'unknown')"
        local ts
        ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        printf '{"schema_version":"1.0","generated":"%s","hostname":"%s","changes":{"hardware":[],"software":[],"os":[]},"summary":{"note":"python3 not available — install python3 for detailed changelog"}}' \
            "$(json_escape "$ts")" "$(json_escape "$hn")" > "$changelog_file"
        log_warn "python3 not available — changelog generated without diff analysis"
    fi
}

# ── Main ──────────────────────────────────────────────────────────────
main() {
    local hn
    hn="$(hostname 2>/dev/null || printf 'unknown')"
    local datestamp
    datestamp="$(date +%Y%m%d)"

    mkdir -p "$OUTPUT_DIR"

    local assess_script="${SCRIPT_DIR}/hardware-assess.sh"
    local update_script="${SCRIPT_DIR}/system-update.sh"

    # Verify scripts exist
    if [[ "$SKIP_ASSESS" -eq 0 ]] && [[ ! -f "$assess_script" ]]; then
        log_error "hardware-assess.sh not found at: $assess_script"
        exit 1
    fi
    if [[ "$SKIP_UPDATE" -eq 0 ]] && [[ ! -f "$update_script" ]]; then
        log_error "system-update.sh not found at: $update_script"
        exit 1
    fi

    local pre_assess="${OUTPUT_DIR}/hardware-assessment-${hn}-${datestamp}-pre.json"
    local update_log="${OUTPUT_DIR}/system-update-${hn}-${datestamp}.json"
    local post_assess="${OUTPUT_DIR}/hardware-assessment-${hn}-${datestamp}-post.json"
    local changelog="${OUTPUT_DIR}/system-changelog-${hn}-${datestamp}.json"

    local quiet_flag=""
    [[ "$QUIET" -eq 1 ]] && quiet_flag="-q"

    log_info "System maintenance v${SCRIPT_VERSION} starting on ${hn}"
    log_info "Output directory: ${OUTPUT_DIR}"

    # ── Phase 1: Pre-update assessment ──
    if [[ "$SKIP_ASSESS" -eq 0 ]]; then
        log_phase "Phase 1/4: Pre-Update Assessment"
        bash "$assess_script" -o "$pre_assess" -p $quiet_flag
        log_success "Pre-assessment saved: ${pre_assess}"
    else
        log_info "Skipping pre-update assessment"
    fi

    # ── Phase 2: System updates ──
    if [[ "$SKIP_UPDATE" -eq 0 ]]; then
        log_phase "Phase 2/4: System Updates"
        local update_args=(-o "$update_log")
        [[ -n "$CONFIG_FILE" ]] && update_args+=(-c "$CONFIG_FILE")
        [[ "$QUIET" -eq 1 ]] && update_args+=(-q)
        bash "$update_script" "${update_args[@]}"
        log_success "Update log saved: ${update_log}"
    else
        log_info "Skipping system updates"
    fi

    # ── Phase 3: Post-update assessment ──
    if [[ "$SKIP_ASSESS" -eq 0 ]]; then
        log_phase "Phase 3/4: Post-Update Assessment"
        bash "$assess_script" -o "$post_assess" -p $quiet_flag
        log_success "Post-assessment saved: ${post_assess}"
    else
        log_info "Skipping post-update assessment"
    fi

    # ── Phase 4: Changelog ──
    log_phase "Phase 4/4: Generating Changelog"
    generate_changelog "$pre_assess" "$post_assess" "$update_log" "$changelog"
    log_success "Changelog saved: ${changelog}"

    # ── Summary ──
    log_phase "Maintenance Complete"
    log_info "Files generated:"
    [[ "$SKIP_ASSESS" -eq 0 ]] && log_info "  Pre-assessment:  ${pre_assess}"
    [[ "$SKIP_UPDATE" -eq 0 ]] && log_info "  Update log:      ${update_log}"
    [[ "$SKIP_ASSESS" -eq 0 ]] && log_info "  Post-assessment: ${post_assess}"
    log_info "  Changelog:       ${changelog}"

    # ── Reboot if requested ──
    if [[ "$REBOOT" -eq 1 ]] && [[ -f /var/run/reboot-required ]]; then
        log_warn "Reboot required — rebooting in 10 seconds (Ctrl+C to cancel)"
        sleep 10
        reboot
    elif [[ -f /var/run/reboot-required ]]; then
        log_warn "Reboot required — run 'sudo reboot' when ready"
    fi
}

main "$@"
