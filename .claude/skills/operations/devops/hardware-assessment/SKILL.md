---
name: hardware-assessment
version: 1.1.0
description: "Cross-platform hardware assessment and system maintenance \u2014 assess\
  \ hardware, update OS/tools/custom software, and track changes over time via JSON\
  \ changelogs"
type: reference
author: workspace-hub
category: operations
capabilities:
- Collect full hardware inventory on Linux (Bash) and Windows (PowerShell)
- Update OS packages, common tools, and custom software lists
- "Orchestrate assess \u2192 update \u2192 re-assess with automatic changelog generation"
- "Zero external dependencies \u2014 uses built-in OS tools only"
- Unified JSON schema across platforms for easy comparison
- Optional root/admin mode for SMART data and RAM type detection
- GPU VRAM detection via nvidia-smi integration
tags:
- hardware
- inventory
- assessment
- system-info
- cross-platform
- json
- diagnostics
- updates
- maintenance
platforms:
- linux
- windows
related_skills:
- docker
- cli-productivity
requires: []
freedom: low
---

# Hardware Assessment

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

*See sub-skills for full details.*
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

## Version History

- **1.1.0** (2026-02-02): Add system-update and system-maintain orchestrator scripts for OS/tools/custom software updates with changelog tracking
- **1.0.0** (2026-02-02): Initial release — Linux Bash + Windows PowerShell scripts with unified JSON schema

## Sub-Skills

- [Troubleshooting](troubleshooting/SKILL.md)

## Sub-Skills

- [Scripts](scripts/SKILL.md)
- [Linux (`hardware-assess.sh`) (+1)](linux-hardware-assesssh/SKILL.md)
- [Output Schema (v1.0)](output-schema-v10/SKILL.md)
- [Linux (+1)](linux/SKILL.md)
- [Workflow: Multi-Machine Inventory](workflow-multi-machine-inventory/SKILL.md)
