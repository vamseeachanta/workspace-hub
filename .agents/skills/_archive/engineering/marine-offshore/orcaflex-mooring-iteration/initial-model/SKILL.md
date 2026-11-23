---
name: orcaflex-mooring-iteration-initial-model
description: 'Sub-skill of orcaflex-mooring-iteration: Initial Model (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Initial Model (+2)

## Initial Model


1. **Start close to target** - Begin with reasonable pretension estimate
2. **Verify static convergence** - Model must converge before iteration
3. **Check line connectivity** - Ensure proper vessel/anchor connections
4. **Reasonable initial lengths** - Avoid extreme configurations


## Configuration


1. **Start with default damping** (0.7) - Reduce if oscillating
2. **Use appropriate method** - Scipy for most cases
3. **Set realistic tolerances** - 1% is typical for design
4. **Limit iterations** - 50-100 usually sufficient


## Troubleshooting


1. **No convergence** - Reduce damping factor
2. **Oscillating** - Increase damping, check Jacobian
3. **Slow convergence** - Check EA values, initial guess
4. **Invalid lengths** - Set min/max length limits
