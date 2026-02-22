---
name: workstations
description: >
  Workstation registry for multi-machine workspace-hub usage. Tracks machine nicknames,
  OS, capabilities, active work assignments, and spare hardware inventory. Reference
  when creating WRK items, planning hardware consolidation, or routing compute-heavy tasks.
version: 3.0.0
updated: 2026-02-22
category: workspace-hub
triggers:
  - which computer
  - workstation
  - computer nickname
  - machine registry
  - working machine
  - multi-machine
  - computer field
  - spare hardware
  - hardware consolidation
  - hardware inventory
related_skills:
  - workspace-hub/session-start
  - workspace-hub/comprehensive-learning
capabilities:
  - machine-registry
  - computer-routing
  - software-capability-map
  - multi-machine-routing
  - cron-integration
requires: []
---
# Workstations Skill — Machine Registry

Tracks workspace-hub machines for multi-workstation workflows. The `computer:` field
in WRK items references a nickname from this registry.

## Machine Registry

Every WRK item **should** set `computer:` in frontmatter. Leave blank only for machine-agnostic tasks (hub docs, skills, queue management). See **When to set computer:** below for the full rule.

| Nickname | Hostname | OS | CPU | RAM | GPU | Primary Use | Assessment |
|----------|----------|----|-----|-----|-----|-------------|------------|
| ace-linux-1 | ace-linux-1 | Ubuntu 24.04.3 LTS | 2x Xeon E5-2630 v3 (16C/32T) | 32 GB DDR4 ECC | GTX 750 Ti 2 GB | Primary — worldenergydata, hub orchestration, digitalmodel | [aceengineer-01.md](../../../specs/modules/hardware-inventory/aceengineer-01.md) |
| ace-linux-2 | ace-linux-2 | Ubuntu 24.04.4 LTS | 2x Xeon E5-2630 v3 (16C/32T) | 32 GB DDR4 ECC | T400 4 GB | Secondary Linux — open-source CFD/FEA/animation dev (blender, gmsh, openfoam, calculix, fenics, freecad, elmer) | [aceengineer-02.md](../../../specs/modules/hardware-inventory/aceengineer-02.md) |
| acma-ws014 | ACMA-WS014 | Windows 11 | i9 2 GHz | 16 GB | 8 GB graphics | Windows work, office tools | Pending |
| acma-ansys05 | ACMA-ANSYS05 | Windows (TBD) | 60 cores, 2.8 GHz | TBD | TBD | OrcaFlex (license-locked), ANSYS, AI/Python | Pending |
| gali-linux-compute-1 | TBD | Linux (TBD) | 128 cores (TBD) | 128 GB | 64 GB VRAM (TBD) | Heavy compute — CFD, FEA, large sims, batch | Preliminary |

### ace-linux-1 Storage

| Device | Size | Type | Model | Notes |
|--------|------|------|-------|-------|
| sda | 7.3 TB | HDD | Seagate ST8000DM004 | Primary data drive |
| sdb | 233 GB | SSD | Crucial CT250BX100 | OS / fast drive |
| sdc | 932 GB | HDD | WD WD10EZEX | Secondary storage |

### ace-linux-2 Storage

| Device | Size | Type | Model | Notes |
|--------|------|------|-------|-------|
| sdb | 465.8 GB | SSD | Samsung 870 EVO 500GB | OS / boot (from spare inventory) |
| sda | 931.5 GB | HDD | WDC WD10EZEX | /media/vamsee/Local Analysis |
| sdc | 2.7 TB | HDD | Seagate ST3000NC002 | /media/vamsee/DDE |

## WRK Item Integration

The `computer:` field is added to WRK frontmatter at **Capture** and confirmed
at **Plan** stage:

```yaml
computer: nickname   # machine where this work is intended to run
```

### Repo-to-machine routing (current)

| Repo / Workload | Machine | Rationale |
|-----------------|---------|-----------|
| worldenergydata | ace-linux-1 | Data stack + Python env live here |
| workspace-hub (orchestration) | ace-linux-1 | Primary hub machine |
| digitalmodel (Python dev) | ace-linux-1 / ace-linux-2 | Open-source dev, either machine |
| assetutilities | ace-linux-1 / ace-linux-2 | Open-source dev, either machine |
| OrcaFlex work (WRK-121, WRK-131) | acma-ansys05 | Node-locked OrcaFlex license |
| ANSYS / AQWA work | acma-ansys05 | ANSYS license on this machine |
| Windows-only tools | acma-ws014 | Windows 11, office tools |
| Heavy compute (CFD, FEA, batch) | gali-linux-compute-1 | 128 cores, 128 GB RAM, 64 GB VRAM |
| Engineering CAD (SolidWorks etc.) | acma-ws014 | Windows machine; add dedicated CAD node when provisioned |

### When to set computer:

- Set at creation if the task is clearly machine-specific (e.g., requires local GPU,
  Windows tool, specific data drive)
- Leave blank if the task is machine-agnostic (hub-only docs, skills, queue management)
- Always set for `working/` items to enable multi-machine handoff tracking

### Multi-machine handoff

When switching machines, `/session-start` checks recent `working/` items for `computer:`
fields and prompts if the current machine differs from the last active one.

## Spare Hardware Inventory

Components available for assembly, upgrade, or consolidation into existing workstations.

| Component | Spec | Status | Notes |
|-----------|------|--------|-------|
| SSD | 500 GB Samsung 870 EVO | **Installed** in ace-linux-2 | Boot drive for AceEngineer-02 |
| GPU 1 | NVIDIA T400 4GB GDDR6 | **Installed** in ace-linux-2 | PCIe; display + light compute |
| GPU 2 | Board ID: BFB06612 / Part: 4110T50R | Available | **Model unidentified** — check chip marking or run `lspci \| grep -i vga` |
| RAM | 4 × 8GB DDR3 ECC UDIMM — Hynix HMT41GU68FR8C (2Rx8 PC3) | Available | 32GB total; DDR3 ECC — requires DDR3 board with ECC support |

### Hardware Notes

- **GPU 2 identification**: BFB06612 is a PCB board ID, not a market name. To identify:
  - Linux: `lspci | grep -i vga` (plug in, boot, check output)
  - Windows: Device Manager → Display Adapters
  - Physical: look for "GeForce / Quadro / Radeon" chip marking on the card
- **GPU 1 (T400)**: Low-profile PCIe, single-slot, 70W, 4 × mDP. Good for CAD/display, not CUDA training.
- **RAM compatibility**: Spare is DDR3 ECC (PC3). ace-linux-1 (Xeon E5-2630 v3, Haswell-EP) uses **DDR4**
  — spare DDR3 ECC RAM is **not compatible** with this machine. Requires a DDR3-era board (Xeon E3/E5 v1/v2)
  to be useful. Check Windows machine RAM type before assuming fit.
- **ace-linux-1 GPU slot**: GTX 750 Ti already installed. T400 could be added as a second card
  (multi-monitor / display offload) if a free PCIe slot exists — check physically.

## Hardware Consolidation

> Fill in once workstation nicknames are confirmed.

### Consolidation Principles

1. **One primary** — single "source of truth" machine for active WRK items and git state
2. **Specialised nodes** — other machines run specific workloads (simulation batch, Windows tools)
   but do not carry main orchestrator context
3. **Spare → node** — build spare parts into a dedicated simulation/compute node rather than
   leaving components unallocated

### Candidate Uses for Spare Build

| Use Case | Fit | Target | Notes |
|----------|-----|--------|-------|
| SSD upgrade | Good | ace-linux-1 | 500GB SSD → replace/supplement existing 233GB SSD |
| Extra display output | Good | ace-linux-1 | T400 (4 × mDP) in second PCIe slot if available |
| GPU upgrade (display) | Good | Windows machine | T400 or GPU 2 as replacement for older card |
| RAM upgrade | Poor (Linux) | Windows machine | DDR3 ECC ≠ compatible with E5-2630 v3 (DDR4 board) — check Windows machine first |
| CUDA ML training | Poor | — | T400 = 320 CUDA cores, 4GB — too limited; GPU 2 TBD |
| Basic ML inference | Fair | ace-linux-1 | T400 can run small GGUF models via llama.cpp alongside GTX 750 Ti |
| Standalone build | Poor | — | No spare motherboard — can't build without one |

## Software Capability Map

Structured capability reference for machine routing decisions and `CL_MACHINE_MODE` config.

```yaml
machines:
  ace-linux-1:
    hostname: ace-linux-1
    programs: [python, uv, git, claude-code, worldenergydata, digitalmodel,
               assetutilities, assethold, legal-scan, pytest]
    exclusive: []
    shares_hub: null
    isolated: false
    cron_variant: full

  ace-linux-2:
    hostname: ace-linux-2
    programs: [python, uv, git, claude-code, digitalmodel, assetutilities,
               blender, gmsh, openfoam, calculix, fenics, freecad, elmer, pytest]
    exclusive: []
    shares_hub: ace-linux-1
    isolated: false
    cron_variant: contribute

  acma-ansys05:
    hostname: ACMA-ANSYS05
    programs: [orcaflex, ansys, python, office]
    exclusive: [orcaflex, ansys]
    shares_hub: null
    isolated: true
    cron_variant: contribute-minimal

  acma-ws014:
    hostname: ACMA-WS014
    programs: [office, windows-tools]
    exclusive: []
    shares_hub: null
    isolated: false
    cron_variant: contribute

  gali-linux-compute-1:
    hostname: TBD
    programs: [cfd, fea, python, batch]
    exclusive: []
    shares_hub: null
    isolated: false
    cron_variant: full
```

### ace-linux-2 open-source tools

| Tool | Domain | Notes |
|------|--------|-------|
| blender | 3D animation / visualization | Rendering, animation, geometry export |
| gmsh | Mesh generation | Pre-processing for FEA/CFD workflows |
| openfoam | Computational fluid dynamics | Open-source CFD solver |
| calculix | FEA solver | Abaqus-compatible input format |
| fenics / fenicsx | FEA / PDE solving | Python-based variational formulations |
| freecad | Open-source CAD + FEA | FEM workbench built-in |
| elmer | Multiphysics FEA | ELISA solver, CSC Finland |

## Routing Rules

Use when setting `computer:` on a new WRK item:

| Keyword in WRK title / tags | Recommended machine |
|-----------------------------|---------------------|
| orcaflex, ansys, aqwa | acma-ansys05 |
| office, windows, excel | acma-ws014 or acma-ansys05 |
| heavy-compute, large-sim, cfd-hpc, fea-hpc | gali-linux-compute-1 |
| blender, animation, openfoam, gmsh, calculix, fenics, freecad, elmer | ace-linux-2 |
| worldenergydata, hub, claude, orchestration | ace-linux-1 |
| open-source-dev, digitalmodel, assetutilities | ace-linux-1 or ace-linux-2 |
| everything else | ace-linux-1 |

## Multi-machine WRK Items

For tasks that span machines, `computer:` accepts a list:

```yaml
computer: [acma-ansys05, ace-linux-1]
```

**Handoff conventions:**
- First machine listed = initiating machine
- Label each checklist step with the machine: `[ace-linux-1] Run mesh generation`
- `/session-start` on the second machine detects `computer:` mismatch and prompts for
  context handoff

## comprehensive-learning Integration

The `cron_variant` field maps directly to `CL_MACHINE_MODE` in the comprehensive-learning
skill. No separate config file needed — the skill reads `hostname` at runtime.

| cron_variant | Role | Machine(s) |
|--------------|------|------------|
| `full` | Runs complete 10-phase pipeline | ace-linux-1 only |
| `contribute` | Commits derived state files + pushes; no pipeline | ace-linux-2, acma-ws014 |
| `contribute-minimal` | Commits candidates + corrections only + pushes | acma-ansys05 (isolated) |

## Update Process

When adding a new machine or updating spare inventory:
1. Run `scripts/maintenance/hardware-info.sh` on the target machine to gather specs
2. Add a row to the registry (or storage) table using the printed table row at the bottom
3. Add an entry to the Software Capability Map YAML above
4. Note primary use, capability constraints, and `computer:` nickname
5. Commit: `chore(workstations): update machine registry / spare inventory`

### Windows equivalent (PowerShell)

```powershell
Get-ComputerInfo | Select-Object CsName, OsName, CsTotalPhysicalMemory
Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
Get-WmiObject Win32_DiskDrive | Select-Object Model, Size, MediaType
Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion
```
