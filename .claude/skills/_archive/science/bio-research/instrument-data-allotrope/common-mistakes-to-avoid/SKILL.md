---
name: instrument-data-allotrope-common-mistakes-to-avoid
description: 'Sub-skill of instrument-data-allotrope: Common Mistakes to Avoid.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Common Mistakes to Avoid

## Common Mistakes to Avoid


| Mistake | Correct Approach |
|---------|------------------|
| Manifest as object | Use URL string |
| Lowercase detection types | Use "Absorbance" not "absorbance" |
| "emission wavelength setting" | Use "detector wavelength setting" for emission |
| All measurements in one document | Group by well/sample location |
| Missing procedure metadata | Extract ALL device settings per measurement |
