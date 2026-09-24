---
name: crossprovider codex docstrings-document-constraints-and-workarounds
description: Docstrings document constraints and workarounds
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [documentation, input-validation, api-design]
---

Functions with implicit ordering or uniqueness constraints (e.g., zone IDs must appear exactly once) should document the constraint in the docstring and suggest workaround patterns. Prevents silent bugs and guides users toward correct API usage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
