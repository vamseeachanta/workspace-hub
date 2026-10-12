---
name: boundary-policy-classification-by-role
description: Classify artifacts as durable vs transient by their functional role rather than directory path, using multi-layer architectural validation
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["architecture", "policy-design", "classification", "artifact-management"]
---

# Boundary Policy Classification by Role

When defining durable vs transient artifact boundaries within a multi-layer architecture, classify by *role* not *path*. Same directory can contain both types (e.g., reports/ has one-shot audits and durable assessments). Ground classification in concrete examples from each layer, validate consistency with parent architecture, and use adversarial review to test for loose language ('it depends') and implementability gaps.