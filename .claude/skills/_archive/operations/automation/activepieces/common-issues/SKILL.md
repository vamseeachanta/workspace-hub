---
name: activepieces-common-issues
description: 'Sub-skill of activepieces: Common Issues (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: Flow not triggering**
```bash
# Check webhook URL is accessible
curl -X POST https://activepieces.example.com/api/v1/webhooks/your-flow-id \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Verify flow is enabled
# Check logs in Activepieces UI
```

**Issue: Connection authentication failing**
```bash
# Test credentials manually
curl -X GET "https://api.service.com/test" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Re-authenticate connection in UI
```

**Issue: Code step timeout**
```yaml
# Increase sandbox timeout
AP_SANDBOX_RUN_TIME_SECONDS: 600
```


## Debugging Tips


```typescript
// Add logging in code steps
console.log('Input:', JSON.stringify(inputs, null, 2));
console.log('Processing step...');

// Return debug info
return {
  result: processedData,
  debug: {
    input_count: inputs.items.length,
    processing_time_ms: Date.now() - startTime
  }
};
```
