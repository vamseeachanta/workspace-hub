---
name: orcawave-damping-sweep-damping-sweep-configuration
description: 'Sub-skill of orcawave-damping-sweep: Damping Sweep Configuration (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Damping Sweep Configuration (+1)

## Damping Sweep Configuration


```yaml
# configs/damping_sweep.yml

damping_sweep:
  model: "models/fpso.owr"

  parameters:
    roll_damping:
      type: "percent_critical"
      values: [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]

*See sub-skills for full details.*

## Model Test Comparison Configuration


```yaml
# configs/model_test_comparison.yml

model_test_comparison:
  orcawave_results: "results/fpso.owr"

  model_test_data:
    roll_decay: "data/roll_decay.csv"
    pitch_decay: "data/pitch_decay.csv"
    regular_wave_tests: "data/regular_waves.csv"

*See sub-skills for full details.*
