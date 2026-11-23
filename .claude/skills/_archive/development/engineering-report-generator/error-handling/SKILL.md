---
name: engineering-report-generator-error-handling
description: 'Sub-skill of engineering-report-generator: Error Handling.'
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
| `FileNotFoundError` | Data file missing | Verify data path is correct |
| `KeyError` | Column not in DataFrame | Check column names match config |
| `ValueError` | Data type mismatch | Convert types before plotting |
| `Empty figure` | No data after filtering | Validate data before visualization |
### Error Template


```python
def safe_generate_report(data_path: str, output_path: str, config: dict) -> dict:
    """Generate report with error handling."""
    try:
        # Validate data exists
        if not Path(data_path).exists():
            return {'status': 'error', 'message': f'Data file not found: {data_path}'}

        # Load and validate
        df = pd.read_csv(data_path)

*See sub-skills for full details.*
