---
name: n8n-common-issues
description: 'Sub-skill of n8n: Common Issues (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: Webhook not receiving data**
```bash
# Check webhook URL
curl -X POST https://n8n.example.com/webhook/your-path \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Verify workflow is active
# Check n8n logs
docker logs n8n-container 2>&1 | grep -i webhook

# Ensure WEBHOOK_URL is correctly set
echo $WEBHOOK_URL
```

**Issue: Credentials not working**
```bash
# Test credential manually
curl -X GET "https://api.example.com/test" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check encryption key is set
# Credentials are encrypted - changing key breaks existing credentials
echo $N8N_ENCRYPTION_KEY | wc -c  # Should be 32+ characters
```

**Issue: Workflow execution timeout**
```yaml
# Increase timeout in docker-compose
environment:
  - EXECUTIONS_TIMEOUT=3600  # 1 hour
  - EXECUTIONS_TIMEOUT_MAX=7200  # 2 hours max
```

**Issue: Memory issues with large datasets**
```javascript
// Stream processing instead of loading all data
// Use pagination in HTTP Request nodes
const PAGE_SIZE = 100;
let page = 1;
let hasMore = true;
const allResults = [];

while (hasMore) {
  const response = await $http.get(
    `https://api.example.com/data?page=${page}&limit=${PAGE_SIZE}`
  );

  allResults.push(...response.data.items);
  hasMore = response.data.has_more;
  page++;
}

return allResults;
```


## Debugging Tips


```javascript
// Add debugging output in Code nodes
console.log('Input data:', JSON.stringify($input.all(), null, 2));
console.log('Environment:', $env.NODE_ENV);
console.log('Workflow:', $workflow.name);

// Check execution context
console.log('Execution ID:', $execution.id);
console.log('Execution mode:', $execution.mode);

// Inspect previous node output
const previousOutput = $('Previous Node Name').all();
console.log('Previous output:', previousOutput);
```

```bash
# View execution logs
docker logs -f n8n-container 2>&1 | grep -E "(error|warn|execution)"

# Check database for failed executions
docker exec -it postgres psql -U n8n -d n8n -c \
  "SELECT id, status, started_at FROM execution_entity WHERE status = 'error' ORDER BY started_at DESC LIMIT 10;"
```
