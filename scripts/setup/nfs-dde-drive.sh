#!/usr/bin/env bash
# nfs-dde-drive.sh — Set up NFS share of the dde drive from ace-linux-2 to ace-linux-1.
#
# Mirror of scripts/setup/nfs-ace-drive.sh with the roles inverted:
# ace-linux-2 owns the dde disk (NTFS, ntfs3) and acts as NFS server;
# ace-linux-1 is the client.
#
# Run as root on the appropriate machine:
#   ace-linux-2 (server): sudo bash scripts/setup/nfs-dde-drive.sh server
#   ace-linux-1 (client): sudo bash scripts/setup/nfs-dde-drive.sh client
#
# From ace-linux-1 you can drive the server side over ssh:
#   ssh -t ace-linux-2 "sudo bash -s server" < scripts/setup/nfs-dde-drive.sh
#
# What this does:
#   server: installs nfs-kernel-server, exports the dde drive to ace-linux-1
#   client: retires the legacy sshfs automount at the same mount point,
#           mounts ace-linux-2's dde drive over NFS, and creates the
#           canonical symlink so the ecosystem-wide reference resolves
#           (see docs/standards/canonical-drive-references.md and
#           scripts/setup/canonical-drive-links.sh)
#
# Prerequisites:
#   - Both machines on the same LAN
#   - ace-linux-1 can resolve "ace-linux-2" (via /etc/hosts or DNS)
set -euo pipefail

MODE="${1:-}"
EXPORT_PATH="/mnt/dde"                          # abs-path-allowed
CLIENT_MOUNT="/mnt/remote/ace-linux-2/dde"      # abs-path-allowed
CANONICAL_LINK="/mnt/dde"                       # abs-path-allowed
SERVER_HOST="ace-linux-2"
CLIENT_HOST="ace-linux-1"

usage() {
    echo "Usage: sudo $0 {server|client|verify}"
    echo ""
    echo "  server  — run on $SERVER_HOST: install NFS server, export $EXPORT_PATH"
    echo "  client  — run on $CLIENT_HOST: retire sshfs, mount $SERVER_HOST:$EXPORT_PATH, link $CANONICAL_LINK"
    echo "  verify  — run on either: check NFS is working"
    exit 1
}

require_root() {
    if [[ $EUID -ne 0 ]]; then
        echo "Error: must run as root (sudo)"
        exit 1
    fi
}

setup_server() {
    require_root
    local hostname
    hostname="$(hostname -s)"
    if [[ "$hostname" != "$SERVER_HOST" ]]; then
        echo "Warning: expected hostname '$SERVER_HOST', got '$hostname'"
        read -rp "Continue anyway? [y/N] " confirm
        [[ "$confirm" =~ ^[Yy]$ ]] || exit 1
    fi

    if ! mountpoint -q "$EXPORT_PATH"; then
        echo "Error: $EXPORT_PATH is not a mounted filesystem — check the dde disk"
        exit 1
    fi

    echo "==> Installing NFS server..."
    apt-get update -qq
    apt-get install -y -qq nfs-kernel-server

    echo "==> Configuring export..."
    # fsid: explicit id so the NTFS (ntfs3) volume is reliably exportable.
    local export_line="$EXPORT_PATH    $CLIENT_HOST(rw,sync,no_subtree_check,crossmnt,fsid=101)"

    if grep -qF "$EXPORT_PATH" /etc/exports 2>/dev/null; then
        echo "Export for $EXPORT_PATH already exists in /etc/exports:"
        grep "$EXPORT_PATH" /etc/exports
        echo "Skipping — edit /etc/exports manually if you need to change it."
    else
        echo "$export_line" >> /etc/exports
        echo "Added to /etc/exports: $export_line"
    fi

    echo "==> Applying exports..."
    exportfs -ra

    echo "==> Starting NFS server..."
    systemctl enable --now nfs-kernel-server

    echo "==> Done. Verify with: exportfs -v"
    exportfs -v
}

retire_sshfs() {
    # The dde drive was previously reached via a fuse.sshfs systemd automount
    # at the same mount point. Comment out its fstab entry and stop its units
    # so the NFS mount can take over the path.
    if grep -E "^[^#].*[[:space:]]$CLIENT_MOUNT[[:space:]].*sshfs" /etc/fstab >/dev/null 2>&1; then
        echo "==> Retiring legacy sshfs entry for $CLIENT_MOUNT..."
        cp /etc/fstab "/etc/fstab.bak.nfs-dde.$(date +%Y%m%d%H%M%S)"
        sed -i -E "\|^[^#].*[[:space:]]$CLIENT_MOUNT[[:space:]].*sshfs|s|^|# retired by nfs-dde-drive.sh: |" /etc/fstab
        echo "Commented out in /etc/fstab (backup written to /etc/fstab.bak.nfs-dde.*)"
    else
        echo "==> No active sshfs fstab entry for $CLIENT_MOUNT — nothing to retire."
    fi

    systemctl daemon-reload

    local automount_unit
    automount_unit="$(systemd-escape -p --suffix=automount "$CLIENT_MOUNT")"
    systemctl stop "$automount_unit" 2>/dev/null || true

    if mountpoint -q "$CLIENT_MOUNT" 2>/dev/null; then
        umount "$CLIENT_MOUNT" 2>/dev/null || umount -l "$CLIENT_MOUNT" || true
    fi
}

setup_client() {
    require_root
    local hostname
    hostname="$(hostname -s)"
    if [[ "$hostname" != "$CLIENT_HOST" ]]; then
        echo "Warning: expected hostname '$CLIENT_HOST', got '$hostname'"
        read -rp "Continue anyway? [y/N] " confirm
        [[ "$confirm" =~ ^[Yy]$ ]] || exit 1
    fi

    echo "==> Installing NFS client..."
    apt-get update -qq
    apt-get install -y -qq nfs-common

    retire_sshfs

    echo "==> Creating mount point..."
    mkdir -p "$CLIENT_MOUNT"

    echo "==> Adding fstab entry..."
    # Same options as the ace mapping on ace-linux-2 (nfs-ace-drive.sh).
    local fstab_line="$SERVER_HOST:$EXPORT_PATH  $CLIENT_MOUNT  nfs  defaults,nofail,rw,bg,intr,soft,timeo=50  0  0"

    if grep -E "^[^#]*$SERVER_HOST:$EXPORT_PATH[[:space:]]" /etc/fstab >/dev/null 2>&1; then
        echo "fstab entry already exists:"
        grep "$SERVER_HOST:$EXPORT_PATH" /etc/fstab
        echo "Skipping — edit /etc/fstab manually if you need to change it."
    else
        echo "$fstab_line" >> /etc/fstab
        echo "Added to fstab: $fstab_line"
    fi

    systemctl daemon-reload

    echo "==> Mounting..."
    mount "$CLIENT_MOUNT" || {
        echo "Mount failed. Check that:"
        echo "  1. $SERVER_HOST is reachable: ping $SERVER_HOST"
        echo "  2. NFS server is running on $SERVER_HOST: showmount -e $SERVER_HOST"
        echo "  3. Firewall allows NFS (port 2049)"
        exit 1
    }

    echo "==> Creating canonical reference $CANONICAL_LINK -> $CLIENT_MOUNT..."
    if [[ -L "$CANONICAL_LINK" ]]; then
        ln -sfn "$CLIENT_MOUNT" "$CANONICAL_LINK"
    elif [[ -e "$CANONICAL_LINK" ]]; then
        echo "Warning: $CANONICAL_LINK exists and is not a symlink — leaving it alone."
        echo "Resolve manually, then run: scripts/setup/canonical-drive-links.sh"
    else
        ln -s "$CLIENT_MOUNT" "$CANONICAL_LINK"
    fi

    echo "==> Done. Verify with: ls $CANONICAL_LINK"
    ls "$CANONICAL_LINK" | head -10
}

verify() {
    echo "==> Checking NFS..."
    local hostname
    hostname="$(hostname -s)"

    if [[ "$hostname" == "$SERVER_HOST" ]]; then
        echo "On server ($SERVER_HOST):"
        echo "  Exports:"
        exportfs -v 2>/dev/null || echo "  (exportfs not available — NFS server not installed?)"
        echo "  NFS service:"
        systemctl is-active nfs-kernel-server 2>/dev/null || echo "  not running"
    fi

    if [[ "$hostname" == "$CLIENT_HOST" ]]; then
        echo "On client ($CLIENT_HOST):"
        echo "  Mount status:"
        if mountpoint -q "$CLIENT_MOUNT" 2>/dev/null; then
            echo "  $CLIENT_MOUNT is mounted"
            df -h "$CLIENT_MOUNT"
        else
            echo "  $CLIENT_MOUNT is NOT mounted"
            echo "  Try: sudo mount $CLIENT_MOUNT"
        fi
        echo "  Canonical reference:"
        if [[ -L "$CANONICAL_LINK" ]]; then
            echo "  $CANONICAL_LINK -> $(readlink "$CANONICAL_LINK")"
        else
            echo "  $CANONICAL_LINK is NOT a symlink — run scripts/setup/canonical-drive-links.sh"
        fi
    fi

    echo "  Showmount (from $hostname):"
    showmount -e "$SERVER_HOST" 2>/dev/null || echo "  (cannot reach NFS server)"
}

case "$MODE" in
    server) setup_server ;;
    client) setup_client ;;
    verify) verify ;;
    *)      usage ;;
esac
