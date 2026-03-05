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

# Check x11vnc is running on ace-linux-2; auto-start if not
echo "Checking x11vnc on ${ACE2_HOST}..."
if ! ssh "${ACE2_HOST}" "ss -tlnp 2>/dev/null | grep -q ':${REMOTE_PORT}'"; then
    echo "x11vnc not running — attempting to start it via SSH..."

    # Prompt for sudo password on ace-linux-2 via PTY, start x11vnc in background, then verify
    echo "Enter sudo password for ace-linux-2 to start x11vnc:"
    ssh -t "${ACE2_HOST}" \
        "sudo x11vnc -display :0 -auth /run/user/120/gdm/Xauthority -forever -nopw -listen localhost -rfbport ${REMOTE_PORT} -bg -o /tmp/x11vnc.log && echo 'x11vnc launched'"

    # Give x11vnc a moment to bind the port
    sleep 2
    if ! ssh "${ACE2_HOST}" "ss -tlnp 2>/dev/null | grep -q ':${REMOTE_PORT}'"; then
        echo "ERROR: x11vnc still not listening on port ${REMOTE_PORT}."
        echo "  Check log: ssh ace-linux-2 'cat /tmp/x11vnc.log'"
        exit 1
    fi
    echo "x11vnc is up."
fi

echo "Starting SSH tunnel ${LOCAL_PORT} → ${ACE2_HOST}:${REMOTE_PORT}..."
ssh -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" "${ACE2_HOST}" -N &
TUNNEL_PID=$!

# Wait for tunnel to be ready (poll instead of fixed sleep)
for i in $(seq 1 10); do
    sleep 0.5
    if ss -tlnp 2>/dev/null | grep -q ":${LOCAL_PORT}"; then
        break
    fi
    if [ "$i" -eq 10 ]; then
        echo "ERROR: SSH tunnel did not establish after 5s"
        kill "${TUNNEL_PID}" 2>/dev/null
        exit 1
    fi
done

echo "Launching VNC viewer (localhost:${LOCAL_PORT})..."
xtigervncviewer "localhost:${LOCAL_PORT}"

# Clean up tunnel when viewer exits
kill "${TUNNEL_PID}" 2>/dev/null
echo "Tunnel closed."

# Usage:
#   ./vnc-ace-linux-2.sh
#
# Prerequisites on ace-linux-2:
#   x11vnc running on port 5900
#   Quick start: sudo x11vnc -display :0 -auth guess -forever -nopw -listen localhost -rfbport 5900 -bg
#   Permanent:   sudo systemctl enable --now x11vnc
