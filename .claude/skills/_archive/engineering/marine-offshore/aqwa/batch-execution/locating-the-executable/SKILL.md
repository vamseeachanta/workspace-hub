---
name: aqwa-batch-execution-locating-the-executable
description: 'Sub-skill of aqwa-batch-execution: Locating the Executable (+4).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Locating the Executable (+4)

## Locating the Executable


```bash
# Find the AQWA executable (path varies by installation)
find /ansys_inc -name "Aqwa" -type f 2>/dev/null

# Typical Linux path (v2025 R1)
AQWA_EXE=/ansys_inc/v251/aqwa/bin/lnx64/Aqwa

# Confirm it exists and is executable
ls -la ${AQWA_EXE}
```

> Directory is `lnx64` on most installations. Verify on your site — may also be `lnamd64`.


## Running AQWA


```bash
# Standard (fresh) run — program type determined by .DAT JOB card
${AQWA_EXE} std <jobname>

# Restart run (continue from previous stage)
${AQWA_EXE} restart <jobname>
```

`<jobname>` is the `.DAT` file base name without extension.
All output files are written to the working directory as `<jobname>.*`.


## Command File for Sequencing Multiple Jobs


```bash
# Create a .com file listing jobnames, one per line
echo -e "stage1\nstage2\nstage3" > mylist.com

# Run all jobs in sequence
${AQWA_EXE} std mylist.com
```


## Checking Exit Status and Success


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


## Full Two-Stage Pipeline Script


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
