---
name: workstations
description: >
  Workstation registry for multi-machine workspace-hub usage. Tracks machine nicknames,
  OS, capabilities, active work assignments, and spare hardware inventory. Reference
  when creating WRK items, planning hardware consolidation, or routing compute-heavy tasks.
version: 1.1.0
updated: 2026-02-19
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
  - workspace-hub/work
capabilities:
  - machine-registry
  - computer-routing
requires: []
---
# Workstations Skill — Machine Registry

Tracks workspace-hub machines for multi-workstation workflows. The `computer:` field
in WRK items references a nickname from this registry.

## Machine Registry

> Nicknames TBD — update this section once settled.
> Run `scripts/maintenance/hardware-info.sh` on each machine to gather specs quickly.

| Nickname | Hostname | OS | CPU | RAM | GPU | Primary Use |
|----------|----------|----|-----|-----|-----|-------------|
| (TBD) | ace-linux-1 | Ubuntu 24.04.4 LTS | Xeon E5-2630 v3 32c/16t | 32GB DDR4 | GTX 750 Ti 2GB | Primary workstation |
| (TBD) | (unknown) | Windows | — | — | — | Windows tools |

### ace-linux-1 Storage

| Device | Size | Type | Model | Notes |
|--------|------|------|-------|-------|
| sda | 7.3 TB | HDD | Seagate ST8000DM004 | Primary data drive |
| sdb | 233 GB | SSD | Crucial CT250BX100 | OS / fast drive |
| sdc | 932 GB | HDD | WD WD10EZEX | Secondary storage |

## WRK Item Integration

The `computer:` field is added to WRK frontmatter at **Capture** and confirmed
at **Plan** stage:

```yaml
computer: nickname   # machine where this work is intended to run
```

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
| SSD | 500 GB | Available | General storage / OS drive for new build |
| GPU 1 | NVIDIA T400 4GB GDDR6 (RTL ENG SCB) | Available | PCIe; CAD display, basic ML inference, multi-monitor |
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

## WRK Item Integration

The `computer:` field is added to WRK frontmatter at **Capture** and confirmed
at **Plan** stage:

```yaml
computer: nickname   # machine where this work is intended to run
```

### When to set computer:

- Set at creation if the task is clearly machine-specific (e.g., requires local GPU,
  Windows tool, specific data drive)
- Leave blank if the task is machine-agnostic (hub-only docs, skills, queue management)
- Always set for `working/` items to enable multi-machine handoff tracking

### Multi-machine handoff

When switching machines, `/session-start` checks recent `working/` items for `computer:`
fields and prompts if the current machine differs from the last active one.

## Update Process

When adding a new machine or updating spare inventory:
1. Run `scripts/maintenance/hardware-info.sh` on the target machine to gather specs
2. Add a row to the registry (or storage) table using the printed table row at the bottom
3. Note primary use, capability constraints, and `computer:` nickname
4. Commit: `chore(workstations): update machine registry / spare inventory`

### Windows equivalent (PowerShell)

```powershell
Get-ComputerInfo | Select-Object CsName, OsName, CsTotalPhysicalMemory
Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
Get-WmiObject Win32_DiskDrive | Select-Object Model, Size, MediaType
Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion
```
