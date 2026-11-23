---
name: n8n-2-webhook-triggers
description: 'Sub-skill of n8n: 2. Webhook Triggers.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 2. Webhook Triggers

## 2. Webhook Triggers


```json
{
  "name": "Webhook Handler",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "incoming-webhook",
        "responseMode": "responseNode",
        "options": {
          "rawBody": true
        }
      },
      "id": "webhook",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [240, 300],
      "webhookId": "unique-webhook-id"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.event_type }}",
              "operation": "equals",
              "value2": "payment.completed"
            }
          ]
        }
      },
      "id": "filter",
      "name": "Filter Payment Events",
      "type": "n8n-nodes-base.filter",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "jsCode": "// Validate webhook signature\nconst crypto = require('crypto');\n\nconst payload = $input.item.json;\nconst signature = $input.item.headers['x-signature'];\nconst secret = $env.WEBHOOK_SECRET;\n\nconst expectedSignature = crypto\n  .createHmac('sha256', secret)\n  .update(JSON.stringify(payload))\n  .digest('hex');\n\nif (signature !== expectedSignature) {\n  throw new Error('Invalid webhook signature');\n}\n\nreturn {\n  ...payload,\n  validated: true,\n  processed_at: new Date().toISOString()\n};"
      },
      "id": "validate",
      "name": "Validate Signature",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "channel": "#payments",
        "text": "=Payment received!\n\nAmount: ${{ $json.amount }}\nCustomer: {{ $json.customer_email }}\nTransaction ID: {{ $json.transaction_id }}",
        "otherOptions": {}
      },
      "id": "slack",
      "name": "Notify Slack",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.1,
      "position": [900, 300],
      "credentials": {
        "slackApi": {
          "id": "3",
          "name": "Slack Bot"
        }
      }
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ JSON.stringify({ status: 'processed', id: $json.transaction_id }) }}"
      },
      "id": "respond",
      "name": "Respond to Webhook",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1120, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [{ "node": "Filter Payment Events", "type": "main", "index": 0 }]
      ]
    },
    "Filter Payment Events": {
      "main": [
        [{ "node": "Validate Signature", "type": "main", "index": 0 }]
      ]
    },
    "Validate Signature": {
      "main": [
        [{ "node": "Notify Slack", "type": "main", "index": 0 }]
      ]
    },
    "Notify Slack": {
      "main": [
        [{ "node": "Respond to Webhook", "type": "main", "index": 0 }]
      ]
    }
  }
}
```
