#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

SOURCE="$ROOT_DIR/specs/wrk/WRK-624/plan.md"
OUT="$TMP_DIR/claude-bundle.md"
python3 "$ROOT_DIR/scripts/review/build-claude-plan-bundle.py" --input "$SOURCE" --output "$OUT"

src_bytes="$(wc -c < "$SOURCE")"
out_bytes="$(wc -c < "$OUT")"

if [[ "$out_bytes" -ge "$src_bytes" ]]; then
  echo "Bundle is not smaller than source" >&2
  exit 1
fi

for heading in "# Claude Compact Plan Review Bundle" "## Executive Summary" "## Review Matrix" "## Testing Strategy" "## Acceptance Criteria"; do
  if ! rg -q "^${heading//\#/\\#}" "$OUT"; then
    echo "Missing heading: $heading" >&2
    exit 1
  fi
done

echo "Claude compact bundle test passed (${out_bytes} < ${src_bytes} bytes)."
