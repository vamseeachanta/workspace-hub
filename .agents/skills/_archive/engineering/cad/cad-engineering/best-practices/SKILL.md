---
name: cad-engineering-best-practices
description: 'Sub-skill of cad-engineering: Best Practices.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


### Format Selection

1. **STEP**: Best for 3D geometry exchange
2. **IGES**: Legacy support, use STEP when possible
3. **DXF**: Best for 2D CAD interoperability
4. **STL**: 3D printing and visualization only

### Conversion Quality

1. Always verify dimensional accuracy after conversion
2. Check for missing entities (arcs, splines, text)
3. Validate layer structure preservation
4. Test with small sample before batch processing

### Automation

1. Use Python scripting for repeatable tasks
2. Create conversion templates for standard workflows
3. Implement quality checks in CI/CD pipelines
4. Document conversion parameters for reproducibility
