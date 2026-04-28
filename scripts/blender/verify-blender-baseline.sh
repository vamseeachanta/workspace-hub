#!/usr/bin/env bash
# verify-blender-baseline.sh - Canonical Blender headless smoke validator for issue #2270.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DEFAULT_VERDICT="$REPO_ROOT/logs/engineering/blender-baseline/latest-verdict.yaml"
SMOKE_SCRIPT="$REPO_ROOT/scripts/blender/smoke-render.py"
DEFAULT_OUTPUT_DIR="$REPO_ROOT/logs/engineering/blender-baseline"
CANONICAL_INVOCATION="blender -b --factory-startup --python scripts/blender/smoke-render.py -- --output <output> --metadata <metadata>"

if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: uv is required for workspace-hub Python helpers" >&2
    exit 2
fi
PYTHON_CMD=(uv run python)

VERDICT_PATH="$DEFAULT_VERDICT"
OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --verdict)
            VERDICT_PATH="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

mkdir -p "$(dirname "$VERDICT_PATH")" "$OUTPUT_DIR"

write_failure_verdict() {
    local error_summary="$1"
    local error_message="$2"
    local blender_path="${3:-}"
    local version="${4:-}"
    local smoke_status="${5:-FAIL}"
    local metadata_valid="${6:-false}"
    local png_valid="${7:-false}"
    "${PYTHON_CMD[@]}" - "$VERDICT_PATH" "$error_summary" "$error_message" "$blender_path" "$version" "$smoke_status" "$metadata_valid" "$png_valid" "$CANONICAL_INVOCATION" <<'PY'
from datetime import UTC, datetime
import os
import socket
import sys
import yaml

(
    path,
    error_summary,
    error_message,
    blender_path,
    version,
    smoke_status,
    metadata_valid,
    png_valid,
    canonical_invocation,
) = sys.argv[1:10]
payload = {
    "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "machine": os.environ.get("BLENDER_HOSTNAME") or socket.gethostname(),
    "blender_path": blender_path,
    "version": version,
    "canonical_invocation": canonical_invocation,
    "overall_verdict": "FAIL",
    "error_summary": error_summary,
    "error_message": error_message,
    "smoke_render": {"status": smoke_status},
    "output_validation": {
        "metadata_schema_valid": metadata_valid == "true",
        "png_signature_valid": png_valid == "true",
        "expected_scene_name": "cube-render",
        "expected_output_name": "cube-render_frame-0001.png",
    },
}
if smoke_status == "NOT_RUN":
    payload["output_validation"]["png_signature_valid"] = False
with open(path, "w", encoding="utf-8") as f:
    yaml.safe_dump(payload, f, sort_keys=False)
PY
}

if [[ -n "${BLENDER_BIN:-}" ]]; then
    blender_path="$BLENDER_BIN"
    if [[ ! -x "$blender_path" ]]; then
        msg="ERROR: Blender binary not found or not executable: $blender_path"
        echo "$msg" >&2
        write_failure_verdict "missing-blender" "$msg" "$blender_path" "" "NOT_RUN" "false" "false"
        exit 1
    fi
else
    blender_path="$(command -v blender || true)"
    if [[ -z "$blender_path" ]]; then
        msg="ERROR: Blender binary not found on PATH; set BLENDER_BIN to override"
        echo "$msg" >&2
        write_failure_verdict "missing-blender" "$msg" "" "" "NOT_RUN" "false" "false"
        exit 1
    fi
fi

version_output="$("$blender_path" --version 2>/dev/null || true)"
version="$(printf '%s\n' "$version_output" | sed -nE 's/^Blender[[:space:]]+([0-9]+(\.[0-9]+){1,2}).*/\1/p' | head -1)"
version="${version:-unknown}"

output_file="$OUTPUT_DIR/cube-render_frame-0001.png"
metadata_file="$OUTPUT_DIR/cube-render_frame-0001.metadata.yaml"
rm -f "$output_file" "$metadata_file"

render_stderr="$(mktemp)"
if ! "$blender_path" -b --factory-startup --python "$SMOKE_SCRIPT" -- --output "$output_file" --metadata "$metadata_file" 2>"$render_stderr"; then
    render_error="$(cat "$render_stderr")"
    rm -f "$render_stderr"
    if [[ -n "$render_error" ]]; then
        printf '%s\n' "$render_error" >&2
    fi
    write_failure_verdict "render-failure" "$render_error" "$blender_path" "$version" "FAIL" "false" "false"
    exit 1
fi
rm -f "$render_stderr"

validate_stderr="$(mktemp)"
if "${PYTHON_CMD[@]}" - "$metadata_file" "$output_file" "$VERDICT_PATH" "$blender_path" "$version" "$CANONICAL_INVOCATION" 2>"$validate_stderr" <<'PY'
from datetime import UTC, datetime
from pathlib import Path
import os
import socket
import sys
import yaml

metadata_path, output_path, verdict_path, blender_path, version, canonical_invocation = sys.argv[1:7]
metadata = yaml.safe_load(Path(metadata_path).read_text(encoding="utf-8")) if Path(metadata_path).exists() else None
errors = []

if not isinstance(metadata, dict):
    errors.append("metadata file missing or not a mapping")
else:
    if metadata.get("scene_name") != "cube-render":
        errors.append("scene_name must be cube-render")
    if metadata.get("frame") != 1:
        errors.append("frame must be 1")
    if metadata.get("render_engine") not in {"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"}:
        errors.append("render_engine must be version-safe EEVEE")
    if metadata.get("resolution") != {"width": 320, "height": 240}:
        errors.append("resolution must be 320x240")
    image = metadata.get("image") or {}
    if image.get("format") != "PNG":
        errors.append("image.format must be PNG")
    if Path(str(image.get("output_file", ""))) != Path(output_path):
        errors.append("image.output_file must match validator output path")
    if int(image.get("file_size_bytes") or 0) <= 8:
        errors.append("image.file_size_bytes must be greater than PNG signature size")
    objects = metadata.get("objects") or []
    if not any(row.get("name") == "Smoke_Cube" and row.get("type") == "MESH" for row in objects if isinstance(row, dict)):
        errors.append("objects must include Smoke_Cube mesh")
    if not metadata.get("camera"):
        errors.append("camera must be recorded")

png_signature_valid = False
output = Path(output_path)
if output.exists():
    png_signature_valid = output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
if not png_signature_valid:
    errors.append("output file must have a valid PNG signature")

metadata_schema_valid = not errors
if not metadata_schema_valid:
    raise ValueError("; ".join(errors))

file_size = output.stat().st_size
payload = {
    "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "machine": os.environ.get("BLENDER_HOSTNAME") or socket.gethostname(),
    "blender_path": blender_path,
    "version": version,
    "canonical_invocation": canonical_invocation,
    "overall_verdict": "PASS",
    "smoke_render": {
        "status": "PASS",
        "scene_name": metadata["scene_name"],
        "render_engine": metadata["render_engine"],
        "resolution": metadata["resolution"],
        "frame": metadata["frame"],
        "output_file": str(output),
        "metadata_file": str(Path(metadata_path)),
        "file_size_bytes": file_size,
    },
    "output_validation": {
        "metadata_schema_valid": True,
        "png_signature_valid": True,
        "expected_scene_name": "cube-render",
        "expected_output_name": "cube-render_frame-0001.png",
    },
}
Path(verdict_path).parent.mkdir(parents=True, exist_ok=True)
with open(verdict_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(payload, f, sort_keys=False)
PY
then
    :
else
    validation_error="$(cat "$validate_stderr")"
    rm -f "$validate_stderr"
    msg="ERROR: metadata validation failed: ${validation_error//$'\n'/ }"
    echo "$msg" >&2
    write_failure_verdict "metadata-invalid" "$msg" "$blender_path" "$version" "FAIL" "false" "true"
    exit 1
fi
rm -f "$validate_stderr"

cat "$VERDICT_PATH"
exit 0
