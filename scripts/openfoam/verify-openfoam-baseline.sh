#!/usr/bin/env bash
# verify-openfoam-baseline.sh — Canonical OpenFOAM v2312 baseline validator wrapper.
# Final YAML owner for issue #2269. Delegates tutorial execution to run-openfoam-tutorials.sh.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DEFAULT_VERDICT="$REPO_ROOT/logs/engineering/openfoam-baseline/latest-verdict.yaml"
RUNNER_SCRIPT_DEFAULT="$REPO_ROOT/scripts/openfoam/run-openfoam-tutorials.sh"
RAW_VERDICT_DEFAULT="${TMPDIR:-/tmp}/openfoam-baseline-raw.yaml"
BASHRC_PATHS_DEFAULT="/usr/lib/openfoam/openfoam2312/etc/bashrc:/opt/openfoam2312/etc/bashrc"

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
    local error_type="$1"
    local error_message="$2"
    local attempted_json="$3"
    python3 - "$VERDICT_PATH" "$error_type" "$error_message" "$attempted_json" <<'PY'
import json, sys, yaml
path, error_type, error_message, attempted_json = sys.argv[1:5]
attempted = json.loads(attempted_json)
payload = {
    "generated_at": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "machine": __import__("os").environ.get("OPENFOAM_HOSTNAME") or __import__("socket").gethostname(),
    "overall_verdict": "FAIL",
    "error_type": error_type,
    "error_message": error_message,
    "attempted_bashrc_paths": attempted,
}
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
for path in "${candidate_bashrcs[@]}"; do
    if [[ -f "$path" ]]; then
        resolved_bashrc="$path"
        break
    fi
done

attempted_json="$(python3 - <<'PY' "${candidate_bashrcs[@]}"
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

set +u
# shellcheck disable=SC1090
source "$resolved_bashrc" 2>/dev/null || true
set -u

runner_script="${OPENFOAM_TUTORIAL_RUNNER_PATH:-$RUNNER_SCRIPT_DEFAULT}"
raw_verdict="${OPENFOAM_RAW_VERDICT_PATH:-$RAW_VERDICT_DEFAULT}"
mkdir -p "$(dirname "$raw_verdict")"
rm -f "$raw_verdict"

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
    write_failure_verdict "runner-failure" "$runner_error" "$attempted_json"
    exit 1
fi
rm -f "$runner_stderr"

version_command="${OPENFOAM_VERSION_COMMAND:-foamVersion}"
version_output="$(bash -lc "$version_command" 2>/dev/null || true)"
version="$(printf '%s' "$version_output" | tr -d '\r' | grep -o 'v[0-9][0-9]*' | head -1)"
version="${version:-${WM_PROJECT_VERSION:-v2312}}"
verification_method="WM_PROJECT_VERSION=${WM_PROJECT_VERSION:-unknown}; foamVersion=${version_output:-missing}; WM_PROJECT_DIR=${WM_PROJECT_DIR:-missing}"
machine_name="${OPENFOAM_HOSTNAME:-$(hostname)}"

python3 - "$raw_verdict" "$VERDICT_PATH" "$resolved_bashrc" "$machine_name" "$version" "$verification_method" <<'PY'
from pathlib import Path
import sys, yaml
raw_path, final_path, resolved_bashrc, machine_name, version, verification_method = sys.argv[1:7]
with open(raw_path, encoding="utf-8") as f:
    raw = yaml.safe_load(f) or {}
rows = []
for row in raw.get("tutorials", []):
    name = row.get("name")
    if name == "damBreak":
        continue
    rows.append(
        {
            "name": name,
            "status": row.get("status"),
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

cat "$VERDICT_PATH"
exit 0
