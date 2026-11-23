# OpenFOAM v13 Parallel Processing Guide

> Complete guide for running OpenFOAM simulations in parallel using MPI
>
> System: 32 CPU cores available (Ubuntu 24.04 LTS)
> OpenFOAM version: v13

## Overview

OpenFOAM supports parallel processing through domain decomposition using MPI (Message Passing Interface). This allows simulations to run significantly faster by distributing the computational work across multiple CPU cores.

## Prerequisites

- OpenFOAM v13 installed
- MPI installed (Open MPI 4.1.6 or compatible)
- Multi-core system (2+ cores)

## Step-by-Step Parallel Workflow

### Step 1: Prepare Your Case

Start with a working serial case:

```bash
cd ~/openfoam-test/bubbleColumn
of13  # Load OpenFOAM environment
```

### Step 2: Create decomposeParDict

Create `system/decomposeParDict` to specify decomposition parameters:

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
FoamFile
{
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains 8;  // Number of processor cores to use

method          scotch;  // Decomposition method

// ************************************************************************* //
```

**Decomposition Methods:**

1. **scotch** (recommended)
   - Automatic load balancing
   - Good for unstructured meshes
   - No additional configuration needed

2. **simple**
   - Geometric decomposition
   - Good for structured meshes
   - Requires directional split specification

3. **hierarchical**
   - Combines simple with ordering
   - Good for anisotropic meshes

4. **manual**
   - User specifies cell assignment
   - Maximum control, most work

### Step 3: Decompose the Mesh

```bash
decomposePar
```

**Output:**
```
/*---------------------------------------------------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  13                                    |
|   \\  /    A nd           | Website:  www.openfoam.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
Build  : 13-3cbc1e0da24d
Exec   : decomposePar
Date   : Jan 09 2026
Time   : 07:05:00
Host   : vamsee-linux1
PID    : 12345
...
Processor 0: field transfer
Processor 1: field transfer
...
End
```

**Result:**
- Creates `processor0/`, `processor1/`, ..., `processor7/` directories
- Each contains a portion of the mesh and initial fields

### Step 4: Run Parallel Simulation

```bash
mpirun -np 8 foamRun -parallel > log.foamRun.parallel 2>&1
```

**Command breakdown:**
- `mpirun`: MPI execution wrapper
- `-np 8`: Use 8 processors
- `foamRun`: OpenFOAM v13 unified solver
- `-parallel`: Enable parallel mode
- `> log.foamRun.parallel`: Redirect output to log file

**Monitoring progress:**
```bash
tail -f log.foamRun.parallel
```

### Step 5: Reconstruct Results

After simulation completes, merge processor results back:

```bash
reconstructPar
```

**Output:**
```
Reconstructing fields for mesh region0
Time = 1
Reconstructing volScalarFields
    alpha.air
    alpha.water
    T.air
    T.water
    p_rgh
    p
...
End
```

**Result:**
- Time directories (1, 2, 3, 4, 5) created in main case directory
- Contains reconstructed fields ready for visualization

### Step 6: Clean Processor Directories (Optional)

```bash
rm -rf processor*
```

This saves disk space but prevents restarting parallel simulation.

## Performance Comparison - bubbleColumn Case

**Case Details:**
- Multiphase Eulerian simulation (air + water)
- Mesh: ~20,000 cells
- Simulation time: 0 → 5 seconds
- Time step: 0.01s

### Serial Execution (1 core)

```bash
foamRun
```

**Results:**
- **Real time:** 26 seconds
- **User time:** 26 seconds
- **System time:** <1 second

### Parallel Execution (8 cores)

```bash
mpirun -np 8 foamRun -parallel
```

**Results:**
- **Real time:** 19.4 seconds
- **User time:** 151 seconds (2m31s total across 8 cores)
- **System time:** 2.3 seconds

### Performance Analysis

```
Speedup = Serial Time / Parallel Time = 26 / 19.4 = 1.34x
Efficiency = Speedup / Number of Cores = 1.34 / 8 = 16.75%
```

**Why not 8x faster?**

1. **Communication overhead**: MPI synchronization between processors
2. **Small case size**: More overhead relative to computation
3. **Serial bottlenecks**: Some solver parts can't parallelize
4. **Load imbalance**: Uneven work distribution

**Typical parallel efficiency:**
- Small cases (<100k cells): 10-30%
- Medium cases (100k-1M cells): 40-70%
- Large cases (>1M cells): 60-85%

## Scaling Guidelines

### Recommended Processor Counts

| Mesh Size | Recommended Cores | Cells per Core |
|-----------|------------------|----------------|
| <50k cells | 2-4 cores | 12,000+ |
| 50k-200k | 4-8 cores | 10,000+ |
| 200k-1M | 8-16 cores | 20,000+ |
| 1M-5M | 16-32 cores | 50,000+ |
| >5M | 32-64+ cores | 100,000+ |

**Rule of thumb:** Aim for at least 10,000 cells per processor for good efficiency.

### Testing Parallel Scalability

Run the same case with different processor counts:

```bash
# Serial (1 core)
time foamRun

# 2 cores
time mpirun -np 2 foamRun -parallel

# 4 cores
time mpirun -np 4 foamRun -parallel

# 8 cores
time mpirun -np 8 foamRun -parallel

# 16 cores
time mpirun -np 16 foamRun -parallel
```

Plot execution time vs. number of cores to find optimal configuration.

## Advanced Parallel Features

### Domain Decomposition for Better Load Balancing

**Hierarchical decomposition with preferred direction:**

```cpp
method          hierarchical;

hierarchicalCoeffs
{
    n           (2 2 2);  // Split: 2×2×2 = 8 domains
    delta       0.001;
    order       xyz;      // Decompose first in x, then y, then z
}
```

**Simple geometric decomposition:**

```cpp
method          simple;

simpleCoeffs
{
    n           (4 2 1);  // 4 in x, 2 in y, 1 in z = 8 domains
    delta       0.001;
}
```

### Viewing Decomposition

Visualize domain decomposition in ParaView:

```bash
# Keep processor directories
# Open in ParaView: File → Open → processor0/VTK/
# Shows colored domains
```

### Parallel Restart

To restart a parallel simulation:

```bash
# Decompose from latest time
decomposePar -latestTime

# Continue simulation
mpirun -np 8 foamRun -parallel
```

### Force Reconstruction at Time Intervals

Edit `system/controlDict`:

```cpp
functions
{
    reconstruct
    {
        type            reconstruct;
        libs            ("libutilityFunctionObjects.so");
        executeControl  timeStep;
        executeInterval 10;  // Reconstruct every 10 time steps
    }
}
```

## Troubleshooting

### Common Issues

**1. MPI not found**
```
Error: mpirun: command not found
```
**Solution:**
```bash
sudo apt-get install openmpi-bin libopenmpi-dev
```

**2. Wrong number of processors**
```
Error: Processor directories inconsistent with number of domains
```
**Solution:**
- Check `numberOfSubdomains` in `decomposeParDict`
- Match with `mpirun -np N`
- Re-run `decomposePar` if changed

**3. Parallel hang or timeout**
```
Simulation starts but hangs during execution
```
**Solution:**
- Check network connectivity (if distributed)
- Verify MPI configuration
- Reduce number of processors
- Check log files in processor directories

**4. Reconstruction fails**
```
Error: Time directories missing in processor folders
```
**Solution:**
- Simulation didn't complete properly
- Check `log.foamRun.parallel` for errors
- Ensure all processor directories have time folders

### Checking Parallel Run Status

```bash
# Monitor MPI processes
ps aux | grep foamRun

# Check processor logs individually
tail processor0/log.foamRun
tail processor1/log.foamRun

# Check load distribution
top  # See if all cores active
```

## Best Practices

1. **Always test serial first**
   - Verify case runs correctly before parallelizing
   - Easier to debug serial issues

2. **Start with fewer cores**
   - Test with 2-4 cores initially
   - Scale up after confirming it works

3. **Keep processor directories temporarily**
   - Useful for debugging
   - Can restart without redecomposing
   - Delete after successful completion

4. **Monitor during parallel runs**
   - Check if all cores are active
   - Look for load imbalances
   - Watch for memory issues

5. **Document your setup**
   - Save `decomposeParDict`
   - Note optimal core count for case type
   - Record timing results

## Parallel Processing Checklist

Before running parallel simulations:

- [ ] Case runs successfully in serial
- [ ] MPI installed and working (`mpirun --version`)
- [ ] `decomposeParDict` created in `system/`
- [ ] `numberOfSubdomains` matches `-np` value
- [ ] Sufficient disk space for processor directories
- [ ] Log file destination specified

After parallel simulation:

- [ ] Check all time directories exist in all processor folders
- [ ] Run `reconstructPar` successfully
- [ ] Verify reconstructed results
- [ ] Compare with serial results (if available)
- [ ] Clean processor directories if no restart needed

## Example: Complete Parallel Workflow

```bash
#!/bin/bash
# complete_parallel_workflow.sh

# Load OpenFOAM
of13

# Case directory
cd ~/openfoam-test/bubbleColumn

# Clean previous runs
rm -rf processor* [0-9]*

# Setup mesh and initial conditions
blockMesh
setFields

# Decompose for 8 cores
decomposePar

# Run parallel simulation
echo "Starting parallel simulation with 8 cores..."
time mpirun -np 8 foamRun -parallel > log.foamRun.parallel 2>&1

# Check if successful
if [ $? -eq 0 ]; then
    echo "Parallel simulation completed successfully"

    # Reconstruct results
    reconstructPar

    # Optional: Clean processor directories
    read -p "Clean processor directories? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf processor*
        echo "Processor directories removed"
    fi
else
    echo "Parallel simulation failed - check log.foamRun.parallel"
fi
```

## System Information

**Current System:**
- CPU: 32 cores available
- RAM: 124GB free
- OS: Ubuntu 24.04 LTS
- OpenFOAM: v13
- MPI: Open MPI 4.1.6

**Parallel Capability:**
- Can run up to 32 parallel processes
- Optimal for large cases (1M+ cells)
- Good speedup expected for medium to large cases

## Additional Resources

- OpenFOAM Parallel Guide: https://doc.cfd.direct/openfoam/user-guide-v13/parallel
- MPI Documentation: https://www.open-mpi.org/doc/
- Domain Decomposition: https://openfoam.org/release/parallel/

---

**Next Steps:**
- Test with larger cases for better parallel efficiency
- Experiment with different decomposition methods
- Monitor system resources during parallel runs
- Scale up to more cores for large simulations
