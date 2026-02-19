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
| GPU 1 | NVIDIA T400 4GB GDDR6 (RTL ENG SCB) | Available | PCIe; CAD display, basic ML inference, multi-monitor |
| GPU 2 | Board ID: BFB06612 / Part: 4110T50R | Available | **Model unidentified** — check chip marking or run `lspci \| grep -i vga` |
| RAM | 4 × 8GB DDR3 ECC UDIMM — Hynix HMT41GU68FR8C (2Rx8 PC3) | Available | 32GB total; DDR3 ECC — requires DDR3 board with ECC support |

### Hardware Notes

- **GPU 2 identification**: BFB06612 is a PCB board ID, not a market name. To identify:
  - Linux: `lspci | grep -i vga` (plug in, boot, check output)
  - Windows: Device Manager → Display Adapters
  - Physical: look for "GeForce / Quadro / Radeon" chip marking on the card
- **GPU 1 (T400)**: Low-profile PCIe, single-slot, 70W, 4 × mDP. Good for CAD/display, not CUDA training.
- **RAM**: DDR3 ECC — needs a DDR3-era board with ECC support (Intel Xeon E3/E5-class or equivalent).
  No spare motherboard in inventory — RAM requires a compatible existing workstation or future board purchase.
- **Two GPUs, no board**: Spares = SSD + 2 GPUs + 32GB DDR3 RAM. Most useful as upgrades to
  existing machines rather than a standalone build (no board to build around).

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
| GPU upgrade to existing workstation | Good | T400 or GPU 2 (once identified) can replace older cards |
| Extra display output | Good | T400 supports 4 × mDP — useful for multi-monitor setup |
| SSD upgrade / extra storage | Good | 500GB SSD = fast OS drive or scratch disk for any workstation |
| RAM upgrade | Fair | 32GB DDR3 ECC — only fits DDR3 boards; verify compatibility first |
| CUDA ML training | Poor | T400 = 320 CUDA cores, 4GB — too limited; GPU 2 TBD |
| Basic ML inference / LLM offload | Fair | T400 can run small GGUF models via llama.cpp |
| Standalone build | Poor | No spare motherboard — can't build without one |

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
