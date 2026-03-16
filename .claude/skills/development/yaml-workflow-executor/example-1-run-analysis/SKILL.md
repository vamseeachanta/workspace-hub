---
name: yaml-workflow-executor-example-1-run-analysis
description: 'Sub-skill of yaml-workflow-executor: Example 1: Run Analysis (+3).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Run Analysis (+3)

## Example 1: Run Analysis


```bash
# Direct execution
python -m workflow_executor config/workflows/analysis.yaml

# With overrides
python -m workflow_executor config/workflows/analysis.yaml \
    --override filter_value=completed \
    --override date_range.start=2024-06-01

# Via bash script
./scripts/run_workflow.sh config/workflows/analysis.yaml -v
```


## Example 2: Batch Processing


```python
from pathlib import Path

# Process multiple configs
config_dir = Path('config/workflows/')
for config_file in config_dir.glob('*.yaml'):
    print(f"Processing: {config_file}")
    result = execute_workflow(str(config_file))
    print(f"Result: {result}")
```


## Example 3: Programmatic Use


```python
# Load and modify config programmatically
config = WorkflowConfig.from_yaml('config/base.yaml')
config.parameters['custom_param'] = 'value'
config.input['data_path'] = 'data/custom_input.csv'

result = router.route(config)
```


## Example 4: Dynamic Workflow Generation


```python
import yaml

def generate_workflow_config(data_files: list, output_dir: str) -> str:
    """Generate workflow config for multiple data files."""
    config = {
        'task': 'pipeline',
        'steps': []
    }

    for i, data_file in enumerate(data_files):
        config['steps'].append({
            'name': f'process_{i}',
            'task': 'analyze_data',
            'input': {'data_path': data_file},
            'output': {'results_path': f'{output_dir}/result_{i}.json'}
        })

    config_path = 'config/generated_workflow.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    return config_path
```
