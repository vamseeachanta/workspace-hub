---
name: orcaflex-file-conversion-1-version-control-preparation
description: 'Sub-skill of orcaflex-file-conversion: 1. Version Control Preparation
  (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Version Control Preparation (+3)

## 1. Version Control Preparation


Convert binary .dat files to YAML for Git tracking:

```bash
python -m digitalmodel.orcaflex.examples_integration.batch_converter \
    --input-dir models/ \
    --output-dir models_version_control/ \
    --pattern "*.dat"

# Commit YAML files to Git
git add models_version_control/*.yml
git commit -m "Add OrcaFlex models in YAML format"
```

## 2. Automated Model Generation


Generate .dat files from YAML templates:

```python
import OrcFxAPI
from pathlib import Path
import yaml

# Load YAML template
with open("template.yml") as f:
    config = yaml.safe_load(f)

*See sub-skills for full details.*

## 3. Batch Analysis Preparation


Convert 180+ example files for analysis:

```python
from digitalmodel.orcaflex.examples_integration.batch_converter import OrcaFlexBatchConverter
from pathlib import Path

# Convert all examples
converter = OrcaFlexBatchConverter(
    input_dir=Path("docs/modules/orcaflex/examples/raw"),
    output_dir=Path("docs/modules/orcaflex/examples/yaml"),

*See sub-skills for full details.*

## 4. Model Inspection and Debugging


Convert .dat to .yml for inspection:

```bash
# Convert problematic model to YAML
python -m digitalmodel.orcaflex.orcaflex_yml_converter problem_model.dat

# Inspect YAML in text editor
code problem_model.yml

# Make corrections in YAML
# Convert back to .dat
python -m digitalmodel.orcaflex.orcaflex_yml_converter problem_model.yml
```
