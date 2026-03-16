---
name: core-coder-error-handling
description: 'Sub-skill of core-coder: Error Handling.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


| Error Type | Cause | Recovery |
|------------|-------|----------|
| ValidationError | Invalid input data | Return 400 with message |
| NotFoundError | Resource doesn't exist | Return 404 |
| AuthorizationError | Insufficient permissions | Return 403 |
| ServiceError | Internal failure | Log, return 500 |
