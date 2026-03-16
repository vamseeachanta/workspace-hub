#!/usr/bin/env bash
# run-openfoam-tutorials.sh — Headless OpenFOAM tutorial runner
# Usage: bash scripts/openfoam/run-openfoam-tutorials.sh [--verdict /path/to/verdict.yaml]
#
# Runs cavity + damBreak tutorials, checks convergence, writes YAML verdict.
# No interactive session or GUI required.

set -eo pipefail

OPENFOAM_BASHRC="/usr/lib/openfoam/openfoam2312/etc/bashrc"
VERDICT_FILE="${1:---verdict}"
if [[ "$VERDICT_FILE" == "--verdict" ]]; then
    VERDICT_FILE="${2:-/tmp/openfoam-tutorial-verdict.yaml}"
fi

# Source OpenFOAM (cannot use set -u — bashrc has unbound variables)
if [[ ! -f "$OPENFOAM_BASHRC" ]]; then
    echo "ERROR: OpenFOAM bashrc not found at $OPENFOAM_BASHRC" >&2
    exit 1
fi
source "$OPENFOAM_BASHRC" 2>/dev/null || true

RUN_DIR="$HOME/foam/run"
mkdir -p "$RUN_DIR"

overall="PASS"
declare -a results

run_tutorial() {
    local name="$1" src="$2"
    shift 2
    local cmds=("$@")

    echo "=== $name ==="
    local dest="$RUN_DIR/$name"
    rm -rf "$dest"
    cp -r "$src" "$dest"
    cd "$dest"

    # 0.orig → 0 (standard OpenFOAM pattern)
    [[ -d "0.orig" && ! -d "0" ]] && cp -r 0.orig 0

    local status="PASS"
    for cmd in "${cmds[@]}"; do
        printf "  %-20s" "$cmd..."
        if eval "$cmd" > "log.$cmd" 2>&1; then
            echo "OK"
        else
            echo "FAILED"
            status="FAIL"
            overall="FAIL"
            break
        fi
    done

    local tdirs
    tdirs=$(find . -maxdepth 1 -regex '.*/[0-9]+\.?[0-9]*' -type d | wc -l)
    echo "  Time directories: $tdirs"
    results+=("$name|$status|$tdirs")
}

# cavity — icoFoam (laminar transient, ~30s)
CAVITY=$(find "$WM_PROJECT_DIR/tutorials" -type d -name "cavity" -path "*/icoFoam/cavity/cavity" | head -1)
[[ -z "$CAVITY" ]] && CAVITY=$(find "$WM_PROJECT_DIR/tutorials" -type d -name "cavity" -path "*/icoFoam/*" | tail -1)
if [[ -n "$CAVITY" ]]; then
    run_tutorial "cavity" "$CAVITY" "blockMesh" "icoFoam"
else
    echo "WARNING: cavity tutorial not found"
    results+=("cavity|NOT_FOUND|0")
    overall="FAIL"
fi

# damBreak — interFoam (VOF multiphase, ~5min)
DAMBREAK=$(find "$WM_PROJECT_DIR/tutorials" -type d -name "damBreak" -path "*/interFoam/laminar/damBreak/damBreak" | head -1)
[[ -z "$DAMBREAK" ]] && DAMBREAK=$(find "$WM_PROJECT_DIR/tutorials" -type d -name "damBreak" -path "*/interFoam/*" | tail -1)
if [[ -n "$DAMBREAK" ]]; then
    run_tutorial "damBreak" "$DAMBREAK" "blockMesh" "setFields" "interFoam"
else
    echo "WARNING: damBreak tutorial not found"
    results+=("damBreak|NOT_FOUND|0")
    overall="FAIL"
fi

# Write verdict
cat > "$VERDICT_FILE" << YAML
generated_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
machine: $(hostname)
openfoam_version: v2312
overall_verdict: $overall
tutorials:
YAML

for r in "${results[@]}"; do
    IFS='|' read -r tname tstatus tdirs <<< "$r"
    cat >> "$VERDICT_FILE" << YAML
  - name: $tname
    status: $tstatus
    time_directories: $tdirs
YAML
done

echo ""
echo "=== VERDICT: $overall ==="
cat "$VERDICT_FILE"
exit $( [[ "$overall" == "PASS" ]] && echo 0 || echo 1 )
