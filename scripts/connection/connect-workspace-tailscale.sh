#!/bin/bash
# ABOUTME: Quick connect script to access Linux workspace via Tailscale VPN
# ABOUTME: Works from anywhere on the internet

WORKSPACE_HOST="100.107.64.76"
WORKSPACE_HOSTNAME="vamsee-linux1"
WORKSPACE_USER="vamsee"
WORKSPACE_PORT=22

echo "=== Connecting to Linux Workspace (Tailscale) ==="

# Check if Tailscale is installed
if ! command -v tailscale &> /dev/null; then
    echo "❌ Tailscale is not installed!"
    echo ""
    echo "Install Tailscale:"
    echo "  Linux: curl -fsSL https://tailscale.com/install.sh | sh"
    echo "  Mac:   brew install tailscale"
    echo ""
    echo "Then run: sudo tailscale up"
    exit 1
fi

# Check if Tailscale is connected
if ! tailscale status &> /dev/null; then
    echo "❌ Tailscale is not connected!"
    echo "Run: sudo tailscale up"
    exit 1
fi

# Check if we can reach the workspace
echo "Checking connection to workspace..."
if ping -c 1 -W 2 $WORKSPACE_HOST &> /dev/null; then
    echo "✓ Workspace is reachable via Tailscale"
else
    echo "❌ Cannot reach workspace!"
    echo "Check:"
    echo "  1. Workspace machine is online"
    echo "  2. Both devices on same Tailscale network"
    echo "  3. Run: tailscale status"
    exit 1
fi

echo "Host: $WORKSPACE_HOST ($WORKSPACE_HOSTNAME)"
echo "User: $WORKSPACE_USER"
echo ""

# Try to use Tabby if available
if command -v tabby &> /dev/null; then
    echo "Opening in Tabby..."
    tabby "ssh://${WORKSPACE_USER}@${WORKSPACE_HOST}:${WORKSPACE_PORT}" &
else
    echo "Tabby not found, using SSH directly..."
    ssh -p $WORKSPACE_PORT ${WORKSPACE_USER}@${WORKSPACE_HOST}
fi

# Usage:
# ./connect-workspace-tailscale.sh
