#!/usr/bin/env bash
set -euo pipefail

action="${1:-}"
shift || true

case "$action" in
    review)
        echo "NO_OUTPUT"
        ;;
    *)
        echo "OK"
        ;;
esac
