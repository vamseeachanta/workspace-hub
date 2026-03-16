#!/usr/bin/env python3
"""Generate calculation-report YAML from OpenFOAM analysis results.

Usage:
    uv run --no-project python scripts/openfoam-analysis/generate-calc-yaml.py \
        --analysis analysis.yaml --case-dir ~/foam/run/my-case/ --output calc.yaml
"""
import argparse
import re
from datetime import date
from pathlib import Path

import yaml


def parse_solver_log(case_dir: Path) -> dict:
    """Extract final residuals and iteration count from solver log."""
    logs = sorted(case_dir.glob("log.*"))
    solver_logs = [l for l in logs if l.name not in ("log.blockMesh", "log.checkMesh", "log.all")]
    if not solver_logs:
        return {"residuals": {}, "iterations": 0, "solver": "unknown"}

    log_path = solver_logs[0]
    solver_name = log_path.name.replace("log.", "")
    text = log_path.read_text()

    pattern = re.compile(
        r"(\w+):\s+Solving for (\w+), "
        r"Initial residual = ([0-9.e+-]+), "
        r"Final residual = ([0-9.e+-]+)"
    )
    residuals = {}
    iterations = 0
    for m in pattern.finditer(text):
        residuals[m.group(2)] = float(m.group(3))
        iterations += 1

    return {"residuals": residuals, "iterations": iterations, "solver": solver_name}


def parse_force_coeffs(case_dir: Path) -> dict | None:
    """Extract force coefficients from postProcessing."""
    forces_dir = case_dir / "postProcessing" / "forces" / "0"
    coeff_file = forces_dir / "coefficient.dat"
    if not coeff_file.exists():
        return None

    lines = [l for l in coeff_file.read_text().splitlines() if not l.startswith("#")]
    if not lines:
        return None

    last = lines[-1].split()
    return {"Cd": float(last[1]), "Cl": float(last[2]), "CmPitch": float(last[3])}


def generate_calc_yaml(analysis_path: str, case_dir: str, output_path: str):
    """Generate calculation-report compatible YAML."""
    # Validation gate — refuse to generate report from invalid results
    import subprocess
    validator = Path(__file__).parent / "validate-analysis.py"
    if validator.exists():
        result = subprocess.run(
            ["uv", "run", "--no-project", "python", str(validator), case_dir],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("ERROR: Analysis validation failed. Fix issues before generating report:")
            print(result.stdout)
            sys.exit(1)

    with open(analysis_path) as f:
        cfg = yaml.safe_load(f)

    case = Path(case_dir)
    log_data = parse_solver_log(case)
    force_data = parse_force_coeffs(case)

    # Load convergence verdict if available
    verdict_path = case / "convergence-verdict.yaml"
    convergence = {}
    if verdict_path.exists():
        with open(verdict_path) as f:
            convergence = yaml.safe_load(f)

    # Build inputs
    inputs = []
    flow = cfg.get("flow", {})
    geom = cfg.get("geometry", {})
    if "velocity" in flow:
        inputs.append({"name": "Flow velocity", "symbol": "U", "value": flow["velocity"], "unit": "m/s"})
    if "density" in flow:
        inputs.append({"name": "Fluid density", "symbol": "rho", "value": flow["density"], "unit": "kg/m³"})
    if "kinematic_viscosity" in flow:
        inputs.append({"name": "Kinematic viscosity", "symbol": "nu", "value": flow["kinematic_viscosity"], "unit": "m²/s"})
    if "diameter" in geom:
        inputs.append({"name": "Structure diameter", "symbol": "D", "value": geom["diameter"], "unit": "m"})

    # Build outputs
    outputs = []
    for req in cfg.get("outputs_required", []):
        value = None
        if force_data and req["symbol"] == "C_D":
            value = force_data["Cd"]
        output_entry = {"name": req["name"], "symbol": req["symbol"], "value": value, "unit": req["unit"]}
        outputs.append(output_entry)

    # Build methodology
    solver = cfg.get("solver", {})
    methodology = {
        "description": f"CFD analysis using OpenFOAM {solver.get('application', 'unknown')} "
                       f"with {solver.get('turbulence_model', 'default')} turbulence model",
        "standard": cfg.get("analysis", {}).get("standard", ""),
        "equations": [
            {"id": "eq1", "name": "Reynolds number", "latex": r"Re = \frac{U D}{\nu}"},
            {"id": "eq2", "name": "Drag force", "latex": r"F_D = \frac{1}{2} \rho C_D A U^2"},
        ],
    }

    # Build charts (residual convergence)
    charts = []
    if log_data["residuals"]:
        charts.append({
            "title": "Final Residuals by Field",
            "type": "bar",
            "data": {
                "labels": list(log_data["residuals"].keys()),
                "datasets": [{"label": "Initial Residual", "data": list(log_data["residuals"].values())}],
            },
        })

    # Assemble report
    report = {
        "metadata": {
            "title": cfg.get("analysis", {}).get("title", "CFD Analysis"),
            "doc_id": f"CFD-{date.today().strftime('%Y%m%d')}-001",
            "revision": "A",
            "date": date.today().isoformat(),
            "author": "OpenFOAM Analysis Workflow",
            "status": "draft",
        },
        "inputs": inputs,
        "methodology": methodology,
        "outputs": outputs,
        "assumptions": cfg.get("assumptions", []),
        "references": cfg.get("references", []),
    }
    if charts:
        report["charts"] = charts

    with open(output_path, "w") as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"Calculation report YAML written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate calc report YAML from OpenFOAM results")
    parser.add_argument("--analysis", required=True, help="Analysis YAML config")
    parser.add_argument("--case-dir", required=True, help="OpenFOAM case directory")
    parser.add_argument("--output", required=True, help="Output calc report YAML path")
    args = parser.parse_args()
    generate_calc_yaml(args.analysis, args.case_dir, args.output)
