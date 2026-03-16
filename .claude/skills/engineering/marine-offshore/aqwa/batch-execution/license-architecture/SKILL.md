---
name: aqwa-batch-execution-license-architecture
description: 'Sub-skill of aqwa-batch-execution: License Architecture (+3).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# License Architecture (+3)

## License Architecture


- Base solver (`ansys` feature): **4 cores free** with Mechanical Enterprise licence
- Beyond 4 cores: requires HPC Pack (`aa_r_hpc`) or Ansys HPC licence
- AQWA uses **OpenMP (shared-memory only)** — all cores must be on a single node
- MPI / multi-node is not supported


## Environment Variables


```bash
export ANSYSLMD_LICENSE_FILE=1055@license-server.domain.com
export ANSYSLI_SERVERS=2325@license-server.domain.com
export OMP_NUM_THREADS=8     # Must match NUM_CORES in Deck 0 (or WB setting)
ulimit -s unlimited          # Required for large models
```


## SLURM Job Script — Standalone


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


## SLURM Job Script — Workbench (runwb2)


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
