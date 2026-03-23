#!/usr/bin/env bash
# nfs-ace-drive.sh — Set up NFS share of /mnt/ace from ace-linux-1 to ace-linux-2.
#
# Run as root on the appropriate machine:
#   ace-linux-1 (server): sudo bash scripts/setup/nfs-ace-drive.sh server
#   ace-linux-2 (client): sudo bash scripts/setup/nfs-ace-drive.sh client
#
# What this does:
#   server: installs nfs-kernel-server, exports /mnt/ace read-only to ace-linux-2
#   client: installs nfs-common, mounts ace-linux-1:/mnt/ace at /mnt/remote/ace-linux-1/ace
#
# Prerequisites:
#   - Both machines on the same LAN
#   - ace-linux-2 can resolve "ace-linux-1" (via /etc/hosts or DNS)
set -euo pipefail

MODE="${1:-}"
EXPORT_PATH="/mnt/ace"
CLIENT_MOUNT="/mnt/remote/ace-linux-1/ace"
SERVER_HOST="ace-linux-1"
CLIENT_HOST="ace-linux-2"

usage() {
    echo "Usage: sudo $0 {server|client|verify}"
    echo ""
    echo "  server  — run on ace-linux-1: install NFS server, export /mnt/ace"
    echo "  client  — run on ace-linux-2: install NFS client, mount ace-linux-1:/mnt/ace"
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

    echo "==> Installing NFS server..."
    apt-get update -qq
    apt-get install -y -qq nfs-kernel-server

    echo "==> Configuring export..."
    local export_line="$EXPORT_PATH    $CLIENT_HOST(rw,sync,no_subtree_check,crossmnt)"

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

    echo "==> Creating mount point..."
    mkdir -p "$CLIENT_MOUNT"

    echo "==> Adding fstab entry..."
    local fstab_line="$SERVER_HOST:$EXPORT_PATH  $CLIENT_MOUNT  nfs  defaults,nofail,rw,bg,intr,soft,timeo=50  0  0"

    if grep -qF "$SERVER_HOST:$EXPORT_PATH" /etc/fstab 2>/dev/null; then
        echo "fstab entry already exists:"
        grep "$SERVER_HOST:$EXPORT_PATH" /etc/fstab
        echo "Skipping — edit /etc/fstab manually if you need to change it."
    else
        echo "$fstab_line" >> /etc/fstab
        echo "Added to fstab: $fstab_line"
    fi

    echo "==> Mounting..."
    mount "$CLIENT_MOUNT" || {
        echo "Mount failed. Check that:"
        echo "  1. ace-linux-1 is reachable: ping $SERVER_HOST"
        echo "  2. NFS server is running on ace-linux-1: showmount -e $SERVER_HOST"
        echo "  3. Firewall allows NFS (port 2049)"
        exit 1
    }

    echo "==> Done. Verify with: ls $CLIENT_MOUNT"
    ls "$CLIENT_MOUNT" | head -10
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
