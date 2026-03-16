---
name: orcawave-to-orcaflex-standard-export-configuration
description: 'Sub-skill of orcawave-to-orcaflex: Standard Export Configuration (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Standard Export Configuration (+1)

## Standard Export Configuration


```yaml
# configs/orcawave_to_orcaflex.yml

conversion:
  input:
    orcawave_file: "models/fpso.owr"

  output:
    directory: "orcaflex_models/"
    vessel_type_file: "fpso_vessel_type.yml"

*See sub-skills for full details.*

## Batch Conversion Configuration


```yaml
# configs/batch_conversion.yml

batch_conversion:
  conditions:
    - name: "draft_22m"
      input: "models/fpso_draft22.owr"
      draft: 22.0
      trim: 0.0


*See sub-skills for full details.*
