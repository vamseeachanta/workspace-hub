#!/usr/bin/env python3
"""Queue processor for solver jobs on licensed-win-1.

ABOUTME: Polls queue/pending/ for YAML job files, runs OrcFxAPI solver,
moves results to queue/completed/ or queue/failed/.

Designed to be invoked by Task Scheduler every 30 minutes:
    python scripts/solver/process-queue.py

Or via Claude Code CLI:
    claude -p "Run: python scripts/solver/process-queue.py"

Exit codes:
    0 - Success (jobs processed or queue empty)
    1 - Fatal error (git failure, etc.)
"""

import datetime
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

try:
    import yaml
except ImportError:
    # Fallback: minimal YAML parser for simple flat key-value files
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PENDING_DIR = REPO_ROOT / "queue" / "pending"
COMPLETED_DIR = REPO_ROOT / "queue" / "completed"
FAILED_DIR = REPO_ROOT / "queue" / "failed"


def log(msg: str) -> None:
    """Print a timestamped log message."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}")


def parse_yaml_simple(path: Path) -> dict:
    """Parse a simple flat YAML file without external dependencies.

    Handles the job schema format: key-value pairs, one per line.
    Does not handle nested structures or lists.
    """
    if yaml is not None:
        with open(path) as f:
            return yaml.safe_load(f)

    data = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Handle boolean-like values
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                data[key] = value
    return data


def git_pull() -> bool:
    """Pull latest changes from origin."""
    log("Pulling latest from origin...")
    result = subprocess.run(
        ["git", "pull", "origin", "main"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log(f"ERROR: git pull failed: {result.stderr}")
        return False
    log(f"git pull: {result.stdout.strip()}")
    return True


def git_push() -> bool:
    """Commit and push queue changes."""
    # Stage all queue changes
    subprocess.run(
        ["git", "add", "queue/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    # Check if there are changes to commit
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    if result.returncode == 0:
        log("No changes to commit")
        return True

    # Commit
    result = subprocess.run(
        ["git", "commit", "-m", "queue: process completed jobs"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log(f"ERROR: git commit failed: {result.stderr}")
        return False

    # Push
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log(f"ERROR: git push failed: {result.stderr}")
        return False

    log("Changes committed and pushed")
    return True


def process_job(job_path: Path) -> bool:
    """Process a single solver job.

    Returns True on success, False on failure.
    """
    job_name = job_path.stem
    log(f"Processing job: {job_name}")

    # Parse job file
    try:
        job = parse_yaml_simple(job_path)
    except Exception as e:
        log(f"ERROR: Cannot parse job file: {e}")
        move_to_failed(job_path, job_name, f"YAML parse error: {e}")
        return False

    solver = job.get("solver", "").lower()
    input_file = job.get("input_file", "")
    export_excel = job.get("export_excel", False)
    description = job.get("description", "")

    if not solver or not input_file:
        log(f"ERROR: Job missing required fields (solver={solver}, input_file={input_file})")
        move_to_failed(job_path, job_name, "Missing required fields: solver and/or input_file")
        return False

    # Resolve input file path relative to repo root
    input_path = REPO_ROOT / input_file
    if not input_path.exists():
        log(f"ERROR: Input file not found: {input_path}")
        move_to_failed(job_path, job_name, f"Input file not found: {input_file}")
        return False

    # Create output directory
    output_dir = COMPLETED_DIR / job_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Move job file to completed directory
    completed_job_path = output_dir / job_path.name
    shutil.move(str(job_path), str(completed_job_path))

    start_time = time.monotonic()

    # Run solver
    try:
        if solver == "orcawave":
            result_files = run_orcawave(input_path, output_dir, export_excel)
        elif solver == "orcaflex":
            result_files = run_orcaflex(input_path, output_dir, export_excel)
        else:
            raise ValueError(f"Unknown solver: {solver}")

        elapsed = time.monotonic() - start_time

        # Write result metadata
        write_result_yaml(
            output_dir,
            status="completed",
            solver=solver,
            input_file=input_file,
            description=description,
            elapsed_seconds=round(elapsed, 1),
            output_files=result_files,
        )

        log(f"Job completed: {job_name} ({elapsed:.1f}s)")
        return True

    except Exception as e:
        elapsed = time.monotonic() - start_time
        log(f"ERROR: Solver failed for {job_name}: {e}")

        # Move everything to failed
        failed_dir = FAILED_DIR / job_name
        if output_dir.exists():
            shutil.move(str(output_dir), str(failed_dir))
        else:
            failed_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(completed_job_path), str(failed_dir / job_path.name))

        write_result_yaml(
            failed_dir,
            status="failed",
            solver=solver,
            input_file=input_file,
            description=description,
            elapsed_seconds=round(elapsed, 1),
            error=str(e),
        )
        return False


def _export_orcawave_xlsx(diff, xlsx_path: Path, job_name: str) -> None:
    """Export OrcaWave Diffraction results to a multi-sheet Excel workbook.

    Reads directly from OrcFxAPI.Diffraction properties after Calculate().
    Sheet layout matches OrcaFlexExporter conventions:
      Summary, RAOs, AddedMass, Damping, Discretization

    Args:
        diff: OrcFxAPI.Diffraction object with completed calculation
        xlsx_path: Output .xlsx file path
        job_name: Job identifier for Summary sheet
    """
    import numpy as np
    import pandas as pd

    TWO_PI = 2.0 * np.pi
    DOF_NAMES = ["Surge", "Sway", "Heave", "Roll", "Pitch", "Yaw"]

    # --- Extract arrays from Diffraction object ---
    freqs_hz = np.array(diff.frequencies)          # Hz, descending order
    periods_s = np.array(diff.periods)             # s, ascending order
    headings_deg = np.array(diff.headings)         # degrees

    # Sort ascending by frequency
    sort_idx = np.argsort(freqs_hz)
    freqs_hz = freqs_hz[sort_idx]
    periods_s = periods_s[sort_idx]
    freqs_rads = freqs_hz * TWO_PI

    # displacementRAOs: (nheadings, nfreqs, 6) complex — reorder freq axis
    raos_raw = np.array(diff.displacementRAOs)     # (nhead, nfreq, 6)
    raos = raos_raw[:, sort_idx, :]               # sort freq axis

    # addedMass / damping: (nfreqs, 6, 6) — reorder freq axis
    am_raw = np.array(diff.addedMass)              # (nfreq, 6, 6)
    damp_raw = np.array(diff.damping)              # (nfreq, 6, 6)
    am = am_raw[sort_idx, :, :]
    damp = damp_raw[sort_idx, :, :]

    nfreq = len(freqs_hz)
    nhead = len(headings_deg)

    with pd.ExcelWriter(str(xlsx_path), engine="openpyxl") as writer:

        # --- Summary sheet ---
        summary = pd.DataFrame({
            "Property": [
                "Job", "Solver", "Frequencies",
                "Freq range (Hz)", "Period range (s)",
                "Headings", "Heading range (deg)",
            ],
            "Value": [
                job_name, "OrcaWave / OrcFxAPI.Diffraction", nfreq,
                f"{freqs_hz.min():.4f} – {freqs_hz.max():.4f}",
                f"{periods_s.min():.2f} – {periods_s.max():.2f}",
                nhead,
                f"{headings_deg.min():.1f} – {headings_deg.max():.1f}",
            ],
        })
        summary.to_excel(writer, sheet_name="Summary", index=False)

        # --- RAOs sheet ---
        # Columns: Freq(rad/s), Period(s), then per-DOF per-heading mag/phase
        rao_dict = {"Frequency (rad/s)": freqs_rads, "Period (s)": periods_s}
        for h_idx, heading in enumerate(headings_deg):
            for d_idx, dof in enumerate(DOF_NAMES):
                vals = raos[h_idx, :, d_idx]          # complex (nfreq,)
                rao_dict[f"{dof}_Mag_H{heading:.1f}"] = np.abs(vals)
                rao_dict[f"{dof}_Phase_H{heading:.1f}"] = np.degrees(np.angle(vals))
        pd.DataFrame(rao_dict).to_excel(writer, sheet_name="RAOs", index=False)

        # --- AddedMass sheet ---
        am_rows = []
        for f_idx in range(nfreq):
            row = {"Frequency (rad/s)": freqs_rads[f_idx], "Period (s)": periods_s[f_idx]}
            for i, di in enumerate(DOF_NAMES):
                for j, dj in enumerate(DOF_NAMES):
                    row[f"{di}_{dj}"] = am[f_idx, i, j]
            am_rows.append(row)
        pd.DataFrame(am_rows).to_excel(writer, sheet_name="AddedMass", index=False)

        # --- Damping sheet ---
        damp_rows = []
        for f_idx in range(nfreq):
            row = {"Frequency (rad/s)": freqs_rads[f_idx], "Period (s)": periods_s[f_idx]}
            for i, di in enumerate(DOF_NAMES):
                for j, dj in enumerate(DOF_NAMES):
                    row[f"{di}_{dj}"] = damp[f_idx, i, j]
            damp_rows.append(row)
        pd.DataFrame(damp_rows).to_excel(writer, sheet_name="Damping", index=False)

        # --- Discretization sheet ---
        df_freq = pd.DataFrame({"Frequency (rad/s)": freqs_rads, "Period (s)": periods_s})
        df_head = pd.DataFrame({"Heading (deg)": headings_deg})
        df_freq.to_excel(writer, sheet_name="Discretization", index=False, startrow=0)
        df_head.to_excel(
            writer, sheet_name="Discretization", index=False, startrow=len(df_freq) + 3
        )


def run_orcawave(input_path: Path, output_dir: Path, export_excel: bool) -> list:
    """Run OrcaWave solver via OrcFxAPI.

    Args:
        input_path: Path to .owd input file
        output_dir: Directory for output files
        export_excel: Whether to also produce .xlsx output

    Returns:
        List of output file names (relative to output_dir)
    """
    try:
        import OrcFxAPI
    except ImportError:
        raise RuntimeError(
            "OrcFxAPI not available. Ensure OrcaFlex is installed and "
            "OrcFxAPI wheel is installed: pip install OrcFxAPI"
        )

    log(f"  Loading: {input_path.name}")
    diff = OrcFxAPI.Diffraction(str(input_path))

    log(f"  Calculating (state={diff.state})...")
    diff.Calculate()
    log(f"  Calculation complete (state={diff.state})")

    # Save .owr result file (SaveResults, not SaveData — SaveData writes input)
    owr_name = input_path.stem + ".owr"
    owr_path = output_dir / owr_name
    diff.SaveResults(str(owr_path))
    log(f"  Saved: {owr_name}")

    output_files = [owr_name]

    # Optional Excel export using direct Diffraction API properties
    if export_excel:
        xlsx_name = input_path.stem + ".xlsx"
        xlsx_path = output_dir / xlsx_name
        try:
            _export_orcawave_xlsx(diff, xlsx_path, job_name=input_path.stem)
            log(f"  Exported: {xlsx_name}")
            output_files.append(xlsx_name)
        except Exception as e:
            log(f"  WARNING: Excel export failed: {e}")

    return output_files


def run_orcaflex(input_path: Path, output_dir: Path, export_excel: bool) -> list:
    """Run OrcaFlex solver via OrcFxAPI.

    Args:
        input_path: Path to .dat input file
        output_dir: Directory for output files
        export_excel: Whether to also produce .xlsx output

    Returns:
        List of output file names (relative to output_dir)
    """
    try:
        import OrcFxAPI
    except ImportError:
        raise RuntimeError(
            "OrcFxAPI not available. Ensure OrcaFlex is installed and "
            "OrcFxAPI wheel is installed: pip install OrcFxAPI"
        )

    log(f"  Loading: {input_path.name}")
    model = OrcFxAPI.Model(str(input_path))

    log("  Running statics...")
    model.CalculateStatics()
    log("  Running dynamics...")
    model.RunSimulation()
    log("  Simulation complete")

    # Save .sim result file
    sim_name = input_path.stem + ".sim"
    sim_path = output_dir / sim_name
    model.SaveSimulation(str(sim_path))
    log(f"  Saved: {sim_name}")

    output_files = [sim_name]

    return output_files


def move_to_failed(job_path: Path, job_name: str, error: str) -> None:
    """Move a job file to the failed directory with error info."""
    failed_dir = FAILED_DIR / job_name
    failed_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(job_path), str(failed_dir / job_path.name))
    write_result_yaml(failed_dir, status="failed", error=error)


def write_result_yaml(
    output_dir: Path,
    status: str,
    solver: str = "",
    input_file: str = "",
    description: str = "",
    elapsed_seconds: float = 0.0,
    output_files: Optional[List[str]] = None,
    error: str = "",
) -> None:
    """Write a result.yaml metadata file."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"status: {status}",
        f"processed_at: {ts}",
    ]
    if solver:
        lines.append(f"solver: {solver}")
    if input_file:
        lines.append(f"input_file: {input_file}")
    if description:
        lines.append(f'description: "{description}"')
    if elapsed_seconds:
        lines.append(f"elapsed_seconds: {elapsed_seconds}")
    if output_files:
        lines.append("output_files:")
        for f in output_files:
            lines.append(f"  - {f}")
    if error:
        lines.append(f'error: "{error}"')

    result_path = output_dir / "result.yaml"
    result_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    """Main entry point for queue processing."""
    log("=== Solver Queue Processor ===")
    log(f"Repo root: {REPO_ROOT}")

    # Pull latest
    if not git_pull():
        log("FATAL: Cannot pull latest changes")
        return 1

    # List pending jobs
    if not PENDING_DIR.exists():
        log("No pending directory found")
        return 0

    job_files = sorted(PENDING_DIR.glob("*.yaml"))
    job_files = [f for f in job_files if f.name != ".gitkeep"]

    if not job_files:
        log("No pending jobs")
        return 0

    log(f"Found {len(job_files)} pending job(s)")

    # Process each job
    success_count = 0
    fail_count = 0

    for job_file in job_files:
        if process_job(job_file):
            success_count += 1
        else:
            fail_count += 1

    log(f"Results: {success_count} completed, {fail_count} failed")

    # Commit and push results
    if not git_push():
        log("WARNING: Failed to push results (will retry on next poll)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
