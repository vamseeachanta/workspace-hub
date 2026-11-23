---
name: parallel-file-processor-error-handling
description: 'Sub-skill of parallel-file-processor: Error Handling.'
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
| `MemoryError` | Too many files loaded | Use batching or streaming |
| `PermissionError` | File access denied | Check file permissions |
| `TimeoutError` | Processing too slow | Increase timeout or optimize |
| `OSError` | Too many open files | Reduce max_workers |
### Error Template


```python
def safe_process_directory(directory: Path, processor: Callable) -> dict:
    """Process directory with comprehensive error handling."""
    try:
        if not directory.exists():
            return {'status': 'error', 'message': 'Directory not found'}

        file_processor = FileProcessor()
        result = file_processor.process_directory(directory, processor)


*See sub-skills for full details.*
