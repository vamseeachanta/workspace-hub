---
name: semantic-search-setup-error-handling
description: 'Sub-skill of semantic-search-setup: Error Handling.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: CUDA out of memory**
- Cause: GPU memory insufficient for model
- Solution: Set `CUDA_VISIBLE_DEVICES=""` to force CPU mode

**Error: Model download fails**
- Cause: Network issues or model not found
- Solution: Check internet connection, verify model name

**Error: numpy.frombuffer dimension mismatch**
- Cause: Embedding stored with different model

*See sub-skills for full details.*
