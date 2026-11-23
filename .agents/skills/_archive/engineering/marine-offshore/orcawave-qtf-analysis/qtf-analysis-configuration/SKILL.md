---
name: orcawave-qtf-analysis-qtf-analysis-configuration
description: 'Sub-skill of orcawave-qtf-analysis: QTF Analysis Configuration (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# QTF Analysis Configuration (+1)

## QTF Analysis Configuration


```yaml
# configs/qtf_analysis.yml

qtf_analysis:
  model:
    file: "models/fpso.owr"

  computation:
    mean_drift: true
    difference_frequency: true

*See sub-skills for full details.*

## Slow Drift Configuration


```yaml
# configs/slow_drift.yml

slow_drift:
  qtf_source: "results/qtf/fpso_full_qtf.yml"

  sea_states:
    - name: "operational"
      hs: 2.5
      tp: 8.0

*See sub-skills for full details.*
