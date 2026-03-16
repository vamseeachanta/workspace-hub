---
name: yaml-configuration-loading-yaml-in-python
description: 'Sub-skill of yaml-configuration: Loading YAML in Python (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Loading YAML in Python (+3)

## Loading YAML in Python


```python
import yaml
from pathlib import Path

def load_config(config_file: str) -> dict:
    """Load YAML configuration file."""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config


*See sub-skills for full details.*

## Writing YAML from Python


```python
import yaml

def save_config(config: dict, output_file: str):
    """Save configuration to YAML file."""
    with open(output_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

# Create configuration
config = {

*See sub-skills for full details.*

## Validation


```python
import yaml
from jsonschema import validate, ValidationError

def validate_config(config_file: str, schema_file: str) -> bool:
    """Validate YAML against JSON schema."""
    with open(config_file) as f:
        config = yaml.safe_load(f)

    with open(schema_file) as f:

*See sub-skills for full details.*

## Merging Configs


```python
def merge_configs(base_config: dict, override_config: dict) -> dict:
    """Deep merge two configuration dictionaries."""
    import copy

    result = copy.deepcopy(base_config)

    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)

*See sub-skills for full details.*
