#!/bin/bash
# setup_cron.sh - Set up daily cron job for context management analysis
# Usage: ./setup_cron.sh [install|remove|status]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_CMD="0 6 * * * $SCRIPT_DIR/daily_context_analysis.sh >> $SCRIPT_DIR/../../.claude/reports/cron.log 2>&1"
CRON_MARKER="# context-management-daily"

show_usage() {
    echo "Usage: $0 [install|remove|status]"
    echo ""
    echo "Commands:"
    echo "  install  - Add daily cron job (runs at 6:00 AM)"
    echo "  remove   - Remove the cron job"
    echo "  status   - Check if cron job is installed"
    echo ""
}

install_cron() {
    # Check if already installed
    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo "Cron job already installed."
        return 0
    fi

    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_CMD $CRON_MARKER") | crontab -

    if [ $? -eq 0 ]; then
        echo "✅ Cron job installed successfully!"
        echo ""
        echo "Schedule: Daily at 6:00 AM"
        echo "Script: $SCRIPT_DIR/daily_context_analysis.sh"
        echo "Log: $SCRIPT_DIR/../../.claude/reports/cron.log"
        echo ""
        echo "To verify: crontab -l"
    else
        echo "❌ Failed to install cron job"
        return 1
    fi
}

remove_cron() {
    if ! crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo "Cron job not found."
        return 0
    fi

    crontab -l 2>/dev/null | grep -v "$CRON_MARKER" | crontab -

    if [ $? -eq 0 ]; then
        echo "✅ Cron job removed successfully!"
    else
        echo "❌ Failed to remove cron job"
        return 1
    fi
}

check_status() {
    echo "Cron Job Status"
    echo "==============="
    echo ""

    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        echo "✅ Installed"
        echo ""
        echo "Current entry:"
        crontab -l 2>/dev/null | grep "$CRON_MARKER"
    else
        echo "❌ Not installed"
        echo ""
        echo "Run '$0 install' to set up the daily cron job."
    fi
}

# Main
case "${1:-status}" in
    install)
        install_cron
        ;;
    remove)
        remove_cron
        ;;
    status)
        check_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
