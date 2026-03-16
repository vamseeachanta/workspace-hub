---
name: n8n-5-data-transformation-with-code-node
description: 'Sub-skill of n8n: 5. Data Transformation with Code Node (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 5. Data Transformation with Code Node (+1)

## 5. Data Transformation with Code Node


```javascript
// Code Node: Advanced Data Transformation
// Mode: Run Once for All Items

// Access all input items
const items = $input.all();

// Group items by category
const groupedByCategory = items.reduce((acc, item) => {
  const category = item.json.category || 'uncategorized';
  if (!acc[category]) {
    acc[category] = [];
  }
  acc[category].push(item.json);
  return acc;
}, {});

// Calculate statistics per category
const categoryStats = Object.entries(groupedByCategory).map(([category, items]) => {
  const values = items.map(i => parseFloat(i.value) || 0);

  return {
    category,
    count: items.length,
    total: values.reduce((a, b) => a + b, 0),
    average: values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0,
    min: Math.min(...values),
    max: Math.max(...values),
    items: items
  };
});

// Sort by total value descending
categoryStats.sort((a, b) => b.total - a.total);

// Add metadata
const result = {
  generated_at: new Date().toISOString(),
  total_items: items.length,
  total_categories: categoryStats.length,
  categories: categoryStats
};

return result;
```

```javascript
// Code Node: HTTP Request with Retry Logic
// Mode: Run Once for Each Item

const maxRetries = 3;
const baseDelay = 1000;

async function fetchWithRetry(url, options, attempt = 1) {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (attempt >= maxRetries) {
      throw error;
    }

    const delay = baseDelay * Math.pow(2, attempt - 1);
    await new Promise(resolve => setTimeout(resolve, delay));

    return fetchWithRetry(url, options, attempt + 1);
  }
}

const item = $input.item.json;

try {
  const result = await fetchWithRetry(
    `https://api.example.com/process/${item.id}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${$env.API_TOKEN}`
      },
      body: JSON.stringify(item)
    }
  );

  return {
    ...item,
    api_response: result,
    status: 'success'
  };
} catch (error) {
  return {
    ...item,
    error: error.message,
    status: 'failed'
  };
}
```


## 6. Credentials Management


```bash
# Environment variables for n8n
export N8N_ENCRYPTION_KEY="your-32-char-encryption-key-here"
export N8N_USER_MANAGEMENT_JWT_SECRET="your-jwt-secret"

# Database configuration
export DB_TYPE=postgresdb
export DB_POSTGRESDB_HOST=localhost
export DB_POSTGRESDB_PORT=5432
export DB_POSTGRESDB_DATABASE=n8n
export DB_POSTGRESDB_USER=n8n
export DB_POSTGRESDB_PASSWORD=secure_password

# External service credentials (set in n8n UI)
# These are stored encrypted in the database
```

```json
{
  "name": "Using Credentials Securely",
  "nodes": [
    {
      "parameters": {
        "url": "={{ $env.API_BASE_URL }}/users",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-Custom-Header",
              "value": "={{ $env.CUSTOM_HEADER_VALUE }}"
            }
          ]
        }
      },
      "id": "http",
      "name": "API Call",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [460, 300],
      "credentials": {
        "httpHeaderAuth": {
          "id": "1",
          "name": "API Key Auth"
        }
      }
    }
  ]
}
```
