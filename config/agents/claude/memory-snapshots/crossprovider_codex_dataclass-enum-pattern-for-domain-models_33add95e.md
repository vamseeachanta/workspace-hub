---
name: crossprovider codex dataclass-enum-pattern-for-domain-models
description: Dataclass + Enum pattern for domain models
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python, type-safety, domain-modeling, architecture]
---

Constrained types (pipe grades, CRS types) should be Enums with value properties; geometric/configuration data should be dataclasses. This pattern enables type safety and reduces string-literal errors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
