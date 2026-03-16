---
name: workstations-hardware-notes
description: 'Sub-skill of workstations: Hardware Notes.'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Hardware Notes

## Hardware Notes


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
