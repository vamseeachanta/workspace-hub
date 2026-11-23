---
name: orcaflex-modal-analysis-with-viv-analysis
description: 'Sub-skill of orcaflex-modal-analysis: With VIV Analysis (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# With VIV Analysis (+1)

## With VIV Analysis


```python
# 1. Run modal analysis to get natural frequencies
modal_results = modal.run_modal_analysis(cfg)

# 2. Use frequencies in VIV assessment
from digitalmodel.subsea.viv_analysis.viv_analysis import VIVAnalysis
viv = VIVAnalysis()
viv_results = viv.screen_for_viv(natural_frequencies, current_profile)
```

## With OrcaFlex Post-Processing


```python
# After modal analysis, run dynamic simulation
# and extract time series at modal frequencies
```
