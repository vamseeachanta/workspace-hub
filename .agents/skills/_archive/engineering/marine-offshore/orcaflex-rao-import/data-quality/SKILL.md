---
name: orcaflex-rao-import-data-quality
description: 'Sub-skill of orcaflex-rao-import: Data Quality (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Data Quality (+2)

## Data Quality


1. **Check source analysis** - Verify AQWA/WAMIT converged
2. **Review frequency range** - Cover wave spectrum
3. **Check peak responses** - Resonance captured
4. **Validate symmetry** - Port/starboard consistent


## Interpolation


1. **Don't extrapolate** - Stay within data range
2. **Preserve peaks** - Use adequate resolution
3. **Check quality metrics** - R² should be > 0.95
4. **Compare with source** - Spot-check values


## OrcaFlex Integration


1. **RAO origin** - Match vessel coordinate system
2. **Period vs frequency** - OrcaFlex uses periods
3. **Phase convention** - Check sign convention
4. **Test static equilibrium** - Verify RAO application
