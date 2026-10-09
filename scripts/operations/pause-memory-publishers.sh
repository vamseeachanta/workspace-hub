#!/usr/bin/env bash
set -euo pipefail

MARKER="#PAUSED-X02 "
DATE_STAMP="${PAUSE_MEMORY_DATE:-$(date +%Y%m%d-%H%M%S)}"
CRONTAB_BIN="${CRONTAB_BIN:-crontab}"
BACKUP_PATH="${PAUSE_MEMORY_BACKUP:-${HOME}/crontab.bak-${DATE_STAMP}}"
TARGETS=("scripts/memory/bridge-hermes-claude.sh" "scripts/cron/comprehensive-learning-nightly.sh")

run_crontab() {
    "$CRONTAB_BIN" "$@"
}

usage() {
    echo "usage: $0 --check|--apply|--undo" >&2
}

mode="${1:-}"
case "$mode" in
    --check|--apply|--undo) ;;
    *) usage; exit 2 ;;
esac

current="$(mktemp)"
updated="$(mktemp)"
trap 'rm -f "$current" "$updated"' EXIT

if ! run_crontab -l > "$current" 2>/dev/null; then
    : > "$current"
fi

transform_apply() {
    local line="$1"
    for target in "${TARGETS[@]}"; do
        if [[ "$line" == *"$target"* && "$line" != "${MARKER}"* ]]; then
            printf '%s%s\n' "$MARKER" "$line"
            return
        fi
    done
    printf '%s\n' "$line"
}

transform_undo() {
    local line="$1"
    if [[ "$line" == "${MARKER}"* ]]; then
        printf '%s\n' "${line#"$MARKER"}"
    else
        printf '%s\n' "$line"
    fi
}

case "$mode" in
    --check)
        matches=0
        for target in "${TARGETS[@]}"; do
            if grep -F "$target" "$current" >/dev/null 2>&1; then
                matches=$((matches + 1))
                echo "would pause: $target"
            else
                echo "not found: $target"
            fi
        done
        exit 0
        ;;
    --apply)
        cp "$current" "$BACKUP_PATH"
        while IFS= read -r line || [[ -n "$line" ]]; do
            transform_apply "$line"
        done < "$current" > "$updated"
        run_crontab - < "$updated"
        echo "backup: $BACKUP_PATH"
        ;;
    --undo)
        while IFS= read -r line || [[ -n "$line" ]]; do
            transform_undo "$line"
        done < "$current" > "$updated"
        run_crontab - < "$updated"
        ;;
esac
