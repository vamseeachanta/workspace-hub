---
name: cad-engineering-lossy-conversions
description: 'Sub-skill of cad-engineering: Lossy Conversions (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Lossy Conversions (+1)

## Lossy Conversions


```python
# Check for conversion losses
losses = converter.check_losses(
    original="model.step",
    converted="model.iges"
)

if losses["geometry_count_diff"] > 0:
    print(f"Lost {losses['geometry_count_diff']} entities")
if losses["accuracy_loss"] > 0.01:
    print(f"Accuracy loss: {losses['accuracy_loss']*100:.1f}%")
```

## Version Compatibility


```python
# Check format version before conversion
info = converter.get_format_info("drawing.dwg")
print(f"DWG Version: {info['version']}")
print(f"Created By: {info['application']}")
print(f"Compatible With: {info['compatible_versions']}")
```
