---
name: hardware-assessment-scripts
description: 'Sub-skill of hardware-assessment: Scripts.'
version: 1.1.0
category: operations
type: reference
scripts_exempt: true
---

# Scripts

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
