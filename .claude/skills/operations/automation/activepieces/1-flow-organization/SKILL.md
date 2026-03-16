---
name: activepieces-1-flow-organization
description: 'Sub-skill of activepieces: 1. Flow Organization (+3).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Flow Organization (+3)

## 1. Flow Organization

```
flows/
├── onboarding/
│   ├── customer-onboarding.json
│   └── employee-onboarding.json
├── integrations/
│   ├── crm-sync.json
│   ├── inventory-sync.json
│   └── payment-webhooks.json
├── notifications/
│   ├── alert-routing.json
│   └── daily-reports.json
└── utilities/
    ├── data-validation.json
    └── error-handler.json
```


## 2. Error Handling Best Practices

```typescript
// Always wrap external calls in try-catch
try {
  const result = await externalApiCall();
  return { success: true, data: result };
} catch (error) {
  // Return structured error for downstream handling
  return {
    success: false,
    error: error.message,
    retryable: !error.message.includes('PERMANENT'),
    timestamp: new Date().toISOString()
  };
}
```


## 3. Security Best Practices

```yaml
# Environment variables
AP_ENCRYPTION_KEY: "32-character-secure-key"
AP_JWT_SECRET: "secure-jwt-secret"
AP_WEBHOOK_TIMEOUT_SECONDS: 30

# Use connections for all credentials
# Never hardcode API keys in flow definitions
```


## 4. Performance Tips

```typescript
// Batch operations when possible
const BATCH_SIZE = 50;
const items = inputs.items;

for (let i = 0; i < items.length; i += BATCH_SIZE) {
  const batch = items.slice(i, i + BATCH_SIZE);
  await processBatch(batch);
}

// Use appropriate timeouts
const controller = new AbortController();
setTimeout(() => controller.abort(), 30000);
```
