#!/usr/bin/env bash
# canonical-drive-links.sh — Make shared-drive references unique and
# consistent across the machine fleet.
#
# Convention (docs/standards/canonical-drive-references.md):
#   Every shared drive has ONE canonical path that resolves on EVERY
#   machine: <MNT_ROOT>/<drive>. On the owner machine it is the physical
#   mount; everywhere else it is a symlink to the NFS transport path
#   <REMOTE_ROOT>/<owner-host>/<drive>. Repos, scripts, and docs must
#   reference the canonical path only — never the transport path.
#
# Idempotent. Run as root on ANY machine in the fleet:
#   sudo bash scripts/setup/canonical-drive-links.sh
#
# The NFS mounts themselves are set up by the per-drive scripts
# (nfs-ace-drive.sh, nfs-dde-drive.sh); this script only reconciles the
# canonical symlinks on top of them.
set -euo pipefail

MNT_ROOT="/mnt"                 # abs-path-allowed
REMOTE_ROOT="/mnt/remote"       # abs-path-allowed

# Registry: drive -> owner host. Add a line per new shared drive.
declare -A DRIVE_OWNER=(
    [ace]="ace-linux-1"
    [dde]="ace-linux-2"
)

if [[ $EUID -ne 0 ]]; then
    echo "Error: must run as root (sudo)"
    exit 1
fi

host="$(hostname -s)"
status=0

for drive in "${!DRIVE_OWNER[@]}"; do
    owner="${DRIVE_OWNER[$drive]}"
    canonical="$MNT_ROOT/$drive"
    transport="$REMOTE_ROOT/$owner/$drive"

    if [[ "$host" == "$owner" ]]; then
        # Owner machine: canonical path must be the physical mount.
        if mountpoint -q "$canonical" 2>/dev/null; then
            echo "OK    $canonical (physical mount, this machine owns '$drive')"
        else
            echo "FAIL  $canonical is not mounted — check the local disk / fstab"
            status=1
        fi
        continue
    fi

    # Remote machine: canonical path must be a symlink to the transport path.
    if [[ -L "$canonical" ]]; then
        if [[ "$(readlink "$canonical")" == "$transport" ]]; then
            echo "OK    $canonical -> $transport"
        else
            ln -sfn "$transport" "$canonical"
            echo "FIXED $canonical -> $transport (was $(readlink "$canonical" || true))"
        fi
    elif mountpoint -q "$canonical" 2>/dev/null; then
        echo "WARN  $canonical is a real mount but '$drive' is owned by $owner — resolve manually"
        status=1
    elif [[ -e "$canonical" ]]; then
        echo "WARN  $canonical exists and is not a symlink — resolve manually"
        status=1
    else
        ln -s "$transport" "$canonical"
        echo "LINKED $canonical -> $transport"
    fi

    # Surface (but don't fail on) a transport path that isn't wired up yet.
    if [[ ! -d "$transport" ]]; then
        echo "NOTE  transport $transport does not exist yet — run the NFS setup script for '$drive'"
    fi
done

exit "$status"
