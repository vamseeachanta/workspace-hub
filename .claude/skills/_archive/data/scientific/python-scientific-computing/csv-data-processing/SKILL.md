---
name: python-scientific-computing-csv-data-processing
description: 'Sub-skill of python-scientific-computing: CSV Data Processing (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# CSV Data Processing (+1)

## CSV Data Processing


```python
import numpy as np

# Load OrcaFlex results
data = np.loadtxt('../data/processed/orcaflex_results.csv',
                   delimiter=',', skiprows=1)

# Process time series
time = data[:, 0]
tension = data[:, 1]

*See sub-skills for full details.*

## YAML Configuration Integration


```python
import yaml
import numpy as np

def run_analysis_from_config(config_file: str):
    with open(config_file) as f:
        config = yaml.safe_load(f)

    # Extract parameters
    L = config['geometry']['length']

*See sub-skills for full details.*
