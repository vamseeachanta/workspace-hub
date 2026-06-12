---
name: crossprovider hermes summary-truncation-breaks-weekly-cadence-durabil
description: Summary truncation breaks weekly cadence durability
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, durability, summary-design, weekly-cadence]
---

Truncating summary lists (e.g., to 25 entries while artifacts contain 100+) diverges from complete counts and obscures true weekly changes. Violates durable machine contract for weekly regeneration; fix requires removing caps or storing complete lists separately.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
