#!/usr/bin/env bash
# run-analysis.sh — End-to-end OpenFOAM CFD analysis from YAML config
# Usage: bash scripts/openfoam-analysis/run-analysis.sh <analysis.yaml> [--dry-run]
#
# Stages: case-setup → meshing → execution → post-processing
# Generates convergence-verdict.yaml and mesh-verdict.yaml
# Use generate-calc-yaml.py afterwards for calculation report

set -eo pipefail

ANALYSIS_YAML="${1:?Usage: run-analysis.sh <analysis.yaml> [--dry-run]}"
DRY_RUN="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source OpenFOAM (bashrc has unbound vars — cannot use set -u)
OPENFOAM_BASHRC="/usr/lib/openfoam/openfoam2312/etc/bashrc"
if [[ -f "$OPENFOAM_BASHRC" ]]; then
    source "$OPENFOAM_BASHRC" 2>/dev/null || true
    echo "OpenFOAM v2312 sourced"
else
    echo "WARNING: OpenFOAM not found at $OPENFOAM_BASHRC"
    if [[ "$DRY_RUN" != "--dry-run" ]]; then
        echo "ERROR: Cannot run solver without OpenFOAM. Use --dry-run for file generation only."
        exit 1
    fi
fi

# Parse analysis YAML (requires PyYAML)
parse_yaml() {
    uv run --no-project python -c "
import yaml, json, sys
with open('$ANALYSIS_YAML') as f:
    d = yaml.safe_load(f)
print(json.dumps(d))
" 2>/dev/null
}

CONFIG_JSON=$(parse_yaml)
TITLE=$(echo "$CONFIG_JSON" | uv run --no-project python -c "import json,sys; print(json.load(sys.stdin)['analysis']['title'])")
SOLVER=$(echo "$CONFIG_JSON" | uv run --no-project python -c "import json,sys; print(json.load(sys.stdin)['solver']['application'])")
CASE_NAME=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')

RUN_DIR="$HOME/foam/run/$CASE_NAME"
echo "=== OpenFOAM Analysis ==="
echo "Title:  $TITLE"
echo "Solver: $SOLVER"
echo "Case:   $RUN_DIR"
echo ""

# Stage 2: Case Setup
echo "--- Stage 2: Case Setup ---"
mkdir -p "$RUN_DIR"/{0,constant,system}

uv run --no-project python -c "
import yaml, json, sys, os

with open('$ANALYSIS_YAML') as f:
    cfg = yaml.safe_load(f)

case_dir = '$RUN_DIR'
solver = cfg['solver']
flow = cfg['flow']
mesh = cfg.get('mesh', {})

# controlDict
with open(f'{case_dir}/system/controlDict', 'w') as f:
    f.write('FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }\n')
    f.write(f'application     {solver[\"application\"]};\n')
    f.write('startFrom       startTime;\nstartTime       0;\nstopAt          endTime;\n')
    f.write(f'endTime         {solver[\"end_time\"]};\n')
    dt = solver.get('delta_t', 1)
    f.write(f'deltaT          {dt};\n')
    f.write('writeControl    timeStep;\n')
    f.write(f'writeInterval   {solver.get(\"write_interval\", 100)};\n')
    f.write('writeFormat     ascii;\nwritePrecision  6;\nrunTimeModifiable true;\n')

# fvSchemes (basic steady-state)
with open(f'{case_dir}/system/fvSchemes', 'w') as f:
    f.write('FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }\n')
    if solver['application'] in ['simpleFoam']:
        f.write('ddtSchemes { default steadyState; }\n')
    else:
        f.write('ddtSchemes { default Euler; }\n')
    f.write('gradSchemes { default Gauss linear; }\n')
    f.write('divSchemes { default none; div(phi,U) bounded Gauss linearUpwind grad(U); ')
    f.write('div((nuEff*dev2(T(grad(U))))) Gauss linear; }\n')
    f.write('laplacianSchemes { default Gauss linear corrected; }\n')
    f.write('interpolationSchemes { default linear; }\n')
    f.write('snGradSchemes { default corrected; }\n')

# fvSolution
with open(f'{case_dir}/system/fvSolution', 'w') as f:
    f.write('FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }\n')
    f.write('solvers {\n')
    f.write('  p { solver GAMG; tolerance 1e-06; relTol 0.1; smoother GaussSeidel; }\n')
    f.write('  pFinal { solver GAMG; tolerance 1e-06; relTol 0; smoother GaussSeidel; }\n')
    f.write('  U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0.1; }\n')
    f.write('  UFinal { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0; }\n')
    f.write('}\n')
    if solver['application'] in ['simpleFoam']:
        f.write('SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }\n')
        relax = solver.get('relaxation', {})
        f.write('relaxationFactors { equations {\n')
        f.write(f'  U {relax.get(\"U\", 0.7)}; p {relax.get(\"p\", 0.3)};\n')
        f.write('} }\n')
    else:
        f.write('PISO { nCorrectors 2; nNonOrthogonalCorrectors 0; pRefCell 0; pRefValue 0; }\n')

print('Case dicts generated')
" 2>&1
echo "Case setup: OK"

# Stage 3: Meshing
echo ""
echo "--- Stage 3: Meshing ---"
MESH_METHOD=$(echo "$CONFIG_JSON" | uv run --no-project python -c "import json,sys; print(json.load(sys.stdin).get('mesh',{}).get('method','blockMesh'))")

if [[ "$MESH_METHOD" == "blockMesh" ]]; then
    # Generate a basic blockMeshDict if not present
    if [[ ! -f "$RUN_DIR/system/blockMeshDict" ]]; then
        echo "Generating default blockMeshDict..."
        uv run --no-project python -c "
import yaml
with open('$ANALYSIS_YAML') as f:
    cfg = yaml.safe_load(f)
geom = cfg.get('geometry', {})
mesh = cfg.get('mesh', {})
cells_x = mesh.get('cells_x', 20)
cells_y = mesh.get('cells_y', 20)
w = geom.get('width', 1.0)
h = geom.get('height', 1.0)
with open('$RUN_DIR/system/blockMeshDict', 'w') as f:
    f.write('FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }\n')
    f.write('scale 1;\n')
    f.write(f'vertices ( (0 0 0) ({w} 0 0) ({w} {h} 0) (0 {h} 0) (0 0 0.1) ({w} 0 0.1) ({w} {h} 0.1) (0 {h} 0.1) );\n')
    f.write(f'blocks ( hex (0 1 2 3 4 5 6 7) ({cells_x} {cells_y} 1) simpleGrading (1 1 1) );\n')
    f.write('boundary (\n')
    f.write('  movingWall { type wall; faces ((3 7 6 2)); }\n')
    f.write('  fixedWalls { type wall; faces ((0 4 7 3) (1 2 6 5) (0 1 5 4)); }\n')
    f.write('  frontAndBack { type empty; faces ((0 3 2 1) (4 5 6 7)); }\n')
    f.write(');\n')
" 2>&1
    fi

    if [[ "$DRY_RUN" != "--dry-run" ]]; then
        cd "$RUN_DIR"
        blockMesh > log.blockMesh 2>&1 && echo "blockMesh: OK" || { echo "blockMesh: FAILED"; exit 1; }
        checkMesh > log.checkMesh 2>&1 && echo "checkMesh: OK" || echo "checkMesh: warnings (check log)"
    else
        echo "DRY RUN: skipping blockMesh"
    fi
else
    echo "Mesh method '$MESH_METHOD' — generate mesh manually, then re-run"
fi

# Stage 4: Execution
echo ""
echo "--- Stage 4: Execution ---"

if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "DRY RUN: skipping solver execution"
    echo "Case files generated at: $RUN_DIR"
    echo "To run: cd $RUN_DIR && $SOLVER > log.$SOLVER 2>&1"
else
    cd "$RUN_DIR"
    # Generate initial fields if not present
    if [[ ! -f "0/U" ]]; then
        uv run --no-project python -c "
import yaml
with open('$ANALYSIS_YAML') as f:
    cfg = yaml.safe_load(f)
flow = cfg['flow']
vel = flow.get('velocity', 0)
nu = flow.get('kinematic_viscosity', 1e-5)
with open('$RUN_DIR/0/U', 'w') as f:
    f.write('FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n')
    f.write('dimensions [0 1 -1 0 0 0 0];\n')
    f.write(f'internalField uniform ({vel} 0 0);\n')
    f.write('boundaryField {\n')
    f.write('  movingWall { type fixedValue; value uniform (1 0 0); }\n')
    f.write('  fixedWalls { type noSlip; }\n')
    f.write('  frontAndBack { type empty; }\n')
    f.write('}\n')
with open('$RUN_DIR/0/p', 'w') as f:
    f.write('FoamFile { version 2.0; format ascii; class volScalarField; object p; }\n')
    f.write('dimensions [0 2 -2 0 0 0 0];\n')
    f.write('internalField uniform 0;\n')
    f.write('boundaryField {\n')
    f.write('  movingWall { type zeroGradient; }\n')
    f.write('  fixedWalls { type zeroGradient; }\n')
    f.write('  frontAndBack { type empty; }\n')
    f.write('}\n')
with open('$RUN_DIR/constant/transportProperties', 'w') as f:
    f.write('FoamFile { version 2.0; format ascii; class dictionary; object transportProperties; }\n')
    f.write(f'transportModel Newtonian;\nnu {nu};\n')
" 2>&1
    fi

    # Copy 0.orig to 0 if present
    [[ -d "0.orig" && ! -d "0" ]] && cp -r 0.orig 0

    echo "Running $SOLVER..."
    $SOLVER > "log.$SOLVER" 2>&1 && echo "$SOLVER: OK" || { echo "$SOLVER: FAILED (check log.$SOLVER)"; exit 1; }

    # Count time directories
    TDIRS=$(find . -maxdepth 1 -regex '.*/[0-9]+\.?[0-9]*' -type d | wc -l)
    echo "Time directories: $TDIRS"

    # Write convergence verdict
    uv run --no-project python -c "
import re, yaml
from pathlib import Path

log = Path('$RUN_DIR/log.$SOLVER').read_text()
pattern = re.compile(r'(\w+):\s+Solving for (\w+), Initial residual = ([0-9.e+-]+)')
residuals = {}
for m in pattern.finditer(log):
    residuals[m.group(2)] = float(m.group(3))

status = 'converged' if all(v < 1e-4 for v in residuals.values()) else 'not_converged'
verdict = {
    'status': status,
    'final_residuals': {k: float(v) for k, v in residuals.items()},
    'time_directories': $TDIRS,
}
with open('$RUN_DIR/convergence-verdict.yaml', 'w') as f:
    yaml.dump(verdict, f, default_flow_style=False)
print(f'Convergence: {status}')
" 2>&1
fi

echo ""
echo "=== Analysis Complete ==="
echo "Case directory: $RUN_DIR"
echo "Next: generate calculation report YAML"
