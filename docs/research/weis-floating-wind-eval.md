# WEIS Evaluation — Floating Wind Turbine Co-Design Framework

**Date:** 2026-03-31
**Issue:** vamseeachanta/workspace-hub#1460
**Evaluated by:** Research agent (web research, no installation)
**Parent issue:** #1397 (OSS Engineering Catalog)

---

## Summary

WEIS (Wind Energy with Integrated Servo-control) is NREL's open-source multi-fidelity co-design framework for floating offshore wind turbines. It couples WISDEM (system engineering), RAFT (frequency-domain hydrodynamics), OpenFAST (time-domain aero-hydro-servo-elastic simulation), and ROSCO (reference controller) under an OpenMDAO optimization driver. Apache-2.0 licensed, DOE WETO Software Stack. The framework parameterizes the full turbine system (blade, tower, platform, mooring) and optimizes for levelized cost of energy (LCOE), with published results showing 1-4% LCOE reductions. Highly relevant to offshore/marine engineering workflows but carries significant installation and compute complexity due to its deep dependency chain and Fortran compilation requirements.

---

## Dependency Chain

WEIS is not a single library but a stack of tightly coupled NREL tools:

```
WEIS (top-level orchestrator + OpenMDAO optimization driver)
 +-- WISDEM (Wind-Plant Integrated System Design & Engineering Model)
 |    +-- CCBlade (blade element momentum aerodynamics)
 |    +-- DrivetrainSE, TowerSE, RotorSE, PlantFinanceSE, ...
 +-- RAFT (Response Amplitudes of Floating Turbines)
 |    +-- MoorPy (quasi-static mooring model)
 |    +-- pyHAMS (potential-flow BEM hydrodynamics, optional)
 |    +-- CCBlade (rotor aerodynamics)
 +-- OpenFAST (time-domain aero-hydro-servo-elastic simulator)
 |    +-- Fortran/C++ compiled binary
 |    +-- HydroDyn, AeroDyn, ServoDyn, ElastoDyn, MoorDyn, ...
 +-- ROSCO (Reference Open-Source Controller)
 |    +-- Fortran-compiled controller DLL/SO
 +-- OpenMDAO (optimization framework)
 +-- PETSc / petsc4py (parallel solver, locked to 3.22.2)
```

### Component Details

| Component | Language | Version (WEIS stack) | PyPI/Conda | Purpose |
|---|---|---|---|---|
| WEIS | Python | 2.0 (docs) | No PyPI; conda env | Top-level co-design driver |
| WISDEM | Python/Fortran | conda-packaged | `wisdem` on PyPI | System engineering: mass, cost, structural sizing |
| RAFT | Python | 1.0.0 (docs) | `OpenRAFT` on PyPI | Frequency-domain floating platform dynamics |
| OpenFAST | Fortran/C++ | v4.0.2 (in WEIS) | conda binary | Time-domain simulation (Level 3 fidelity) |
| ROSCO | Python/Fortran | conda-packaged | conda | Wind turbine controller |
| MoorPy | Python | pip-installable | PyPI | Quasi-static mooring line model |
| pyHAMS | Python/Fortran | source install | No PyPI | BEM potential-flow hydrodynamics wrapper |
| OpenMDAO | Python | pip-installable | PyPI/conda | Multidisciplinary optimization framework |
| PETSc | C/Fortran | 3.22.2 (locked) | conda | Parallel linear/nonlinear solvers |

---

## Multi-Fidelity Architecture

WEIS operates at three fidelity levels:

| Level | Tool | Domain | Speed | Use Case |
|---|---|---|---|---|
| Level 1 | RAFT | Frequency-domain | Seconds per case | Design space exploration, initial optimization |
| Level 2 | OpenFAST (linearized) | Linearized time-domain | Minutes per case | Controller tuning, stability analysis |
| Level 3 | OpenFAST (nonlinear) | Full time-domain | Hours per DLC set | Design load verification, certification |

The optimization driver (OpenMDAO) can switch between fidelity levels, enabling efficient design space exploration at Level 1 with verification at Level 3.

---

## Installation Complexity Assessment

**Complexity: High**

### Requirements

- **Python:** >=3.9 (3.10-3.12 supported)
- **Package manager:** Miniforge3 / Anaconda (conda required; pip-only install not supported)
- **Compilers:** Fortran (gfortran), C, C++ — required for OpenFAST and ROSCO compilation
- **Build tools:** CMake, meson, ninja, meson-python
- **Windows:** m2w64-toolchain + libpython (WSL recommended instead)
- **Platforms:** Linux, macOS, WSL, native Windows

### Installation Process

```bash
# 1. Clone repository
git clone https://github.com/WISDEM/WEIS.git
cd WEIS

# 2. Create conda environment (resolves ~100+ packages)
conda env create --name weis-env -f environment.yml
conda activate weis-env

# 3. WEIS modules now installed via conda (previously subtree/source)
# OpenFAST binary delivered via conda package
```

### Pain Points

1. **Conda environment resolution** — the environment.yml has extensive pinned dependencies; resolution can take 10-30 minutes with conda (mamba recommended as faster solver)
2. **Fortran compilation** — OpenFAST and ROSCO require Fortran compilers; build failures on non-standard toolchains are common (see OpenFAST issue tracker)
3. **PETSc version lock** — petsc4py pinned to 3.22.2; conflicts with other scientific Python environments are likely
4. **Disk footprint** — full WEIS conda environment is multi-GB (OpenFAST binary + all NREL tools + scientific Python stack)
5. **No pip install** — cannot `pip install weis`; must use conda environment from repo
6. **Developer workflow** — modifying individual sub-modules (e.g., RAFT) requires installing from source within the WEIS conda env, creating a mixed-install maintenance burden

---

## Hardware and Compute Requirements

| Workload | CPU | RAM | Time | Notes |
|---|---|---|---|---|
| RAFT (Level 1) optimization | Any modern CPU | 4 GB | Seconds-minutes | Pure Python, lightweight |
| OpenFAST single DLC | 1 core | 4 GB | 5-30 min per case | Serial Fortran execution |
| OpenFAST DLC suite (IEC) | 8-64 cores | 16-64 GB | Hours-days | Embarrassingly parallel across load cases |
| Full WEIS optimization | 16+ cores recommended | 32+ GB | Hours-days | OpenMDAO drives many OpenFAST evaluations |
| HPC deployment | Cluster nodes | Depends | Hours | WEIS supports batch job submission |

**Key observation:** RAFT alone (Level 1) is lightweight and can run on any workstation. The computational burden comes from OpenFAST time-domain simulations (Level 2/3), which are the high-fidelity verification step. A meaningful WEIS optimization campaign typically requires HPC or a multi-core workstation with significant runtime.

---

## Relevance to Offshore/Marine Engineering Workflows

### Strong Fit

- **Floating platform optimization** — WEIS is the only open-source tool that couples platform geometry, mooring design, controller tuning, and structural sizing in a single optimization loop
- **Mooring system design** — MoorPy (quasi-static) and MoorDyn (dynamic, via OpenFAST) provide two fidelity levels for mooring analysis
- **Hydrodynamic analysis** — RAFT provides frequency-domain RAOs, added mass, radiation damping; OpenFAST HydroDyn provides time-domain wave loads
- **IEC 61400-3 compliance** — OpenFAST can run the design load case (DLC) matrix required for floating wind certification

### Overlap with Existing Tools

| Capability | WEIS Tool | Existing in Workspace | Overlap |
|---|---|---|---|
| BEM hydrodynamics | pyHAMS (via RAFT) | Capytaine (adopted) | Partial — different BEM solvers |
| Mooring analysis | MoorPy / MoorDyn | None currently | New capability |
| Frequency-domain RAOs | RAFT | Capytaine post-processing | Complementary — RAFT adds aero + controls |
| Platform geometry | WISDEM | None currently | New capability |
| Format conversion | HydroDyn I/O | BEMRosetta (deferred) | Related — HydroDyn is the target format |

### Gap It Fills

The workspace currently has Capytaine for BEM hydrodynamics but lacks:
1. Aero-hydro-servo-elastic coupled simulation
2. Floating platform optimization (geometry + mooring + controller)
3. Design load case automation for certification
4. Controller co-design capability

WEIS fills all four gaps but at significant complexity cost.

---

## Standalone Components Worth Tracking

Some WEIS sub-tools are independently useful without the full stack:

| Tool | Standalone Value | Install Difficulty | Notes |
|---|---|---|---|
| **RAFT** | High — frequency-domain floating turbine analysis | Medium — conda env with MoorPy, CCBlade, pyHAMS | `pip install OpenRAFT` available but may lag |
| **MoorPy** | High — quasi-static mooring line analysis | Low — pip installable | Useful for any mooring design workflow |
| **ROSCO** | Medium — reference controller for OpenFAST | Medium — Fortran compilation | Useful only with OpenFAST |
| **WISDEM** | Medium — turbine system engineering | Medium — `pip install wisdem` available | Large scope; many sub-modules |

**RAFT + MoorPy** represent the most accessible entry point for floating offshore engineering without committing to the full WEIS stack.

---

## Recommendation

**Defer** — with a phased research path defined.

WEIS is the most comprehensive open-source floating wind co-design framework available, and it is the correct long-term target for floating wind optimization workflows. However, the installation complexity (Fortran compilation, conda-only, PETSc version pinning, multi-GB footprint) and compute requirements (HPC for meaningful optimization) make immediate adoption impractical. The dependency chain is deep and brittle — any version mismatch between WISDEM, RAFT, OpenFAST, and ROSCO can break the stack.

### Phased Integration Path

**Phase 1 — RAFT standalone (near-term, low risk)**
1. Install RAFT in an isolated conda environment on dev-secondary
2. Run frequency-domain analysis on IEA 15 MW reference turbine (semi-submersible)
3. Compare RAFT hydrodynamic coefficients against Capytaine results
4. Validate MoorPy mooring outputs against known benchmarks
5. Assess: does RAFT add value beyond Capytaine for our use cases?

**Phase 2 — MoorPy integration (near-term, low risk)**
1. `pip install moorpy` in existing Python environment
2. Test quasi-static mooring line analysis for catenary and taut-leg configurations
3. Integrate with existing digitalmodel mooring workflows if applicable

**Phase 3 — Full WEIS (deferred until Phase 1-2 validated)**
1. Clone WEIS to dev-secondary, create dedicated conda environment
2. Run IEA 15 MW floating reference turbine example end-to-end
3. Benchmark OpenFAST time-domain results against published NREL data
4. Evaluate optimization campaign feasibility on available hardware
5. Decision gate: adopt for active projects or remain research-only

### Trigger Conditions for Phase 3

- A project requires floating wind turbine design optimization (not just analysis)
- HPC access is available for OpenFAST DLC campaigns
- Capytaine + RAFT (Phase 1) proves insufficient for the analysis scope

---

## One-Liner Verdict

WEIS is the gold-standard open-source floating wind co-design framework but its deep Fortran/conda dependency chain and HPC compute needs warrant a phased approach — start with RAFT and MoorPy standalone before committing to the full stack.

---

## Installation

**Date:** 2026-03-31
**Venv path:** `/mnt/local-analysis/raft-env` (Python 3.12.3)

### Packages Installed

| Package | Version | Source | Import Test |
|---|---|---|---|
| RAFT | 1.6 | PyPI (`pip install RAFT`) | `import raft` — passed |
| MoorPy | 1.3.0 | PyPI (`pip install moorpy`) | `import moorpy` — passed |

### Key Dependencies (auto-resolved)

- numpy 2.4.4, scipy 1.17.1, matplotlib 3.10.8, pyyaml 6.0.3

### Notes

- RAFT 1.6 on PyPI is a pure-Python wheel — no Fortran compilation required for standalone use
- MoorPy 1.3.0 is a pure-Python wheel — straightforward pip install
- This is the standalone RAFT installation (Phase 1 from the eval), separate from the full WEIS stack
- Optional dependency pyHAMS (BEM hydrodynamics) is **not** included — it requires Fortran compilation and is not on PyPI
- To activate: `source /mnt/local-analysis/raft-env/bin/activate`

---

## References

- [WEIS GitHub — WISDEM/WEIS](https://github.com/WISDEM/WEIS)
- [WEIS Documentation](https://weis.readthedocs.io/en/latest/)
- [WEIS Installation Guide](https://weis.readthedocs.io/en/latest/installation.html)
- [How WEIS Works](https://weis.readthedocs.io/en/latest/how_weis_works.html)
- [RAFT GitHub — WISDEM/RAFT](https://github.com/WISDEM/RAFT)
- [RAFT Documentation](https://openraft.readthedocs.io/en/latest/)
- [OpenRAFT on PyPI](https://pypi.org/project/OpenRAFT/)
- [WISDEM GitHub](https://github.com/WISDEM/WISDEM)
- [WISDEM on PyPI](https://pypi.org/project/wisdem/)
- [OpenFAST Documentation](https://openfast.readthedocs.io/en/main/)
- [OpenFAST Installation Guide](https://openfast.readthedocs.io/en/main/source/install/index.html)
- [NREL RAFT Software Page](https://www.nrel.gov/research/software/raft-response-amplitudes-of-floating-turbines)
- [ARPA-E WEIS Project](https://arpa-e.energy.gov/programs-and-initiatives/search-all-projects/wind-energy-integrated-servo-control-weis-toolset-enable-controls-co-design-floating-offshore-wind-energy-systems)
- [NREL WEIS Publication (2025)](https://research-hub.nrel.gov/en/publications/wind-energy-with-integrated-servo-control-weis-a-toolset-to-enabl/)
- [Control Co-Design of a Floating Offshore Wind Turbine (OSTI)](https://www.osti.gov/biblio/2222415)
