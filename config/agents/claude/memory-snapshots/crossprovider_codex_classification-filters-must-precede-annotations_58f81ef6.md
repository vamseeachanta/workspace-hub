---
name: crossprovider codex classification-filters-must-precede-annotations
description: Classification filters must precede annotations
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [classification, logic-order, state-management]
---

When adding annotation and filtering to a classifier (e.g., showing `not_before` dates), the filtering logic must exclude items from ready states before annotating them. Annotating without filtering gives false impression of readiness. Both the filtering and annotation are necessary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
