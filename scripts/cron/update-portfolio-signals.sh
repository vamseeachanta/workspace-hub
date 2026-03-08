#!/usr/bin/env bash
# update-portfolio-signals.sh — WRK-1020
# Thin wrapper: delegates to uv run --no-project python update_portfolio_signals.py
# Usage: bash update-portfolio-signals.sh [--dry-run] [--lookback N] [--output PATH]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec uv run --no-project python "${SCRIPT_DIR}/update_portfolio_signals.py" "$@"
