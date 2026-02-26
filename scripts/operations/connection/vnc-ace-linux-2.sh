#!/usr/bin/env bash
# ABOUTME: Open a VNC desktop session to ace-linux-2 via SSH tunnel
# ABOUTME: Forwards port 5900, then launches xtigervncviewer on localhost

ACE2_HOST="vamsee@ace-linux-2"
LOCAL_PORT=5900
REMOTE_PORT=5900

echo "=== VNC → ace-linux-2 ==="

# Check for viewer
if ! command -v xtigervncviewer &>/dev/null; then
    echo "ERROR: xtigervncviewer not found. Install: sudo apt install tigervnc-viewer"
    exit 1
fi

echo "Starting SSH tunnel ${LOCAL_PORT} → ${ACE2_HOST}:${REMOTE_PORT}..."
ssh -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" "${ACE2_HOST}" -N &
TUNNEL_PID=$!

# Give tunnel a moment to establish
sleep 1

echo "Launching VNC viewer (localhost:${LOCAL_PORT})..."
xtigervncviewer "localhost:${LOCAL_PORT}"

# Clean up tunnel when viewer exits
kill "${TUNNEL_PID}" 2>/dev/null
echo "Tunnel closed."

# Usage:
#   ./vnc-ace-linux-2.sh
#
# Prerequisites on ace-linux-2:
#   x11vnc running on port 5900 (autostart at ~/.config/autostart/x11vnc.desktop)
