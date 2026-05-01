#!/usr/bin/env bash
# ntfs3-trial.sh — guided trial of the in-kernel ntfs3 driver for /mnt/local-analysis.
#
# Pairs with: docs/runbooks/perf-tuning.md "Next action" section.
#
# Phases (run in order, separately, on different invocations):
#   probe      Read-only diagnostic. Verifies kernel module, prints fstab + open
#              handles + hermes processes. Safe; run any time. (default)
#   swap       Destructive-adjacent. Backs up fstab, runs pre-bench, unmounts,
#              probes volume cleanliness, swaps fstab to ntfs3, remounts, runs
#              post-bench. Asks for confirmation before each destructive step.
#   rollback   Restore /etc/fstab.pre-ntfs3 and remount with ntfs-3g.
#   bench      Run perf-bench.sh with a manual label (debugging).
#
# Refuses to run `swap` non-interactively or while CWD is inside the target mount.

set -euo pipefail

PHASE="${1:-probe}"
MOUNT="/mnt/local-analysis"
DEVICE="/dev/sdc1"
FSTAB="/etc/fstab"
FSTAB_BACKUP="/etc/fstab.pre-ntfs3"
LOG="/tmp/ntfs3-trial-$(date +%Y%m%d-%H%M%S).log"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "${MOUNT}/workspace-hub")"
BENCH="${REPO_ROOT}/scripts/benchmarks/perf-bench.sh"

exec > >(tee -a "$LOG") 2>&1

confirm() {
    [[ -t 0 ]] || { echo "ABORT: non-interactive shell, refusing destructive step ($1)"; exit 2; }
    read -r -p "$1 [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]]
}

probe() {
    echo "=== Phase: probe (read-only) ==="
    echo "Log: $LOG"
    echo ""

    echo "[1/5] Kernel module ntfs3"
    local module_file
    module_file=$(find "/lib/modules/$(uname -r)/kernel/fs/ntfs3" -name 'ntfs3.ko*' 2>/dev/null | head -1)
    if [[ -z "$module_file" ]]; then
        echo "      FAIL: module file not found for kernel $(uname -r)."
        echo "      Install with: sudo apt install linux-modules-extra-\$(uname -r)"
        exit 1
    fi
    echo "      module file: $module_file"
    if grep -q ntfs3 /proc/filesystems; then
        echo "      OK: ntfs3 already loaded"
    else
        echo "      module shipped but not loaded — attempting modprobe"
        if ! sudo modprobe ntfs3; then
            echo "      FAIL: modprobe failed. Common cause: this script was run"
            echo "      without a real TTY (sudo can't prompt). Re-run from an"
            echo "      interactive terminal."
            exit 1
        fi
        if ! grep -q ntfs3 /proc/filesystems; then
            echo "      FAIL: modprobe returned 0 but ntfs3 still not in /proc/filesystems"
            exit 1
        fi
        echo "      OK: ntfs3 loaded"
    fi

    echo "[2/5] Current mount of $MOUNT"
    mount | grep -F "$MOUNT" || { echo "      FAIL: not mounted"; exit 1; }

    echo "[3/5] fstab line"
    grep -F "$MOUNT" "$FSTAB" || echo "      (no fstab entry — would not auto-mount on boot)"

    echo "[4/5] Open handles (must be empty before swap)"
    local handles
    handles=$(sudo lsof "$MOUNT" 2>/dev/null | tail -n +2 | wc -l)
    if (( handles == 0 )); then
        echo "      OK: no open handles"
    else
        echo "      WARN: $handles open handles — close before running swap:"
        sudo lsof "$MOUNT" 2>/dev/null | head -10
    fi

    echo "[5/5] Hermes processes"
    if pgrep -af hermes >/dev/null 2>&1; then
        echo "      WARN: hermes running — stop before swap"
        pgrep -af hermes
    else
        echo "      OK: hermes not running"
    fi

    echo ""
    echo "Next: $0 swap"
}

swap() {
    echo "=== Phase: swap (DESTRUCTIVE — will unmount $MOUNT) ==="
    echo "Log: $LOG"
    echo ""

    case "$PWD" in
        "$MOUNT"|"$MOUNT"/*)
            echo "ABORT: current working directory is inside $MOUNT."
            echo "Run from a path outside the target mount (e.g., cd \$HOME)."
            exit 2
            ;;
    esac

    confirm "Run pre-ntfs3 benchmark first?" && "$BENCH" pre-ntfs3 || echo "(skipped pre-bench)"

    if [[ ! -f "$FSTAB_BACKUP" ]]; then
        echo "Backing up fstab → $FSTAB_BACKUP"
        sudo cp "$FSTAB" "$FSTAB_BACKUP"
    else
        echo "fstab backup already exists at $FSTAB_BACKUP — leaving as-is"
    fi

    confirm "Unmount $MOUNT now?" || { echo "Aborted by user."; exit 0; }

    local handles
    handles=$(sudo lsof "$MOUNT" 2>/dev/null | tail -n +2 | wc -l)
    if (( handles > 0 )); then
        echo "FAIL: $handles open handles remain. Inspect with:"
        echo "  sudo lsof $MOUNT"
        echo "  sudo fuser -vm $MOUNT"
        exit 1
    fi

    sudo umount "$MOUNT"
    echo "Unmounted."

    echo ""
    echo "ntfsfix --no-action probe (read-only):"
    sudo ntfsfix --no-action "$DEVICE" || {
        echo "WARN: ntfsfix probe reported issues. Review output above."
        confirm "Continue with ntfs3 swap anyway?" || {
            echo "Reverting: remounting with ntfs-3g (fstab unchanged)"
            sudo mount "$MOUNT"
            exit 0
        }
    }

    confirm "Swap fstab to ntfs3 and remount?" || {
        echo "Reverting: remounting with ntfs-3g (fstab unchanged)"
        sudo mount "$MOUNT"
        exit 0
    }

    echo "Editing fstab — line containing $MOUNT: ntfs-3g → ntfs3"
    sudo sed -i.bak "\\|${MOUNT}|s/ntfs-3g/ntfs3/" "$FSTAB"
    grep -F "$MOUNT" "$FSTAB"

    sudo systemctl daemon-reload
    sudo mount "$MOUNT"

    if mount | grep -F "$MOUNT" | grep -q ntfs3; then
        echo "OK: $MOUNT is now mounted with ntfs3"
    else
        echo "WARN: did not land on ntfs3 — current mount line:"
        mount | grep -F "$MOUNT"
    fi

    echo ""
    echo "Post-ntfs3 benchmark"
    "$BENCH" post-ntfs3

    echo ""
    echo "=== Comparison ==="
    column -t -s $'\t' "${REPO_ROOT}/scripts/benchmarks/results.tsv" | grep -E "label|pre-ntfs3|post-ntfs3" || true

    echo ""
    echo "If git_status improved >10x: success — keep ntfs3."
    echo "If little/no improvement: rollback with: $0 rollback"
}

rollback() {
    echo "=== Phase: rollback (restore ntfs-3g) ==="
    [[ -f "$FSTAB_BACKUP" ]] || { echo "FAIL: $FSTAB_BACKUP not found"; exit 1; }

    case "$PWD" in
        "$MOUNT"|"$MOUNT"/*)
            echo "ABORT: cwd is inside $MOUNT — cd elsewhere first"
            exit 2
            ;;
    esac

    sudo umount "$MOUNT" 2>/dev/null || true
    sudo cp "$FSTAB_BACKUP" "$FSTAB"
    sudo systemctl daemon-reload
    sudo mount "$MOUNT"

    echo "Restored. Current mount:"
    mount | grep -F "$MOUNT"
}

bench() {
    "$BENCH" "${2:-manual-$(date +%s)}"
}

case "$PHASE" in
    probe)    probe ;;
    swap)     swap ;;
    rollback) rollback ;;
    bench)    shift; bench "$@" ;;
    *)        echo "Usage: $0 {probe|swap|rollback|bench [label]}"; exit 1 ;;
esac
