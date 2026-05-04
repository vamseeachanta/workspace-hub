---
name: orcaflex-file-conversion-file-organization
description: 'Sub-skill of orcaflex-file-conversion: File Organization (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# File Organization (+1)

## File Organization


```
project/
├── models/
│   ├── original/          # Original .dat files (read-only)
│   ├── working/           # Working .yml files (editable)
│   └── generated/         # Generated .dat files for execution
├── results/
│   └── .sim/             # Simulation results
└── conversion_logs/      # Conversion reports and logs
```


## Workflow Recommendations


1. **Keep originals**: Always preserve original .dat files
2. **Version control YAML**: Commit .yml files, not .dat files
3. **Validate conversions**: Enable validation for production
4. **Batch processing**: Use parallel processing for large datasets
5. **Document changes**: Add comments in YAML files for modifications
