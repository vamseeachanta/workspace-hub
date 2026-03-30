---
name: activepieces-7-approval-flows
description: 'Sub-skill of activepieces: 7. Approval Flows.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 7. Approval Flows

## 7. Approval Flows


```typescript
// Human approval workflow
const approvalFlow = {
  "displayName": "Expense Approval Workflow",
  "trigger": {
    "name": "webhook",
    "type": "WEBHOOK",
    "settings": {},
    "displayName": "New Expense Request"
  },
  "steps": [
    {
      "name": "validate_expense",
      "type": "CODE",
      "settings": {
        "input": {
          "expense": "{{trigger.body}}"
        },
        "sourceCode": {
          "code": `
export const code = async (inputs) => {
  const { expense } = inputs;

  return {
    ...expense,
    requires_approval: expense.amount > 500,
    approval_level: expense.amount > 5000 ? 'executive' : expense.amount > 500 ? 'manager' : 'auto',
    formatted_amount: new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(expense.amount)
  };
};`
        }
      },
      "displayName": "Validate Expense"
    },
    {
      "name": "check_approval_required",
      "type": "BRANCH",
      "settings": {
        "conditions": [
          {
            "name": "needs_approval",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{validate_expense.requires_approval}} === true"
            },
            "steps": [
              {
                "name": "send_approval_request",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-slack",
                  "actionName": "send_message",
                  "input": {
                    "channel": "#expense-approvals",
                    "blocks": [
                      {
                        "type": "header",
                        "text": {
                          "type": "plain_text",
                          "text": "Expense Approval Required"
                        }
                      },
                      {
                        "type": "section",
                        "fields": [
                          { "type": "mrkdwn", "text": "*Submitted by:*\n{{validate_expense.employee_name}}" },
                          { "type": "mrkdwn", "text": "*Amount:*\n{{validate_expense.formatted_amount}}" },
                          { "type": "mrkdwn", "text": "*Category:*\n{{validate_expense.category}}" },
                          { "type": "mrkdwn", "text": "*Description:*\n{{validate_expense.description}}" }
                        ]
                      },
                      {
                        "type": "actions",
                        "elements": [
                          {
                            "type": "button",
                            "text": { "type": "plain_text", "text": "Approve" },
                            "style": "primary",
                            "action_id": "approve_expense",
                            "value": "{{validate_expense.id}}"
                          },
                          {
                            "type": "button",
                            "text": { "type": "plain_text", "text": "Reject" },
                            "style": "danger",
                            "action_id": "reject_expense",
                            "value": "{{validate_expense.id}}"
                          }
                        ]
                      }
                    ]
                  }
                }
              },
              {
                "name": "wait_for_approval",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-approval",
                  "actionName": "wait_for_approval",
                  "input": {
                    "timeout_hours": 48,
                    "approval_link_text": "Click to review expense"
                  }
                }
              },
              {
                "name": "process_decision",
                "type": "BRANCH",
                "settings": {
                  "conditions": [
                    {
                      "name": "approved",
                      "expression": {
                        "type": "EXPRESSION",
                        "value": "{{wait_for_approval.status}} === 'APPROVED'"
                      },
                      "steps": [
                        {
                          "name": "process_reimbursement",
                          "type": "PIECE",
                          "settings": {
                            "pieceName": "@activepieces/piece-http",
                            "actionName": "send_request",
                            "input": {
                              "method": "POST",
                              "url": "{{connections.finance_api.base_url}}/reimbursements",
                              "body": {
                                "expense_id": "{{validate_expense.id}}",
                                "amount": "{{validate_expense.amount}}",
                                "employee_id": "{{validate_expense.employee_id}}",
                                "approved_by": "{{wait_for_approval.approved_by}}"
                              }
                            }
                          }
                        }
                      ]
                    },
                    {
                      "name": "rejected",
                      "expression": {
                        "type": "EXPRESSION",
                        "value": "{{wait_for_approval.status}} === 'REJECTED'"
                      },
                      "steps": [
                        {
                          "name": "notify_rejection",
                          "type": "PIECE",
                          "settings": {
                            "pieceName": "@activepieces/piece-gmail",
                            "actionName": "send_email",
                            "input": {
                              "to": "{{validate_expense.employee_email}}",
                              "subject": "Expense Request Rejected",
                              "body": "Your expense request for {{validate_expense.formatted_amount}} has been rejected."
                            }
                          }
                        }
                      ]
                    }
                  ]
                }
              }
            ]
          },
          {
            "name": "auto_approve",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{validate_expense.requires_approval}} === false"
            },
            "steps": [
              {
                "name": "auto_process",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-http",
                  "actionName": "send_request",
                  "input": {
                    "method": "POST",
                    "url": "{{connections.finance_api.base_url}}/reimbursements",
                    "body": {
                      "expense_id": "{{validate_expense.id}}",
                      "amount": "{{validate_expense.amount}}",

*Content truncated — see parent skill for full reference.*
