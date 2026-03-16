---
name: orcawave-multi-body-export-for-time-domain
description: 'Sub-skill of orcawave-multi-body: Export for Time-Domain.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Export for Time-Domain

## Export for Time-Domain


```python
from digitalmodel.orcawave.multibody import MultiBodyOrcaFlexExporter

# Export multi-body results for OrcaFlex
exporter = MultiBodyOrcaFlexExporter()

# Load multi-body results
exporter.load_results("results/multibody/coupled.owr")

# Export individual vessel types

*See sub-skills for full details.*
