#!/usr/bin/env bash
# WRK-294: Standardize ace-linux-1 mount path documentation
# Run as: sudo bash scripts/operations/wrk-294-ace-linux-1.sh
#
# What this does:
#   1. Verifies fstab entries use UUID (not device names)
#   2. Creates descriptive symlink /mnt/ace-data -> /mnt/ace
#   3. Disables GNOME desktop auto-mount
#   4. Reports final mount status

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

echo "=== WRK-294: ace-linux-1 Mount Standardization ==="
echo ""

# ── Step 0: Verify we're on ace-linux-1 ──────────────────────────────
if [[ "$(hostname)" != "ace-linux-1" ]]; then
    fail "This script must run on ace-linux-1 (current: $(hostname))"
    exit 1
fi

# ── Step 1: Verify fstab uses UUID ───────────────────────────────────
echo "[1/4] Checking fstab entries..."

if grep -q "21cb3066-da55-4cf9-901f-6bf52c0e315f" /etc/fstab; then
    ok "/mnt/ace uses UUID in fstab (7.3 TB Seagate)"
else
    fail "/mnt/ace not found by UUID in fstab"
    exit 1
fi

if grep -q "260E6F0E0E6ED679" /etc/fstab; then
    ok "/mnt/local-analysis uses UUID in fstab (932 GB WDC)"
else
    fail "/mnt/local-analysis not found by UUID in fstab"
    exit 1
fi

# ── Step 2: Create descriptive symlink ───────────────────────────────
echo ""
echo "[2/4] Creating descriptive symlink /mnt/ace-data -> /mnt/ace..."

if [[ -L /mnt/ace-data ]]; then
    EXISTING=$(readlink /mnt/ace-data)
    if [[ "$EXISTING" == "/mnt/ace" ]]; then
        ok "Symlink /mnt/ace-data -> /mnt/ace already exists"
    else
        fail "/mnt/ace-data exists but points to $EXISTING (not /mnt/ace)"
        exit 1
    fi
elif [[ -e /mnt/ace-data ]]; then
    fail "/mnt/ace-data exists but is not a symlink — remove manually first"
    exit 1
else
    ln -s /mnt/ace /mnt/ace-data
    ok "Created symlink /mnt/ace-data -> /mnt/ace"
fi

# ── Step 3: Disable GNOME desktop auto-mount ─────────────────────────
echo ""
echo "[3/4] Disabling GNOME desktop auto-mount..."

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

# ── Step 4: Final verification ───────────────────────────────────────
echo ""
echo "[4/4] Final mount verification..."
echo ""

PASS=true

if findmnt -n /mnt/ace > /dev/null 2>&1; then
    ACE_SIZE=$(df -h /mnt/ace --output=size | tail -1 | tr -d ' ')
    ACE_USED=$(df -h /mnt/ace --output=pcent | tail -1 | tr -d ' ')
    ok "/mnt/ace: mounted ($ACE_SIZE, $ACE_USED used) — 7.3 TB Seagate bulk data"
else
    fail "/mnt/ace: NOT MOUNTED"
    PASS=false
fi

if findmnt -n /mnt/local-analysis > /dev/null 2>&1; then
    LA_SIZE=$(df -h /mnt/local-analysis --output=size | tail -1 | tr -d ' ')
    LA_USED=$(df -h /mnt/local-analysis --output=pcent | tail -1 | tr -d ' ')
    ok "/mnt/local-analysis: mounted ($LA_SIZE, $LA_USED used) — 932 GB WDC workspace"
else
    fail "/mnt/local-analysis: NOT MOUNTED"
    PASS=false
fi

if [[ -L /mnt/ace-data ]] && [[ "$(readlink /mnt/ace-data)" == "/mnt/ace" ]]; then
    ok "/mnt/ace-data -> /mnt/ace (descriptive symlink)"
else
    fail "/mnt/ace-data symlink missing or incorrect"
    PASS=false
fi

echo ""
echo "=== Summary ==="
if $PASS; then
    ok "All mounts verified. ace-linux-1 drive naming is standardized."
    echo ""
    echo "  Drive map:"
    echo "    /mnt/ace            — 7.3 TB Seagate (bulk data, documents, O&G standards)"
    echo "    /mnt/ace-data       — symlink to /mnt/ace (descriptive alias)"
    echo "    /mnt/local-analysis — 932 GB WDC (workspace-hub, repos, active work)"
    echo "    /                   — 233 GB SSD (OS, boot)"
else
    fail "Some checks failed — see output above"
    exit 1
fi
