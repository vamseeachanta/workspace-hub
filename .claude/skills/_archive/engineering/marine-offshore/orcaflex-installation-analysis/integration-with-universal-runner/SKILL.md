---
name: orcaflex-installation-analysis-integration-with-universal-runner
description: 'Sub-skill of orcaflex-installation-analysis: Integration with Universal
  Runner.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Integration with Universal Runner

## Integration with Universal Runner


After generating installation models, run batch simulations:

```python
from digitalmodel.orcaflex.universal import UniversalOrcaFlexRunner

# Initialize runner
runner = UniversalOrcaFlexRunner(
    input_directory="results/installation/",
    output_directory="results/installation/.sim/",
    mock_mode=False
)

# Run all installation models
results = runner.run_batch(
    pattern="el_*.yml",
    parallel=True,
    max_workers=4
)

# Check results
for file_name, status in results.items():
    print(f"{file_name}: {'SUCCESS' if status['success'] else 'FAILED'}")
```
