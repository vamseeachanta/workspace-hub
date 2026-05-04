---
name: yaml-workflow-executor-error-handling
description: 'Sub-skill of yaml-workflow-executor: Error Handling.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Config file missing | Verify config path |
| `ValueError: Unknown task` | Handler not registered | Check task name spelling |
| `KeyError` | Missing required config field | Add missing field to YAML |
| `yaml.YAMLError` | Invalid YAML syntax | Validate YAML format |
### Error Template


```python
def safe_execute_workflow(yaml_path: str) -> dict:
    """Execute workflow with comprehensive error handling."""
    try:
        # Validate config exists
        if not Path(yaml_path).exists():
            return {'status': 'error', 'message': f'Config not found: {yaml_path}'}

        # Load and validate
        config = WorkflowConfig.from_yaml(yaml_path)

*See sub-skills for full details.*
