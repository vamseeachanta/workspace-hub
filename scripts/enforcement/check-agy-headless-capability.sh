#!/usr/bin/env bash
# check-agy-headless-capability.sh — Level-2 pre-flight for #3207.
#
# agy (Antigravity CLI) is only a valid dispatch provider when it exposes a
# HEADLESS mode (`--print`). This gate confirms that before the wrapper is used,
# so we never ship/dispatch a wrapper that can't run non-interactively.
#
# Exit: 0 = agy headless present (or agy absent on this box — not a failure, other
#           machines legitimately lack it); 1 = agy present but NO --print.
# Env: AGY_CMD (override the binary, for tests).
set -uo pipefail

AGY_CMD="${AGY_CMD:-agy}"

if ! command -v "$AGY_CMD" &>/dev/null; then
  echo "agy not installed (AGY_CMD=$AGY_CMD) — skip (absent != failure)"
  exit 0
fi

# Anchor on the flag column (leading whitespace + the flag), NOT a mention of
# "--print" inside another flag's description (#3207 r1-F7). Capture stderr too.
if "$AGY_CMD" --help 2>&1 | grep -qE '^[[:space:]]+--print[[:space:]]'; then
  echo "agy headless mode (--print) present — dispatch supported"
  exit 0
fi

echo "agy is installed but exposes NO --print (headless) mode — keep agy dispatch unsupported" >&2
exit 1
