---
name: data-pipeline-processor-error-handling
description: 'Sub-skill of data-pipeline-processor: Error Handling.'
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
| `UnicodeDecodeError` | Wrong encoding | Use DataReader with encoding fallback |
| `KeyError` | Missing column | Check column names in config |
| `ValueError` | Type conversion failed | Use errors='coerce' or validate first |
| `MemoryError` | File too large | Use chunked reading |
| `FileNotFoundError` | Input file missing | Verify file path |
### Error Template


```python
def safe_pipeline_run(config: PipelineConfig) -> dict:
    """Run pipeline with comprehensive error handling."""
    try:
        # Validate input exists
        if not Path(config.input_path).exists():
            return {'status': 'error', 'stage': 'input', 'message': 'File not found'}

        pipeline = DataPipeline(config)
        return pipeline.run()

*See sub-skills for full details.*
