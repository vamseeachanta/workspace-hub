#!/usr/bin/env bash
# verify-openfoam-baseline.sh — Canonical OpenFOAM v2312 baseline validator wrapper.
# Final YAML owner for issue #2269. Delegates tutorial execution to run-openfoam-tutorials.sh.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DEFAULT_VERDICT="$REPO_ROOT/logs/engineering/openfoam-baseline/latest-verdict.yaml"
RUNNER_SCRIPT_DEFAULT="$REPO_ROOT/scripts/openfoam/run-openfoam-tutorials.sh"
RAW_VERDICT_DEFAULT="${TMPDIR:-/tmp}/openfoam-baseline-raw.yaml"
BASHRC_PATHS_DEFAULT="/usr/lib/openfoam/openfoam2312/etc/bashrc:/opt/openfoam2312/etc/bashrc"
if command -v uv >/dev/null 2>&1; then
    PYTHON_CMD=(uv run python)
else
    PYTHON_CMD=(python3)
fi

VERDICT_PATH="$DEFAULT_VERDICT"
BENCHMARK=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --verdict)
            VERDICT_PATH="$2"
            shift 2
            ;;
        --benchmark)
            BENCHMARK="$2"
            shift 2
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

mkdir -p "$(dirname "$VERDICT_PATH")"

write_failure_verdict() {
    local error_summary="$1"
    local error_message="$2"
    local attempted_json="$3"
    local resolved_bashrc_path="${4:-}"
    local verification_method="${5:-}"
    "${PYTHON_CMD[@]}" - "$VERDICT_PATH" "$error_summary" "$error_message" "$attempted_json" "$resolved_bashrc_path" "$verification_method" <<'PY'
import json, sys, yaml
from datetime import datetime, UTC
path, error_summary, error_message, attempted_json, resolved_bashrc_path, verification_method = sys.argv[1:7]
attempted = json.loads(attempted_json)
payload = {
    "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "machine": __import__("os").environ.get("OPENFOAM_HOSTNAME") or __import__("socket").gethostname(),
    "overall_verdict": "FAIL",
    "error_summary": error_summary,
    "error_message": error_message,
    "attempted_bashrc_paths": attempted,
    "tutorials": [],
}
if resolved_bashrc_path:
    payload["resolved_bashrc_path"] = resolved_bashrc_path
if verification_method:
    payload["verification_method"] = verification_method
with open(path, "w", encoding="utf-8") as f:
    yaml.safe_dump(payload, f, sort_keys=False)
PY
}

if [[ -n "$BENCHMARK" && "$BENCHMARK" != "pitzDaily" ]]; then
    msg="ERROR: unsupported benchmark '$BENCHMARK'; allowed values: pitzDaily"
    echo "$msg" >&2
    write_failure_verdict "unsupported-benchmark" "$msg" "[]"
    exit 2
fi

IFS=':' read -r -a candidate_bashrcs <<< "${OPENFOAM_BASHRC_PATHS:-$BASHRC_PATHS_DEFAULT}"
resolved_bashrc=""
skipped_bashrc=""
for path in "${candidate_bashrcs[@]}"; do
    if [[ -f "$path" ]]; then
        if [[ -z "$resolved_bashrc" ]]; then
            resolved_bashrc="$path"
        else
            skipped_bashrc="$path"
            break
        fi
    fi
done

attempted_json="$("${PYTHON_CMD[@]}" - <<'PY' "${candidate_bashrcs[@]}"
import json, sys
print(json.dumps(sys.argv[1:]))
PY
)"

if [[ -z "$resolved_bashrc" ]]; then
    msg="ERROR: OpenFOAM bashrc not found. Attempted probe order: ${candidate_bashrcs[*]}"
    echo "$msg" >&2
    write_failure_verdict "missing-bashrc" "$msg" "$attempted_json"
    exit 1
fi

if [[ -n "$skipped_bashrc" ]]; then
    echo "INFO: secondary supported bashrc skipped: $skipped_bashrc" >&2
fi

export OPENFOAM_BASHRC="$resolved_bashrc"
set +u
# shellcheck disable=SC1090
source "$resolved_bashrc" 2>/dev/null || true
set -u

runner_script="${OPENFOAM_TUTORIAL_RUNNER_PATH:-$RUNNER_SCRIPT_DEFAULT}"
raw_verdict="${OPENFOAM_RAW_VERDICT_PATH:-$RAW_VERDICT_DEFAULT}"
mkdir -p "$(dirname "$raw_verdict")"
rm -f "$raw_verdict"

version_command="${OPENFOAM_VERSION_COMMAND:-foamVersion}"
version_output="$(bash -lc "$version_command" 2>/dev/null || true | tr -d '\r')"
version="$(printf '%s' "$version_output" | grep -o 'v[0-9][0-9]*' | head -1)"
version="${version:-${WM_PROJECT_VERSION:-v2312}}"
normalized_foam_version="$version"
verification_method="WM_PROJECT_VERSION=${WM_PROJECT_VERSION:-unknown}; foamVersion=${normalized_foam_version}; WM_PROJECT_DIR=${WM_PROJECT_DIR:-missing}"
machine_name="${OPENFOAM_HOSTNAME:-$(hostname)}"
wm_project_dir="${WM_PROJECT_DIR:-}"
wm_project_version="${WM_PROJECT_VERSION:-}"

if [[ "$version" != "v2312" || "$wm_project_version" != "v2312" || "$wm_project_dir" != *openfoam2312* ]]; then
    msg="ERROR: version mismatch for canonical OpenFOAM baseline (expected v2312 / *openfoam2312*, got WM_PROJECT_VERSION=${wm_project_version:-missing}, foamVersion=${normalized_foam_version:-missing}, WM_PROJECT_DIR=${wm_project_dir:-missing})"
    echo "$msg" >&2
    write_failure_verdict "version-mismatch" "$msg" "$attempted_json" "$resolved_bashrc" "$verification_method"
    exit 1
fi

selected_tutorials="cavity"
if [[ -n "$BENCHMARK" ]]; then
    selected_tutorials="$selected_tutorials,$BENCHMARK"
fi

runner_stderr="$(mktemp)"
if ! bash "$runner_script" --verdict "$raw_verdict" --tutorials "$selected_tutorials" 2>"$runner_stderr"; then
    runner_error="$(cat "$runner_stderr")"
    rm -f "$runner_stderr"
    if [[ -n "$runner_error" ]]; then
        printf '%s\n' "$runner_error" >&2
    fi
    write_failure_verdict "runner-failure" "$runner_error" "$attempted_json" "$resolved_bashrc"
    exit 1
fi
rm -f "$runner_stderr"

normalize_stderr="$(mktemp)"
if "${PYTHON_CMD[@]}" - "$raw_verdict" "$VERDICT_PATH" "$resolved_bashrc" "$machine_name" "$version" "$verification_method" 2>"$normalize_stderr" <<'PY'
from pathlib import Path
import sys, yaml
raw_path, final_path, resolved_bashrc, machine_name, version, verification_method = sys.argv[1:7]
with open(raw_path, encoding="utf-8") as f:
    raw = yaml.safe_load(f) or {}
if not raw.get("generated_at"):
    raise ValueError("generated_at missing from raw verdict")
if raw.get("overall_verdict") not in {"PASS", "FAIL"}:
    raise ValueError("overall_verdict must be PASS or FAIL")
rows = []
for row in raw.get("tutorials", []):
    name = row.get("name")
    status = row.get("status")
    if name == "damBreak":
        continue
    if status not in {"PASS", "FAIL", "NOT_FOUND"}:
        raise ValueError(f"tutorial status must be PASS/FAIL/NOT_FOUND, got {status!r}")
    rows.append(
        {
            "name": name,
            "status": status,
            "time_directories": int(row.get("time_directories", 0)),
        }
    )
payload = {
    "generated_at": raw.get("generated_at"),
    "machine": machine_name,
    "resolved_bashrc_path": resolved_bashrc,
    "fork": "ESI/OpenFOAM.com",
    "version": version,
    "verification_method": verification_method,
    "overall_verdict": raw.get("overall_verdict", "FAIL"),
    "tutorials": rows,
}
Path(final_path).parent.mkdir(parents=True, exist_ok=True)
with open(final_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(payload, f, sort_keys=False)
PY
then
    :
else
    normalize_error="$(cat "$normalize_stderr")"
    rm -f "$normalize_stderr"
    msg="ERROR: schema invalid for normalized OpenFOAM verdict: ${normalize_error//$'\n'/ }"
    echo "$msg" >&2
    write_failure_verdict "schema-invalid" "$msg" "$attempted_json" "$resolved_bashrc" "$verification_method"
    exit 1
fi
rm -f "$normalize_stderr"

cat "$VERDICT_PATH"
exit 0
