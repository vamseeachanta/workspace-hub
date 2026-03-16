---
name: n8n-integration-with-slack-google-sheets-and-email
description: 'Sub-skill of n8n: Integration with Slack, Google Sheets, and Email.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Integration with Slack, Google Sheets, and Email

## Integration with Slack, Google Sheets, and Email


```json
{
  "name": "Multi-Channel Notification System",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "notify",
        "responseMode": "responseNode"
      },
      "id": "webhook",
      "name": "Incoming Notification",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "jsCode": "// Determine notification channels\nconst payload = $input.item.json;\n\nconst channels = [];\n\n// Add channels based on priority\nif (payload.priority === 'high' || payload.priority === 'critical') {\n  channels.push('slack');\n  channels.push('email');\n}\n\nif (payload.log_to_sheet) {\n  channels.push('sheets');\n}\n\nif (channels.length === 0) {\n  channels.push('slack'); // Default\n}\n\nreturn {\n  ...payload,\n  channels,\n  processed_at: new Date().toISOString()\n};"
      },
      "id": "router",
      "name": "Route Notification",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.channels.join(',') }}",
              "operation": "contains",
              "value2": "slack"
            }
          ]
        }
      },
      "id": "slack-filter",
      "name": "Send to Slack?",
      "type": "n8n-nodes-base.filter",
      "typeVersion": 2,
      "position": [680, 200]
    },
    {
      "parameters": {
        "channel": "={{ $json.priority === 'critical' ? '#critical-alerts' : '#notifications' }}",
        "text": "=*{{ $json.title }}*\n\n{{ $json.message }}\n\nPriority: {{ $json.priority }}\nSource: {{ $json.source }}",
        "attachments": [],
        "otherOptions": {}
      },
      "id": "slack",
      "name": "Post to Slack",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.1,
      "position": [900, 200],
      "credentials": {
        "slackApi": {
          "id": "3",
          "name": "Slack Bot"
        }
      }
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.channels.join(',') }}",
              "operation": "contains",
              "value2": "email"
            }
          ]
        }
      },
      "id": "email-filter",
      "name": "Send Email?",
      "type": "n8n-nodes-base.filter",
      "typeVersion": 2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "sendTo": "={{ $json.recipient_email || 'team@example.com' }}",
        "subject": "=[{{ $json.priority.toUpperCase() }}] {{ $json.title }}",
        "emailType": "html",
        "html": "=<h2>{{ $json.title }}</h2>\n<p>{{ $json.message }}</p>\n<hr>\n<p><strong>Priority:</strong> {{ $json.priority }}</p>\n<p><strong>Source:</strong> {{ $json.source }}</p>\n<p><strong>Time:</strong> {{ $json.processed_at }}</p>"
      },
      "id": "email",
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2.1,
      "position": [900, 300],
      "credentials": {
        "smtp": {
          "id": "5",
          "name": "SMTP"
        }
      }
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.channels.join(',') }}",
              "operation": "contains",
              "value2": "sheets"
            }
          ]
        }
      },
      "id": "sheets-filter",
      "name": "Log to Sheets?",
      "type": "n8n-nodes-base.filter",
      "typeVersion": 2,
      "position": [680, 400]
    },
    {
      "parameters": {
        "operation": "append",
        "documentId": {
          "__rl": true,
          "value": "={{ $env.GOOGLE_SHEET_ID }}",
          "mode": "id"
        },
        "sheetName": {
          "__rl": true,
          "value": "Notifications",
          "mode": "list"
        },
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "Timestamp": "={{ $json.processed_at }}",
            "Title": "={{ $json.title }}",
            "Message": "={{ $json.message }}",
            "Priority": "={{ $json.priority }}",
            "Source": "={{ $json.source }}"
          }
        }
      },
      "id": "sheets",
      "name": "Log to Google Sheets",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.1,
      "position": [900, 400],
      "credentials": {
        "googleSheetsOAuth2Api": {
          "id": "6",
          "name": "Google Sheets"
        }
      }
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ JSON.stringify({ success: true, channels: $json.channels }) }}"
      },
      "id": "respond",
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1120, 300]
    }
  ],
  "connections": {
    "Incoming Notification": {
      "main": [
        [{ "node": "Route Notification", "type": "main", "index": 0 }]
      ]
    },
    "Route Notification": {
      "main": [
        [
          { "node": "Send to Slack?", "type": "main", "index": 0 },
          { "node": "Send Email?", "type": "main", "index": 0 },
          { "node": "Log to Sheets?", "type": "main", "index": 0 }
        ]
      ]
    },
    "Send to Slack?": {
      "main": [
        [{ "node": "Post to Slack", "type": "main", "index": 0 }]

*Content truncated — see parent skill for full reference.*
