---
name: hardware-assessment
version: 1.1.0
description: Cross-platform hardware assessment and system maintenance — assess hardware, update OS/tools/custom software, and track changes over time via JSON changelogs
author: workspace-hub
category: devops
capabilities:
  - Collect full hardware inventory on Linux (Bash) and Windows (PowerShell)
  - Update OS packages, common tools, and custom software lists
  - Orchestrate assess → update → re-assess with automatic changelog generation
  - Zero external dependencies — uses built-in OS tools only
  - Unified JSON schema across platforms for easy comparison
  - Optional root/admin mode for SMART data and RAM type detection
  - GPU VRAM detection via nvidia-smi integration
tags: [hardware, inventory, assessment, system-info, cross-platform, json, diagnostics, updates, maintenance]
platforms: [linux, windows]
related_skills:
  - docker
  - cli-productivity
---

# Hardware Assessment & System Maintenance Skill

Collect hardware specifications, update system software, and track changes over time on any Linux or Windows machine. Designed for fleet inventory, upgrade planning, and ongoing maintenance.

## When to Use This Skill

### USE when:
- Inventorying machines for consolidation or repurposing decisions
- Comparing hardware specs across multiple devices
- Planning GPU, RAM, or storage upgrades
- Auditing SMART health status across storage devices
- Keeping machines updated (OS packages, tools, custom software)
- Tracking what changed after updates via changelogs
- Documenting system configurations for compliance or handoff

### DON'T USE when:
- You need real-time monitoring (use Prometheus/Grafana instead)
- You need benchmark/performance data (this collects specs, not performance)

## Scripts

| Script | Platform | Purpose |
|--------|----------|---------|
| `hardware-assess.sh` | Linux | Collect hardware specs to JSON |
| `hardware-assess.ps1` | Windows | Collect hardware specs to JSON |
| `system-update.sh` | Linux | Update OS, tools, custom software |
| `system-update.ps1` | Windows | Update OS, tools, custom software |
| `system-maintain.sh` | Linux | Orchestrator: assess → update → re-assess → changelog |
| `system-maintain.ps1` | Windows | Orchestrator: assess → update → re-assess → changelog |

All scripts live in `scripts/operations/system/`.

## Quick Start

### Linux
```bash
# Copy script to target machine, then:
bash hardware-assess.sh -p

# With sudo for SMART data + RAM type:
sudo bash hardware-assess.sh -p

# Custom output path:
bash hardware-assess.sh -o /tmp/inventory.json --pretty
```

### Windows (PowerShell)
```powershell
# Run in PowerShell:
.\hardware-assess.ps1 -Pretty

# Custom output:
.\hardware-assess.ps1 -OutputFile C:\temp\inventory.json -Pretty
```

### Full Maintenance (assess + update + re-assess)
```bash
# Linux — runs all 4 phases, outputs to maintenance/ directory:
sudo bash system-maintain.sh -d ./maintenance

# With custom software config:
sudo bash system-maintain.sh -c ./custom-packages.json -d ./maintenance

# Assessment only (no updates):
bash system-maintain.sh --skip-update -d ./maintenance
```

```powershell
# Windows — same workflow:
.\system-maintain.ps1 -OutputDir .\maintenance

# With custom software:
.\system-maintain.ps1 -ConfigFile .\custom-packages.json -OutputDir .\maintenance
```

### Update Only (no assessment)
```bash
# Linux:
sudo bash system-update.sh -c ./custom-packages.json

# Windows:
.\system-update.ps1 -ConfigFile .\custom-packages.json
```

### Custom Software Config (JSON)
```json
{
  "packages": {
    "apt": ["openfoam", "freecad", "paraview", "smartmontools"],
    "snap": ["code"],
    "pip": ["numpy", "polars"]
  },
  "ppas": ["ppa:openfoam/latest"],
  "scripts": [
    { "name": "custom-tool", "check": "custom-tool --version", "install": "curl -sSL https://example.com/install.sh | bash" }
  ]
}
```

## CLI Flags

### Linux (`hardware-assess.sh`)
| Flag | Description |
|------|-------------|
| `-o`, `--output FILE` | Override output file path |
| `-p`, `--pretty` | Pretty-print JSON (uses jq or python3) |
| `-q`, `--quiet` | Suppress log messages |
| `-h`, `--help` | Show usage |

### Windows (`hardware-assess.ps1`)
| Flag | Description |
|------|-------------|
| `-OutputFile FILE` | Override output file path |
| `-Pretty` | Pretty-print JSON |
| `-Quiet` | Suppress log messages |
| `-Help` | Show usage |

## Output Schema (v1.0)

Both scripts produce identical JSON structure:

```json
{
  "schema_version": "1.0",
  "script_version": "1.0.0",
  "platform": "linux|windows",
  "timestamp": "ISO-8601",
  "cpu": {
    "model": "Intel Xeon E5-2630 v3 @ 2.40GHz",
    "architecture": "x86_64",
    "sockets": 2,
    "cores_per_socket": 8,
    "total_cores": 16,
    "threads_per_core": 2,
    "total_threads": 32,
    "max_mhz": "3200.0000",
    "l3_cache": "40 MiB"
  },
  "memory": {
    "total_kb": 32810676,
    "total_gb": "31.3",
    "type": "DDR4",
    "speed": "2133 MT/s"
  },
  "gpu": [{
    "name": "NVIDIA Corporation GM107 [GeForce GTX 750 Ti]",
    "pci_id": "81:00.0",
    "vram_mb": 2048,
    "driver_version": "535.288.01"
  }],
  "storage": [{
    "device": "/dev/sda",
    "size": "7.3T",
    "model": "ST8000DM004-2U9188",
    "serial": "ZR15GL5E",
    "type": "disk",
    "transport": "sata",
    "smart": {
      "status": "PASSED",
      "temperature_c": 35,
      "power_on_hours": 12450
    }
  }],
  "motherboard": {
    "vendor": "ASUSTeK COMPUTER INC.",
    "model": "Z10PE-D16 Series",
    "firmware_version": "0501",
    "firmware_date": "11/28/2014"
  },
  "network": [{
    "name": "enp3s0f0",
    "mac": "00:11:22:33:44:55",
    "state": "UP",
    "mtu": 1500,
    "speed_mbps": 1000,
    "ipv4": "192.168.1.100/24",
    "driver": "igb"
  }],
  "os": {
    "name": "Ubuntu 24.04.3 LTS",
    "kernel": "6.8.0-90-generic",
    "architecture": "x86_64",
    "hostname": "vamsee-linux1",
    "uptime_seconds": 78542
  }
}
```

## Privilege Levels

### Linux
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

### Windows
| Data | Standard user | Administrator |
|------|--------------|---------------|
| All CIM/WMI data | Full | Full |
| SMART counters | May be limited | Full |
| Storage reliability | May be limited | Full |

## Workflow: Multi-Machine Inventory

```bash
# 1. Copy script to each machine and run
scp hardware-assess.sh user@machine1:~/
ssh user@machine1 'bash ~/hardware-assess.sh -p -q'
scp user@machine1:~/hardware-assessment-*.json ./inventory/

# 2. Compare results
python3 -c "
import json, glob
for f in sorted(glob.glob('inventory/*.json')):
    d = json.load(open(f))
    cpu = d['cpu']
    mem = d['memory']
    gpus = d.get('gpu', [])
    gpu_str = gpus[0]['name'] if gpus else 'None'
    print(f\"{d['os']['hostname']:20s} | {cpu['model']:40s} | {cpu['total_cores']}C/{cpu['total_threads']}T | {mem['total_gb']} GB | {gpu_str}\")
"
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Memory type "unknown" | Not running as root | Run with `sudo` |
| SMART "unavailable" | Not root or smartctl missing | `sudo apt install smartmontools` + run with `sudo` |
| GPU VRAM null | nvidia-smi not installed | Install NVIDIA drivers |
| 0 storage devices | lsblk not available | Check PATH or install util-linux |
| PowerShell: access denied | CIM queries blocked | Run as Administrator |

## Version History

- **1.1.0** (2026-02-02): Add system-update and system-maintain orchestrator scripts for OS/tools/custom software updates with changelog tracking
- **1.0.0** (2026-02-02): Initial release — Linux Bash + Windows PowerShell scripts with unified JSON schema
