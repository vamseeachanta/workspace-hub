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

| Nickname | OS | Primary Use | Notes |
|----------|-----|-------------|-------|
| (TBD) | Linux | — | — |
| (TBD) | Windows | — | — |

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
| GPU | NVIDIA T400 4GB GDDR6 (RTL ENG SCB) | Available | PCIe; good for CAD display, basic ML inference, multi-monitor |
| Motherboard | BFB06612 / 4110T50R | Available | Verify socket before pairing with RAM |
| RAM | 4 × 8GB DDR3 ECC UDIMM — Hynix HMT41GU68FR8C-RD (2Rx8 PC3) | Available | 32GB total; DDR3 — requires DDR3-era board |

### Hardware Notes

- **RAM compatibility**: HMT41GU68FR8C is DDR3 ECC UDIMM. Requires a motherboard with ECC support
  and DDR3 slots (Intel Xeon E3/E5-era or equivalent). Confirm BFB06612 board supports ECC before pairing.
- **GPU fit**: T400 is a low-profile PCIe card (single-slot, 70W) — fits in any ATX/mATX chassis.
  Supports 4 × mDP outputs. Suitable for workstation CAD + display acceleration, not CUDA-heavy ML.
- **Build potential**: SSD + GPU + board + 32GB DDR3 = a capable background compute node for
  batch OrcaFlex runs, simulation offload, or a dedicated Linux build/test server.

## Hardware Consolidation

> Fill in once workstation nicknames are confirmed.

### Consolidation Principles

1. **One primary** — single "source of truth" machine for active WRK items and git state
2. **Specialised nodes** — other machines run specific workloads (simulation batch, Windows tools)
   but do not carry main orchestrator context
3. **Spare → node** — build spare parts into a dedicated simulation/compute node rather than
   leaving components unallocated

### Candidate Uses for Spare Build

| Use Case | Fit | Notes |
|----------|-----|-------|
| OrcaFlex batch simulation node | Good | CPU-bound; 32GB RAM adequate for mid-size models |
| Linux build/test server | Good | Lightweight; SSD + RAM sufficient |
| CUDA ML training | Poor | T400 = 320 CUDA cores, 4GB — too limited for serious training |
| Basic ML inference / LLM offload | Fair | T400 can run small GGUF models via llama.cpp |
| CAD workstation | Fair | T400 supports Quadro drivers; adequate for FreeCAD/FEM work |

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
1. Add a row to the registry or inventory table
2. Note OS, primary use, capability constraints
3. Commit: `chore(workstations): update machine registry / spare inventory`
