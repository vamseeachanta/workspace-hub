---
name: orcaflex-modeling-common-issues
description: 'Sub-skill of orcaflex-modeling: Common Issues.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


1. **License Not Available**
   ```python
   # Use mock mode for development/testing
   runner = UniversalOrcaFlexRunner(mock_mode=True)
   ```

2. **Model Convergence Failure**
   - Check initial conditions
   - Reduce time step
   - Verify boundary conditions

3. **Memory Issues with Large Batches**
   - Limit `max_workers` parameter
   - Process in smaller batches
   - Use sequential processing for very large models
