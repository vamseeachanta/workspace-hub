---
name: paraview-interface-cli-execution
description: 'Sub-skill of paraview-interface: CLI Execution (+3).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# CLI Execution (+3)

## CLI Execution


```bash
# Run ParaView Python script (with GUI libraries, offscreen)
pvpython script.py

# Run in pure batch mode (no GUI libraries needed)
pvbatch script.py

# Parallel execution with MPI
mpirun -np 4 pvbatch script.py

# With offscreen rendering (mesa)
pvbatch --force-offscreen-rendering script.py

# Specify specific mesa/EGL
DISPLAY=:0 pvpython script.py
```


## pvpython vs pvbatch


| Feature | pvpython | pvbatch |
|---------|----------|---------|
| GUI available | Yes (can show windows) | No (headless only) |
| MPI parallel | No | Yes |
| Offscreen | Via `--force-offscreen-rendering` | Default |
| Use case | Interactive scripts, debugging | Production batch jobs |


## CLI Flags


| Flag | Purpose |
|------|---------|
| `--force-offscreen-rendering` | Force offscreen (no display needed) |
| `--mesa` | Use Mesa software rendering |
| `-dr` | Disable registry (ignore saved settings) |
| `--state=file.pvsm` | Load ParaView state file |
| `--data=file.vtk` | Load data file |


## Environment Setup


```bash
# Typical ParaView environment (installed via package manager)
export PATH=/usr/bin:$PATH  # pvpython, pvbatch in standard path

# Or from tarball installation
export PARAVIEW_HOME=/opt/ParaView-5.12
export PATH=$PARAVIEW_HOME/bin:$PATH
export LD_LIBRARY_PATH=$PARAVIEW_HOME/lib:$LD_LIBRARY_PATH
```
