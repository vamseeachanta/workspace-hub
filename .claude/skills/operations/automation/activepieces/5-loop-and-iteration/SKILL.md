---
name: activepieces-5-loop-and-iteration
description: 'Sub-skill of activepieces: 5. Loop and Iteration.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 5. Loop and Iteration

## 5. Loop and Iteration


```typescript
// Loop over items
const loopFlow = {
  "displayName": "Batch Order Processing",
  "trigger": {
    "name": "webhook",
    "type": "WEBHOOK",
    "settings": {},
    "displayName": "Batch Orders"
  },
  "steps": [
    {
      "name": "process_orders",
      "type": "LOOP_ON_ITEMS",
      "settings": {
        "items": "{{trigger.body.orders}}",
        "steps": [
          {
            "name": "validate_order",
            "type": "CODE",
            "settings": {
              "input": {
                "order": "{{loop.item}}"
              },
              "sourceCode": {
                "code": `
export const code = async (inputs) => {
  const { order } = inputs;

  const errors = [];

  if (!order.customer_id) errors.push('Missing customer_id');
  if (!order.items || order.items.length === 0) errors.push('No items in order');
  if (!order.total || order.total <= 0) errors.push('Invalid total');

  return {
    valid: errors.length === 0,
    errors,
    order: errors.length === 0 ? order : null
  };
};`
              }
            },
            "displayName": "Validate Order"
          },
          {
            "name": "check_inventory",
            "type": "PIECE",
            "settings": {
              "pieceName": "@activepieces/piece-http",
              "actionName": "send_request",
              "input": {
                "method": "POST",
                "url": "{{connections.inventory_api.base_url}}/api/check-availability",
                "headers": {
                  "Authorization": "Bearer {{connections.inventory_api.api_key}}"
                },
                "body": {
                  "items": "{{validate_order.order.items}}"
                }
              }
            },
            "displayName": "Check Inventory"
          },
          {
            "name": "process_payment",
            "type": "PIECE",
            "settings": {
              "pieceName": "@activepieces/piece-stripe",
              "actionName": "create_charge",
              "input": {
                "amount": "{{validate_order.order.total}}",
                "currency": "usd",
                "customer": "{{validate_order.order.stripe_customer_id}}",
                "description": "Order {{validate_order.order.id}}"
              }
            },
            "displayName": "Process Payment"
          },
          {
            "name": "create_shipment",
            "type": "PIECE",
            "settings": {
              "pieceName": "@activepieces/piece-shippo",
              "actionName": "create_shipment",
              "input": {
                "address_from": "{{connections.shippo.warehouse_address}}",
                "address_to": "{{validate_order.order.shipping_address}}",
                "parcels": "{{validate_order.order.items}}"
              }
            },
            "displayName": "Create Shipment"
          }
        ]
      },
      "displayName": "Process Each Order"
    },
    {
      "name": "summarize_results",
      "type": "CODE",
      "settings": {
        "input": {
          "results": "{{process_orders}}"
        },
        "sourceCode": {
          "code": `
export const code = async (inputs) => {
  const { results } = inputs;

  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  return {
    total_processed: results.length,
    successful: successful.length,
    failed: failed.length,
    failed_orders: failed.map(f => ({
      order_id: f.order_id,
      error: f.error
    })),
    total_revenue: successful.reduce((sum, r) => sum + r.amount, 0)
  };
};`
        }
      },
      "displayName": "Summarize Results"
    }
  ]
};
```
