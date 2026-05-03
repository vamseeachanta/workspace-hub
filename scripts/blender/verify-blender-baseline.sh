#!/usr/bin/env bash
# verify-blender-baseline.sh — Canonical Blender headless baseline validator wrapper.
# Final YAML owner for issue #2270. Runs a minimal cube-render smoke case.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DEFAULT_VERDICT="$REPO_ROOT/logs/engineering/blender-baseline/latest-verdict.yaml"
DEFAULT_RENDER_DIR="${TMPDIR:-/tmp}/blender-baseline-smoke"
DEFAULT_RENDER_OUTPUT="$DEFAULT_RENDER_DIR/smoke-render.png"
if command -v uv >/dev/null 2>&1; then
    PYTHON_CMD=(uv run python)
else
    PYTHON_CMD=(python3)
fi

VERDICT_PATH="$DEFAULT_VERDICT"
RENDER_OUTPUT="${BLENDER_RENDER_OUTPUT:-$DEFAULT_RENDER_OUTPUT}"
BLENDER_BIN="${BLENDER_BIN:-blender}"
SMOKE_SCRIPT="$REPO_ROOT/scripts/blender/smoke-render.py"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --verdict)
            VERDICT_PATH="$2"
            shift 2
            ;;
        --output)
            RENDER_OUTPUT="$2"
            shift 2
            ;;
        --help)
            cat <<'EOF'
Usage: scripts/blender/verify-blender-baseline.sh [--verdict PATH] [--output PATH]

Validates the repo's Blender headless baseline by running:
  blender -b --python scripts/blender/smoke-render.py -- --output <png>

Environment overrides:
  BLENDER_BIN       Path/name of Blender binary (testable dependency injection)
  BLENDER_HOSTNAME  Machine name to write into the verdict
EOF
            exit 0
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

mkdir -p "$(dirname "$VERDICT_PATH")" "$(dirname "$RENDER_OUTPUT")"

write_verdict() {
    local verdict="$1"
    local error_summary="${2:-}"
    local error_message="${3:-}"
    local version="${4:-}"
    "${PYTHON_CMD[@]}" - "$VERDICT_PATH" "$verdict" "$error_summary" "$error_message" "$version" "$RENDER_OUTPUT" <<'PY'
import os, socket, sys, yaml
from datetime import UTC, datetime
path, verdict, error_summary, error_message, version, render_output = sys.argv[1:7]
payload = {
    "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "machine": os.environ.get("BLENDER_HOSTNAME") or socket.gethostname(),
    "tool": "blender",
    "overall_verdict": verdict,
    "smoke_case": "cube-render",
    "verification_method": "blender -b --python scripts/blender/smoke-render.py",
}
if version:
    payload["version"] = version
if verdict == "PASS":
    payload["render_output"] = render_output
else:
    payload["error_summary"] = error_summary
    payload["error_message"] = error_message
with open(path, "w", encoding="utf-8") as f:
    yaml.safe_dump(payload, f, sort_keys=False)
PY
}

resolve_blender() {
    if [[ -x "$BLENDER_BIN" ]]; then
        printf '%s\n' "$BLENDER_BIN"
        return 0
    fi
    if command -v "$BLENDER_BIN" >/dev/null 2>&1; then
        command -v "$BLENDER_BIN"
        return 0
    fi
    return 1
}

if ! RESOLVED_BLENDER="$(resolve_blender)"; then
    msg="ERROR: Blender binary not found: $BLENDER_BIN"
    echo "$msg" >&2
    write_verdict "FAIL" "missing-blender" "$msg"
    exit 1
fi

version_output="$($RESOLVED_BLENDER --version 2>&1 || true)"
version="$("${PYTHON_CMD[@]}" - "$version_output" <<'PY'
import re, sys
text = sys.argv[1]
match = re.search(r"Blender\s+([0-9]+(?:\.[0-9]+){1,2})", text)
print(match.group(1) if match else "unknown")
PY
)"

render_stderr="${TMPDIR:-/tmp}/blender-baseline-render-stderr.$$"
if ! "$RESOLVED_BLENDER" -b --python "$SMOKE_SCRIPT" -- --output "$RENDER_OUTPUT" 2>"$render_stderr"; then
    msg="$(cat "$render_stderr")"
    rm -f "$render_stderr"
    echo "$msg" >&2
    write_verdict "FAIL" "render-failure" "$msg" "$version"
    exit 1
fi
rm -f "$render_stderr"

if [[ ! -s "$RENDER_OUTPUT" ]]; then
    msg="ERROR: smoke render did not create a non-empty PNG at $RENDER_OUTPUT"
    echo "$msg" >&2
    write_verdict "FAIL" "missing-render-output" "$msg" "$version"
    exit 1
fi

write_verdict "PASS" "" "" "$version"
echo "Blender baseline PASS: version=$version render=$RENDER_OUTPUT verdict=$VERDICT_PATH"
