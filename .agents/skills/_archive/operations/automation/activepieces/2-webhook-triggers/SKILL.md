---
name: activepieces-2-webhook-triggers
description: 'Sub-skill of activepieces: 2. Webhook Triggers.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 2. Webhook Triggers

## 2. Webhook Triggers


```typescript
// Webhook trigger configuration
const webhookFlow = {
  "displayName": "Payment Webhook Handler",
  "trigger": {
    "name": "webhook",
    "type": "WEBHOOK",
    "settings": {
      "inputUiInfo": {
        "customizedInputs": {}
      }
    },
    "displayName": "Payment Webhook"
  },
  "steps": [
    {
      "name": "verify_signature",
      "type": "CODE",
      "settings": {
        "input": {
          "payload": "{{trigger.body}}",
          "signature": "{{trigger.headers['x-signature']}}",
          "secret": "{{connections.payment_webhook_secret}}"
        },
        "sourceCode": {
          "code": `
import crypto from 'crypto';

export const code = async (inputs) => {
  const { payload, signature, secret } = inputs;

  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');

  if (signature !== expectedSignature) {
    throw new Error('Invalid webhook signature');
  }

  return {
    verified: true,
    event: payload.event_type,
    data: payload.data
  };
};`
        }
      },
      "displayName": "Verify Webhook Signature"
    },
    {
      "name": "route_by_event",
      "type": "BRANCH",
      "settings": {
        "conditions": [
          {
            "name": "payment_completed",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{verify_signature.event}} === 'payment.completed'"
            }
          },
          {
            "name": "payment_failed",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{verify_signature.event}} === 'payment.failed'"
            }
          },
          {
            "name": "refund_initiated",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{verify_signature.event}} === 'refund.initiated'"
            }
          }
        ]
      },
      "displayName": "Route by Event Type"
    }
  ]
};
```
