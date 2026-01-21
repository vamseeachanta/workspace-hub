#!/bin/bash
# setup_maintenance_cron.sh - Set up daily cron job for repository maintenance
# Usage: ./setup_maintenance_cron.sh [install|remove|status|run]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
REPORT_DIR="$WORKSPACE_ROOT/.claude/reports/maintenance"
CRON_CMD="0 6 * * * $SCRIPT_DIR/daily_repo_maintenance.sh >> $REPORT_DIR/cron.log 2>&1"
CRON_MARKER="# daily-repo-maintenance"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

show_usage() {
    echo -e "${CYAN}Daily Repository Maintenance Cron Setup${NC}"
    echo ""
    echo "Usage: $0 [install|remove|status|run]"
    echo ""
    echo "Commands:"
    echo "  install  - Add daily cron job (runs at 6:00 AM)"
    echo "  remove   - Remove the cron job"
    echo "  status   - Check if cron job is installed"
    echo "  run      - Run maintenance now (for testing)"
    echo ""
    echo "Target repositories:"
    echo "  - workspace-hub"
    echo "  - digitalmodel"
    echo "  - worldenergydata"
    echo "  - assetutilities"
    echo "  - aceengineer-website"
    echo ""
    echo "Workflow sequence (daily):"
    echo "  1. Repository Health Analysis"
    echo "  2. Hidden Folder Audit"
    echo "  3. Build Artifact Cleanup"
    echo "  4. Report Generation"
    echo ""
    echo "Reports: $REPORT_DIR/"
}

install_cron() {
    # Ensure scripts are executable
    chmod +x "$SCRIPT_DIR/daily_repo_maintenance.sh"

    # Create report directory
    mkdir -p "$REPORT_DIR"

    # Check if already installed
    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo -e "${YELLOW}Cron job already installed.${NC}"
        echo ""
        echo "Current entry:"
        crontab -l 2>/dev/null | grep "$CRON_MARKER"
        return 0
    fi

    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_CMD $CRON_MARKER") | crontab -

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Cron job installed successfully!${NC}"
        echo ""
        echo "Schedule:   Daily at 6:00 AM"
        echo "Script:     $SCRIPT_DIR/daily_repo_maintenance.sh"
        echo "Log:        $REPORT_DIR/cron.log"
        echo "Reports:    $REPORT_DIR/daily-maintenance-*.md"
        echo ""
        echo "To verify:  crontab -l"
        echo "To test:    $0 run"
    else
        echo -e "${RED}❌ Failed to install cron job${NC}"
        return 1
    fi
}

remove_cron() {
    if ! crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo -e "${YELLOW}Cron job not found.${NC}"
        return 0
    fi

    crontab -l 2>/dev/null | grep -v "$CRON_MARKER" | crontab -

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Cron job removed successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to remove cron job${NC}"
        return 1
    fi
}

check_status() {
    echo -e "${CYAN}Daily Repository Maintenance Status${NC}"
    echo -e "${CYAN}════════════════════════════════════${NC}"
    echo ""

    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo -e "Cron Job: ${GREEN}✅ Installed${NC}"
        echo ""
        echo "Current entry:"
        crontab -l 2>/dev/null | grep "$CRON_MARKER"
    else
        echo -e "Cron Job: ${YELLOW}❌ Not installed${NC}"
        echo ""
        echo "Run '$0 install' to set up the daily cron job."
    fi

    echo ""
    echo -e "${CYAN}Recent Reports${NC}"
    echo -e "${CYAN}──────────────${NC}"

    if [ -d "$REPORT_DIR" ]; then
        ls -lt "$REPORT_DIR"/daily-maintenance-*.md 2>/dev/null | head -5
        if [ $? -ne 0 ]; then
            echo "  No reports generated yet."
        fi
    else
        echo "  Report directory not created yet."
    fi

    echo ""
    echo -e "${CYAN}Recent Logs${NC}"
    echo -e "${CYAN}───────────${NC}"

    if [ -f "$REPORT_DIR/cron.log" ]; then
        tail -10 "$REPORT_DIR/cron.log"
    else
        echo "  No log file yet."
    fi
}

run_now() {
    echo -e "${CYAN}Running daily maintenance now...${NC}"
    echo ""

    if [ ! -x "$SCRIPT_DIR/daily_repo_maintenance.sh" ]; then
        chmod +x "$SCRIPT_DIR/daily_repo_maintenance.sh"
    fi

    mkdir -p "$REPORT_DIR"
    "$SCRIPT_DIR/daily_repo_maintenance.sh" --verbose

    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
    echo "Latest report:"
    ls -lt "$REPORT_DIR"/daily-maintenance-*.md 2>/dev/null | head -1
}

# Main
case "${1:-}" in
    install)
        install_cron
        ;;
    remove)
        remove_cron
        ;;
    status)
        check_status
        ;;
    run)
        run_now
        ;;
    --help|-h)
        show_usage
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
