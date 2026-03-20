---
name: workstations-dev-primary-storage
description: 'Sub-skill of workstations: dev-primary Storage (+1).'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# dev-primary Storage (+1)

## dev-primary Storage


| Device | Size | Type | Model | Notes |
|--------|------|------|-------|-------|
| sda | 7.3 TB | HDD | Seagate ST8000DM004 | /mnt/ace (bulk data); symlink /mnt/ace-data |
| sdb | 233 GB | SSD | Crucial CT250BX100 | / (OS, boot) |
| sdc | 932 GB | HDD | WD WD10EZEX | /mnt/local-analysis (workspace-hub, repos) |


## dev-secondary Storage


| Device | Size | Type | Model | Notes |
|--------|------|------|-------|-------|
| sdb | 465.8 GB | SSD | Samsung 870 EVO 500GB | OS / boot (from spare inventory) |
| sda | 931.5 GB | HDD | WDC WD10EZEX | /mnt/local-analysis |
| sdc | 2.7 TB | HDD | Seagate ST3000NC002 | /mnt/dde |
