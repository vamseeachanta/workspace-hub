---
name: orcawave-qtf-analysis-cli-usage
description: 'Sub-skill of orcawave-qtf-analysis: CLI Usage.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# CLI Usage

## CLI Usage


```bash
# Compute full QTF
python -m digitalmodel.orcawave.qtf compute \
    --model models/fpso.owr \
    --method full \
    --output results/qtf/

# Mean drift extraction
python -m digitalmodel.orcawave.qtf mean-drift \
    --model models/fpso.owr \
    --method momentum \
    --output results/mean_drift.csv

# Newman approximation
python -m digitalmodel.orcawave.qtf newman \
    --raos results/fpso_raos.csv \
    --output results/newman_qtf.yml

# Slow drift analysis
python -m digitalmodel.orcawave.qtf slow-drift \
    --qtf results/qtf/fpso_full.yml \
    --hs 4.0 --tp 10.0 \
    --output results/slow_drift/

# Export to OrcaFlex
python -m digitalmodel.orcawave.qtf export \
    --qtf results/qtf/fpso_full.yml \
    --format orcaflex \
    --output orcaflex_models/fpso_qtf.yml
```
