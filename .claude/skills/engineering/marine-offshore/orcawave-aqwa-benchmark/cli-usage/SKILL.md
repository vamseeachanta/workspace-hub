---
name: orcawave-aqwa-benchmark-cli-usage
description: 'Sub-skill of orcawave-aqwa-benchmark: CLI Usage.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# CLI Usage

## CLI Usage


```bash
# Run full benchmark comparison
python -m digitalmodel.diffraction.benchmark compare \
    --aqwa aqwa_results/vessel.LIS \
    --orcawave orcawave_results/vessel.owr \
    --output reports/comparison.html

# Peak-focused validation
python -m digitalmodel.diffraction.benchmark validate \
    --aqwa aqwa_results/vessel.LIS \
    --orcawave orcawave_results/vessel.owr \
    --tolerance 0.05 \
    --peak-threshold 0.10

# Generate comparison plots
python -m digitalmodel.diffraction.benchmark plot \
    --aqwa aqwa_results/vessel.LIS \
    --orcawave orcawave_results/vessel.owr \
    --output plots/ \
    --format html

# Export comparison data
python -m digitalmodel.diffraction.benchmark export \
    --aqwa aqwa_results/vessel.LIS \
    --orcawave orcawave_results/vessel.owr \
    --format csv \
    --output comparison_data.csv
```
