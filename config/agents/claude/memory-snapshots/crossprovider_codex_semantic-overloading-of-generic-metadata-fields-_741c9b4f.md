---
name: crossprovider codex semantic-overloading-of-generic-metadata-fields-
description: Semantic overloading of generic metadata fields causes misclassification
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, metadata, classification]
---

Using a generic field like `note:` to signal workflow state (parked, paused) causes future items that use that field for its intended purpose to be silently misclassified. Use explicit dedicated fields for state signals (e.g., `parked_reason`, `paused: true`) to avoid ambiguity and regression.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
