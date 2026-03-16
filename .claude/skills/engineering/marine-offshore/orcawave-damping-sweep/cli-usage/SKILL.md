---
name: orcawave-damping-sweep-cli-usage
description: 'Sub-skill of orcawave-damping-sweep: CLI Usage.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# CLI Usage

## CLI Usage


```bash
# Run damping sweep
python -m digitalmodel.orcawave.damping sweep \
    --model models/fpso.owr \
    --parameter roll_damping \
    --values 0.02,0.04,0.06,0.08,0.10 \
    --output results/roll_sweep/

# Multi-parameter sweep
python -m digitalmodel.orcawave.damping multi-sweep \
    --config configs/damping_sweep.yml \
    --output results/multi_sweep/

# Calculate critical damping
python -m digitalmodel.orcawave.damping critical \
    --model models/fpso.owr \
    --output critical_damping.csv

# Compare with model tests
python -m digitalmodel.orcawave.damping compare \
    --orcawave results/fpso.owr \
    --model-test data/roll_decay.csv \
    --output reports/comparison.html

# Estimate bilge keel damping

*See sub-skills for full details.*
