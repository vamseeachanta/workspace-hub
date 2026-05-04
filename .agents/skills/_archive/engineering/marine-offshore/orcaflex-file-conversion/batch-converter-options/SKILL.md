---
name: orcaflex-file-conversion-batch-converter-options
description: 'Sub-skill of orcaflex-file-conversion: Batch Converter Options (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Batch Converter Options (+1)

## Batch Converter Options


```python
OrcaFlexBatchConverter(
    input_dir=Path,              # Source directory
    output_dir=Path,             # Destination directory
    use_mock=False,              # Use mock mode if OrcFxAPI unavailable
    validate=True,               # Validate YAML structure
    max_retries=2                # Retry attempts for failed conversions
)
```


## Conversion Modes


| Mode | Description | Use Case |
|------|-------------|----------|
| **Real** | Uses OrcFxAPI | Production conversions with license |
| **Mock** | Creates placeholder YAML | Testing without license |
