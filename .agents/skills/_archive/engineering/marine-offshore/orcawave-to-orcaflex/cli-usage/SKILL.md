---
name: orcawave-to-orcaflex-cli-usage
description: 'Sub-skill of orcawave-to-orcaflex: CLI Usage.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# CLI Usage

## CLI Usage


```bash
# Basic conversion
python -m digitalmodel.orcawave.convert \
    --input models/fpso.owr \
    --output orcaflex_models/fpso_vessel_type.yml

# With viscous damping
python -m digitalmodel.orcawave.convert \
    --input models/fpso.owr \
    --output orcaflex_models/fpso_vessel_type.yml \
    --roll-damping 0.05 \
    --pitch-damping 0.03

# Include QTF
python -m digitalmodel.orcawave.convert \
    --input models/fpso.owr \
    --output orcaflex_models/fpso_vessel_type.yml \
    --include-qtf \
    --include-mean-drift

# Batch conversion
python -m digitalmodel.orcawave.convert batch \
    --config configs/batch_conversion.yml

# Validate before export

*See sub-skills for full details.*
