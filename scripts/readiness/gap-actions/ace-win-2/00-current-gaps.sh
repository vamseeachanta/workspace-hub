#!/usr/bin/env bash
# Print the live ace-win-2 equality verdicts and the remaining non-OK gaps.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

MACHINE="${1:-ace-win-2}"

if command -v uv >/dev/null 2>&1; then
  PY=(uv run --no-project python)
elif command -v python >/dev/null 2>&1; then
  PY=(python)
else
  PY=(python3)
fi

json="$(uv run --script scripts/readiness/build-equality-matrix.py --json --machine "$MACHINE")"
printf '%s\n' "$json"

printf '\nRemaining non-OK gaps for %s:\n' "$MACHINE"
MATRIX_JSON="$json" "${PY[@]}" - "$MACHINE" <<'PY'
import json
import os
import sys

machine = sys.argv[1]
data = json.loads(os.environ["MATRIX_JSON"]).get(machine, {})
ok = {
    "CONFORMS",
    "EQUAL",
    "EXPECTED-DIFF",
    "EXPECTED-DIVERGENCE",
    "CURATED-FRESH",
    "SKILL-LINKS-OK",
    "PUBLISH-OK",
    "MEMORY-FRESH",
    "PARITY",
}
bad = [(key, value) for key, value in data.items() if value not in ok]
if not bad:
    print("none")
else:
    for key, value in bad:
        print(f"- {key}: {value}")
PY
