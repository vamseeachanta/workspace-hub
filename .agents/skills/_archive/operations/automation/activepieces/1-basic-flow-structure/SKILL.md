---
name: activepieces-1-basic-flow-structure
description: 'Sub-skill of activepieces: 1. Basic Flow Structure.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Basic Flow Structure

## 1. Basic Flow Structure


```typescript
// Flow definition structure
interface Flow {
  id: string;
  projectId: string;
  folderId?: string;
  status: 'ENABLED' | 'DISABLED';
  schedule?: {
    cronExpression: string;
    timezone: string;
  };
  trigger: Trigger;
  steps: Step[];
}

// Example flow JSON
const basicFlow = {
  "displayName": "New Customer Onboarding",
  "trigger": {
    "name": "webhook",
    "type": "WEBHOOK",
    "settings": {
      "inputUiInfo": {}
    },
    "valid": true,
    "displayName": "Webhook Trigger"
  },
  "steps": [
    {
      "name": "validate_data",
      "type": "CODE",
      "settings": {
        "input": {
          "customer": "{{trigger.body.customer}}"
        },
        "sourceCode": {
          "code": "export const code = async (inputs) => {\n  const { customer } = inputs;\n  \n  if (!customer.email || !customer.name) {\n    throw new Error('Missing required fields');\n  }\n  \n  return {\n    valid: true,\n    customer: {\n      ...customer,\n      email: customer.email.toLowerCase().trim(),\n      created_at: new Date().toISOString()\n    }\n  };\n};"
        }
      },
      "displayName": "Validate Customer Data"
    },
    {
      "name": "create_crm_contact",
      "type": "PIECE",
      "settings": {
        "pieceName": "@activepieces/piece-hubspot",
        "pieceVersion": "~0.5.0",
        "actionName": "create_contact",
        "input": {
          "email": "{{validate_data.customer.email}}",
          "firstName": "{{validate_data.customer.name.split(' ')[0]}}",
          "lastName": "{{validate_data.customer.name.split(' ').slice(1).join(' ')}}",
          "properties": {
            "source": "activepieces_onboarding",
            "created_via": "automation"
          }
        }
      },
      "displayName": "Create HubSpot Contact"
    },
    {
      "name": "send_welcome_email",
      "type": "PIECE",
      "settings": {
        "pieceName": "@activepieces/piece-sendgrid",
        "pieceVersion": "~0.3.0",
        "actionName": "send_email",
        "input": {
          "to": "{{validate_data.customer.email}}",
          "subject": "Welcome to Our Platform!",
          "html": "<h1>Welcome, {{validate_data.customer.name}}!</h1><p>We're excited to have you on board.</p>"
        }
      },
      "displayName": "Send Welcome Email"
    },
    {
      "name": "notify_team",
      "type": "PIECE",
      "settings": {
        "pieceName": "@activepieces/piece-slack",
        "pieceVersion": "~0.6.0",
        "actionName": "send_message",
        "input": {
          "channel": "#new-customers",
          "text": "New customer onboarded: {{validate_data.customer.name}} ({{validate_data.customer.email}})"
        }
      },
      "displayName": "Notify Sales Team"
    }
  ]
};
```
