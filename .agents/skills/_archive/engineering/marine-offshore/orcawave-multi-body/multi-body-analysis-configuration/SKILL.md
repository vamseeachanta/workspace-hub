---
name: orcawave-multi-body-multi-body-analysis-configuration
description: 'Sub-skill of orcawave-multi-body: Multi-Body Analysis Configuration
  (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Multi-Body Analysis Configuration (+1)

## Multi-Body Analysis Configuration


```yaml
# configs/multibody_analysis.yml

multibody:
  name: "FPSO_STS_Operation"

  bodies:
    - name: "FPSO"
      mesh: "geometry/fpso_panels.gdf"
      position: [0.0, 0.0, 0.0]

*See sub-skills for full details.*

## STS Operability Configuration


```yaml
# configs/sts_operability.yml

sts_operability:
  vessels:
    fpso:
      mesh: "geometry/fpso.gdf"
      loa: 300.0
      beam: 50.0
      draft: 22.0

*See sub-skills for full details.*
