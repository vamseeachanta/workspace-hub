#!/usr/bin/env bash
# weekly-engineering-update.sh — Update all engineering suite programs
# Usage: sudo bash scripts/setup/weekly-engineering-update.sh [--dry-run | --status]
#
# Manages updates for:
#   apt:  gmsh, paraview, freecad, openfoam, qgis, google-earth-pro-stable
#   snap: blender
#   pip:  meshio, PyFoam, pyvista
#
# Exit codes: 0 = all OK, 1 = partial failure (logged)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
REPORT_DIR="$WORKSPACE_ROOT/.claude/reports/maintenance"
DATE_STAMP="$(date +%Y%m%d)"
LOGFILE="/var/log/engineering-suite-update-${DATE_STAMP}.log"
SUMMARY_FILE="$REPORT_DIR/engineering-updates.log"

DRY_RUN=false
STATUS_ONLY=false
FAILURES=0

# apt packages to upgrade (only the top-level ones)
APT_PACKAGES=(
    gmsh
    paraview
    freecad
    openfoam2312-default
    qgis
    google-earth-pro-stable
)

# snap packages
SNAP_PACKAGES=(blender)

# pip packages (installed as user)
PIP_PACKAGES=(meshio PyFoam pyvista)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOGFILE"; }

version_apt() {
    dpkg-query -W -f='${Version}' "$1" 2>/dev/null || echo "not-installed"
}

version_snap() {
    snap list "$1" 2>/dev/null | awk 'NR==2{print $2}' || echo "not-installed"
}

version_pip() {
    local user_home
    user_home=$(eval echo "~${SUDO_USER:-$USER}")
    su - "${SUDO_USER:-$USER}" -c "pip3 show $1 2>/dev/null" \
        | awk '/^Version:/{print $2}' || echo "not-installed"
}

# ---------------------------------------------------------------------------
# Pre-flight
# ---------------------------------------------------------------------------
preflight() {
    if [[ $EUID -ne 0 ]]; then
        echo "ERROR: Run with sudo or as root."
        echo "  sudo bash $0 $*"
        exit 1
    fi
    mkdir -p "$REPORT_DIR"
    mkdir -p "$(dirname "$LOGFILE")"
}

# ---------------------------------------------------------------------------
# --status: show current versions and exit
# ---------------------------------------------------------------------------
show_status() {
    echo "Engineering Suite — Current Versions"
    echo "====================================="
    echo ""
    printf "%-28s %-12s %s\n" "PROGRAM" "VERSION" "METHOD"
    printf "%-28s %-12s %s\n" "-------" "-------" "------"

    for pkg in "${APT_PACKAGES[@]}"; do
        printf "%-28s %-12s %s\n" "$pkg" "$(version_apt "$pkg")" "apt"
    done
    for pkg in "${SNAP_PACKAGES[@]}"; do
        printf "%-28s %-12s %s\n" "$pkg" "$(version_snap "$pkg")" "snap"
    done
    for pkg in "${PIP_PACKAGES[@]}"; do
        printf "%-28s %-12s %s\n" "$pkg" "$(version_pip "$pkg")" "pip"
    done
}

# ---------------------------------------------------------------------------
# Capture all versions into associative arrays
# ---------------------------------------------------------------------------
declare -A BEFORE_VERSIONS
declare -A AFTER_VERSIONS

capture_versions() {
    local prefix="$1"
    for pkg in "${APT_PACKAGES[@]}"; do
        if [[ "$prefix" == "before" ]]; then
            BEFORE_VERSIONS["apt:$pkg"]="$(version_apt "$pkg")"
        else
            AFTER_VERSIONS["apt:$pkg"]="$(version_apt "$pkg")"
        fi
    done
    for pkg in "${SNAP_PACKAGES[@]}"; do
        if [[ "$prefix" == "before" ]]; then
            BEFORE_VERSIONS["snap:$pkg"]="$(version_snap "$pkg")"
        else
            AFTER_VERSIONS["snap:$pkg"]="$(version_snap "$pkg")"
        fi
    done
    for pkg in "${PIP_PACKAGES[@]}"; do
        if [[ "$prefix" == "before" ]]; then
            BEFORE_VERSIONS["pip:$pkg"]="$(version_pip "$pkg")"
        else
            AFTER_VERSIONS["pip:$pkg"]="$(version_pip "$pkg")"
        fi
    done
}

# ---------------------------------------------------------------------------
# Update routines
# ---------------------------------------------------------------------------
update_apt() {
    log "--- apt update ---"
    apt update -qq 2>&1 | tee -a "$LOGFILE"

    for pkg in "${APT_PACKAGES[@]}"; do
        if dpkg -l "$pkg" &>/dev/null; then
            if $DRY_RUN; then
                log "[dry-run] would upgrade: $pkg"
                apt install --dry-run "$pkg" 2>&1 | tail -3 | tee -a "$LOGFILE"
            else
                log "Upgrading $pkg..."
                apt install -y --only-upgrade "$pkg" 2>&1 | tail -3 | tee -a "$LOGFILE" || {
                    log "WARN: apt upgrade failed for $pkg"
                    ((FAILURES++))
                }
            fi
        else
            log "SKIP: $pkg not installed"
        fi
    done
}

update_snap() {
    log "--- snap refresh ---"
    for pkg in "${SNAP_PACKAGES[@]}"; do
        if snap list "$pkg" &>/dev/null; then
            if $DRY_RUN; then
                log "[dry-run] would refresh: $pkg (current: $(version_snap "$pkg"))"
            else
                log "Refreshing $pkg..."
                snap refresh "$pkg" 2>&1 | tee -a "$LOGFILE" || {
                    log "WARN: snap refresh failed for $pkg"
                    ((FAILURES++))
                }
            fi
        else
            log "SKIP: $pkg not installed via snap"
        fi
    done
}

update_pip() {
    log "--- pip upgrade ---"
    local target_user="${SUDO_USER:-$USER}"

    for pkg in "${PIP_PACKAGES[@]}"; do
        if $DRY_RUN; then
            log "[dry-run] would upgrade pip package: $pkg (current: $(version_pip "$pkg"))"
        else
            log "Upgrading pip package: $pkg..."
            su - "$target_user" -c \
                "pip3 install --user --upgrade $pkg 2>&1" \
                | tee -a "$LOGFILE" || {
                    log "WARN: pip upgrade failed for $pkg"
                    ((FAILURES++))
                }
        fi
    done
}

# ---------------------------------------------------------------------------
# Summary report
# ---------------------------------------------------------------------------
write_summary() {
    local changes=0
    local summary=""

    summary+="$(date '+%Y-%m-%d %H:%M:%S') — Weekly Engineering Update\n"
    summary+="──────────────────────────────────────────────────────\n"

    for key in "${!BEFORE_VERSIONS[@]}"; do
        local before="${BEFORE_VERSIONS[$key]}"
        local after="${AFTER_VERSIONS[$key]}"
        if [[ "$before" != "$after" ]]; then
            summary+="  UPDATED: $key  $before -> $after\n"
            ((changes++))
        fi
    done

    if [[ $changes -eq 0 ]]; then
        summary+="  No version changes detected.\n"
    else
        summary+="  Total updates: $changes\n"
    fi

    if [[ $FAILURES -gt 0 ]]; then
        summary+="  Failures: $FAILURES (see $LOGFILE)\n"
    fi

    summary+="\n"

    echo -e "$summary" | tee -a "$SUMMARY_FILE"
    log "Summary appended to $SUMMARY_FILE"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    # Parse flags
    for arg in "$@"; do
        case "$arg" in
            --dry-run) DRY_RUN=true ;;
            --status)  STATUS_ONLY=true ;;
            --help|-h)
                echo "Usage: sudo bash $0 [--dry-run | --status]"
                echo ""
                echo "  --dry-run   Preview updates without applying"
                echo "  --status    Show current installed versions"
                echo "  (no flag)   Run full update"
                exit 0
                ;;
            *)
                echo "Unknown flag: $arg"
                echo "Usage: sudo bash $0 [--dry-run | --status]"
                exit 1
                ;;
        esac
    done

    preflight

    if $STATUS_ONLY; then
        show_status
        exit 0
    fi

    log "========================================="
    log "Engineering Suite Update — $DATE_STAMP"
    if $DRY_RUN; then
        log "MODE: dry-run (no changes will be applied)"
    fi
    log "========================================="

    capture_versions "before"

    update_apt
    update_snap
    update_pip

    if ! $DRY_RUN; then
        capture_versions "after"
        write_summary
    fi

    log "========================================="
    if [[ $FAILURES -gt 0 ]]; then
        log "Completed with $FAILURES failure(s). See log: $LOGFILE"
        exit 1
    else
        log "All updates completed successfully."
        exit 0
    fi
}

main "$@"
