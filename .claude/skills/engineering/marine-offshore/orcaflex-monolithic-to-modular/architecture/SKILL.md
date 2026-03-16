---
name: orcaflex-monolithic-to-modular-architecture
description: 'Sub-skill of orcaflex-monolithic-to-modular: Architecture.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Architecture

## Architecture


```
┌──────────────┐    ┌────────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ .dat / .yml  │───>│ MonolithicExtractor │───>│ ProjectInputSpec │───>│ ModularModel     │
│ (monolithic) │    │   (extractor.py)    │    │   (spec.yml)     │    │ Generator        │
└──────────────┘    └────────────────────┘    └──────────────────┘    └────────┬────────┘
                                                                               │
                                                                    ┌──────────▼──────────┐
                                                                    │  modular/           │
                                                                    │  ├── master.yml     │
                                                                    │  ├── includes/      │
                                                                    │  │   ├── 01_general │
                                                                    │  │   ├── 03_env     │
                                                                    │  │   └── 20_generic │
                                                                    │  └── inputs/        │
                                                                    │      └── params.yml │
                                                                    └─────────────────────┘
```
