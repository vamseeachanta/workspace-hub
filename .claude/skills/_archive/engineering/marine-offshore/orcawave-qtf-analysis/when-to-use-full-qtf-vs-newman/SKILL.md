---
name: orcawave-qtf-analysis-when-to-use-full-qtf-vs-newman
description: 'Sub-skill of orcawave-qtf-analysis: When to Use Full QTF vs Newman (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# When to Use Full QTF vs Newman (+2)

## When to Use Full QTF vs Newman


| Scenario | Recommendation |
|----------|----------------|
| Initial design | Newman approximation |
| Mooring design | Full QTF |
| Shallow water (d < 100m) | Full QTF required |
| Deep water (d > 300m) | Newman often sufficient |
| Bi-directional seas | Full QTF |
| Long-crested seas | Newman acceptable |
| SPM/turret systems | Full QTF |


## Computational Considerations


1. **Frequency Resolution**: Use 20-30 frequencies minimum for accurate QTF
2. **Heading Pairs**: Exploit symmetry to reduce computation
3. **Memory**: Full QTF matrices can be large; consider frequency range
4. **Validation**: Compare Newman vs Full for at least one condition
5. **Mesh Quality**: QTF more sensitive to mesh than first-order


## Integration with Mooring Analysis


```python
from digitalmodel.orcawave.qtf import QTFMooringIntegration

# Prepare QTF for mooring analysis
integration = QTFMooringIntegration()

# Load QTF results
integration.load_qtf("results/qtf/fpso_full.yml")

# Convert to mooring analysis format
integration.export_for_mooring_analysis(
    output_file="mooring/qtf_loading.yml",
    format="OrcaFlex",
    include_mean_drift=True,
    include_slow_drift=True,
    sea_state={
        "hs": 4.0,
        "tp": 10.0,
        "gamma": 3.3
    }
)
```
