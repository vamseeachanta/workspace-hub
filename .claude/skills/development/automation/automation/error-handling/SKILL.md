---
name: automation-error-handling
description: 'Sub-skill of automation: Error Handling (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling (+2)

## Error Handling


```python
# Retry with exponential backoff
def with_retry(func, max_attempts=3, base_delay=1):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
```

## Secret Management


```yaml
# Use environment variables or secret stores
env:
  API_KEY: ${{ secrets.API_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Idempotency


```python
# Ensure operations can be safely retried
def process_with_idempotency(record_id, data):
    existing = get_by_id(record_id)
    if existing and existing.checksum == compute_checksum(data):
        return existing  # Already processed
    return upsert(record_id, data)
```
