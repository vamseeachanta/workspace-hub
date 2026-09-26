#!/usr/bin/env bash
# AI Review Routing Gate — shell wrapper for review_routing_gate.py
#
# Usage:
#   scripts/ai/review-routing-gate.sh --pr 42
#   git diff main...HEAD | scripts/ai/review-routing-gate.sh --stdin
#   scripts/ai/review-routing-gate.sh --diff-file changes.diff
#
# Policy: docs/standards/AI_REVIEW_ROUTING_POLICY.md
# Issue: #1515

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

exec uv run python "$SCRIPT_DIR/review_routing_gate.py" "$@"
