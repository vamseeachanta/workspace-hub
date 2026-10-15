#!/usr/bin/env bash
# Refuse unsafe checkout locations without creating or changing anything.
# Measured on 2026-10-15 for 17,771 files: an NTFS-formatted FUSE data volume
# took 133 minutes to add and 52 minutes to remove a worktree; the host SSD
# took 130 seconds and 33 seconds. Sparse checkouts still require a safe volume.
# Exit codes: 0 safe, 2 usage, 3 unsafe/unknown type, 4 insufficient/unknown space.
# Start helper: worktree_location_guard.sh --dest "$W" --min-free-gb "$FLOOR" || exit $?
set -euo pipefail

# Shell patterns are intentional; extend this one list when new types are found.
SLOW_TYPES=(fuseblk fuse 'fuse.*' ntfs ntfs3 ntfs-3g)

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
        printf 'REFUSED (exit 3): %s is on a %s mount: an NTFS or FUSE volume. Job worktrees are created on the host SSD: on such a volume a 17,771-file checkout took 133 minutes to add and 52 minutes to remove, against 130 seconds and 33 seconds on the host SSD. Point the checkout root at a folder on the host SSD (a sparse checkout there is fine; a sparse checkout on this volume is not). The job start is stopped; nothing was done and no fallback to this volume or to any other folder was made.\n' "$dest" "$fs_type" >&2
        exit 3
done

if ! df_output=$(df -Pk -- "$ancestor" 2>/dev/null); then
    printf 'REFUSED (exit 4): %s on %s mount: free space could not be read; floor=%s GB. Nothing was done.\n' "$dest" "$fs_type" "$min_free_gb" >&2
    exit 4
fi
free_kb=$(printf '%s\n' "$df_output" | awk 'NR == 2 {print $4}')
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
