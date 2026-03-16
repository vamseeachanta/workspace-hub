---
name: orcaflex-monolithic-to-modular-output-structure
description: 'Sub-skill of orcaflex-monolithic-to-modular: Output Structure.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Output Structure

## Output Structure


```
modular/
├── master.yml              # Entry point with include directives
├── includes/
│   ├── 01_general.yml      # General section (simulation, solver settings)
│   ├── 03_environment.yml  # Environment (water, waves, current, wind)
│   └── 20_generic_objects.yml  # All object sections (types, instances, singletons)
└── inputs/
    └── parameters.yml      # Extracted key parameters
```
