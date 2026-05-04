---
name: github-workflow-error-handling
description: 'Sub-skill of github-workflow: Error Handling.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: ENOSPC (No space left)**
- Cause: Disk space exhausted
- Solution: Clear caches, use smaller runners

**Error: Rate limit exceeded**
- Cause: Too many API calls
- Solution: Add delays, use caching

**Error: Timeout exceeded**
- Cause: Long-running job
- Solution: Increase timeout or optimize job
