---
name: crossprovider codex pydantic-field-detection-via-hasattr-fails-use-m
description: Pydantic field detection via hasattr() fails; use model_fields dict instead
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pydantic, schema-validation, testing]
---

Plans checking for dependency fields via `hasattr(RunConfig, 'field_name')` will always return False on Pydantic BaseModel classes, even after the field is added. Check Pydantic models via `'field_name' in RunConfig.model_fields`, and dataclasses via `'field_name' in RunResult.__annotations__`. This pattern broke #610's dependency predicates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
