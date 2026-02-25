#!/usr/bin/env bash
# setup-engineering-update-cron.sh — Install/remove weekly engineering update cron
# Usage: sudo bash scripts/setup/setup-engineering-update-cron.sh [install|remove|status|run]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
REPORT_DIR="$WORKSPACE_ROOT/.claude/reports/maintenance"
UPDATE_SCRIPT="$SCRIPT_DIR/weekly-engineering-update.sh"
CRON_CMD="0 3 * * 0 $UPDATE_SCRIPT >> /var/log/engineering-suite-update-cron.log 2>&1"
CRON_MARKER="# weekly-engineering-update"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

show_usage() {
    echo -e "${CYAN}Weekly Engineering Suite Update — Cron Setup${NC}"
    echo ""
    echo "Usage: sudo $0 [install|remove|status|run]"
    echo ""
    echo "Commands:"
    echo "  install  - Add weekly cron job (Sunday 03:00)"
    echo "  remove   - Remove the cron job"
    echo "  status   - Check if cron job is installed"
    echo "  run      - Run update now (for testing)"
    echo ""
    echo "Programs managed:"
    echo "  apt:  gmsh, paraview, freecad, openfoam, qgis, google-earth-pro"
    echo "  snap: blender"
    echo "  pip:  meshio, PyFoam, pyvista"
    echo ""
    echo "Reports: $REPORT_DIR/engineering-updates.log"
}

install_cron() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}ERROR: Must run as root (sudo)${NC}"
        exit 1
    fi

    chmod +x "$UPDATE_SCRIPT"
    mkdir -p "$REPORT_DIR"

    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo -e "${YELLOW}Cron job already installed.${NC}"
        echo ""
        echo "Current entry:"
        crontab -l 2>/dev/null | grep "$CRON_MARKER"
        return 0
    fi

    (crontab -l 2>/dev/null; echo "$CRON_CMD $CRON_MARKER") | crontab -

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Cron job installed successfully.${NC}"
        echo ""
        echo "Schedule:   Weekly Sunday at 03:00"
        echo "Script:     $UPDATE_SCRIPT"
        echo "Cron log:   /var/log/engineering-suite-update-cron.log"
        echo "Summary:    $REPORT_DIR/engineering-updates.log"
        echo ""
        echo "To verify:  sudo crontab -l"
        echo "To test:    sudo $0 run"
    else
        echo -e "${RED}Failed to install cron job${NC}"
        return 1
    fi
}

remove_cron() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}ERROR: Must run as root (sudo)${NC}"
        exit 1
    fi

    if ! crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo -e "${YELLOW}Cron job not found.${NC}"
        return 0
    fi

    crontab -l 2>/dev/null | grep -v "$CRON_MARKER" | crontab -

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Cron job removed successfully.${NC}"
    else
        echo -e "${RED}Failed to remove cron job${NC}"
        return 1
    fi
}

check_status() {
    echo -e "${CYAN}Weekly Engineering Update — Status${NC}"
    echo -e "${CYAN}═══════════════════════════════════${NC}"
    echo ""

    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo -e "Cron Job: ${GREEN}Installed${NC}"
        echo ""
        echo "Current entry:"
        crontab -l 2>/dev/null | grep "$CRON_MARKER"
    else
        echo -e "Cron Job: ${YELLOW}Not installed${NC}"
        echo ""
        echo "Run 'sudo $0 install' to set up the weekly cron job."
    fi

    echo ""
    echo -e "${CYAN}Recent Updates${NC}"
    echo -e "${CYAN}──────────────${NC}"

    if [[ -f "$REPORT_DIR/engineering-updates.log" ]]; then
        tail -20 "$REPORT_DIR/engineering-updates.log"
    else
        echo "  No update history yet."
    fi

    echo ""
    echo -e "${CYAN}Current Versions${NC}"
    echo -e "${CYAN}────────────────${NC}"
    bash "$UPDATE_SCRIPT" --status
}

run_now() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}ERROR: Must run as root (sudo)${NC}"
        exit 1
    fi

    echo -e "${CYAN}Running engineering suite update now...${NC}"
    echo ""

    chmod +x "$UPDATE_SCRIPT"
    mkdir -p "$REPORT_DIR"
    bash "$UPDATE_SCRIPT"
}

# Main
case "${1:-}" in
    install)  install_cron ;;
    remove)   remove_cron ;;
    status)   check_status ;;
    run)      run_now ;;
    --help|-h) show_usage ;;
    *)
        show_usage
        exit 1
        ;;
esac
