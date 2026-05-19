#!/usr/bin/env bash
# detect-os.sh — Canonical OS detection for workspace-hub setup tooling.
# Issue: vamseeachanta/workspace-hub#2751 (Phase 1, G1+r2-C2)
#
# Emits one of: linux | macos | windows | unknown
#
# Vocabulary aligned with scripts/memory/bootstrap-machine.sh:26 (which already
# emits `macos` for Darwin). All setup scripts source this helper instead of
# duplicating inline `case $(uname -s)` blocks.
#
# Usage:
#   source scripts/setup/lib/detect-os.sh
#   os="$(detect_os)" || { echo "unsupported OS" >&2; exit 1; }

detect_os() {
    case "$(uname -s 2>/dev/null)" in
        Linux*)               echo "linux"  ;;
        Darwin*)              echo "macos"  ;;
        MINGW*|CYGWIN*|MSYS*) echo "windows" ;;
        *)                    echo "unknown"; return 1 ;;
    esac
}
