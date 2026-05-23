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

# Ensure a FRESH, healthy x11vnc on ace-linux-2.
#
# A port merely bound on :5900 is NOT proof of health. If the GNOME/Wayland
# session restarts underneath a long-lived x11vnc, the process keeps its TCP
# socket but its X connection is dead: it accepts viewers, completes the RFB
# handshake, then serves 0 frames ("End of stream" / "0 rects" on the viewer).
# The old "if not listening, start it" check happily reused such a zombie.
# So we always kill any existing instance and relaunch against the current
# display, after verifying that display is actually reachable with its auth.
echo "Ensuring fresh x11vnc on ${ACE2_HOST}..."
LAUNCH_STATUS=$(ssh "${ACE2_HOST}" "bash -s ${REMOTE_PORT}" <<'REMOTE'
PORT="$1"
# Display from the live X socket — works for both Xorg and Xwayland (:0, :1, …).
XDISP=$(ls /tmp/.X11-unix/ 2>/dev/null | head -1 | sed 's/X/:/')
XDISP="${XDISP:-:0}"
# Auth, in order of likelihood: classic Xorg/Xwayland -auth, then the GDM
# Wayland Xauthority, then mutter's Xwayland auth, then let x11vnc guess.
XAUTH=$(ps wwwaux | grep -E ' /usr/lib/xorg/Xorg | Xwayland ' | grep -v grep \
        | grep -oP '(?<=-auth )\S+' | head -1)
if [ -z "$XAUTH" ] || [ ! -r "$XAUTH" ]; then
    for c in "/run/user/$(id -u)/gdm/Xauthority" /run/user/$(id -u)/.mutter-Xwaylandauth.*; do
        [ -r "$c" ] && XAUTH="$c" && break
    done
fi
[ -z "$XAUTH" ] && XAUTH=guess
# Refuse to launch against a dead display — surfaces "no graphical session"
# instead of producing another silently-broken VNC server.
if ! XAUTHORITY="$XAUTH" DISPLAY="$XDISP" xdpyinfo >/dev/null 2>&1; then
    echo "UNREACHABLE display=$XDISP auth=$XAUTH"; exit 0
fi
pkill -x x11vnc 2>/dev/null || true
sleep 1
x11vnc -display "$XDISP" -auth "$XAUTH" -forever -nopw \
       -listen localhost -rfbport "$PORT" -bg -o /tmp/x11vnc.log >/dev/null 2>&1
sleep 2
if ss -tlnp 2>/dev/null | grep -q ":$PORT"; then
    echo "OK display=$XDISP auth=$XAUTH"
else
    echo "FAILED display=$XDISP auth=$XAUTH"; tail -n 5 /tmp/x11vnc.log
fi
REMOTE
)
echo "  ${LAUNCH_STATUS}"
case "${LAUNCH_STATUS}" in
    OK*) : ;;  # fresh server up
    UNREACHABLE*)
        echo "ERROR: display is not reachable on ace-linux-2 — is anyone logged into the desktop?"
        echo "  Log in graphically on ace-linux-2, then re-run this script."
        exit 1 ;;
    *)
        echo "ERROR: x11vnc failed to start (see /tmp/x11vnc.log on ace-linux-2)."
        exit 1 ;;
esac

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
