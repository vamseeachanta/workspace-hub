#!/usr/bin/env bash
# assetutilities-pre-push.sh — Pre-push gate: run downstream contract tests
# when assetutilities/src/ changes are being pushed.
# Registered in assetutilities/.pre-commit-config.yaml stages: [push]
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

# ── Bypass support ────────────────────────────────────────────────────────────
if [[ "${SKIP_CROSS_REPO_CHECK:-0}" == "1" ]]; then
    echo "SKIP_CROSS_REPO_CHECK=1: bypassing cross-repo integration check" >&2
    BYPASS_LOG="${REPO_ROOT}/logs/hooks/pre-push-bypass.jsonl"
    mkdir -p "$(dirname "$BYPASS_LOG")"
    printf '{"timestamp":"%s","wrk":"WRK-1091","reason":"SKIP_CROSS_REPO_CHECK","script":"assetutilities-pre-push.sh"}\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$BYPASS_LOG" || true
    exit 0
fi

# ── Detect if assetutilities/src/ changed in the commits being pushed ─────────
# This script is called by pre-commit which is configured with `files: ^src/`
# so we know assetutilities/src/ changed if this script is executing.
ASSETUTILITIES_CHANGED=true

if [[ "$ASSETUTILITIES_CHANGED" != "true" ]]; then
    exit 0
fi

echo "assetutilities/src/ changed — running downstream contract tests..." >&2
INTEGRATION_SCRIPT="${REPO_ROOT}/scripts/testing/run-cross-repo-integration.sh"
if [[ ! -x "$INTEGRATION_SCRIPT" ]]; then
    echo "Integration script not found: $INTEGRATION_SCRIPT — skipping" >&2
    exit 0
fi

if ! bash "$INTEGRATION_SCRIPT" --fail-fast; then
    echo "" >&2
    echo "Cross-repo contract tests FAILED — push blocked." >&2
    echo "  Fix the failing downstream contracts before pushing assetutilities changes." >&2
    echo "  To bypass: SKIP_CROSS_REPO_CHECK=1 git push" >&2
    exit 1
fi
