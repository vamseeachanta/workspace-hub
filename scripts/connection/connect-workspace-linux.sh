#!/bin/bash
# ABOUTME: Quick connect script for Linux/Mac machines to access Linux workspace
# ABOUTME: Opens SSH connection in Tabby or fallback to terminal

WORKSPACE_HOST="192.168.1.100"
WORKSPACE_USER="vamsee"
WORKSPACE_PORT=22

echo "=== Connecting to Linux Workspace ==="
echo "Host: $WORKSPACE_HOST"
echo "User: $WORKSPACE_USER"

# Try to use Tabby if available
if command -v tabby &> /dev/null; then
    echo "Opening in Tabby..."
    tabby "ssh://${WORKSPACE_USER}@${WORKSPACE_HOST}:${WORKSPACE_PORT}" &
else
    echo "Tabby not found, using SSH directly..."
    ssh -p $WORKSPACE_PORT ${WORKSPACE_USER}@${WORKSPACE_HOST}
fi

# Usage:
# ./connect-workspace-linux.sh
