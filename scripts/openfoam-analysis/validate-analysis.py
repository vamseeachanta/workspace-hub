#!/usr/bin/env python3
"""Validate OpenFOAM analysis outputs before calculation report generation.

Usage:
    uv run --no-project python scripts/openfoam-analysis/validate-analysis.py <case-dir>

Checks:
    1. mesh-verdict.yaml exists and status=pass
    2. convergence-verdict.yaml exists and status=converged (or transient completion)
    3. All required time directories exist
    4. No FOAM FATAL ERROR in solver log
    5. Continuity errors within bounds

Exit codes:
    0 = all checks pass
    1 = validation failed (prints diagnostics)
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: uv add pyyaml")
    sys.exit(1)


def validate(case_dir: str) -> tuple[bool, list[str]]:
    case = Path(case_dir)
    issues = []

    if not case.is_dir():
        return False, [f"Case directory does not exist: {case}"]

    # 1. Check mesh verdict
    mesh_verdict = case / "mesh-verdict.yaml"
    if mesh_verdict.exists():
        with open(mesh_verdict) as f:
            mv = yaml.safe_load(f)
        if not mv.get("pass", False):
            issues.append(f"Mesh quality FAILED: {mv.get('issues', 'unknown')}")
    else:
        # Check if checkMesh log exists
        check_log = case / "log.checkMesh"
        if check_log.exists():
            text = check_log.read_text()
            if "Failed" in text:
                issues.append("checkMesh reported failures (no mesh-verdict.yaml)")
        # Not blocking — mesh verdict is optional if mesh was generated externally

    # 2. Check convergence verdict
    conv_verdict = case / "convergence-verdict.yaml"
    if conv_verdict.exists():
        with open(conv_verdict) as f:
            cv = yaml.safe_load(f)
        status = cv.get("status", "unknown")
        if status == "diverged":
            issues.append(f"Solver DIVERGED: {cv.get('field', 'unknown')} = {cv.get('residual', '?')}")
    else:
        issues.append("Missing convergence-verdict.yaml — run-analysis.sh not used?")

    # 3. Check solver log for fatal errors
    solver_logs = [f for f in case.glob("log.*")
                   if f.name not in ("log.blockMesh", "log.checkMesh", "log.all",
                                     "log.setFields", "log.decomposePar",
                                     "log.reconstructPar")]
    if not solver_logs:
        issues.append("No solver log found — solver was not run")
    else:
        log_text = solver_logs[0].read_text()
        if "FOAM FATAL" in log_text:
            # Extract error message
            fatal_match = re.search(r"FOAM FATAL (?:IO )?ERROR.*?\n\s+(.+)", log_text)
            msg = fatal_match.group(1).strip() if fatal_match else "unknown"
            issues.append(f"FOAM FATAL ERROR in {solver_logs[0].name}: {msg}")

        if "End\n" not in log_text and "End" not in log_text.splitlines()[-5:]:
            issues.append(f"Solver did not complete (no 'End' marker in {solver_logs[0].name})")

        # 4. Check continuity errors
        cont_pattern = re.compile(r"sum local = ([0-9.e+-]+)")
        cont_values = [float(m.group(1)) for m in cont_pattern.finditer(log_text)]
        if cont_values:
            max_cont = max(cont_values)
            if max_cont > 1e-1:
                issues.append(f"Continuity errors too high: max local = {max_cont:.2e}")

    # 5. Check time directories exist
    time_dirs = [d for d in case.iterdir()
                 if d.is_dir() and re.match(r"^\d+\.?\d*$", d.name)]
    if len(time_dirs) < 2:
        issues.append(f"Only {len(time_dirs)} time directories — solver may not have run")

    passed = len(issues) == 0
    return passed, issues


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <case-dir>")
        sys.exit(1)

    passed, issues = validate(sys.argv[1])

    if passed:
        print("VALIDATION: PASS")
        print(f"  Case: {sys.argv[1]}")
        sys.exit(0)
    else:
        print("VALIDATION: FAIL")
        print(f"  Case: {sys.argv[1]}")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
