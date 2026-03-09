#!/usr/bin/env bash
# pre-push.sh — Pre-push gate hook
# Delivered by WRK-1070. WRK-1064 will add further gates (test suite, etc.).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
if command -v gitleaks >/dev/null 2>&1; then
    bash "${REPO_ROOT}/scripts/security/secrets-scan.sh"
else
    echo "[pre-push] gitleaks not installed — skipping secrets scan (install via pre-commit)" >&2
fi
