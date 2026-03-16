---
name: activepieces-4-branching-and-conditional-logic
description: 'Sub-skill of activepieces: 4. Branching and Conditional Logic.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 4. Branching and Conditional Logic

## 4. Branching and Conditional Logic


```typescript
// Branch step with multiple conditions
const branchingFlow = {
  "displayName": "Lead Qualification Flow",
  "trigger": {
    "name": "webhook",
    "type": "WEBHOOK",
    "settings": {},
    "displayName": "New Lead"
  },
  "steps": [
    {
      "name": "enrich_lead",
      "type": "PIECE",
      "settings": {
        "pieceName": "@activepieces/piece-clearbit",
        "pieceVersion": "~0.2.0",
        "actionName": "enrich_company",
        "input": {
          "domain": "{{trigger.body.company_domain}}"
        }
      },
      "displayName": "Enrich Lead Data"
    },
    {
      "name": "calculate_score",
      "type": "CODE",
      "settings": {
        "input": {
          "lead": "{{trigger.body}}",
          "enriched": "{{enrich_lead}}"
        },
        "sourceCode": {
          "code": `
export const code = async (inputs) => {
  const { lead, enriched } = inputs;
  let score = 0;

  // Company size scoring
  if (enriched.metrics?.employees > 1000) score += 30;
  else if (enriched.metrics?.employees > 100) score += 20;
  else if (enriched.metrics?.employees > 10) score += 10;

  // Industry scoring
  const highValueIndustries = ['technology', 'finance', 'healthcare'];
  if (highValueIndustries.includes(enriched.category?.industry?.toLowerCase())) {
    score += 25;
  }

  // Title scoring
  const seniorTitles = ['ceo', 'cto', 'vp', 'director', 'head'];
  if (seniorTitles.some(t => lead.title?.toLowerCase().includes(t))) {
    score += 20;
  }

  // Budget scoring
  if (lead.budget > 100000) score += 25;
  else if (lead.budget > 50000) score += 15;
  else if (lead.budget > 10000) score += 10;

  return {
    score,
    tier: score >= 70 ? 'hot' : score >= 40 ? 'warm' : 'cold',
    lead: { ...lead, enriched }
  };
};`
        }
      },
      "displayName": "Calculate Lead Score"
    },
    {
      "name": "route_by_tier",
      "type": "BRANCH",
      "settings": {
        "conditions": [
          {
            "name": "hot_lead",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{calculate_score.tier}} === 'hot'"
            },
            "steps": [
              {
                "name": "notify_sales_urgent",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-slack",
                  "actionName": "send_message",
                  "input": {
                    "channel": "#hot-leads",
                    "text": "HOT LEAD: {{calculate_score.lead.name}} from {{calculate_score.lead.company}} (Score: {{calculate_score.score}})"
                  }
                }
              },
              {
                "name": "create_salesforce_lead",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-salesforce",
                  "actionName": "create_record",
                  "input": {
                    "objectName": "Lead",
                    "fields": {
                      "FirstName": "{{calculate_score.lead.first_name}}",
                      "LastName": "{{calculate_score.lead.last_name}}",
                      "Company": "{{calculate_score.lead.company}}",
                      "Email": "{{calculate_score.lead.email}}",
                      "LeadSource": "Website",
                      "Rating": "Hot"
                    }
                  }
                }
              },
              {
                "name": "schedule_demo",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-calendly",
                  "actionName": "create_scheduling_link",
                  "input": {
                    "event_type": "sales-demo",
                    "invitee_email": "{{calculate_score.lead.email}}"
                  }
                }
              }
            ]
          },
          {
            "name": "warm_lead",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{calculate_score.tier}} === 'warm'"
            },
            "steps": [
              {
                "name": "add_to_nurture",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-mailchimp",
                  "actionName": "add_subscriber",
                  "input": {
                    "list_id": "{{connections.mailchimp.nurture_list_id}}",
                    "email": "{{calculate_score.lead.email}}",
                    "tags": ["warm-lead", "nurture-sequence"]
                  }
                }
              }
            ]
          },
          {
            "name": "cold_lead",
            "expression": {
              "type": "EXPRESSION",
              "value": "{{calculate_score.tier}} === 'cold'"
            },
            "steps": [
              {
                "name": "add_to_drip",
                "type": "PIECE",
                "settings": {
                  "pieceName": "@activepieces/piece-mailchimp",
                  "actionName": "add_subscriber",
                  "input": {
                    "list_id": "{{connections.mailchimp.general_list_id}}",
                    "email": "{{calculate_score.lead.email}}",
                    "tags": ["cold-lead"]
                  }
                }
              }
            ]
          }
        ]
      },
      "displayName": "Route by Lead Tier"
    }
  ]
};
```
