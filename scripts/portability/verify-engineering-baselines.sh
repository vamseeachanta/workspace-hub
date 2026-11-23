#!/usr/bin/env bash
# verify-engineering-baselines.sh — unified OpenFOAM + Blender smoke baseline aggregator.
# Issue #2272.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPORT_DIR="$REPO_ROOT/logs/engineering/smoke-verification"
TOOL="all"
EMIT_JSON=0
OPENFOAM_VALIDATOR_DEFAULT="$REPO_ROOT/scripts/openfoam/verify-openfoam-baseline.sh"
BLENDER_VALIDATOR_DEFAULT="$REPO_ROOT/scripts/blender/verify-blender-baseline.sh"
if command -v uv >/dev/null 2>&1; then
    PYTHON_CMD=(uv run python)
else
    PYTHON_CMD=(python3)
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tool)
            TOOL="$2"
            shift 2
            ;;
        --report-dir)
            REPORT_DIR="$2"
            shift 2
            ;;
        --json)
            EMIT_JSON=1
            shift
            ;;
        --help)
            cat <<'EOF'
Usage: scripts/portability/verify-engineering-baselines.sh [--tool openfoam|blender|all] [--report-dir PATH] [--json]

Runs the per-tool baseline validators and writes consolidated-verdict.yaml.
Environment overrides:
  OPENFOAM_BASELINE_VALIDATOR  defaults to scripts/openfoam/verify-openfoam-baseline.sh
  BLENDER_BASELINE_VALIDATOR   defaults to scripts/blender/verify-blender-baseline.sh
  SMOKE_HOSTNAME               machine name to write into the consolidated verdict
EOF
            exit 0
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

case "$TOOL" in
    all|openfoam|blender) ;;
    *)
        echo "ERROR: unknown tool '$TOOL'; allowed values: openfoam, blender, all" >&2
        exit 2
        ;;
esac

mkdir -p "$REPORT_DIR"

TOOLS=()
if [[ "$TOOL" == "all" || "$TOOL" == "openfoam" ]]; then
    TOOLS+=("openfoam")
fi
if [[ "$TOOL" == "all" || "$TOOL" == "blender" ]]; then
    TOOLS+=("blender")
fi

for selected in "${TOOLS[@]}"; do
    case "$selected" in
        openfoam)
            validator="${OPENFOAM_BASELINE_VALIDATOR:-$OPENFOAM_VALIDATOR_DEFAULT}"
            verdict="$REPORT_DIR/openfoam-verdict.yaml"
            ;;
        blender)
            validator="${BLENDER_BASELINE_VALIDATOR:-$BLENDER_VALIDATOR_DEFAULT}"
            verdict="$REPORT_DIR/blender-verdict.yaml"
            ;;
    esac
    if [[ ! -x "$validator" ]]; then
        cat > "$verdict" <<YAML
tool: $selected
overall_verdict: FAIL
error_summary: missing-validator
error_message: "Validator is not executable: $validator"
YAML
    else
        set +e
        "$validator" --verdict "$verdict"
        rc=$?
        set -e
        if [[ ! -f "$verdict" ]]; then
            cat > "$verdict" <<YAML
tool: $selected
overall_verdict: FAIL
error_summary: missing-verdict
error_message: "Validator exited $rc without writing $verdict"
YAML
        fi
    fi
done

CONSOLIDATED="$REPORT_DIR/consolidated-verdict.yaml"
"${PYTHON_CMD[@]}" - "$REPORT_DIR" "$CONSOLIDATED" "${TOOLS[@]}" <<'PY'
import os, socket, sys, yaml
from datetime import UTC, datetime
report_dir = sys.argv[1]
consolidated = sys.argv[2]
tools = sys.argv[3:]
entries = []
overall = "PASS"
for name in tools:
    verdict_file = os.path.join(report_dir, f"{name}-verdict.yaml")
    with open(verdict_file, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    status = raw.get("overall_verdict", "FAIL")
    if status != "PASS":
        overall = "FAIL"
    entry = {
        "name": name,
        "status": status,
        "version": raw.get("version", raw.get(f"{name}_version", "unknown")),
        "verdict_file": verdict_file,
    }
    if status != "PASS":
        entry["error_summary"] = raw.get("error_summary", "validator-failure")
    entries.append(entry)
payload = {
    "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "machine": os.environ.get("SMOKE_HOSTNAME") or socket.gethostname(),
    "overall_verdict": overall,
    "tools": entries,
}
with open(consolidated, "w", encoding="utf-8") as f:
    yaml.safe_dump(payload, f, sort_keys=False)
PY

if [[ "$EMIT_JSON" -eq 1 ]]; then
    "${PYTHON_CMD[@]}" - "$CONSOLIDATED" <<'PY'
import json, sys, yaml
with open(sys.argv[1], encoding="utf-8") as f:
    print(json.dumps(yaml.safe_load(f), separators=(",", ":")))
PY
else
    "${PYTHON_CMD[@]}" - "$CONSOLIDATED" <<'PY'
import sys, yaml
with open(sys.argv[1], encoding="utf-8") as f:
    payload = yaml.safe_load(f)
print("Tool      | Status | Version | Verdict File")
for entry in payload["tools"]:
    print(f"{entry['name']:<9} | {entry['status']:<6} | {entry.get('version','unknown'):<7} | {entry['verdict_file']}")
print(f"Overall verdict: {payload['overall_verdict']}")
PY
fi

"${PYTHON_CMD[@]}" - "$CONSOLIDATED" <<'PY'
import sys, yaml
with open(sys.argv[1], encoding="utf-8") as f:
    payload = yaml.safe_load(f)
sys.exit(0 if payload.get("overall_verdict") == "PASS" else 1)
PY
