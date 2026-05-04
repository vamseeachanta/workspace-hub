---
name: orcawave-multi-body-cli-usage
description: 'Sub-skill of orcawave-multi-body: CLI Usage.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# CLI Usage

## CLI Usage


```bash
# Run multi-body analysis
python -m digitalmodel.orcawave.multibody run \
    --config configs/multibody_analysis.yml \
    --output results/multibody/

# Analyze gap resonance
python -m digitalmodel.orcawave.multibody gap-resonance \
    --results results/multibody/coupled.owr \
    --gap-width 8.0 \
    --output plots/gap_resonance.html

# Compute shielding factors
python -m digitalmodel.orcawave.multibody shielding \
    --results results/multibody/coupled.owr \
    --shielding-body FPSO \
    --target-body Shuttle_Tanker \
    --output reports/shielding.csv

# STS operability analysis
python -m digitalmodel.orcawave.multibody operability \
    --config configs/sts_operability.yml \
    --output reports/sts_operability.html

# Extract coupling matrices
python -m digitalmodel.orcawave.multibody coupling \
    --results results/multibody/coupled.owr \
    --frequency 0.1 \
    --output coupling_matrices.csv
```
