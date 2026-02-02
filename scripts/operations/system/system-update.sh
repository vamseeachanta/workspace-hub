#!/bin/bash
set -euo pipefail
# ABOUTME: System update script (Linux). Updates OS packages, common tools, and custom software. Logs all changes to JSON.

SCRIPT_VERSION="1.0.0"
SCHEMA_VERSION="1.0"

# ── Defaults ──────────────────────────────────────────────────────────
CONFIG_FILE=""
OUTPUT_FILE=""
SKIP_OS=0
SKIP_TOOLS=0
SKIP_CUSTOM=0
DO_REBOOT=0
QUIET=0

# ── Color Logging ─────────────────────────────────────────────────────
_CLR_BLUE='\033[0;34m'
_CLR_YELLOW='\033[0;33m'
_CLR_RED='\033[0;31m'
_CLR_GREEN='\033[0;32m'
_CLR_RESET='\033[0m'

log_info() {
    [[ "$QUIET" -eq 1 ]] && return
    printf "${_CLR_BLUE}[INFO]${_CLR_RESET} %s\n" "$*" >&2
}

log_warn() {
    [[ "$QUIET" -eq 1 ]] && return
    printf "${_CLR_YELLOW}[WARN]${_CLR_RESET} %s\n" "$*" >&2
}

log_error() {
    printf "${_CLR_RED}[ERROR]${_CLR_RESET} %s\n" "$*" >&2
}

log_success() {
    [[ "$QUIET" -eq 1 ]] && return
    printf "${_CLR_GREEN}[OK]${_CLR_RESET} %s\n" "$*" >&2
}

# ── JSON Escape Helper ────────────────────────────────────────────────
json_escape() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    # Remove control characters (tabs, newlines, carriage returns)
    s="$(printf '%s' "$s" | tr -d '\000-\011\013-\037')"
    printf '%s' "$s"
}

# ── JSON Array from Bash Array ────────────────────────────────────────
# Usage: json_string_array "${arr[@]}"  (or empty for [])
json_string_array() {
    if [[ $# -eq 0 ]]; then
        printf '[]'
        return
    fi
    local result="["
    local first=1
    for item in "$@"; do
        [[ "$first" -eq 1 ]] && first=0 || result+=","
        result+="\"$(json_escape "$item")\""
    done
    result+="]"
    printf '%s' "$result"
}

# ── JSON Object Array ────────────────────────────────────────────────
# Joins pre-built JSON object strings into an array
json_object_array() {
    if [[ $# -eq 0 ]]; then
        printf '[]'
        return
    fi
    local result="["
    local first=1
    for item in "$@"; do
        [[ "$first" -eq 1 ]] && first=0 || result+=","
        result+="$item"
    done
    result+="]"
    printf '%s' "$result"
}

# ── Usage / Help ──────────────────────────────────────────────────────
usage() {
    cat <<'HELPEOF'
Usage: system-update.sh [OPTIONS]

Update OS packages, common development tools, and custom software.
Produces a structured JSON log of all changes.

Options:
  -c, --config FILE     Path to custom software config (JSON)
  -o, --output FILE     Override update log output path
      --skip-os         Skip OS package updates (apt, snap)
      --skip-tools      Skip common tools updates
      --skip-custom     Skip custom software updates
      --reboot          Reboot after updates if needed (default: warn only)
  -q, --quiet           Suppress log messages
  -h, --help            Show this help message

Output:
  By default writes to ./system-update-<HOSTNAME>-<YYYYMMDD>.json

Examples:
  sudo system-update.sh
  sudo system-update.sh -c /etc/custom-packages.json --reboot
  sudo system-update.sh --skip-custom -o /tmp/update.json
  sudo system-update.sh --skip-os --skip-tools -c pkgs.json
HELPEOF
}

# ── CLI Argument Parsing ──────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --skip-os)
            SKIP_OS=1
            shift
            ;;
        --skip-tools)
            SKIP_TOOLS=1
            shift
            ;;
        --skip-custom)
            SKIP_CUSTOM=1
            shift
            ;;
        --reboot)
            DO_REBOOT=1
            shift
            ;;
        -q|--quiet)
            QUIET=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# ── Root Check ────────────────────────────────────────────────────────
check_root() {
    if [[ $EUID -ne 0 ]]; then
        if [[ "$SKIP_OS" -eq 1 ]] && [[ "$SKIP_TOOLS" -eq 1 ]]; then
            log_warn "Not running as root — OS and tools updates already skipped"
            return 0
        fi
        log_error "This script must be run as root (sudo) for package operations"
        log_error "Alternatively, use --skip-os --skip-tools to skip privileged updates"
        exit 1
    fi
}

# ── Reboot Detection ─────────────────────────────────────────────────
check_reboot_required() {
    if [[ -f /var/run/reboot-required ]]; then
        printf 'true'
    else
        printf 'false'
    fi
}

# ── Read JSON Config Helper ──────────────────────────────────────────
# Minimal JSON value extraction — works for simple arrays and strings.
# Falls back gracefully if python3/jq are unavailable.
json_read_array() {
    local file="$1"
    local key="$2"
    # Try jq first, then python3
    if command -v jq &>/dev/null; then
        jq -r "${key}[]? // empty" "$file" 2>/dev/null || true
    elif command -v python3 &>/dev/null; then
        python3 -c "
import json, sys
try:
    data = json.load(open('${file}'))
    keys = '${key}'.strip('.').split('.')
    obj = data
    for k in keys:
        obj = obj.get(k, {})
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, str):
                print(item)
            elif isinstance(item, dict):
                print(json.dumps(item))
except Exception:
    pass
" 2>/dev/null || true
    else
        log_warn "Neither jq nor python3 available — cannot parse config file"
    fi
}

json_read_object_array() {
    local file="$1"
    local key="$2"
    if command -v jq &>/dev/null; then
        jq -c "${key}[]? // empty" "$file" 2>/dev/null || true
    elif command -v python3 &>/dev/null; then
        python3 -c "
import json
try:
    data = json.load(open('${file}'))
    keys = '${key}'.strip('.').split('.')
    obj = data
    for k in keys:
        obj = obj.get(k, {})
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                print(json.dumps(item))
except Exception:
    pass
" 2>/dev/null || true
    else
        log_warn "Neither jq nor python3 available — cannot parse config file"
    fi
}

json_read_field() {
    local json_str="$1"
    local field="$2"
    if command -v jq &>/dev/null; then
        printf '%s' "$json_str" | jq -r ".${field} // empty" 2>/dev/null || true
    elif command -v python3 &>/dev/null; then
        printf '%s' "$json_str" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('${field}', ''))
except Exception:
    pass
" 2>/dev/null || true
    fi
}

# ── Update OS Packages (APT) ─────────────────────────────────────────
update_os_packages() {
    if [[ "$SKIP_OS" -eq 1 ]]; then
        printf '{"status":"skipped","manager":"apt","upgraded_count":0,"newly_installed_count":0,"removed_count":0,"packages":[],"errors":[]}'
        return
    fi

    log_info "Updating OS packages (apt)..."

    local status="success"
    local upgraded_count=0
    local newly_installed_count=0
    local removed_count=0
    local packages=()
    local errors=()

    # Step 1: apt update
    log_info "  Refreshing package lists..."
    local apt_update_out=""
    if ! apt_update_out="$(apt-get update 2>&1)"; then
        errors+=("apt-get update failed: $(printf '%s' "$apt_update_out" | tail -3 | tr '\n' ' ')")
        log_warn "  apt-get update encountered errors"
    fi

    # Step 2: Capture upgradable packages BEFORE upgrading
    log_info "  Checking upgradable packages..."
    local upgradable_list=""
    upgradable_list="$(apt list --upgradable 2>/dev/null | tail -n +2)" || upgradable_list=""

    if [[ -z "$upgradable_list" ]]; then
        log_info "  No packages to upgrade"
    else
        # Parse upgradable list into package descriptions
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            # Format: package/source version1 arch [upgradable from: version0]
            local pkg_name="" new_ver="" old_ver=""
            pkg_name="$(printf '%s' "$line" | cut -d'/' -f1)"
            new_ver="$(printf '%s' "$line" | awk '{print $2}')"
            old_ver="$(printf '%s' "$line" | grep -oP 'from: \K[^\]]+' || true)"
            if [[ -n "$pkg_name" ]]; then
                if [[ -n "$old_ver" ]]; then
                    packages+=("${pkg_name} ${old_ver} -> ${new_ver}")
                else
                    packages+=("${pkg_name} -> ${new_ver}")
                fi
            fi
        done <<< "$upgradable_list"

        # Step 3: apt upgrade
        log_info "  Upgrading ${#packages[@]} packages..."
        local apt_upgrade_out=""
        if ! apt_upgrade_out="$(DEBIAN_FRONTEND=noninteractive apt-get upgrade -y 2>&1)"; then
            errors+=("apt-get upgrade failed")
            status="failed"
            log_error "  apt-get upgrade failed"
        else
            # Parse upgrade output for counts
            # "X upgraded, Y newly installed, Z to remove"
            local counts_line=""
            counts_line="$(printf '%s\n' "$apt_upgrade_out" | grep -oP '\d+ upgraded, \d+ newly installed, \d+ to remove' | tail -1)" || counts_line=""
            if [[ -n "$counts_line" ]]; then
                upgraded_count="$(printf '%s' "$counts_line" | grep -oP '^\d+')" || upgraded_count=0
                newly_installed_count="$(printf '%s' "$counts_line" | grep -oP ', \K\d+(?= newly)')" || newly_installed_count=0
                removed_count="$(printf '%s' "$counts_line" | grep -oP ', \K\d+(?= to remove)')" || removed_count=0
            fi
            log_success "  Upgrade complete: ${upgraded_count} upgraded, ${newly_installed_count} new, ${removed_count} removed"
        fi
    fi

    # Step 4: apt autoremove
    log_info "  Running autoremove..."
    local autoremove_out=""
    if ! autoremove_out="$(DEBIAN_FRONTEND=noninteractive apt-get autoremove -y 2>&1)"; then
        errors+=("apt-get autoremove failed")
        log_warn "  autoremove encountered errors"
    fi

    # Build JSON
    local esc_status esc_manager
    esc_status="$(json_escape "$status")"
    esc_manager="$(json_escape "apt")"
    local packages_json
    packages_json="$(json_string_array "${packages[@]+"${packages[@]}"}")"
    local errors_json
    errors_json="$(json_string_array "${errors[@]+"${errors[@]}"}")"

    [[ ! "$upgraded_count" =~ ^[0-9]+$ ]] && upgraded_count=0
    [[ ! "$newly_installed_count" =~ ^[0-9]+$ ]] && newly_installed_count=0
    [[ ! "$removed_count" =~ ^[0-9]+$ ]] && removed_count=0

    printf '{"status":"%s","manager":"%s","upgraded_count":%d,"newly_installed_count":%d,"removed_count":%d,"packages":%s,"errors":%s}' \
        "$esc_status" "$esc_manager" "$upgraded_count" "$newly_installed_count" "$removed_count" \
        "$packages_json" "$errors_json"
}

# ── Update Snap Packages ─────────────────────────────────────────────
update_snap_packages() {
    if [[ "$SKIP_OS" -eq 1 ]]; then
        printf '{"status":"skipped","upgraded_count":0,"packages":[],"errors":[]}'
        return
    fi

    if ! command -v snap &>/dev/null; then
        log_info "Snap not available on this system"
        printf '{"status":"unavailable","upgraded_count":0,"packages":[],"errors":[]}'
        return
    fi

    log_info "Updating snap packages..."

    local status="success"
    local upgraded_count=0
    local packages=()
    local errors=()

    local snap_out=""
    if ! snap_out="$(snap refresh 2>&1)"; then
        # snap refresh returns non-zero when "All snaps up to date"
        if printf '%s' "$snap_out" | grep -qi "All snaps up to date"; then
            log_info "  All snaps up to date"
        else
            errors+=("snap refresh failed: $(printf '%s' "$snap_out" | tail -3 | tr '\n' ' ')")
            status="failed"
            log_warn "  snap refresh encountered errors"
        fi
    else
        # Parse refreshed snaps from output
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            # Skip header lines and informational messages
            if printf '%s' "$line" | grep -qiE '(refreshed|updated|upgraded)'; then
                packages+=("$line")
                upgraded_count=$((upgraded_count + 1))
            fi
        done <<< "$snap_out"
        if [[ "$upgraded_count" -gt 0 ]]; then
            log_success "  Refreshed ${upgraded_count} snap packages"
        else
            log_info "  All snaps up to date"
        fi
    fi

    local packages_json
    packages_json="$(json_string_array "${packages[@]+"${packages[@]}"}")"
    local errors_json
    errors_json="$(json_string_array "${errors[@]+"${errors[@]}"}")"
    local esc_status
    esc_status="$(json_escape "$status")"

    printf '{"status":"%s","upgraded_count":%d,"packages":%s,"errors":%s}' \
        "$esc_status" "$upgraded_count" "$packages_json" "$errors_json"
}

# ── Get Tool Version (safe) ──────────────────────────────────────────
get_tool_version() {
    local tool="$1"
    local version=""
    case "$tool" in
        nvidia)
            version="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 | tr -d '[:space:]')" || version=""
            ;;
        docker)
            version="$(docker --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1)" || version=""
            ;;
        flatpak)
            version="$(flatpak --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1)" || version=""
            ;;
        pip)
            version="$(pip3 --version 2>/dev/null | grep -oP '\d+\.\d+[\.\d]*' | head -1)" || version=""
            ;;
        npm)
            version="$(npm --version 2>/dev/null | head -1 | tr -d '[:space:]')" || version=""
            ;;
        node)
            version="$(node --version 2>/dev/null | head -1 | tr -d 'v[:space:]')" || version=""
            ;;
        uv)
            version="$(uv --version 2>/dev/null | grep -oP '\d+\.\d+[\.\d]*' | head -1)" || version=""
            ;;
    esac
    printf '%s' "${version:-unknown}"
}

# ── Build Tool Status JSON ────────────────────────────────────────────
build_tool_json() {
    local status="$1"
    local from_version="$2"
    local to_version="$3"

    local esc_status esc_from esc_to
    esc_status="$(json_escape "$status")"
    esc_from="$(json_escape "$from_version")"
    esc_to="$(json_escape "$to_version")"

    printf '{"status":"%s","from_version":"%s","to_version":"%s"}' \
        "$esc_status" "$esc_from" "$esc_to"
}

# ── Update Tools ──────────────────────────────────────────────────────
update_tools() {
    if [[ "$SKIP_TOOLS" -eq 1 ]]; then
        printf '{"nvidia_driver":{"status":"skipped","from_version":"","to_version":""},"docker":{"status":"skipped","from_version":"","to_version":""},"flatpak":{"status":"skipped","upgraded_count":0},"pip":{"status":"skipped","from_version":"","to_version":""},"npm":{"status":"skipped","from_version":"","to_version":""},"uv":{"status":"skipped","from_version":"","to_version":""}}'
        return
    fi

    log_info "Updating common development tools..."

    # ── NVIDIA Driver ─────────────────────────────────────────────────
    local nvidia_json=""
    if command -v nvidia-smi &>/dev/null; then
        log_info "  Checking NVIDIA driver..."
        local nv_before
        nv_before="$(get_tool_version nvidia)"
        # NVIDIA driver is typically updated via apt (already handled in OS packages)
        # Just record the current version
        local nv_after
        nv_after="$(get_tool_version nvidia)"
        if [[ "$nv_before" == "$nv_after" ]]; then
            nvidia_json="$(build_tool_json "unchanged" "$nv_before" "$nv_after")"
        else
            nvidia_json="$(build_tool_json "updated" "$nv_before" "$nv_after")"
        fi
        log_info "  NVIDIA driver: ${nv_after}"
    else
        nvidia_json="$(build_tool_json "unavailable" "" "")"
        log_info "  NVIDIA driver: not installed"
    fi

    # ── Docker ────────────────────────────────────────────────────────
    local docker_json=""
    if command -v docker &>/dev/null; then
        log_info "  Checking Docker..."
        local docker_before
        docker_before="$(get_tool_version docker)"
        # Docker is typically updated via apt (already handled in OS packages)
        local docker_after
        docker_after="$(get_tool_version docker)"
        if [[ "$docker_before" == "$docker_after" ]]; then
            docker_json="$(build_tool_json "unchanged" "$docker_before" "$docker_after")"
        else
            docker_json="$(build_tool_json "updated" "$docker_before" "$docker_after")"
        fi
        log_info "  Docker: ${docker_after}"
    else
        docker_json="$(build_tool_json "unavailable" "" "")"
        log_info "  Docker: not installed"
    fi

    # ── Flatpak ───────────────────────────────────────────────────────
    local flatpak_json=""
    if command -v flatpak &>/dev/null; then
        log_info "  Updating Flatpak packages..."
        local flatpak_out=""
        local flatpak_count=0
        local flatpak_status="success"
        if ! flatpak_out="$(flatpak update -y --noninteractive 2>&1)"; then
            flatpak_status="failed"
            log_warn "  Flatpak update encountered errors"
        else
            # Count updated apps (lines with arrow pattern or "updating" lines)
            flatpak_count="$(printf '%s\n' "$flatpak_out" | grep -ciE '(updating|updated)' || true)"
            [[ ! "$flatpak_count" =~ ^[0-9]+$ ]] && flatpak_count=0
            log_success "  Flatpak: ${flatpak_count} updated"
        fi
        local esc_fp_status
        esc_fp_status="$(json_escape "$flatpak_status")"
        flatpak_json="$(printf '{"status":"%s","upgraded_count":%d}' "$esc_fp_status" "$flatpak_count")"
    else
        flatpak_json='{"status":"unavailable","upgraded_count":0}'
        log_info "  Flatpak: not installed"
    fi

    # ── pip ────────────────────────────────────────────────────────────
    local pip_json=""
    if command -v pip3 &>/dev/null; then
        log_info "  Updating pip..."
        local pip_before
        pip_before="$(get_tool_version pip)"
        pip3 install --upgrade pip --quiet --root-user-action=ignore 2>/dev/null || true
        local pip_after
        pip_after="$(get_tool_version pip)"
        if [[ "$pip_before" == "$pip_after" ]]; then
            pip_json="$(build_tool_json "unchanged" "$pip_before" "$pip_after")"
        else
            pip_json="$(build_tool_json "updated" "$pip_before" "$pip_after")"
            log_success "  pip: ${pip_before} -> ${pip_after}"
        fi
        [[ "$pip_before" == "$pip_after" ]] && log_info "  pip: ${pip_after} (unchanged)"
    else
        pip_json="$(build_tool_json "unavailable" "" "")"
        log_info "  pip: not installed"
    fi

    # ── npm (global update) ───────────────────────────────────────────
    local npm_json=""
    if command -v npm &>/dev/null; then
        log_info "  Updating npm global packages..."
        local npm_before
        npm_before="$(get_tool_version npm)"
        npm update -g --loglevel=error 2>/dev/null || true
        local npm_after
        npm_after="$(get_tool_version npm)"
        if [[ "$npm_before" == "$npm_after" ]]; then
            npm_json="$(build_tool_json "unchanged" "$npm_before" "$npm_after")"
        else
            npm_json="$(build_tool_json "updated" "$npm_before" "$npm_after")"
            log_success "  npm: ${npm_before} -> ${npm_after}"
        fi
        [[ "$npm_before" == "$npm_after" ]] && log_info "  npm: ${npm_after} (unchanged)"
    else
        npm_json="$(build_tool_json "unavailable" "" "")"
        log_info "  npm: not installed"
    fi

    # ── uv ────────────────────────────────────────────────────────────
    local uv_json=""
    if command -v uv &>/dev/null; then
        log_info "  Updating uv..."
        local uv_before
        uv_before="$(get_tool_version uv)"
        uv self update --quiet 2>/dev/null || true
        local uv_after
        uv_after="$(get_tool_version uv)"
        if [[ "$uv_before" == "$uv_after" ]]; then
            uv_json="$(build_tool_json "unchanged" "$uv_before" "$uv_after")"
        else
            uv_json="$(build_tool_json "updated" "$uv_before" "$uv_after")"
            log_success "  uv: ${uv_before} -> ${uv_after}"
        fi
        [[ "$uv_before" == "$uv_after" ]] && log_info "  uv: ${uv_after} (unchanged)"
    else
        uv_json="$(build_tool_json "unavailable" "" "")"
        log_info "  uv: not installed"
    fi

    printf '{"nvidia_driver":%s,"docker":%s,"flatpak":%s,"pip":%s,"npm":%s,"uv":%s}' \
        "$nvidia_json" "$docker_json" "$flatpak_json" "$pip_json" "$npm_json" "$uv_json"
}

# ── Update Custom Software ───────────────────────────────────────────
update_custom() {
    if [[ "$SKIP_CUSTOM" -eq 1 ]]; then
        printf '{"status":"skipped","items":[]}'
        return
    fi

    if [[ -z "$CONFIG_FILE" ]]; then
        log_info "No custom config file specified (use -c to provide one)"
        printf '{"status":"skipped","items":[]}'
        return
    fi

    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_warn "Config file not found: ${CONFIG_FILE}"
        local esc_err
        esc_err="$(json_escape "Config file not found: ${CONFIG_FILE}")"
        printf '{"status":"failed","items":[{"name":"config","action":"skip","result":"%s"}]}' "$esc_err"
        return
    fi

    log_info "Processing custom software from: ${CONFIG_FILE}"

    local status="success"
    local items=()

    # ── PPAs ──────────────────────────────────────────────────────────
    local ppa=""
    while IFS= read -r ppa; do
        [[ -z "$ppa" ]] && continue
        log_info "  Checking PPA: ${ppa}"
        local esc_ppa
        esc_ppa="$(json_escape "$ppa")"
        # Check if PPA is already added
        local ppa_short="${ppa#ppa:}"
        if grep -rq "${ppa_short}" /etc/apt/sources.list.d/ 2>/dev/null; then
            log_info "    PPA already present"
            items+=("$(printf '{"name":"%s","action":"skip","result":"already present"}' "$esc_ppa")")
        else
            if add-apt-repository -y "$ppa" &>/dev/null; then
                log_success "    PPA added"
                items+=("$(printf '{"name":"%s","action":"install","result":"added"}' "$esc_ppa")")
            else
                log_warn "    Failed to add PPA"
                items+=("$(printf '{"name":"%s","action":"install","result":"failed to add"}' "$esc_ppa")")
                status="failed"
            fi
        fi
    done < <(json_read_array "$CONFIG_FILE" ".ppas")

    # Refresh apt if we added PPAs
    local ppa_count=0
    for item in "${items[@]+"${items[@]}"}"; do
        if printf '%s' "$item" | grep -q '"added"'; then
            ppa_count=$((ppa_count + 1))
        fi
    done
    if [[ "$ppa_count" -gt 0 ]]; then
        log_info "  Refreshing package lists after PPA additions..."
        apt-get update -qq 2>/dev/null || true
    fi

    # ── APT Packages ──────────────────────────────────────────────────
    local pkg=""
    while IFS= read -r pkg; do
        [[ -z "$pkg" ]] && continue
        log_info "  Processing apt package: ${pkg}"
        local esc_pkg
        esc_pkg="$(json_escape "$pkg")"

        if dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
            # Already installed — upgrade if possible
            local current_ver=""
            current_ver="$(dpkg -l "$pkg" 2>/dev/null | grep "^ii" | awk '{print $3}' | head -1)" || current_ver=""
            if DEBIAN_FRONTEND=noninteractive apt-get install --only-upgrade -y "$pkg" &>/dev/null; then
                local new_ver=""
                new_ver="$(dpkg -l "$pkg" 2>/dev/null | grep "^ii" | awk '{print $3}' | head -1)" || new_ver=""
                if [[ "$current_ver" == "$new_ver" ]]; then
                    log_info "    ${pkg}: already latest (${current_ver})"
                    items+=("$(printf '{"name":"%s","action":"skip","result":"already latest (%s)"}' "$esc_pkg" "$(json_escape "${current_ver}")")")
                else
                    log_success "    ${pkg}: upgraded ${current_ver} -> ${new_ver}"
                    items+=("$(printf '{"name":"%s","action":"upgrade","result":"%s -> %s"}' "$esc_pkg" "$(json_escape "${current_ver}")" "$(json_escape "${new_ver}")")")
                fi
            else
                log_warn "    ${pkg}: upgrade failed"
                items+=("$(printf '{"name":"%s","action":"upgrade","result":"failed"}' "$esc_pkg")")
                status="failed"
            fi
        else
            # Not installed — install it
            if DEBIAN_FRONTEND=noninteractive apt-get install -y "$pkg" &>/dev/null; then
                local inst_ver=""
                inst_ver="$(dpkg -l "$pkg" 2>/dev/null | grep "^ii" | awk '{print $3}' | head -1)" || inst_ver=""
                log_success "    ${pkg}: installed (${inst_ver})"
                items+=("$(printf '{"name":"%s","action":"install","result":"installed (%s)"}' "$esc_pkg" "$(json_escape "${inst_ver}")")")
            else
                log_warn "    ${pkg}: install failed"
                items+=("$(printf '{"name":"%s","action":"install","result":"failed"}' "$esc_pkg")")
                status="failed"
            fi
        fi
    done < <(json_read_array "$CONFIG_FILE" ".packages.apt")

    # ── Snap Packages ─────────────────────────────────────────────────
    if command -v snap &>/dev/null; then
        while IFS= read -r pkg; do
            [[ -z "$pkg" ]] && continue
            log_info "  Processing snap package: ${pkg}"
            local esc_pkg
            esc_pkg="$(json_escape "$pkg")"

            if snap list "$pkg" &>/dev/null; then
                log_info "    ${pkg}: already installed via snap"
                items+=("$(printf '{"name":"snap:%s","action":"skip","result":"already installed"}' "$esc_pkg")")
            else
                if snap install "$pkg" &>/dev/null; then
                    log_success "    ${pkg}: installed via snap"
                    items+=("$(printf '{"name":"snap:%s","action":"install","result":"installed"}' "$esc_pkg")")
                else
                    # Try with --classic for packages that need it
                    if snap install "$pkg" --classic &>/dev/null; then
                        log_success "    ${pkg}: installed via snap (classic)"
                        items+=("$(printf '{"name":"snap:%s","action":"install","result":"installed (classic)"}' "$esc_pkg")")
                    else
                        log_warn "    ${pkg}: snap install failed"
                        items+=("$(printf '{"name":"snap:%s","action":"install","result":"failed"}' "$esc_pkg")")
                        status="failed"
                    fi
                fi
            fi
        done < <(json_read_array "$CONFIG_FILE" ".packages.snap")
    fi

    # ── Pip Packages ──────────────────────────────────────────────────
    if command -v pip3 &>/dev/null; then
        while IFS= read -r pkg; do
            [[ -z "$pkg" ]] && continue
            log_info "  Processing pip package: ${pkg}"
            local esc_pkg
            esc_pkg="$(json_escape "$pkg")"

            local pip_before=""
            pip_before="$(pip3 show "$pkg" 2>/dev/null | grep -oP '^Version: \K.*' | head -1)" || pip_before=""

            if pip3 install --upgrade "$pkg" --quiet --root-user-action=ignore 2>/dev/null; then
                local pip_after=""
                pip_after="$(pip3 show "$pkg" 2>/dev/null | grep -oP '^Version: \K.*' | head -1)" || pip_after=""
                if [[ -z "$pip_before" ]]; then
                    log_success "    ${pkg}: installed (${pip_after})"
                    items+=("$(printf '{"name":"pip:%s","action":"install","result":"installed (%s)"}' "$esc_pkg" "$(json_escape "${pip_after}")")")
                elif [[ "$pip_before" == "$pip_after" ]]; then
                    log_info "    ${pkg}: already latest (${pip_after})"
                    items+=("$(printf '{"name":"pip:%s","action":"skip","result":"already latest (%s)"}' "$esc_pkg" "$(json_escape "${pip_after}")")")
                else
                    log_success "    ${pkg}: upgraded ${pip_before} -> ${pip_after}"
                    items+=("$(printf '{"name":"pip:%s","action":"upgrade","result":"%s -> %s"}' "$esc_pkg" "$(json_escape "${pip_before}")" "$(json_escape "${pip_after}")")")
                fi
            else
                log_warn "    ${pkg}: pip install/upgrade failed"
                items+=("$(printf '{"name":"pip:%s","action":"install","result":"failed"}' "$esc_pkg")")
                status="failed"
            fi
        done < <(json_read_array "$CONFIG_FILE" ".packages.pip")
    fi

    # ── Custom Scripts ────────────────────────────────────────────────
    while IFS= read -r script_obj; do
        [[ -z "$script_obj" ]] && continue

        local script_name=""
        local script_check=""
        local script_install=""
        script_name="$(json_read_field "$script_obj" "name")"
        script_check="$(json_read_field "$script_obj" "check")"
        script_install="$(json_read_field "$script_obj" "install")"

        [[ -z "$script_name" ]] && continue
        log_info "  Processing custom script: ${script_name}"
        local esc_name
        esc_name="$(json_escape "$script_name")"

        if [[ -n "$script_check" ]] && eval "$script_check" &>/dev/null; then
            local check_ver=""
            check_ver="$(eval "$script_check" 2>/dev/null | head -1 | tr -d '[:space:]')" || check_ver=""
            log_info "    ${script_name}: already available (${check_ver})"
            items+=("$(printf '{"name":"%s","action":"skip","result":"already installed (%s)"}' "$esc_name" "$(json_escape "${check_ver}")")")
        elif [[ -n "$script_install" ]]; then
            log_info "    ${script_name}: installing..."
            if eval "$script_install" &>/dev/null; then
                log_success "    ${script_name}: installed"
                items+=("$(printf '{"name":"%s","action":"install","result":"installed"}' "$esc_name")")
            else
                log_warn "    ${script_name}: install failed"
                items+=("$(printf '{"name":"%s","action":"install","result":"failed"}' "$esc_name")")
                status="failed"
            fi
        else
            log_warn "    ${script_name}: no install command specified"
            items+=("$(printf '{"name":"%s","action":"skip","result":"no install command"}' "$esc_name")")
        fi
    done < <(json_read_object_array "$CONFIG_FILE" ".scripts")

    local esc_status
    esc_status="$(json_escape "$status")"
    local items_json
    items_json="$(json_object_array "${items[@]+"${items[@]}"}")"

    printf '{"status":"%s","items":%s}' "$esc_status" "$items_json"
}

# ── Pretty Print ──────────────────────────────────────────────────────
pretty_print_json() {
    local file="$1"
    if command -v jq &>/dev/null; then
        local tmp_file="${file}.tmp"
        if jq '.' "$file" > "$tmp_file" 2>/dev/null; then
            mv "$tmp_file" "$file"
            log_info "Pretty-printed with jq"
        else
            rm -f "$tmp_file"
            log_warn "jq pretty-print failed, keeping compact JSON"
        fi
    elif command -v python3 &>/dev/null; then
        local tmp_file="${file}.tmp"
        if python3 -m json.tool "$file" > "$tmp_file" 2>/dev/null; then
            mv "$tmp_file" "$file"
            log_info "Pretty-printed with python3"
        else
            rm -f "$tmp_file"
            log_warn "python3 pretty-print failed, keeping compact JSON"
        fi
    fi
}

# ── Build Summary String ─────────────────────────────────────────────
build_summary() {
    local os_json="$1"
    local snap_json="$2"
    local tools_json="$3"

    local os_count=0 snap_count=0 tool_count=0

    # Extract OS package count
    os_count="$(printf '%s' "$os_json" | grep -oP '"upgraded_count":\K[0-9]+' | head -1)" || os_count=0
    [[ ! "$os_count" =~ ^[0-9]+$ ]] && os_count=0

    # Extract snap count
    snap_count="$(printf '%s' "$snap_json" | grep -oP '"upgraded_count":\K[0-9]+' | head -1)" || snap_count=0
    [[ ! "$snap_count" =~ ^[0-9]+$ ]] && snap_count=0

    # Count updated tools (those with status "updated")
    tool_count="$(printf '%s' "$tools_json" | grep -o '"status":"updated"' | wc -l)" || tool_count=0
    [[ ! "$tool_count" =~ ^[0-9]+$ ]] && tool_count=0

    printf 'Updated %d OS packages, %d snap packages, %d tools' "$os_count" "$snap_count" "$tool_count"
}

# ── Main ──────────────────────────────────────────────────────────────
main() {
    check_root

    local hn
    hn="$(hostname 2>/dev/null || printf 'unknown')"
    local datestamp
    datestamp="$(date +%Y%m%d)"

    if [[ -z "$OUTPUT_FILE" ]]; then
        OUTPUT_FILE="./system-update-${hn}-${datestamp}.json"
    fi

    log_info "System update v${SCRIPT_VERSION} starting"
    log_info "Output file: ${OUTPUT_FILE}"
    log_info "Hostname: ${hn}"

    local timestamp_start
    timestamp_start="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    # ── Run Updates ───────────────────────────────────────────────────
    log_info "── OS Packages ─────────────────────────────────────────"
    local os_json=""
    if os_json="$(update_os_packages)"; then
        true
    else
        log_error "OS package update function failed"
        os_json='{"status":"failed","manager":"apt","upgraded_count":0,"newly_installed_count":0,"removed_count":0,"packages":[],"errors":["update function crashed"]}'
    fi

    log_info "── Snap Packages ───────────────────────────────────────"
    local snap_json=""
    if snap_json="$(update_snap_packages)"; then
        true
    else
        log_error "Snap update function failed"
        snap_json='{"status":"failed","upgraded_count":0,"packages":[],"errors":["update function crashed"]}'
    fi

    log_info "── Development Tools ───────────────────────────────────"
    local tools_json=""
    if tools_json="$(update_tools)"; then
        true
    else
        log_error "Tools update function failed"
        tools_json='{"nvidia_driver":{"status":"failed","from_version":"","to_version":""},"docker":{"status":"failed","from_version":"","to_version":""},"flatpak":{"status":"failed","upgraded_count":0},"pip":{"status":"failed","from_version":"","to_version":""},"npm":{"status":"failed","from_version":"","to_version":""},"uv":{"status":"failed","from_version":"","to_version":""}}'
    fi

    log_info "── Custom Software ─────────────────────────────────────"
    local custom_json=""
    if custom_json="$(update_custom)"; then
        true
    else
        log_error "Custom software update function failed"
        custom_json='{"status":"failed","items":[]}'
    fi

    local timestamp_end
    timestamp_end="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    # ── Reboot Detection ──────────────────────────────────────────────
    local reboot_required
    reboot_required="$(check_reboot_required)"

    # ── Summary ───────────────────────────────────────────────────────
    local summary
    summary="$(build_summary "$os_json" "$snap_json" "$tools_json")"

    # ── Build Final JSON ──────────────────────────────────────────────
    local esc_sv esc_schv esc_hn esc_ts_start esc_ts_end esc_summary
    esc_sv="$(json_escape "$SCRIPT_VERSION")"
    esc_schv="$(json_escape "$SCHEMA_VERSION")"
    esc_hn="$(json_escape "$hn")"
    esc_ts_start="$(json_escape "$timestamp_start")"
    esc_ts_end="$(json_escape "$timestamp_end")"
    esc_summary="$(json_escape "$summary")"

    local full_json
    full_json="$(printf '{"schema_version":"%s","script_version":"%s","platform":"linux","hostname":"%s","timestamp_start":"%s","timestamp_end":"%s","updates":{"os_packages":%s,"snap_packages":%s,"tools":%s,"custom":%s},"reboot_required":%s,"summary":"%s"}' \
        "$esc_schv" "$esc_sv" "$esc_hn" "$esc_ts_start" "$esc_ts_end" \
        "$os_json" "$snap_json" "$tools_json" "$custom_json" \
        "$reboot_required" "$esc_summary")"

    printf '%s\n' "$full_json" > "$OUTPUT_FILE"

    # Pretty-print
    pretty_print_json "$OUTPUT_FILE"

    local file_size
    file_size="$(wc -c < "$OUTPUT_FILE" 2>/dev/null | tr -d '[:space:]')"

    log_info "────────────────────────────────────────────────────────"
    log_success "Update complete: ${OUTPUT_FILE} (${file_size} bytes)"
    log_info "Summary: ${summary}"

    if [[ "$reboot_required" == "true" ]]; then
        if [[ "$DO_REBOOT" -eq 1 ]]; then
            log_warn "Reboot required — rebooting in 10 seconds..."
            log_warn "Press Ctrl+C to cancel"
            sleep 10
            reboot
        else
            log_warn "Reboot required — run 'sudo reboot' when ready"
        fi
    fi
}

main "$@"
