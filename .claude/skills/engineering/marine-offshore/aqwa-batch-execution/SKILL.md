---
name: aqwa-batch-execution
description: Run ANSYS AQWA analyses in batch/headless mode on Linux. Covers CLI
  execution, DAT input file structure, multi-stage analysis chaining, output file
  parsing, failure diagnosis, and HPC job scheduling.
version: 1.0.0
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

## Version Metadata

```yaml
version: 1.0.0
ansys_versions_tested: ['2023R1', '2024R1', '2024R2', '2025R1']
os: Linux (x86_64)
note: Windows Workbench batch via runwb2 is separate — see section below
```

## When to Use

- Running AQWA analyses on a Linux HPC cluster or workstation
- Automating multi-stage analysis pipelines (LINE → DRIFT → NAUT)
- Batch processing multiple vessel configurations or wave conditions
- CI/CD integration: automated hydrodynamic analysis on model changes
- Overnight/unattended analysis runs

## AQWA Programs and Analysis Sequence

| Program | CLI name | Purpose | Requires |
|---------|----------|---------|---------|
| AQWA-LINE | `line` | Frequency-domain diffraction/radiation | DAT file |
| AQWA-LIBRIUM | `lib` | Equilibrium position (static) | LINE results |
| AQWA-DRIFT | `drift` | Wave drift forces (QTF) | LINE results |
| AQWA-NAUT | `naut` | Time-domain irregular waves | LINE + DRIFT |
| AqwaReader | `AqwaReader` | Results extraction utility | Any AQWA output |

**Typical chain for mooring analysis:**
```
AQWA-LINE → AQWA-DRIFT → AQWA-NAUT
```

**Typical chain for RAO/coefficient export:**
```
AQWA-LINE → AqwaReader → OrcaFlex import
```

## Linux Batch Execution

### Executable Location

```bash
# ANSYS install root (set by site or environment)
ANSYS_ROOT=/ansys_inc/v${VER}   # e.g. v251 for 2025R1
AQWA_BIN=${ANSYS_ROOT}/aqwa/bin/lnamd64

# Confirm executable exists
ls ${AQWA_BIN}/aqwa
```

### Running AQWA Programs

```bash
# AQWA-LINE — frequency domain diffraction (always run first)
${AQWA_BIN}/aqwa line myjob

# AQWA-LIBRIUM — equilibrium (uses LINE results)
${AQWA_BIN}/aqwa lib myjob

# AQWA-DRIFT — drift forces (uses LINE results)
${AQWA_BIN}/aqwa drift myjob

# AQWA-NAUT — time domain (uses LINE + DRIFT results)
${AQWA_BIN}/aqwa naut myjob
```

Input file: `myjob.DAT` must exist in the working directory.
All outputs are written to the working directory using `myjob.*` naming.

### Checking Exit Status

```bash
${AQWA_BIN}/aqwa line myjob
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "AQWA-LINE FAILED (exit $STATUS)"
    grep -E "ERROR|FATAL|STOP" myjob.LIS | tail -20
    exit 1
fi
echo "AQWA-LINE complete"
```

### Full Pipeline Script

```bash
#!/usr/bin/env bash
set -euo pipefail

AQWA_BIN=/ansys_inc/v251/aqwa/bin/lnamd64
JOBNAME=${1:-myjob}

echo "=== AQWA-LINE ==="
${AQWA_BIN}/aqwa line ${JOBNAME}
grep -q "AQWA ANALYSIS COMPLETE\|ANALYSIS COMPLETE" ${JOBNAME}.LIS || {
    echo "LINE failed — check ${JOBNAME}.LIS"; exit 1; }

echo "=== AQWA-DRIFT ==="
${AQWA_BIN}/aqwa drift ${JOBNAME}

echo "=== AQWA-NAUT ==="
${AQWA_BIN}/aqwa naut ${JOBNAME}

echo "=== AqwaReader — extract RAOs ==="
${AQWA_BIN}/AqwaReader \
    --input ${JOBNAME}.LIS \
    --output ${JOBNAME}_raos.csv \
    --type RAO

echo "Pipeline complete."
```

## DAT Input File Structure

AQWA uses fixed-format ASCII input. **Line length limit: 80 characters (strictly enforced).**

### Top-Level Structure

```
JOB  <jobname>  AQWA         ! Job header — columns 1-72
OPTIONS ...                  ! Global options
STRU                         ! Structure geometry block
FINI                         ! End geometry
HYDR                         ! Hydrodynamic conditions block
FINI                         ! End hydro
END                          ! End of file
```

### Minimal AQWA-LINE DAT Template

```
JOB  MYJOB AQWA
OPTIONS GOON                  ! Continue past non-fatal errors
*
STRU          0
  PROP       0
    MATE      1
  1000.0    0.0    0.0
    GEOM      1
  NOD5
  1  0.0   0.0   0.0        ! Node definitions: ID  X  Y  Z
  2  50.0  0.0   0.0
  ...
  ELMN      1               ! Element definitions for structure n
  101  QPPL DIFF            ! QPPL=quad panel, DIFF=diffracting
  1  2  3  4                ! Node connectivity
  ...
  MASS      1
  1.2E7    0.0    0.0       ! Mass matrix (6x6)
  ...
  ZLWL      1
  0.0                       ! Z-coordinate of waterline
  1ILID AUTO 21             ! Irregular frequency removal (required)
  SEAG      1
  20  10                    ! Panel count nx ny (2 params — non-Workbench mode)
FINI
*
HYDR
  PERD                      ! Wave periods
  5.0  7.0  10.0  14.0  20.0
  DIRN                      ! Wave directions (degrees)
  0.0  45.0  90.0  135.0  180.0
  ACCL
  9.81                      ! Gravity
  DENS
  1025.0                    ! Water density kg/m³
  DPTH
  200.0                     ! Water depth (m), or DPTH DPTH for deep
FINI
END
```

### Key DAT Conventions

| Convention | Detail |
|-----------|--------|
| Element type | `QPPL DIFF` — omitting `DIFF` makes panels non-diffracting (silent error) |
| ILID card | `1ILID AUTO 21` — irregular frequency removal; required after ZLWL |
| SEAG card | 2 params in standalone mode (`nx ny`); 6-param bounding box is Workbench-only |
| OPTIONS GOON | Continues past non-fatal errors; does NOT bypass FATAL mesh errors |
| Line length | 80 columns max; AQWA truncates silently — count characters carefully |
| Blank lines | Permitted between cards; comment lines start with `*` |
| Negative Z | Wetted surface nodes have Z ≤ 0 (waterline = 0) |

### Multi-Structure DAT

For multi-body analyses, increment structure index:

```
STRU          0
  GEOM      1    ! Structure 1
  ...
  GEOM      2    ! Structure 2
  ...
FINI
```

## Output Files

| Extension | Content | Key for |
|-----------|---------|---------|
| `.LIS` | Listing: RAOs, added mass, damping, QTFs, warnings | Primary output |
| `.HYD` | Binary hydrodynamic database | DRIFT/NAUT inputs |
| `.RES` | Binary restart file | Continuation runs |
| `.PLT` | Plot data (ASCII) | Visualization |
| `.OUT` | Standard output (solver log) | Debugging |
| `.ERR` | Error file (if generated) | Fatal errors |

### Checking LIS for Success/Failure

```bash
# Success indicator
grep -c "AQWA ANALYSIS COMPLETE" myjob.LIS

# Failure indicators
grep -E "^\s*(ERROR|FATAL|STOP)" myjob.LIS

# Warning summary (non-fatal)
grep "WARNING" myjob.LIS | wc -l
```

### Parsing RAOs from LIS (Python)

```python
import re
from pathlib import Path

def extract_raos_from_lis(lis_path: str) -> dict:
    """Extract RAO table from AQWA-LINE .LIS file."""
    content = Path(lis_path).read_text()

    # RAO section begins with WAVE FREQUENCY header
    # First RAO section = displacement; skip velocity/acceleration sections
    rao_blocks = re.findall(
        r'WAVE FREQUENCY\s*=\s*([\d.]+).*?'
        r'SURGE.*?SWAY.*?HEAVE.*?ROLL.*?PITCH.*?YAW(.*?)(?=WAVE FREQUENCY|$)',
        content, re.DOTALL
    )

    raos = {}
    for freq_str, block in rao_blocks:
        freq = float(freq_str)
        # Parse amplitude/phase rows per direction
        rows = re.findall(
            r'([\d.]+)\s+' + r'([\d.]+)\s+([-\d.]+)\s+' * 6,
            block
        )
        raos[freq] = rows

    return raos
```

## Failure Diagnosis

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `FATAL: ELEMENT ASPECT RATIO` | Panel aspect ratio too extreme | Remesh: panels should be ~square |
| `FATAL: INTERSECTING PANELS` | Geometry self-intersects | Fix mesh in CAD / MeshTool |
| `ERROR: LICENSE` | ANSYS license not available | Check `ANSYSLMD_LICENSE_FILE`; wait for free token |
| `ERROR: FACET RADIUS` | 90° corner check fails | Use smaller panels at corners |
| `STOP: MEMORY` | Insufficient RAM | Reduce panel count or increase `ulimit -v` |
| LIS exists but is empty | Executable not found or wrong path | Verify `${AQWA_BIN}/aqwa` exists and is executable |
| Run completes but no RAOs | DIFF keyword missing on elements | Add `DIFF` to all `QPPL` element type cards |
| Added mass asymmetric | Geometry not symmetric or mesh too coarse | Check symmetry planes; refine mesh |
| `ERROR: SEAG` | Wrong number of SEAG parameters | Use 2-param SEAG in standalone (not Workbench) mode |

### Common Debug Sequence

```bash
# 1. Check license
echo $ANSYSLMD_LICENSE_FILE

# 2. Run with verbose output redirected
${AQWA_BIN}/aqwa line myjob 2>&1 | tee myjob.run.log

# 3. Scan LIS for fatal errors
grep -n "FATAL\|ERROR\|STOP\|WARNING" myjob.LIS

# 4. Check panel count and mesh stats
grep -A5 "TOTAL NUMBER OF PANELS" myjob.LIS

# 5. Verify geometry (check LIS for STRU section echo)
grep -A20 "STRUCTURE GEOMETRY" myjob.LIS | head -40
```

## HPC / SLURM Integration

### SLURM Job Script

```bash
#!/usr/bin/env bash
#SBATCH --job-name=aqwa_line
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=aqwa_%j.log

# Load ANSYS module (site-specific)
module load ansys/2024R2

# Set license
export ANSYSLMD_LICENSE_FILE=1055@license-server.example.com

AQWA_BIN=${ANSYS_ROOT}/aqwa/bin/lnamd64
JOBNAME=fpso_line

cd ${SLURM_SUBMIT_DIR}

echo "Starting AQWA-LINE: $(date)"
${AQWA_BIN}/aqwa line ${JOBNAME}
echo "AQWA-LINE done: $(date)"

# Validate
grep -q "AQWA ANALYSIS COMPLETE" ${JOBNAME}.LIS && \
    echo "SUCCESS" || echo "FAILED — check ${JOBNAME}.LIS"
```

### Environment Variables

```bash
# License server (required)
export ANSYSLMD_LICENSE_FILE=1055@license-server

# ANSYS root (set by module or manually)
export ANSYS_ROOT=/ansys_inc/v251

# Stack size (needed for large models)
ulimit -s unlimited

# Core dump (disable for clean HPC runs)
ulimit -c 0
```

## Windows Workbench Batch (runwb2)

On Windows, Workbench projects can be run in batch via `runwb2`:

```bat
rem Run AQWA Workbench project in batch
"C:\Program Files\ANSYS Inc\v251\Framework\bin\Win64\runwb2" ^
    -B -F "C:\analyses\fpso.wbpj" ^
    -R "C:\analyses\update_all.wbjn"
```

Minimal journal (`update_all.wbjn`):

```python
# Workbench journal — update all systems
Reset()
Update()
Save()
Exit()
```

> **Note:** On Linux, `runwb2` is not available. Use CLI (`aqwa line/drift/naut`) directly.

## Validation Checklist

After any AQWA-LINE run, verify:

- [ ] `grep "AQWA ANALYSIS COMPLETE" <job>.LIS` returns a match
- [ ] RAO at zero frequency → surge/sway/yaw ≈ 1.0, heave ≈ 1.0 (long-wave limit)
- [ ] Added mass matrix is positive semi-definite (check eigenvalues)
- [ ] Damping matrix is positive semi-definite at all frequencies
- [ ] Roll RAO peak frequency matches expected natural period
- [ ] Panel count printed in LIS matches expected (no silent truncation)
- [ ] No `WARNING: NON-DIFFRACTING` messages (would mean DIFF keyword missing)

## Integration with Downstream Tools

| Target | Data | Method |
|--------|------|--------|
| OrcaFlex | RAOs + added mass + damping | `aqwa-analysis` skill → CSV/YAML → `orcaflex-vessel-setup` |
| OrcaWave benchmark | RAOs + coefficients | `orcawave-aqwa-benchmark` skill |
| Python post-processing | LIS text parsing | `aqwa-analysis` skill Python API |
| BEMRosetta | HYD binary | `bemrosetta` skill converter |
