#!/usr/bin/env bash
set -euo pipefail

action="${1:-}"
shift || true

case "$action" in
    review)
        if command -v gemini >/dev/null 2>&1; then
            echo "OK"
        else
            echo "NO_OUTPUT"
        fi
        ;;
    *)
        if command -v gemini >/dev/null 2>&1; then
            echo "OK"
        else
            echo "ERROR"
        fi
        ;;
esac
