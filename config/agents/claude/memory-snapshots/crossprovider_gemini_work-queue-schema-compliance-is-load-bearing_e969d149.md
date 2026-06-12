---
name: crossprovider gemini work-queue-schema-compliance-is-load-bearing
description: Work queue schema compliance is load-bearing
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [schema, work-queue, automation-reliability, validation]
---

Inconsistent frontmatter in WRK files (`plan_reviewed`, `plan_approved`, `provider`, `complexity` missing on active items) breaks routing and automation. CI hygiene gates must validate required fields on all active items, not just new ones. Gradual enforcement with error reporting lets existing items be fixed before blocking mode kicks in.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
