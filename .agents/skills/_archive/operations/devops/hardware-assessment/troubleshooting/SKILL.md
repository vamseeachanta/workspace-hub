---
name: hardware-assessment-troubleshooting
description: 'Sub-skill of hardware-assessment: Troubleshooting.'
version: 1.1.0
category: operations
type: reference
scripts_exempt: true
---

# Troubleshooting

## Troubleshooting


| Issue | Cause | Fix |
|-------|-------|-----|
| Memory type "unknown" | Not running as root | Run with `sudo` |
| SMART "unavailable" | Not root or smartctl missing | `sudo apt install smartmontools` + run with `sudo` |
| GPU VRAM null | nvidia-smi not installed | Install NVIDIA drivers |
| 0 storage devices | lsblk not available | Check PATH or install util-linux |
| PowerShell: access denied | CIM queries blocked | Run as Administrator |
