#!/usr/bin/env bash
# WRK-307: Fix KVM display loss on ace-linux-2 (NVIDIA T400 + KVM EDID drop)
#
# PROBLEM: After switching KVM away from ace-linux-2 and back, the NVIDIA T400
#          stops driving display output (EDID signal lost via KVM).
#
# THIS SCRIPT APPLIES: Option B/C — Switch GDM to X11 + force EDID via Xorg config
#
# PERMANENT FIX: Buy a DisplayPort EDID emulator dongle (~$10) and plug into
#                the KVM DP output port for ace-linux-2. Hardware-level fix,
#                no script needed. See WRK-307 for details.
#
# QUICK RECOVERY (no script): From ace-linux-1 or any SSH terminal:
#   ssh vamsee@ace-linux-2 "loginctl unlock-session $(loginctl list-sessions | awk '/seat0/{print $1}')"
#   # If that doesn't work:
#   ssh vamsee@ace-linux-2 "sudo systemctl restart gdm"
#
# USAGE (run from ace-linux-1 or any machine with SSH access to ace-linux-2):
#   bash fix-kvm-display-ace-linux-2.sh [--restart-gdm]
#
# OPTIONS:
#   --restart-gdm   Also restart GDM after applying config (kills active session)
#
# CONNECTION INFO:
#   LAN:       ssh vamsee@192.168.1.103  (or ssh vamsee@ace-linux-2)
#   Tailscale: ssh vamsee@100.93.161.27  (any network)
#
# RELATED: WRK-307 (.claude/work-queue/pending/WRK-307.md)
#          specs/modules/hardware-inventory/aceengineer-02.md

set -euo pipefail

TARGET="ace-linux-2"
RESTART_GDM=false

for arg in "$@"; do
  [[ "$arg" == "--restart-gdm" ]] && RESTART_GDM=true
done

echo "=== WRK-307: ace-linux-2 KVM display fix ==="
echo "Target: $TARGET"
echo ""

# --- Step 1: Verify SSH connectivity ---
echo "[1] Checking SSH connectivity to $TARGET..."
if ! ssh -o ConnectTimeout=5 "vamsee@$TARGET" "echo ok" &>/dev/null; then
  echo "ERROR: Cannot reach $TARGET via SSH."
  echo "  Try: ssh vamsee@192.168.1.103   (LAN)"
  echo "  Try: ssh vamsee@100.93.161.27   (Tailscale)"
  exit 1
fi
echo "    SSH OK"

# --- Step 2: Capture live EDID from sysfs (no X11 required) ---
echo "[2] Capturing EDID from card2-DP-3 sysfs..."
EDID_SIZE=$(ssh "vamsee@$TARGET" "wc -c < /sys/class/drm/card2/card2-DP-3/edid 2>/dev/null || echo 0")
if [[ "$EDID_SIZE" -lt 128 ]]; then
  echo "    WARNING: EDID is $EDID_SIZE bytes (expected 256) — monitor may not be connected."
  echo "    Proceeding with existing /etc/X11/edid.bin if present."
else
  ssh "vamsee@$TARGET" "sudo cp /sys/class/drm/card2/card2-DP-3/edid /etc/X11/edid.bin"
  echo "    EDID captured OK ($EDID_SIZE bytes)"
fi

# --- Step 3: Write Xorg config (DFP-5 = NVIDIA X11 name for the connected DP output) ---
echo "[3] Writing Xorg config /etc/X11/xorg.conf.d/10-force-display.conf..."
ssh "vamsee@$TARGET" "sudo mkdir -p /etc/X11/xorg.conf.d && sudo tee /etc/X11/xorg.conf.d/10-force-display.conf > /dev/null" << 'XORGEOF'
# WRK-307: Force NVIDIA T400 to keep DFP-5 (DP output, Samsung monitor) alive
# even when KVM drops EDID signal. NVIDIA X11 driver names: DFP-0..DFP-5.
# DFP-5 = boot display, connected via DisplayPort on card2-DP-3 (DRM name).
Section "Device"
    Identifier "NVIDIA T400"
    Driver "nvidia"
    BusID "PCI:129:0:0"
    Option "ConnectedMonitor" "DFP-5"
    Option "CustomEDID" "DFP-5:/etc/X11/edid.bin"
EndSection
XORGEOF
echo "    Xorg config written OK"

# --- Step 4: Switch GDM from Wayland to X11 ---
echo "[4] Ensuring GDM uses X11 (not Wayland)..."
WAYLAND_STATE=$(ssh "vamsee@$TARGET" "grep 'WaylandEnable' /etc/gdm3/custom.conf || echo 'not found'")
if echo "$WAYLAND_STATE" | grep -q "^WaylandEnable=false"; then
  echo "    Already X11 (WaylandEnable=false)"
else
  ssh "vamsee@$TARGET" "sudo cp /etc/gdm3/custom.conf /etc/gdm3/custom.conf.bak"
  ssh "vamsee@$TARGET" "sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/' /etc/gdm3/custom.conf"
  echo "    GDM switched to X11 OK"
fi

# --- Step 5: Optionally restart GDM ---
echo ""
echo "=== Config applied. ==="
if [[ "$RESTART_GDM" == true ]]; then
  echo "[5] Restarting GDM (WARNING: kills active graphical session)..."
  ssh "vamsee@$TARGET" "sudo systemctl restart gdm"
  echo "    GDM restarted. Login screen should appear on KVM."
else
  echo "    To activate: ssh vamsee@$TARGET 'sudo systemctl restart gdm'"
  echo "    Or run this script with --restart-gdm"
  echo ""
  echo "    QUICK RECOVERY (no restart, try first):"
  SESSION=$(ssh "vamsee@$TARGET" "loginctl list-sessions 2>/dev/null | awk '/seat0/{print \$1}' | head -1")
  if [[ -n "$SESSION" ]]; then
    echo "    ssh vamsee@$TARGET 'loginctl unlock-session $SESSION'"
  fi
fi
echo ""
echo "NOTE: Permanent fix = DP EDID emulator dongle (~\$10) in KVM DP port."
echo "      See WRK-307: .claude/work-queue/pending/WRK-307.md"
echo ""
echo "REMOTE DESKTOP ALTERNATIVE (view ace-linux-2 display from ace-linux-1):"
echo "  Start VNC on ace-linux-2:  ssh vamsee@ace-linux-2 'x11vnc -display :1 -auth /run/user/1000/gdm/Xauthority -forever -bg -nopw -listen localhost -rfbport 5900'"
echo "  Tunnel to ace-linux-1:     ssh -L 5900:localhost:5900 vamsee@ace-linux-2 -N &"
echo "  Connect viewer:            vncviewer localhost:5900"
echo "  (Requires x11vnc: sudo apt install x11vnc on ace-linux-2)"
