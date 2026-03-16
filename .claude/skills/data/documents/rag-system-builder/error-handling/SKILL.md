---
name: rag-system-builder-error-handling
description: 'Sub-skill of rag-system-builder: Error Handling.'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: anthropic.APIError (rate limit)**
- Cause: Too many API requests
- Solution: Add exponential backoff retry logic

**Error: Empty search results**
- Cause: No relevant documents in knowledge base
- Solution: Expand search with lower similarity threshold

**Error: Context too long**
- Cause: Top-k chunks exceed model context window

*See sub-skills for full details.*
