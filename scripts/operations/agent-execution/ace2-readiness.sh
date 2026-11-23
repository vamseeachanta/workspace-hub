#!/usr/bin/env bash
# Compatibility wrapper for the reusable Hermes workstation preflight checker.
set -euo pipefail

REMOTE="${REMOTE:-ace-linux-2}"
FORMAT_ARGS=()

usage() {
  cat <<USAGE
Usage: bash scripts/operations/agent-execution/ace2-readiness.sh [--remote HOST] [--markdown]

Runs the canonical Hermes preflight readiness probe for an overflow worker host.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote) REMOTE="$2"; shift 2 ;;
    --markdown) FORMAT_ARGS+=(--markdown); shift ;;
    --json) FORMAT_ARGS+=(--json); shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
cd "$REPO_ROOT"

uv run python -m scripts.preflight.hermes_preflight --target "$REMOTE" "${FORMAT_ARGS[@]}"
