---
name: n8n-1-basic-workflow-structure
description: 'Sub-skill of n8n: 1. Basic Workflow Structure.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Basic Workflow Structure

## 1. Basic Workflow Structure


```json
{
  "name": "Basic Data Pipeline",
  "nodes": [
    {
      "parameters": {},
      "id": "start-node",
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "url": "https://api.example.com/data",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "httpHeaderAuth",
        "options": {
          "response": {
            "response": {
              "responseFormat": "json"
            }
          }
        }
      },
      "id": "http-request",
      "name": "Fetch Data",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [460, 300],
      "credentials": {
        "httpHeaderAuth": {
          "id": "1",
          "name": "API Key"
        }
      }
    },
    {
      "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": "// Transform each item\nconst item = $input.item.json;\n\nreturn {\n  id: item.id,\n  name: item.name.toUpperCase(),\n  processed_at: new Date().toISOString(),\n  source: 'n8n-pipeline'\n};"
      },
      "id": "transform",
      "name": "Transform Data",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "resource": "row",
        "operation": "create",
        "tableId": "={{ $env.AIRTABLE_TABLE_ID }}",
        "options": {}
      },
      "id": "airtable",
      "name": "Save to Airtable",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 2,
      "position": [900, 300],
      "credentials": {
        "airtableTokenApi": {
          "id": "2",
          "name": "Airtable Token"
        }
      }
    }
  ],
  "connections": {
    "Start": {
      "main": [
        [{ "node": "Fetch Data", "type": "main", "index": 0 }]
      ]
    },
    "Fetch Data": {
      "main": [
        [{ "node": "Transform Data", "type": "main", "index": 0 }]
      ]
    },
    "Transform Data": {
      "main": [
        [{ "node": "Save to Airtable", "type": "main", "index": 0 }]
      ]
    }
  },
  "settings": {
    "executionOrder": "v1"
  }
}
```
