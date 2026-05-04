---
name: orcawave-to-orcaflex-error-handling
description: 'Sub-skill of orcawave-to-orcaflex: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
# Handle conversion errors
try:
    converter = OrcaWaveConverter(vessel)
    data = converter.convert()

except MissingDataError as e:
    print(f"Required data missing: {e}")
    # Check OrcaWave analysis completeness

except FrequencyMismatchError as e:
    print(f"Frequency discretization issue: {e}")
    # Interpolate to common frequencies

except CoordinateTransformError as e:
    print(f"Coordinate transformation failed: {e}")
    # Verify origin definitions

except ExportError as e:
    print(f"Export failed: {e}")
    # Check output directory permissions
```
