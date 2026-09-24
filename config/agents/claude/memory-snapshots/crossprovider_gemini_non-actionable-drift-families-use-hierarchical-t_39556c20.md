---
name: crossprovider gemini non-actionable-drift-families-use-hierarchical-t
description: Non-actionable drift families use hierarchical taxonomy to avoid churn
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [audit, classification, taxonomy-design]
---

Group related non-actionable families under a parent bucket (e.g., `non_repo_artifact` for generated-site, build outputs, adjacent projects) rather than flat peer categories. Clarifies classifier precedence and prevents taxonomy redesign when the next non-actionable family appears.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
