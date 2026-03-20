---
name: workstations-consolidation-principles
description: 'Sub-skill of workstations: Consolidation Principles (+1).'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Consolidation Principles (+1)

## Consolidation Principles


1. **One primary** — single "source of truth" machine for active WRK items and git state
2. **Specialised nodes** — other machines run specific workloads (simulation batch, Windows tools)
   but do not carry main orchestrator context
3. **Spare → node** — build spare parts into a dedicated simulation/compute node rather than
   leaving components unallocated


## Candidate Uses for Spare Build


| Use Case | Fit | Target | Notes |
|----------|-----|--------|-------|
| SSD upgrade | Good | dev-primary | 500GB SSD → replace/supplement existing 233GB SSD |
| Extra display output | Good | dev-primary | T400 (4 × mDP) in second PCIe slot if available |
| GPU upgrade (display) | Good | Windows machine | T400 or GPU 2 as replacement for older card |
| RAM upgrade | Poor (Linux) | Windows machine | DDR3 ECC ≠ compatible with E5-2630 v3 (DDR4 board) — check Windows machine first |
| CUDA ML training | Poor | — | T400 = 320 CUDA cores, 4GB — too limited; GPU 2 TBD |
| Basic ML inference | Fair | dev-primary | T400 can run small GGUF models via llama.cpp alongside GTX 750 Ti |
| Standalone build | Poor | — | No spare motherboard — can't build without one |
