---
name: aqwa-batch-execution
description: Run ANSYS AQWA analyses in batch/headless mode on Linux. Covers CLI
  execution, DAT input file structure, multi-stage analysis chaining, output file
  parsing, failure diagnosis, and HPC job scheduling.
version: 1.1.0
updated: 2026-02-24
category: offshore-engineering
triggers:
- AQWA batch
- AQWA command line
- AQWA Linux
- run AQWA headless
- AQWA-LINE batch
- AQWA DAT file
- AQWA job script
- AQWA SLURM
- AQWA HPC
- AQWA execution
- AQWA pipeline
capabilities: []
requires: []
see_also:
- aqwa-analysis
- diffraction-analysis
- orcawave-aqwa-benchmark
---
# AQWA Batch Execution Skill

Run ANSYS AQWA analyses from the Linux command line without a GUI. On Linux,
command-line execution is the **only** available mode — no Workbench GUI is present.
The analysis program type (LINE / LIBR / NAUT / DRIFT) is set inside the `.DAT` file,
not on the command line.

## Version Metadata

```yaml
version: 1.1.0
ansys_versions_tested: ['2023R1', '2024R1', '2024R2', '2025R1']
os: Linux x86_64 (RHEL); Windows via Workbench runwb2
linux_gui: not available — CLI only
note: AQWA is NOT supported on SUSE Linux; RHEL is the documented platform
```

## AQWA Programs and Analysis Sequence

| Program | DAT JOB code | Purpose | Stage |
|---------|-------------|---------|-------|
| AQWA-LINE | `LINE` | Frequency-domain diffraction/radiation | 1 |
| AQWA-LIBRIUM | `LIBR` | Equilibrium position (static) | 2 |
| AQWA-DRIFT | `DRFT` | Wave drift / QTF forces | 3 |
| AQWA-NAUT | `NAUT` | Time-domain irregular waves | 3 |

**Program type is selected via `JOB <name> <code>` in Deck 0 of the `.DAT` file.**
Use `RESTART` records to chain stages: Stage 1 (LINE) → Stage 2 (LIBR) → Stage 3 (NAUT/DRIFT).

## Linux Batch Execution

### Locating the Executable

```bash
# Find the AQWA executable (path varies by installation)
find /ansys_inc -name "Aqwa" -type f 2>/dev/null

# Typical Linux path (v2025 R1)
AQWA_EXE=/ansys_inc/v251/aqwa/bin/lnx64/Aqwa

# Confirm it exists and is executable
ls -la ${AQWA_EXE}
```

> Directory is `lnx64` on most installations. Verify on your site — may also be `lnamd64`.

### Running AQWA

```bash
# Standard (fresh) run — program type determined by .DAT JOB card
${AQWA_EXE} std <jobname>

# Restart run (continue from previous stage)
${AQWA_EXE} restart <jobname>
```

`<jobname>` is the `.DAT` file base name without extension.
All output files are written to the working directory as `<jobname>.*`.

### Command File for Sequencing Multiple Jobs

```bash
# Create a .com file listing jobnames, one per line
echo -e "stage1\nstage2\nstage3" > mylist.com

# Run all jobs in sequence
${AQWA_EXE} std mylist.com
```

### Checking Exit Status and Success

```bash
${AQWA_EXE} std analysis
# Exit code is unreliable — check output files instead:

if grep -qi "error\|fatal\|abort" analysis.mes 2>/dev/null; then
    echo "AQWA FAILED — check analysis.mes and analysis.lis"
    exit 1
elif [ -f analysis.res ] && [ -f analysis.plt ]; then
    echo "AQWA SUCCEEDED"
else
    echo "AQWA INCOMPLETE — check analysis.mes"
    exit 1
fi
```

### Full Two-Stage Pipeline Script

```bash
#!/usr/bin/env bash
set -euo pipefail

AQWA_EXE=/ansys_inc/v251/aqwa/bin/lnx64/Aqwa
JOBNAME=${1:-analysis}

check_run() {
    local job=$1
    if grep -qi "error\|fatal" ${job}.mes 2>/dev/null; then
        echo "FAILED: ${job}"; cat ${job}.mes; exit 1
    fi
    [ -f ${job}.res ] || { echo "FAILED: no .res for ${job}"; exit 1; }
    echo "OK: ${job}"
}

echo "=== Stage 1: AQWA-LINE (diffraction) ==="
# JOB card in ${JOBNAME}.DAT must read: JOB analysis LINE
${AQWA_EXE} std ${JOBNAME}
check_run ${JOBNAME}

echo "=== Stage 3: AQWA-NAUT (time domain) ==="
# Separate .DAT with JOB card: JOB analysis NAUT + RESTART 3 3
cp ${JOBNAME}.dat ${JOBNAME}_naut.dat
# (edit RESTART record to 3 3 and JOB code to NAUT before running)
${AQWA_EXE} restart ${JOBNAME}_naut
check_run ${JOBNAME}_naut

echo "Pipeline complete."
```

## DAT Input File Structure

AQWA uses fixed-column, free-field ASCII format. **Hard limit: 80 characters per line.**
The file is divided into numbered "Decks" (categories), each terminated by `END`.
The entire file is terminated with `STOP`.

### Deck 0 — Job Control (mandatory for all runs)

```
SYSTEM DATA AREA 50000        ! Scratch memory allocation (bytes)
JOB      analysis LINE        ! <jobname> <program_code>
TITLE    FPSO Diffraction Analysis 2026
NUM_CORES 8                   ! OpenMP threads (base licence: max 4 free)
OPTIONS  REST AHD1 END        ! REST=restart capable; AHD1=write ASCII .AH1
RESTART  1 1                  ! Start stage, stop stage (1=LINE, 2=LIBR, 3=NAUT)
```

Common `OPTIONS` flags:

| Flag | Effect |
|------|--------|
| `REST` | Enable restart capability (writes `.RES`) |
| `AHD1` | Write ASCII hydrodynamic database (`.AH1`) for OrcaFlex import |
| `GOON` | Continue past non-fatal errors |
| `NOFIG` | Suppress figure output |
| `NOLIST` | Suppress listing output |

### Deck Structure (Categories 1–6 for AQWA-LINE)

| Category | Keyword | Purpose |
|----------|---------|---------|
| 0 | (top of file) | Job control (JOB, TITLE, NUM_CORES, OPTIONS, RESTART) |
| 1 | `COOR` | Node coordinates: `ID  X  Y  Z` |
| 2 | `QPPL` / `TPPL` | Element topology: quad/tri panel connectivity |
| 3 | `PMAS` | Mass properties |
| 4 | `GEOM` | Geometric properties / CoG / inertia |
| 5 | `GLOB` | Global environment (DPTH, DENS, ACCG) |
| 6 | `FREQ` / `DIRN` | Wave frequencies and directions |
| — | `STOP` | Terminates entire input file |

### Minimal AQWA-LINE DAT Template

```
SYSTEM DATA AREA 50000
JOB      fpso LINE
TITLE    FPSO Hydrodynamic Diffraction
NUM_CORES 8
OPTIONS  REST AHD1 END
RESTART  1 1
COOR
   1001   0.0    0.0    0.0
   1002  50.0    0.0    0.0
   1003  50.0   15.0    0.0
   1004   0.0   15.0    0.0
END
QPPL
   QPPL DIFF
   1001  1001  1002  1003  1004
END
PMAS
   ...
END
GEOM
   ...
END
GLOB
DPTH     200.0
DENS     1025.0
ACCG     9.81
END
FREQ
   0.2  0.3  0.4  0.5  0.6  0.8  1.0  1.2  1.5  2.0
END
DIRN
   0.0  45.0  90.0  135.0  180.0
END
STOP
```

### Critical DAT Conventions

| Convention | Detail |
|-----------|--------|
| `QPPL DIFF` | Omitting `DIFF` makes panels non-diffracting — no error, wrong results |
| `ILID AUTO 21` | Irregular frequency removal; add after ZLWL waterline card |
| `SEAG nx ny` | 2 params in standalone mode; 6-param form is Workbench-only |
| `OPTIONS GOON` | Overrides non-fatal errors; does NOT bypass FATAL mesh errors |
| 80-col limit | Strictly enforced — AQWA truncates silently at column 80 |
| `STOP` vs `END` | `STOP` terminates the whole file; `END` terminates each category |

## Output Files

| Extension | Type | Contents |
|-----------|------|---------|
| `.LIS` | ASCII | Full listing: input echo, RAOs, added mass, radiation damping, warnings |
| `.RES` | Binary | Restart/results database — required input for Stages 2 and 3 |
| `.PLT` | Binary | Plotting database — used by AGS GUI and AqwaReader |
| `.MES` | ASCII | Messages: warnings, errors, abort messages — **check this first** |
| `.HYD` | Binary | Hydrodynamic database (frequencies, added mass, damping, wave forces) |
| `.AH1` | ASCII | ASCII hydro database (generated only with `AHD1` option) — OrcaFlex import |
| `.VAC` | Binary scratch | Temporary file during dynamic runs; must be writable — lock failure → abort |
| `.QTF` | ASCII | Quadratic Transfer Functions for second-order wave loads |

### Detecting Success vs. Failure

```bash
# 1. Check .MES first (most direct failure indicator)
grep -qi "error\|fatal\|abort" analysis.mes && echo "FAILED"

# 2. Check for .RES (produced only on successful Stage 1 completion)
[ -f analysis.res ] || echo "NO RESTART FILE — run failed"

# 3. Check .LIS for completion marker (exact string is version-dependent)
grep -i "analysis complete\|normal termination" analysis.lis

# 4. Count panels processed (sanity check)
grep "TOTAL NUMBER OF PANELS" analysis.lis
```

### Parsing RAOs from `.LIS` (Python)

```python
import re
from pathlib import Path

def check_lis_success(lis_path: Path) -> bool:
    text = lis_path.read_text(errors="replace")
    if re.search(r"FATAL ERROR|ERROR DETECTED", text, re.IGNORECASE):
        return False
    if re.search(r"ANALYSIS COMPLETE|NORMAL TERMINATION", text, re.IGNORECASE):
        return True
    return False  # inconclusive

def parse_rao_block(lis_path: Path) -> list[dict]:
    """Extract RAO amplitude/phase from AQWA-LINE .LIS (fixed-column format)."""
    text = lis_path.read_text(errors="replace")
    # First RAO section = displacement RAOs; skip velocity/acceleration
    blocks = re.findall(
        r"WAVE FREQUENCY\s*=\s*([\d.]+)(.*?)(?=WAVE FREQUENCY|\Z)",
        text, re.DOTALL
    )
    results = []
    for freq_str, block in blocks:
        rows = re.findall(
            r"([\d.]+)\s+" + r"([\d.]+)\s+([-\d.]+)\s+" * 6,
            block
        )
        results.append({"freq_rad_s": float(freq_str), "rows": rows})
    return results
```

### AqwaReader Batch Export

AqwaReader extracts results to CSV without the GUI. On Windows it must run via `workbench.bat`:

```bat
rem Windows — must use workbench.bat wrapper
"C:\Program Files\ANSYS Inc\v251\aisol\workbench.bat" -cmd ^
  "C:\Program Files\ANSYS Inc\v251\aisol\bin\winx64\AqwaReader.exe" ^
  --Type Graphical ^
  --InFile analysis.plt ^
  --OutFile results\rao ^
  --Format csv ^
  --Struct 1 --Freq 1 --Dir 1 ^
  --PLT1 1 --PLT2 1 --PLT3 1 --PLT4 3
```

On Linux, run AqwaReader without the wrapper (path follows same `lnx64` convention).
After any interactive AqwaReader session, it prints the exact command-line used — copy
this into your script and loop over `--Freq` and `--Dir` indices.

## Failure Diagnosis

| Symptom | Likely Cause | Check |
|---------|-------------|-------|
| No output files at all | Executable not found or license failure | Verify path; check `$ANSYSLMD_LICENSE_FILE` |
| `.MES`: `LICENSE` | License checkout failed | License server, feature name, core count |
| `.MES`: `ELEMENT ... LESS THAN MINIMUM` | Mesh quality — aspect ratio | Remesh: panels should be ~square |
| `.MES`: `DAOPEN: Open failure on file ANALYSIS.VAC` | Disk space or file lock | Free disk; kill stale AQWA process |
| `.MES`: `FER FAILED TO CONVERGE` | Frequency response convergence | Reduce frequency step; check damping |
| `.MES`: `MEMORY` | Insufficient RAM | Increase `SYSTEM DATA AREA`; reduce panel count |
| No RAOs in `.LIS` | `DIFF` keyword missing from `QPPL` | Add `DIFF` to all diffracting panels |
| `.MES`: `SEAG` error | Wrong SEAG parameter count | Use 2-param `SEAG nx ny` in standalone |
| Stage 2/3 fails immediately | `.RES` from Stage 1 missing | Re-run Stage 1; confirm `.RES` was written |
| Wrong results (no error) | Waterline panels not diffracting | Check `.LIS` for `NON-DIFFRACTING` warnings |

### Debug Sequence

```bash
# Step 1 — check license
echo "License: $ANSYSLMD_LICENSE_FILE"
lmstat -a -c $ANSYSLMD_LICENSE_FILE 2>/dev/null | grep -i aqwa

# Step 2 — run with all output captured
${AQWA_EXE} std analysis 2>&1 | tee analysis.run.log

# Step 3 — triage .MES (most informative)
cat analysis.mes

# Step 4 — scan .LIS for fatal lines
grep -n "FATAL\|ERROR\|STOP\|WARNING" analysis.lis | head -40

# Step 5 — confirm panel count echo
grep "TOTAL NUMBER OF PANELS" analysis.lis
```

## HPC / SLURM Integration

### License Architecture

- Base solver (`ansys` feature): **4 cores free** with Mechanical Enterprise licence
- Beyond 4 cores: requires HPC Pack (`aa_r_hpc`) or Ansys HPC licence
- AQWA uses **OpenMP (shared-memory only)** — all cores must be on a single node
- MPI / multi-node is not supported

### Environment Variables

```bash
export ANSYSLMD_LICENSE_FILE=1055@license-server.domain.com
export ANSYSLI_SERVERS=2325@license-server.domain.com
export OMP_NUM_THREADS=8     # Must match NUM_CORES in Deck 0 (or WB setting)
ulimit -s unlimited          # Required for large models
```

### SLURM Job Script — Standalone

```bash
#!/usr/bin/env bash
#SBATCH --job-name=aqwa_line
#SBATCH --partition=compute
#SBATCH --nodes=1                 # AQWA is SMP — single node only
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=aqwa_%j.out
#SBATCH --error=aqwa_%j.err

module load ansys/v251           # Module name is site-specific

export ANSYSLMD_LICENSE_FILE=1055@license-server
export ANSYSLI_SERVERS=2325@license-server
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

AQWA_EXE=/ansys_inc/v251/aqwa/bin/lnx64/Aqwa
WORK_DIR=/scratch/${USER}/${SLURM_JOB_ID}
mkdir -p ${WORK_DIR}
cp analysis.dat ${WORK_DIR}/
cd ${WORK_DIR}

${AQWA_EXE} std analysis

if [ -f analysis.res ]; then
    echo "SUCCESS"
    cp analysis.lis analysis.res analysis.plt analysis.ah1 ${SLURM_SUBMIT_DIR}/
else
    echo "FAILED — check analysis.mes:"
    cat analysis.mes
    exit 1
fi
```

### SLURM Job Script — Workbench (runwb2)

```bash
#!/usr/bin/env bash
#SBATCH --job-name=aqwa_wb
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=08:00:00

module load ansys/v251

export ANSYSLMD_LICENSE_FILE=1055@license-server
export ANSYSLI_SERVERS=2325@license-server

RUNWB2=/ansys_inc/v251/Framework/bin/Linux64/runwb2

${RUNWB2} -B \
    -F "/path/to/project.wbpj" \
    -R "/path/to/solve.wbjn"
exit $?
```

Minimal `solve.wbjn` (IronPython 2.7):

```python
SetScriptVersion(Version="0.1.0")
Open(FilePath=r"/path/to/project.wbpj")
system1 = GetSystem(Name="AQW")      # Name set by user in WB project
system1.Update(AllDependencies=True)
Save(Overwrite=True)
```

## Python Subprocess Pattern

```python
import subprocess
from pathlib import Path

AQWA_EXE = Path("/ansys_inc/v251/aqwa/bin/lnx64/Aqwa")

def run_aqwa(work_dir: Path, job_name: str, job_type: str = "std") -> bool:
    """Run AQWA batch. Returns True on success."""
    result = subprocess.run(
        [str(AQWA_EXE), job_type, job_name],
        cwd=str(work_dir), capture_output=True, text=True,
    )
    mes = (work_dir / f"{job_name}.mes")
    if mes.exists() and any(
        kw in mes.read_text(errors="replace").upper()
        for kw in ("ERROR", "FATAL", "ABORT")
    ):
        return False
    return (work_dir / f"{job_name}.res").exists()
```

## No Dedicated Python Package

The PyAnsys metapackage (33+ packages) does **not** include a dedicated AQWA client
as of 2025 R1. Automate AQWA via:
- `subprocess` + direct `.DAT` / `Aqwa` executable (recommended for standalone)
- `subprocess` + `runwb2` (for Workbench projects)
- `.LIS` / `.AH1` text parsing for results extraction

## Validation Checklist

After any AQWA-LINE run:

- [ ] `.MES` file has no `ERROR` / `FATAL` / `ABORT` strings
- [ ] `.RES` and `.PLT` files exist (required for Stage 2/3)
- [ ] Panel count in `.LIS` matches expected model size
- [ ] No `NON-DIFFRACTING` warnings in `.LIS` (would mean missing `DIFF` keyword)
- [ ] Surge/sway/yaw RAO → 1.0 at low frequency (long-wave limit)
- [ ] Heave RAO → 1.0 at low frequency
- [ ] Added mass matrix is positive semi-definite at all frequencies
- [ ] Roll RAO peak aligns with expected natural period

## Integration with Downstream Tools

| Target | File | Skill |
|--------|------|-------|
| OrcaFlex vessel type | `.AH1` (ASCII hydro) or `.LIS` parsed | `orcawave-to-orcaflex`, `aqwa-analysis` |
| OrcaWave benchmark | `.LIS` RAOs + coefficients | `orcawave-aqwa-benchmark` |
| BEMRosetta converter | `.HYD` binary | `bemrosetta` |
| Python post-processing | `.LIS` text parsing | `aqwa-analysis` Python API |
