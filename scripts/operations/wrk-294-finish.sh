#!/usr/bin/env bash
# WRK-294: Finish standardizing dev-secondary mount paths
# Run as: sudo bash scripts/operations/wrk-294-finish.sh
#
# What this does:
#   1. Unmounts desktop auto-mounts for sda2 (if active)
#   2. Mounts sda2 at /mnt/local-analysis via fstab
#   3. Disables GNOME desktop auto-mount to prevent dual-mount conflicts
#   4. Verifies both /mnt/local-analysis and /mnt/dde are mounted
#   5. Reports status for manual reboot verification
#
# Prerequisites:
#   - fstab entries already added (by wrk-294-fstab-setup.sh)
#   - /mnt/local-analysis and /mnt/dde directories exist

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

echo "=== WRK-294: Finish Mount Standardization ==="
echo ""

# ── Step 0: Verify we're on dev-secondary ──────────────────────────────
if [[ "$(hostname)" != "dev-secondary" ]]; then
    fail "This script must run on dev-secondary (current: $(hostname))"
    exit 1
fi

# ── Step 1: Verify fstab entries exist ───────────────────────────────
echo "[1/5] Checking fstab entries..."
if grep -q "ACDE7D47DE7D0ABA" /etc/fstab && grep -q "C8F2A5DAF2A5CD4E" /etc/fstab; then
    ok "Both UUID entries found in /etc/fstab"
else
    fail "Missing fstab entries — run wrk-294-fstab-setup.sh first"
    exit 1
fi

# ── Step 2: Handle sda2 mount ────────────────────────────────────────
echo ""
echo "[2/5] Mounting /dev/sda2 at /mnt/local-analysis..."

SDA2_CURRENT=$(findmnt -n -o TARGET /dev/sda2 2>/dev/null || true)

if [[ "$SDA2_CURRENT" == "/mnt/local-analysis" ]]; then
    ok "/dev/sda2 already mounted at /mnt/local-analysis"
elif [[ -n "$SDA2_CURRENT" ]]; then
    warn "/dev/sda2 currently at: $SDA2_CURRENT — unmounting..."
    umount "$SDA2_CURRENT" || warn "Could not unmount $SDA2_CURRENT (may be busy)"
    # Remove empty desktop mount dir if it was created by udisks2
    if [[ "$SDA2_CURRENT" == /media/* ]] && [[ -d "$SDA2_CURRENT" ]]; then
        rmdir "$SDA2_CURRENT" 2>/dev/null || true
    fi
    mount /mnt/local-analysis
    ok "Mounted /dev/sda2 at /mnt/local-analysis"
else
    echo "  /dev/sda2 not currently mounted — mounting via fstab..."
    mount /mnt/local-analysis
    ok "Mounted /dev/sda2 at /mnt/local-analysis"
fi

# ── Step 3: Verify sdc2 mount ────────────────────────────────────────
echo ""
echo "[3/5] Verifying /dev/sdc2 at /mnt/dde..."

SDC2_CURRENT=$(findmnt -n -o TARGET /dev/sdc2 2>/dev/null || true)

if [[ "$SDC2_CURRENT" == "/mnt/dde" ]]; then
    ok "/dev/sdc2 mounted at /mnt/dde"
elif [[ -n "$SDC2_CURRENT" ]]; then
    warn "/dev/sdc2 currently at: $SDC2_CURRENT — remounting..."
    umount "$SDC2_CURRENT" || warn "Could not unmount $SDC2_CURRENT"
    mount /mnt/dde
    ok "Remounted /dev/sdc2 at /mnt/dde"
else
    mount /mnt/dde
    ok "Mounted /dev/sdc2 at /mnt/dde"
fi

# ── Step 4: Disable GNOME desktop auto-mount ─────────────────────────
echo ""
echo "[4/5] Disabling GNOME desktop auto-mount..."

# Run as the actual user (not root) since gsettings is per-user
REAL_USER="${SUDO_USER:-vamsee}"
if su - "$REAL_USER" -c "gsettings set org.gnome.desktop.media-handling automount false" 2>/dev/null; then
    ok "GNOME automount disabled for $REAL_USER"
else
    warn "Could not set gsettings (may need GUI session) — disable manually:"
    warn "  gsettings set org.gnome.desktop.media-handling automount false"
fi
if su - "$REAL_USER" -c "gsettings set org.gnome.desktop.media-handling automount-open false" 2>/dev/null; then
    ok "GNOME automount-open disabled for $REAL_USER"
fi

# ── Step 5: Final verification ───────────────────────────────────────
echo ""
echo "[5/5] Final verification..."
echo ""

PASS=true

# Check sda2
if findmnt -n /mnt/local-analysis > /dev/null 2>&1; then
    SDA2_SIZE=$(df -h /mnt/local-analysis --output=size | tail -1 | tr -d ' ')
    SDA2_USED=$(df -h /mnt/local-analysis --output=pcent | tail -1 | tr -d ' ')
    ok "/mnt/local-analysis: mounted ($SDA2_SIZE, $SDA2_USED used)"
else
    fail "/mnt/local-analysis: NOT MOUNTED"
    PASS=false
fi

# Check sdc2
if findmnt -n /mnt/dde > /dev/null 2>&1; then
    SDC2_SIZE=$(df -h /mnt/dde --output=size | tail -1 | tr -d ' ')
    SDC2_USED=$(df -h /mnt/dde --output=pcent | tail -1 | tr -d ' ')
    ok "/mnt/dde: mounted ($SDC2_SIZE, $SDC2_USED used)"
else
    fail "/mnt/dde: NOT MOUNTED"
    PASS=false
fi

# Check workspace-hub directory exists on local-analysis
if [[ -d /mnt/local-analysis/workspace-hub ]]; then
    ok "/mnt/local-analysis/workspace-hub exists"
else
    warn "/mnt/local-analysis/workspace-hub not found — may need to clone repo here"
fi

echo ""
echo "=== Summary ==="
if $PASS; then
    ok "All mounts active. Now:"
    echo "  1. Reboot:  sudo reboot"
    echo "  2. After reboot, verify:  lsblk -o NAME,UUID,SIZE,MOUNTPOINT"
    echo "  3. Check automount stayed off:  gsettings get org.gnome.desktop.media-handling automount"
else
    fail "Some mounts failed — check output above"
    exit 1
fi
