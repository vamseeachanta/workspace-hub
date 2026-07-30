#!/usr/bin/env bash
# ABOUTME: Open a VNC desktop session to ace-linux-2 via SSH tunnel
# ABOUTME: Headless-first: TigerVNC :1 (5901, always-on); --mirror attaches to the physical :0

ACE2_HOST="vamsee@ace-linux-2"
LOCAL_PORT=5900

# Two remote server modes:
#   default  — headless TigerVNC virtual desktop :1 (system unit tigervncserver@:1,
#              127.0.0.1:5901, SecurityTypes=None — safe because localhost-only +
#              SSH tunnel). Works with NOBODY logged into the physical desktop.
#   --mirror — x11vnc attached to the live physical display :0 (requires a
#              graphical login on ace-linux-2; shows the real screen).
MODE="headless"
[[ "${1:-}" == "--mirror" ]] && MODE="mirror"

echo "=== VNC → ace-linux-2 (${MODE}) ==="

# Check for viewer
if ! command -v xtigervncviewer &>/dev/null; then
    echo "ERROR: xtigervncviewer not found. Install: sudo apt install tigervnc-viewer"
    exit 1
fi

REMOTE_PORT=""
if [[ "$MODE" == "headless" ]]; then
    # Headless path: verify the always-on TigerVNC :1 is listening on 5901.
    # Nudge the unit (passwordless sudo only; -n never prompts) if the port is quiet.
    HL_STATUS=$(ssh "${ACE2_HOST}" '
        if ss -tln 2>/dev/null | grep -q "127.0.0.1:5901"; then
            echo OK
        else
            sudo -n systemctl restart tigervncserver@:1.service 2>/dev/null
            sleep 2
            ss -tln 2>/dev/null | grep -q "127.0.0.1:5901" && echo OK || echo DOWN
        fi')
    if [[ "$HL_STATUS" == "OK" ]]; then
        REMOTE_PORT=5901
        echo "Headless TigerVNC :1 is up (127.0.0.1:5901)."
    else
        echo "Headless TigerVNC :1 not listening — falling back to --mirror path..."
        MODE="mirror"
    fi
fi

if [[ "$MODE" == "mirror" ]]; then
    REMOTE_PORT=5900
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
# Physical display only — X1 is the headless TigerVNC display (served directly
# on 5901 by the headless path; mirroring it via x11vnc would be redundant).
XDISP=":0"
[ -S /tmp/.X11-unix/X0 ] || { echo "UNREACHABLE display=:0 (no X0 socket)"; exit 0; }
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
            echo "ERROR: physical display :0 is not reachable — nobody is logged into the desktop."
            echo "  The headless desktop was also unavailable. On ace-linux-2 check:"
            echo "    systemctl status tigervncserver@:1.service"
            exit 1 ;;
        *)
            echo "ERROR: x11vnc failed to start (see /tmp/x11vnc.log on ace-linux-2)."
            exit 1 ;;
    esac
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
#   ./vnc-ace-linux-2.sh            # headless desktop (:1, no login needed)
#   ./vnc-ace-linux-2.sh --mirror   # mirror the physical :0 (needs desktop login)
#
# Prerequisites on ace-linux-2:
#   headless: tigervncserver@:1.service enabled (127.0.0.1:5901, SecurityTypes=None, localhost-only)
#   mirror:   a live graphical login on :0 (x11vnc is launched on demand)
