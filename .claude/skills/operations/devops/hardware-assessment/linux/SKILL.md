---
name: hardware-assessment-linux
description: 'Sub-skill of hardware-assessment: Linux (+1).'
version: 1.1.0
category: operations
type: reference
scripts_exempt: true
---

# Linux (+1)

## Linux


| Data | No root | With sudo |
|------|---------|-----------|
| CPU, OS, Network | Full | Full |
| Memory total | Full | Full |
| Memory type/speed | "unknown" | DDR type + speed via dmidecode |
| GPU name + driver | Full | Full |
| GPU VRAM | Via nvidia-smi | Via nvidia-smi |
| Storage devices | Full | Full |
| SMART health | "unavailable" | Full via smartctl |
| Motherboard | Via /sys/class/dmi/id/ | Full via dmidecode |

## Windows


| Data | Standard user | Administrator |
|------|--------------|---------------|
| All CIM/WMI data | Full | Full |
| SMART counters | May be limited | Full |
| Storage reliability | May be limited | Full |
