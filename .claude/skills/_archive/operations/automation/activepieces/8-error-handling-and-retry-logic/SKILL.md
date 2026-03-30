---
name: activepieces-8-error-handling-and-retry-logic
description: 'Sub-skill of activepieces: 8. Error Handling and Retry Logic.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 8. Error Handling and Retry Logic

## 8. Error Handling and Retry Logic


```typescript
// Error handling patterns
const errorHandlingFlow = {
  "displayName": "Resilient API Integration",
  "trigger": {
    "name": "schedule",
    "type": "SCHEDULE",
    "settings": {
      "cronExpression": "*/15 * * * *"
    },
    "displayName": "Every 15 Minutes"
  },
  "steps": [
    {
      "name": "fetch_with_retry",
      "type": "CODE",
      "settings": {
        "input": {
          "api_url": "{{connections.external_api.base_url}}/data",
          "api_key": "{{connections.external_api.api_key}}"
        },
        "sourceCode": {
          "code": `
export const code = async (inputs) => {
  const { api_url, api_key } = inputs;
  const maxRetries = 3;
  const baseDelay = 1000;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(api_url, {
        headers: { Authorization: \`Bearer \${api_key}\` },
        signal: AbortSignal.timeout(30000)  // 30 second timeout
      });

      if (response.status === 429) {
        // Rate limited - wait and retry
        const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
        if (attempt < maxRetries) {
          await new Promise(r => setTimeout(r, retryAfter * 1000));
          continue;
        }
      }

      if (!response.ok) {
        throw new Error(\`HTTP \${response.status}: \${response.statusText}\`);
      }

      const data = await response.json();
      return {
        success: true,
        data,
        attempts: attempt
      };

    } catch (error) {
      if (attempt === maxRetries) {
        return {
          success: false,
          error: error.message,
          attempts: attempt
        };
      }

      // Exponential backoff
      const delay = baseDelay * Math.pow(2, attempt - 1);
      await new Promise(r => setTimeout(r, delay));
    }
  }
};`
        }
      },
      "displayName": "Fetch with Retry"
    },
    {
      "name": "handle_result",
      "type": "BRANCH",
      "settings": {
        "conditions": [
          {
            "name": "success",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{fetch_with_retry.success}} === true"
            },
            "steps": [
              {
                "name": "process_data",
                "type": "CODE",
                "settings": {
                  "input": {
                    "data": "{{fetch_with_retry.data}}"
                  },
                  "sourceCode": {
                    "code": `
export const code = async (inputs) => {
  const { data } = inputs;
  // Process successful data
  return {
    processed: true,
    count: data.length,
    timestamp: new Date().toISOString()
  };
};`
                  }
                }
              }
            ]
          },
          {
            "name": "failure",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{fetch_with_retry.success}} === false"
            },
            "steps": [
              {
                "name": "alert_failure",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-slack",
                  "actionName": "send_message",
                  "input": {
                    "channel": "#alerts",
                    "text": "API Integration Failed after {{fetch_with_retry.attempts}} attempts. Error: {{fetch_with_retry.error}}"
                  }
                }
              },
              {
                "name": "log_failure",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-http",
                  "actionName": "send_request",
                  "input": {
                    "method": "POST",
                    "url": "{{connections.logging_api.base_url}}/errors",
                    "body": {
                      "flow": "Resilient API Integration",
                      "error": "{{fetch_with_retry.error}}",
                      "attempts": "{{fetch_with_retry.attempts}}",
                      "timestamp": "{{now}}"
                    }
                  }
                }
              }
            ]
          }
        ]
      },
      "displayName": "Handle Result"
    }
  ]
};
```
