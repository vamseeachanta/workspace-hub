---
name: crossprovider gemini plan-review-schemas-and-contracts-must-be-explic
description: Plan review: schemas and contracts must be explicit before pseudocode
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [plan-review, schema-design, contract-definition]
---

Gemini adversarial reviews consistently surface defects from underspecified schemas (e.g., `routing-rules.yaml` boundary vs `routing-config.yaml` undefined), missing identity contracts (`doc_key` namespace enforcement, legacy-compatibility rules), and undefined atomic guarantees (checkpoint file state shape, write atomicity). Schemas should be drafted in Design Decisions or Resource Intelligence section before pseudocode references them.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
