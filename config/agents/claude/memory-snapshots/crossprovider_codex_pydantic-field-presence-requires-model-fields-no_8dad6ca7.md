---
name: crossprovider codex pydantic-field-presence-requires-model-fields-no
description: Pydantic field presence requires model_fields, not hasattr()
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pydantic, dataclass, field-checking, gotcha]
---

Checking `hasattr(PydanticModel, "field_name")` returns False even when field_name is defined in the model. Use `"field_name" in Model.model_fields` for Pydantic, `"field_name" in Model.__annotations__` for dataclasses. This breaks dependency predicates checking if optional fields have landed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
