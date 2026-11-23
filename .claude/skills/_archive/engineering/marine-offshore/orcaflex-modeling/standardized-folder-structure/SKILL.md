---
name: orcaflex-modeling-standardized-folder-structure
description: 'Sub-skill of orcaflex-modeling: Standardized Folder Structure.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Standardized Folder Structure

## Standardized Folder Structure


All OrcaFlex analyses MUST use this directory structure:

```
<analysis_directory>/
├── .dat/                    # OrcaFlex data files
│   ├── original/           # Original unmodified files
│   ├── modified/           # Modified during iteration
│   └── archive/            # Timestamped archives
├── .sim/                    # OrcaFlex simulation files
├── configs/                 # Configuration files
│   └── analysis_config.yml
├── results/                 # Analysis outputs
│   ├── summary/
│   ├── time_series/
│   └── reports/
├── logs/                    # Execution logs
└── scripts/                 # Helper scripts
```
