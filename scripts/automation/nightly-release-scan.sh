#!/usr/bin/env bash
# nightly-release-scan.sh — Detect AI tool version changes and create WRK items.
#
# Compares installed CLI versions against config/ai-tools/release-scan-state.yaml.
# When a new version is found, delegates to release_scan_wrk.py to create a WRK
# item prompting the human to run /release-notes-adoption next session.
#
# Usage:
#   bash scripts/automation/nightly-release-scan.sh [--dry-run] [--provider claude|codex|gemini|all]
#
# Exit codes: 0 = success (including "no changes"), 1 = internal error
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# ── Parse arguments ──────────────────────────────────────────────────
DRY_RUN=""
PROVIDER="all"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)  DRY_RUN="--dry-run"; shift ;;
        --provider) PROVIDER="${2:-all}"; shift 2 ;;
        *)          echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

# ── Resolve Python ───────────────────────────────────────────────────
source "${REPO_ROOT}/scripts/lib/python-resolver.sh"

# ── Detect installed versions ────────────────────────────────────────
_get_version() {
    local cmd="$1"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo ""
        return
    fi
    "$cmd" --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo ""
}

CLAUDE_V=""
CODEX_V=""
GEMINI_V=""

case "$PROVIDER" in
    all)
        CLAUDE_V=$(_get_version claude)
        CODEX_V=$(_get_version codex)
        GEMINI_V=$(_get_version gemini)
        ;;
    claude) CLAUDE_V=$(_get_version claude) ;;
    codex)  CODEX_V=$(_get_version codex) ;;
    gemini) GEMINI_V=$(_get_version gemini) ;;
    *)      echo "Unknown provider: $PROVIDER" >&2; exit 1 ;;
esac

VERSIONS="claude=${CLAUDE_V},codex=${CODEX_V},gemini=${GEMINI_V}"

echo "Detected versions: claude=${CLAUDE_V:-n/a} codex=${CODEX_V:-n/a} gemini=${GEMINI_V:-n/a}"

# ── Delegate to Python for state comparison + WRK creation ───────────
uv run --no-project ${PYTHON} "${REPO_ROOT}/scripts/automation/release_scan_wrk.py" \
    --workspace-root "${REPO_ROOT}" \
    --versions "${VERSIONS}" \
    --providers "${PROVIDER}" \
    ${DRY_RUN}
