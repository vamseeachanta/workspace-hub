---
name: orcaflex-file-conversion-common-issues
description: 'Sub-skill of orcaflex-file-conversion: Common Issues.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**1. OrcFxAPI Not Available**
```python
try:
    import OrcFxAPI
except ImportError:
    print("ERROR: OrcFxAPI not available")
    print("Install: pip install <OrcaFlex_install_dir>/OrcFxAPI/Python")
    # Fall back to mock mode
    converter = OrcaFlexBatchConverter(use_mock=True)
```

*See sub-skills for full details.*
