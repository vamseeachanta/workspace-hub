---
name: crossprovider codex pydantic-models-need-extra-forbid-for-field-vali
description: Pydantic models need extra='forbid' for field validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pydantic, validation, schema]
---

Setting arbitrary_types_allowed=True doesn't prevent stray emitted keys; must add extra='forbid' to model_config for reliable field whitelisting. Multiple models in this codebase lack this, allowing undetected YAML round-trip defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
