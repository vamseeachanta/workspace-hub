---
name: n8n-4-conditional-branching-and-error-handling
description: 'Sub-skill of n8n: 4. Conditional Branching and Error Handling.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 4. Conditional Branching and Error Handling

## 4. Conditional Branching and Error Handling


```json
{
  "name": "Order Processing with Error Handling",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "process-order",
        "responseMode": "responseNode"
      },
      "id": "webhook",
      "name": "Order Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "id": "condition-1",
              "leftValue": "={{ $json.order_total }}",
              "rightValue": 1000,
              "operator": {
                "type": "number",
                "operation": "gte"
              }
            }
          ],
          "combinator": "and"
        },
        "options": {}
      },
      "id": "switch",
      "name": "High Value Order?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "url": "https://api.payment.com/process",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "order_id",
              "value": "={{ $json.order_id }}"
            },
            {
              "name": "amount",
              "value": "={{ $json.order_total }}"
            },
            {
              "name": "priority",
              "value": "high"
            }
          ]
        },
        "options": {}
      },
      "id": "high-value-payment",
      "name": "Process High Value",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [680, 200],
      "onError": "continueErrorOutput"
    },
    {
      "parameters": {
        "url": "https://api.payment.com/process",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "order_id",
              "value": "={{ $json.order_id }}"
            },
            {
              "name": "amount",
              "value": "={{ $json.order_total }}"
            },
            {
              "name": "priority",
              "value": "normal"
            }
          ]
        }
      },
      "id": "normal-payment",
      "name": "Process Normal",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [680, 400],
      "onError": "continueErrorOutput"
    },
    {
      "parameters": {
        "jsCode": "// Handle payment error\nconst error = $input.item.json;\n\nreturn {\n  status: 'failed',\n  error_message: error.message || 'Payment processing failed',\n  order_id: $('Order Webhook').item.json.order_id,\n  timestamp: new Date().toISOString(),\n  retry_eligible: true\n};"
      },
      "id": "error-handler",
      "name": "Handle Error",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [900, 500]
    },
    {
      "parameters": {
        "channel": "#alerts",
        "text": "=Payment Failed!\n\nOrder ID: {{ $json.order_id }}\nError: {{ $json.error_message }}\nRetry Eligible: {{ $json.retry_eligible }}",
        "otherOptions": {}
      },
      "id": "slack-alert",
      "name": "Alert Team",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.1,
      "position": [1120, 500],
      "credentials": {
        "slackApi": {
          "id": "3",
          "name": "Slack Bot"
        }
      }
    },
    {
      "parameters": {
        "mode": "combine",
        "combineBy": "combineAll",
        "options": {}
      },
      "id": "merge",
      "name": "Merge Results",
      "type": "n8n-nodes-base.merge",
      "typeVersion": 2.1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ JSON.stringify({ status: 'processed', order_id: $json.order_id }) }}"
      },
      "id": "respond-success",
      "name": "Success Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1120, 300]
    }
  ],
  "connections": {
    "Order Webhook": {
      "main": [
        [{ "node": "High Value Order?", "type": "main", "index": 0 }]
      ]
    },
    "High Value Order?": {
      "main": [
        [{ "node": "Process High Value", "type": "main", "index": 0 }],
        [{ "node": "Process Normal", "type": "main", "index": 0 }]
      ]
    },
    "Process High Value": {
      "main": [
        [{ "node": "Merge Results", "type": "main", "index": 0 }],
        [{ "node": "Handle Error", "type": "main", "index": 0 }]
      ]
    },
    "Process Normal": {
      "main": [
        [{ "node": "Merge Results", "type": "main", "index": 1 }],
        [{ "node": "Handle Error", "type": "main", "index": 0 }]
      ]
    },
    "Handle Error": {
      "main": [
        [{ "node": "Alert Team", "type": "main", "index": 0 }]
      ]
    },
    "Merge Results": {

*Content truncated — see parent skill for full reference.*
