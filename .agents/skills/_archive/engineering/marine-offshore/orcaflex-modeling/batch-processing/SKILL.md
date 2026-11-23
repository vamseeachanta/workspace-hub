---
name: orcaflex-modeling-batch-processing
description: 'Sub-skill of orcaflex-modeling: Batch Processing.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Batch Processing

## Batch Processing


```python
from digitalmodel.orcaflex.run_to_sim import OrcaFlexModelRunner

# Initialize runner
runner = OrcaFlexModelRunner()

# Run single model → .sim file
runner.run_single_model(
    model_file="model.yml",
    output_dir="results/.sim/"

*See sub-skills for full details.*
