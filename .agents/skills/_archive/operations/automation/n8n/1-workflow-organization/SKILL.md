---
name: n8n-1-workflow-organization
description: 'Sub-skill of n8n: 1. Workflow Organization (+4).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Workflow Organization (+4)

## 1. Workflow Organization

```
workflows/
├── core/
│   ├── data-validation.json
│   ├── error-handler.json
│   └── notification-router.json
├── integrations/
│   ├── slack-bot.json
│   ├── github-sync.json
│   └── crm-sync.json
├── scheduled/
│   ├── daily-reports.json
│   └── weekly-cleanup.json
└── webhooks/
    ├── payment-processor.json
    └── form-handler.json
```


## 2. Error Handling Patterns

```javascript
// Always use try-catch in Code nodes
try {
  const result = await riskyOperation();
  return { success: true, data: result };
} catch (error) {
  // Log error details
  console.error('Operation failed:', error.message);

  // Return structured error for downstream handling
  return {
    success: false,
    error: error.message,
    timestamp: new Date().toISOString(),
    retryable: error.code !== 'PERMANENT_FAILURE'
  };
}
```


## 3. Security Best Practices

```yaml
# Production environment variables
N8N_ENCRYPTION_KEY: "32-character-secure-key"
N8N_USER_MANAGEMENT_JWT_SECRET: "secure-jwt-secret"
N8N_BASIC_AUTH_ACTIVE: "true"
N8N_BASIC_AUTH_USER: "admin"
N8N_BASIC_AUTH_PASSWORD: "${SECURE_PASSWORD}"

# Webhook security
WEBHOOK_URL: "https://n8n.example.com/"
N8N_WEBHOOK_TUNNEL_URL: ""  # Disable tunnel in production

# Database encryption
DB_POSTGRESDB_SSL_ENABLED: "true"
DB_POSTGRESDB_SSL_REJECT_UNAUTHORIZED: "true"
```


## 4. Performance Optimization

```javascript
// Batch processing for large datasets
const BATCH_SIZE = 100;
const items = $input.all();
const results = [];

for (let i = 0; i < items.length; i += BATCH_SIZE) {
  const batch = items.slice(i, i + BATCH_SIZE);

  // Process batch
  const batchResults = await Promise.all(
    batch.map(item => processItem(item.json))
  );

  results.push(...batchResults);

  // Optional: Add delay between batches to avoid rate limits
  if (i + BATCH_SIZE < items.length) {
    await new Promise(resolve => setTimeout(resolve, 100));
  }
}

return results;
```


## 5. Testing Workflows

```bash
# Export workflow for version control
curl -X GET "http://localhost:5678/api/v1/workflows/1" \
  -H "X-N8N-API-KEY: your-api-key" \
  -o workflow-backup.json

# Import workflow
curl -X POST "http://localhost:5678/api/v1/workflows" \
  -H "X-N8N-API-KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d @workflow-backup.json

# Execute workflow via API
curl -X POST "http://localhost:5678/api/v1/workflows/1/activate" \
  -H "X-N8N-API-KEY: your-api-key"
```
