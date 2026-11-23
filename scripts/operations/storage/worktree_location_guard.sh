#!/usr/bin/env bash
# Refuse unsafe checkout locations without creating or changing anything.
# Measured on 2026-10-15 for 17,771 files: an NTFS-formatted FUSE data volume
# took 133 minutes to add and 52 minutes to remove a worktree; the host SSD
# took 130 seconds and 33 seconds. Sparse checkouts still require a safe volume.
# Exit codes: 0 safe, 2 usage, 3 unsafe/unknown type, 4 insufficient/unknown space.
# Start helper: worktree_location_guard.sh --dest "$W" --min-free-gb "$FLOOR" || exit $?
set -euo pipefail

# Shell patterns are intentional; extend this one list when new types are found.
SLOW_TYPES=(fuseblk fuse 'fuse.*' ntfs ntfs3 ntfs-3g
            9p v9fs drvfs cifs smb smb2 smb3 nfs nfs3 nfs4)

usage() {
    printf 'Usage: %s --dest <dir> [--min-free-gb <n>]\n' "${0##*/}" >&2
    exit 2
}

dest=''
min_free_gb=${JOB_CHECKOUT_MIN_FREE_GB-50}
while (($#)); do
    case $1 in
        --dest) (($# >= 2)) || usage; dest=$2; shift 2 ;;
        --min-free-gb) (($# >= 2)) || usage; min_free_gb=$2; shift 2 ;;
        *) usage ;;
    esac
done
[[ -n $dest && $min_free_gb =~ ^[0-9]+([.][0-9]+)?$ ]] || usage

refuse_location() {
    printf 'REFUSED (exit 3): %s is on a %s. Job worktrees are created on the host SSD: on Linux an NTFS-formatted FUSE volume with a 17,771-file checkout took 133 minutes to add and 52 minutes to remove, against 130 seconds and 33 seconds on the host SSD. Point the checkout root at a folder on the host SSD (a sparse checkout there is fine; a sparse checkout on an unsafe volume is not). The job start is stopped; nothing was done and no fallback to this volume or to any other folder was made.\n' "$dest" "$1" >&2
    exit 3
}

windows=false
case $(uname -s 2>/dev/null) in
    MINGW*|MSYS*|CYGWIN*) windows=true ;;
esac
if $windows; then
    # Reject UNC before ancestor traversal can reduce it to a local directory.
    [[ $dest != //* && $dest != \\\\* ]] || refuse_location 'network or non-local path'
fi

ancestor=$dest
while [[ ! -e $ancestor ]]; do
    parent=$(dirname -- "$ancestor")
    [[ $parent != "$ancestor" ]] || break
    ancestor=$parent
done
# Resolve symlinks in the existing ancestor before probing its filesystem.
if ! ancestor=$(cd -P -- "$ancestor" 2>/dev/null && pwd -P); then
    printf 'REFUSED (exit 3): %s: filesystem type could not be read; ancestor is not an accessible directory. The job start is stopped; nothing was done and no fallback was made.\n' "$dest" >&2
    exit 3
fi

valid_type() {
    [[ -n $1 && $1 != unknown && $1 != UNKNOWN && $1 != *[[:space:]]* ]]
}
fs_type=''
if $windows; then
    # Git for Windows supplies cygpath. Drive letters alone do not prove locality:
    # a mapped network drive must also be rejected by the fixed-drive query.
    if ! windows_path=$(cygpath -m -- "$ancestor" 2>/dev/null) ||
       [[ ! $windows_path =~ ^[A-Za-z]:/ ]]; then
        refuse_location 'network or non-local path'
    fi
    powershell_tool=''
    for candidate in powershell.exe powershell pwsh.exe pwsh; do
        if command -v "$candidate" >/dev/null 2>&1; then
            powershell_tool=$candidate
            break
        fi
    done
    [[ -n $powershell_tool ]] || refuse_location 'network or non-local path'
    drive=${windows_path:0:2}
    if ! drive_type=$("$powershell_tool" -NoLogo -NoProfile -NonInteractive -Command \
        "(Get-CimInstance -ClassName Win32_LogicalDisk -Filter \"DeviceID='$drive'\").DriveType" 2>/dev/null); then
        refuse_location 'network or non-local path'
    fi
    [[ ${drive_type//$'\r'/} == 3 ]] || refuse_location 'network or non-local path'
    fs_type='windows-local-fixed'
else
    if ! fs_type=$(stat -f -c %T -- "$ancestor" 2>/dev/null) || ! valid_type "$fs_type"; then
        if ! fs_type=$(findmnt -n -o FSTYPE --target "$ancestor" 2>/dev/null) || ! valid_type "$fs_type"; then
            printf 'REFUSED (exit 3): %s: filesystem type could not be read. Choose a folder on the host SSD. The job start is stopped; nothing was done and no fallback was made.\n' "$dest" >&2
            exit 3
        fi
    fi
    for slow_type in "${SLOW_TYPES[@]}"; do
        # The list supports exact types and a trailing * for a type family.
        if [[ $slow_type == *'*' ]]; then
            [[ $fs_type == "${slow_type%\*}"* ]] || continue
        else
            [[ $fs_type == "$slow_type" ]] || continue
        fi
        refuse_location "$fs_type mount"
    done
fi

free_kb=''
if ! $windows && space=$(stat -f -c '%a %S' -- "$ancestor" 2>/dev/null); then
    # stat reports available blocks and bytes per block, independent of names.
    read -r available_blocks block_size extra <<< "$space" || true
    if [[ $available_blocks =~ ^[0-9]+$ && $block_size =~ ^[0-9]+$ &&
          $block_size != 0 && -z $extra && $space != *$'\n'* ]]; then
        free_kb=$(awk -v blocks="$available_blocks" -v size="$block_size" \
            'BEGIN {printf "%.0f", int(blocks * size / 1024)}')
    fi
fi
if [[ -z $free_kb ]]; then
    if ! df_output=$(df -Pk -- "$ancestor" 2>/dev/null); then
        df_output=''
    fi
    # Source and mount names may contain spaces. Anchor on a capacity field
    # preceded by numeric size, used and available fields, never a fixed column.
    free_kb=$(printf '%s\n' "$df_output" | awk '
        NR > 1 {
            for (i = 5; i <= NF; i++) {
                if ($i ~ /^[0-9]+%$/ && $(i-3) ~ /^[0-9]+$/ &&
                    $(i-2) ~ /^[0-9]+$/ && $(i-1) ~ /^[0-9]+$/) {
                    print $(i-1)
                    exit
                }
            }
        }')
fi

if [[ ! $free_kb =~ ^[0-9]+$ ]]; then
    printf 'REFUSED (exit 4): %s on %s mount: free space could not be read; floor=%s GB. Nothing was done.\n' "$dest" "$fs_type" "$min_free_gb" >&2
    exit 4
fi
free_gb=$(awk -v kb="$free_kb" 'BEGIN {printf "%.1f", kb / 1048576}')
if ! awk -v kb="$free_kb" -v floor="$min_free_gb" 'BEGIN {exit !(kb >= floor * 1048576)}'; then
    printf 'REFUSED (exit 4): %s on %s mount: %s; free_gb=%s is below floor=%s GB. Nothing was done.\n' "$dest" "$fs_type" "$ancestor" "$free_gb" "$min_free_gb" >&2
    exit 4
fi
printf 'worktree_location=ok fs=%s free_gb=%s dest=%s\n' "$fs_type" "$free_gb" "$dest"
