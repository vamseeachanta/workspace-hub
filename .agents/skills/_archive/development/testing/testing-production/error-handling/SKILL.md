---
name: testing-production-error-handling
description: 'Sub-skill of testing-production: Error Handling.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Mock Found in Production Code


```bash
# Identify and report violations
grep -rn "mock\|fake\|stub" src/ --exclude-dir=__tests__ | while read line; do
  echo "VIOLATION: $line"
  echo "ACTION: Replace with real implementation"
done
```
### External Service Unavailable


```typescript
// Graceful handling of service outages during validation
try {
  await validateExternalService(service);
} catch (error) {
  if (error.code === 'ECONNREFUSED') {
    console.warn(`Service ${service.name} unavailable - skipping validation`);
    skippedValidations.push(service.name);
  } else {
    throw error;

*See sub-skills for full details.*
