---
name: bemrosetta-best-practices
description: 'Sub-skill of bemrosetta: Best Practices.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Always validate before conversion**
   ```python
   report = validate_coefficients(results, strict=True)
   if not report.is_valid:
       raise ValueError(f"Invalid coefficients: {report.errors}")
   ```

2. **Check mesh quality before use**
   ```python
   report = handler.validate_mesh(mesh)
   if report.quality_score < 70:
       print("Warning: Low mesh quality")
   ```

3. **Use native parsers for reliability**
   - Native Python parsers don't require BEMRosetta executable
   - BEMRosetta executable provides extended features when available

4. **Handle missing data gracefully**
   ```python
   warnings = converter.validate_input(results)
   for w in warnings:
       logger.warning(w)
   ```
