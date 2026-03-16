---
name: windmill-5-flow-orchestration
description: 'Sub-skill of windmill: 5. Flow Orchestration.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 5. Flow Orchestration

## 5. Flow Orchestration


```yaml
# flows/order_processing_flow.yaml
summary: Order Processing Pipeline
description: |
  End-to-end order processing with validation, payment, and fulfillment.
  Includes approval for high-value orders.

value:
  modules:
    - id: validate_order
      value:
        type: script
        path: f/order_processing/validate_order
        input_transforms:
          order:
            type: javascript
            expr: flow_input.order

    - id: check_inventory
      value:
        type: script
        path: f/inventory/check_availability
        input_transforms:
          items:
            type: javascript
            expr: results.validate_order.items

    - id: route_by_value
      value:
        type: branchone
        branches:
          - summary: High Value Order
            expr: results.validate_order.total > 5000
            modules:
              - id: request_approval
                value:
                  type: approval
                  timeout: 86400  # 24 hours
                  approvers:
                    - admin@example.com
                    - manager@example.com

              - id: process_approved
                value:
                  type: script
                  path: f/payments/process_payment
                  input_transforms:
                    order_id:
                      type: javascript
                      expr: results.validate_order.order_id
                    amount:
                      type: javascript
                      expr: results.validate_order.total

          - summary: Normal Order
            expr: results.validate_order.total <= 5000
            modules:
              - id: process_normal
                value:
                  type: script
                  path: f/payments/process_payment
                  input_transforms:
                    order_id:
                      type: javascript
                      expr: results.validate_order.order_id
                    amount:
                      type: javascript
                      expr: results.validate_order.total

    - id: create_shipment
      value:
        type: script
        path: f/fulfillment/create_shipment
        input_transforms:
          order_id:
            type: javascript
            expr: results.validate_order.order_id
          shipping_address:
            type: javascript
            expr: results.validate_order.shipping_address

    - id: send_confirmation
      value:
        type: script
        path: f/notifications/send_order_confirmation
        input_transforms:
          email:
            type: javascript
            expr: results.validate_order.customer_email
          order_details:
            type: javascript
            expr: |
              {
                order_id: results.validate_order.order_id,
                total: results.validate_order.total,
                tracking_number: results.create_shipment.tracking_number
              }

schema:
  $schema: https://json-schema.org/draft/2020-12/schema
  type: object
  properties:
    order:
      type: object
      properties:
        customer_email:
          type: string
          format: email
        items:
          type: array
          items:
            type: object
        shipping_address:
          type: object
      required:
        - customer_email
        - items
        - shipping_address
  required:
    - order
```
