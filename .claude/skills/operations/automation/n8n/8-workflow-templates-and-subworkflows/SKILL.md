---
name: n8n-8-workflow-templates-and-subworkflows
description: 'Sub-skill of n8n: 8. Workflow Templates and Subworkflows.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 8. Workflow Templates and Subworkflows

## 8. Workflow Templates and Subworkflows


```json
{
  "name": "Main Orchestrator Workflow",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "orchestrate",
        "responseMode": "lastNode"
      },
      "id": "webhook",
      "name": "Start",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "workflowId": "={{ $env.DATA_VALIDATION_WORKFLOW_ID }}",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "data": "={{ $json.payload }}",
            "rules": "={{ $json.validation_rules }}"
          }
        }
      },
      "id": "validate",
      "name": "Run Validation Workflow",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.is_valid }}",
              "value2": true
            }
          ]
        }
      },
      "id": "check-valid",
      "name": "Is Valid?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "workflowId": "={{ $env.PROCESSING_WORKFLOW_ID }}",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "validated_data": "={{ $json.data }}"
          }
        }
      },
      "id": "process",
      "name": "Run Processing Workflow",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1,
      "position": [900, 200]
    },
    {
      "parameters": {
        "workflowId": "={{ $env.ERROR_HANDLER_WORKFLOW_ID }}",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "error_data": "={{ $json }}",
            "source": "orchestrator"
          }
        }
      },
      "id": "error-workflow",
      "name": "Run Error Handler",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1,
      "position": [900, 400]
    }
  ],
  "connections": {
    "Start": {
      "main": [
        [{ "node": "Run Validation Workflow", "type": "main", "index": 0 }]
      ]
    },
    "Run Validation Workflow": {
      "main": [
        [{ "node": "Is Valid?", "type": "main", "index": 0 }]
      ]
    },
    "Is Valid?": {
      "main": [
        [{ "node": "Run Processing Workflow", "type": "main", "index": 0 }],
        [{ "node": "Run Error Handler", "type": "main", "index": 0 }]
      ]
    }
  }
}
```
