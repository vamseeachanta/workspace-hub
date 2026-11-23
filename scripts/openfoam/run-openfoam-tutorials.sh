#!/usr/bin/env bash
# run-openfoam-tutorials.sh — Headless OpenFOAM tutorial runner
# Usage: bash scripts/openfoam/run-openfoam-tutorials.sh [--skip-bootstrap] [--verdict /path/to/verdict.yaml] [--tutorials cavity,pitzDaily]
#
# Runs selected tutorials, checks convergence, writes YAML verdict.
# No interactive session or GUI required.

set -eo pipefail

OPENFOAM_BASHRC="${OPENFOAM_BASHRC:-/usr/lib/openfoam/openfoam2312/etc/bashrc}"
VERDICT_FILE="/tmp/openfoam-tutorial-verdict.yaml"
TUTORIALS="cavity"
SKIP_BOOTSTRAP=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-bootstrap)
            SKIP_BOOTSTRAP=1
            shift
            ;;
        --verdict)
            VERDICT_FILE="$2"
            shift 2
            ;;
        --tutorials)
            TUTORIALS="$2"
            shift 2
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

# Source OpenFOAM (cannot use set -u — bashrc has unbound variables)
if [[ "$SKIP_BOOTSTRAP" == "1" ]]; then
    if [[ -z "${WM_PROJECT_DIR:-}" || -z "${WM_PROJECT_VERSION:-}" ]]; then
        echo "ERROR: --skip-bootstrap requires WM_PROJECT_DIR and WM_PROJECT_VERSION to be set" >&2
        exit 1
    fi
else
    echo "WARNING: runner standalone bootstrap mode is deprecated; prefer verify-openfoam-baseline.sh" >&2
    if [[ ! -f "$OPENFOAM_BASHRC" ]]; then
        echo "ERROR: OpenFOAM bashrc not found at $OPENFOAM_BASHRC" >&2
        exit 1
    fi
    source "$OPENFOAM_BASHRC" 2>/dev/null || true
fi

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

run_selected_tutorials() {
    local selected="$1"
    IFS=',' read -r -a names <<< "$selected"
    for tutorial in "${names[@]}"; do
        case "$tutorial" in
            cavity)
                local cavity
                cavity=$(find "$WM_PROJECT_DIR/tutorials" -type d -name "cavity" -path "*/icoFoam/cavity/cavity" | head -1)
                [[ -z "$cavity" ]] && cavity=$(find "$WM_PROJECT_DIR/tutorials" -type d -name "cavity" -path "*/icoFoam/*" | tail -1)
                if [[ -n "$cavity" ]]; then
                    run_tutorial "cavity" "$cavity" "blockMesh" "icoFoam"
                else
                    echo "WARNING: cavity tutorial not found"
                    results+=("cavity|NOT_FOUND|0")
                    overall="FAIL"
                fi
                ;;
            damBreak)
                local dambreak
                dambreak=$(find "$WM_PROJECT_DIR/tutorials" -type d -name "damBreak" -path "*/interFoam/laminar/damBreak/damBreak" | head -1)
                [[ -z "$dambreak" ]] && dambreak=$(find "$WM_PROJECT_DIR/tutorials" -type d -name "damBreak" -path "*/interFoam/*" | tail -1)
                if [[ -n "$dambreak" ]]; then
                    run_tutorial "damBreak" "$dambreak" "blockMesh" "setFields" "interFoam"
                else
                    echo "WARNING: damBreak tutorial not found"
                    results+=("damBreak|NOT_FOUND|0")
                    overall="FAIL"
                fi
                ;;
            pitzDaily)
                local pitzdaily
                pitzdaily=$(find "$WM_PROJECT_DIR/tutorials" -type d -name "pitzDaily" -path "*/simpleFoam/pitzDaily" | head -1)
                if [[ -n "$pitzdaily" ]]; then
                    run_tutorial "pitzDaily" "$pitzdaily" "blockMesh" "simpleFoam"
                else
                    echo "WARNING: pitzDaily tutorial not found"
                    results+=("pitzDaily|NOT_FOUND|0")
                    overall="FAIL"
                fi
                ;;
            *)
                echo "ERROR: unsupported tutorial '$tutorial'" >&2
                exit 2
                ;;
        esac
    done
}

run_selected_tutorials "$TUTORIALS"

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
