---
name: crossprovider hermes conditional-registry-schema-validation-for-dispa
description: Conditional registry schema validation for dispatch vs non-dispatch machines
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [config-validation, schema-design, conditional-requirements]
---

Configuration schemas with machine dispatch metadata should validate required fields conditionally: non-dispatch machines (like gali-linux-compute-1) should not require dispatch-specific fields (storage, telegram_hermes config), but dispatch-enabled hosts must satisfy full schema. Validate schema only against machines with dispatch_enabled:true, not all machines.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
