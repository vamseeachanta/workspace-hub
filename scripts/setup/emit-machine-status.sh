#!/usr/bin/env bash
# emit-machine-status.sh — Entry point for per-machine harness-parity status emission.
# Issue: vamseeachanta/workspace-hub#2751 (Phase 3, G9)
#
# Thin wrapper that sources the logic from lib/emit-machine-status.sh and invokes
# the main entry. Output paths and policies documented in the lib script.
#
# Usage:
#   bash scripts/setup/emit-machine-status.sh                # uses git rev-parse root
#   bash scripts/setup/emit-machine-status.sh <repo_root>    # explicit (tests/CI)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/emit-machine-status.sh
source "${SCRIPT_DIR}/lib/emit-machine-status.sh"

REPO_ROOT_ARG="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
emit_machine_status "${REPO_ROOT_ARG}"

echo ""
echo "Next steps:"
echo "  1. Review: cat config/machine-baselines/*.md"
echo "  2. Commit + push the new/updated baseline files."
echo "  3. Post the .md content as a comment on operational tracker #2753:"
echo "     https://github.com/vamseeachanta/workspace-hub/issues/2753"
